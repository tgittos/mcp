import sys
import subprocess
from dataclasses import dataclass
import dotenv
import os
import asyncio
import json

from openai import OpenAI
from loguru import logger
from mcp.client import MCPClient

dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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

    async def execute(self):
        """Executes Ralph's task in a loop until completion."""
        try:
            tools_response = await self.mcp_client.list_tools()
            tools = tools_response.get("result", {}).get("tools", [])

            formatted_tools = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                } for tool in tools
            ]

            messages = [
                {"role": "system", "content": self.agent},
                {"role": "user", "content": self.message}
            ]

            response = llm_completion(messages, functions=formatted_tools)

            while response.function_call:
                function_call = response.function_call
                function_name = function_call.name
                arguments = json.loads(function_call.arguments) if isinstance(function_call.arguments, str) else function_call.arguments

                if function_name and arguments:
                    logger.info(f"Function call detected: {function_name} with arguments {arguments}")

                    # Invoke the tool via MCP client
                    tool_response = await self.mcp_client.call_tool(function_name, arguments)
                    tool_content = tool_response.get("result", {}).get("content", [])

                    messages.append({
                        "role": "assistant",
                        "content": tool_content if tool_content else "Tool executed successfully."
                    })

                    response = llm_completion(
                        messages=messages,
                        functions=formatted_tools
                    )
                else:
                    logger.error("Invalid function call structure in response.")
            else:
                print(f"LLM response: {response.content}")
                messages.append({
                    "role": "assistant",
                    "content": response.content if response.content else "No content returned from LLM."
                })
        except RuntimeError as e:
            print(f"Error querying MCP server for tools: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ralph.py <message>")
        sys.exit(1)

    agent = "You are Ralph, an autonomous agent that specifies, plans, writes, and fixes software in Python."
    message = sys.argv[1]
    if os.path.exists("AGENT.md"):
        with open("AGENT.md", "r") as f:
            agent = f.read()

    # start the MCP server in a separate process
    logger.info("Starting MCP server...")
    mcp_server_process = subprocess.Popen(
        [sys.executable, "src/mcp/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    ralph = Ralph(agent, message, server_stdin=mcp_server_process.stdin, server_stdout=mcp_server_process.stdout)
    logger.info("Executing Ralph with provided prompt...")
    asyncio.run(ralph.execute())

    mcp_server_process.terminate()
    mcp_server_process.wait()
    sys.exit(0)

if __name__ == "__main__":
    main()