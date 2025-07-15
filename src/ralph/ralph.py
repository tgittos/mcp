import sys
import subprocess
from dataclasses import dataclass
import dotenv
import os
import asyncio

from openai import OpenAI
from loguru import logger
from mcp.client import MCPClient
from mcp.server import MCPServer

dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger.add(sys.stderr, level="INFO", format="{time} {level} {message}")

def llm_completion(prompt, model="gpt-4o-mini", temperature=0.0, functions=[]):
    """Completes a prompt using the LLM, specifying available tools."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        functions=functions,
    )
    return response.choices[0].message.content


class Ralph:
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.is_complete = False
        self.mcp_client = MCPClient()

    async def execute(self):
        """Executes Ralph's task in a loop until completion."""
        try:
            tools_response = await self.mcp_client.list_tools()
            tools = tools_response.get("tools", [])

            formatted_tools = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                } for tool in tools
            ]

            response = llm_completion(self.prompt, functions=formatted_tools)

            print(f"LLM response: {response}")
        except RuntimeError as e:
            print(f"Error querying MCP server for tools: {e}")


if __name__ == "__main__":
    prompt = ""
    if len(sys.argv) < 2:
        if os.path.exists("AGENT.md"):
            with open("AGENT.md", "r") as f:
                prompt = f.read()
        else:
            print("No prompt provided and AGENT.md not found. Please provide a prompt or create an AGENT.md file.")
            exit(1)
    else:
        prompt = sys.argv[1]

    # start the MCP server in a separate process
    logger.info("Starting MCP server...")
    mcp_server_process = subprocess.Popen(
        [sys.executable, "src/mcp/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    ralph = Ralph(prompt)
    asyncio.run(ralph.execute())

    mcp_server_process.terminate()
    mcp_server_process.wait()
    sys.exit(0)
