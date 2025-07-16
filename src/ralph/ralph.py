import sys
import subprocess
from dataclasses import dataclass
import dotenv
import os
import asyncio
import json
from typing import List

from openai import OpenAI
from loguru import logger
from mcp.client import MCPClient

dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time} {level} {message}")


def llm_completion(messages, model="gpt-4o-mini", temperature=0.0, functions=[]):
    """Completes a prompt using the LLM, specifying available tools."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        functions=functions,
    )
    return response.choices[0].message

class Ralph:
    def __init__(self, agent: str, message: str, server_stdin=None, server_stdout=None):
        self.messages = []
        self.agent = agent
        self.message = message
        self.mcp_client = MCPClient(reader=server_stdout, writer=server_stdin)
        self.plan_file = "fix_plan.md"

    async def read_plan(self) -> List[str]:
        """Reads the plan file and returns a list of plan items (lines)."""
        try:
            response = await self.mcp_client.call_tool("read_file", {"path": self.plan_file})
            content = response.get("result", {}).get("content", "")
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            return lines
        except Exception as e:
            logger.warning(f"Plan file not found or error reading: {e}. Creating new plan file.")
            await self.write_plan([])
            return []

    async def write_plan(self, items: List[str]):
        """Writes the plan items back to the plan file."""
        content = "\n".join(items) + "\n"
        await self.mcp_client.call_tool("write_file", {"path": self.plan_file, "content": content})

    def select_top_item(self, items: List[str]) -> int:
        """Selects the index of the top unresolved item (not marked as done)."""
        for idx, item in enumerate(items):
            if not item.lstrip().startswith("[x] "):
                return idx
        return -1

    def mark_item_done(self, items: List[str], idx: int) -> List[str]:
        """Marks the item at idx as done."""
        if 0 <= idx < len(items):
            item = items[idx]
            if not item.lstrip().startswith("[x] "):
                # Replace leading '- ' or '* ' or nothing with '[x] '
                stripped = item.lstrip('-* ').strip()
                items[idx] = f"[x] {stripped}"
        return items

    def plan_needs_update(self, items: List[str]) -> bool:
        """Stub: Returns True if the plan needs to be updated (e.g., empty or stale)."""
        return not items  # For now, only checks if plan is empty

    async def generate_or_update_plan(self) -> List[str]:
        """Stub: Generates or updates the plan. For now, returns a placeholder plan."""
        logger.info("Planning phase: generating a new plan.")
        # In a real implementation, this would analyze the codebase, etc.
        return ["- Implement feature X", "- Fix bug Y", "- Refactor module Z"]

    async def act_on_item(self, item: str):
        """Uses the LLM to reason about the plan item and call tools as needed."""
        # Discover available tools
        tools_response = await self.mcp_client.list_tools()
        tools = tools_response.get("result", {}).get("tools", [])
        formatted_tools = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            } for tool in tools
        ]
        logger.info(f"Available tools: {', '.join(tool['name'] for tool in formatted_tools)}")

        messages = [
            {"role": "system", "content": self.agent},
            {"role": "user", "content": item}
        ]

        logger.debug(f"Ralph: {self.agent}")
        logger.debug(f"Plan item: {item}")

        response = llm_completion(messages, functions=formatted_tools)

        while getattr(response, 'function_call', None):
            function_call = response.function_call
            messages.append(response.model_dump())
            function_name = function_call.name
            arguments = json.loads(function_call.arguments) if isinstance(function_call.arguments, str) else function_call.arguments
            logger.info(f"Calling function: {function_name} with arguments: {arguments}")
            if function_name and arguments is not None:
                tool_response = await self.mcp_client.call_tool(function_name, arguments)
                tool_content = tool_response.get("result", {})
                messages.append({
                    "role": "assistant",
                    "content": tool_content if isinstance(tool_content, str) else json.dumps(tool_content)
                })
                response = llm_completion(
                    messages=messages,
                    functions=formatted_tools
                )
            else:
                logger.error("Invalid function call structure in response.")
                break
        else:
            logger.info(f"Assistant: {response.content if response.content else 'No content returned from LLM.'}")
            messages.append({
                "role": "assistant",
                "content": response.content if response.content else "No content returned from LLM."
            })

    async def execute(self):
        """Executes Ralph's plan-driven loop with planning-to-working transition and LLM tool orchestration."""
        try:
            while True:
                plan_items = await self.read_plan()
                if self.plan_needs_update(plan_items):
                    logger.info("Plan is missing or needs update. Entering planning phase.")
                    plan_items = await self.generate_or_update_plan()
                    await self.write_plan(plan_items)
                idx = self.select_top_item(plan_items)
                if idx == -1:
                    logger.info("All plan items are complete! Exiting.")
                    break
                current_item = plan_items[idx]
                await self.act_on_item(current_item)
                plan_items = self.mark_item_done(plan_items, idx)
                await self.write_plan(plan_items)
        except RuntimeError as e:
            print(f"Error querying MCP server for tools: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ralph.py <message>")
        sys.exit(1)

    agent = "You are Ralph, an autonomous agent that specifies, plans, writes, and fixes software."
    message = sys.argv[1]
    if os.path.exists("AGENT.md"):
        with open("AGENT.md", "r") as f:
            agent = f.read()

    # start the MCP server in a separate process
    mcp_server_process = subprocess.Popen(
        [sys.executable, "src/mcp/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    ralph = Ralph(agent, message, server_stdin=mcp_server_process.stdin, server_stdout=mcp_server_process.stdout)
    asyncio.run(ralph.execute())

    mcp_server_process.terminate()
    mcp_server_process.wait()
    sys.exit(0)

if __name__ == "__main__":
    main()
