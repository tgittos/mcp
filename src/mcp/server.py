import asyncio
import json
import sys
from typing import Any, Dict

from loguru import logger
from mcp.tools.fetch_url import fetch_url_tool, fetch_url_metadata
from mcp.tools.read_file import read_file_tool, read_file_metadata
from mcp.tools.write_file import write_file_tool, write_file_metadata
from mcp.tools.run_command import run_command_tool, run_command_metadata
from mcp.tools.list_files import list_files_tool, list_files_metadata
from mcp.tools.ralph import ralph, ralph_metadata

class MCPServer:
    """Simple MCP server implementation"""

    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, tool_function: Any, description: str, input_schema: Dict[str, Any]):
        """Register a tool with the server"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "function": tool_function
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "url-fetcher",
                            "version": "1.0.0"
                        }
                    }
                }

            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": tool["name"],
                                "description": tool["description"],
                                "inputSchema": tool["inputSchema"]
                            } for tool in self.tools.values()
                        ]
                    }
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    result = await tool["function"](arguments)
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

            elif method == "notifications/initialized":
                # No response needed for notifications
                return {}

            else:
                raise ValueError(f"Unknown method: {method}")

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    async def run(self):
        """Run the MCP server"""
        logger.info("Starting MCP server...")
        logger.info(f"Available tools: {', '.join(self.tools.keys())}")
        while True:
            try:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                try:
                    request = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                # Handle the request
                response = await self.handle_request(request)

                # Log the response for debugging
                logger.debug(f"Sending response: {response}")

                # Send response to stdout (if not None)
                if response is not None:
                    print(json.dumps(response), flush=True)

            except KeyboardInterrupt:
                break
            except Exception as e:
                # Log error but continue running
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Server error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

def main():
    """Synchronous wrapper for the asynchronous main function."""
    server = MCPServer()

    # Register fetch_url tool
    server.register_tool(
        name=fetch_url_metadata["name"],
        tool_function=fetch_url_tool,
        description=fetch_url_metadata["description"],
        input_schema=fetch_url_metadata["inputSchema"]
    )

    # Register read_file tool
    server.register_tool(
        name=read_file_metadata["name"],
        tool_function=read_file_tool,
        description=read_file_metadata["description"],
        input_schema=read_file_metadata["inputSchema"]
    )

    # Register write_file tool
    server.register_tool(
        name=write_file_metadata["name"],
        tool_function=write_file_tool,
        description=write_file_metadata["description"],
        input_schema=write_file_metadata["inputSchema"]
    )

    # Register run_command tool
    server.register_tool(
        name=run_command_metadata["name"],
        tool_function=run_command_tool,
        description=run_command_metadata["description"],
        input_schema=run_command_metadata["inputSchema"]
    )

    # Register list_files tool
    server.register_tool(
        name=list_files_metadata["name"],
        tool_function=list_files_tool,
        description=list_files_metadata["description"],
        input_schema=list_files_metadata["inputSchema"]
    )

    # Register ralph tool
    server.register_tool(
        name=ralph_metadata["name"],
        tool_function=ralph,
        description=ralph_metadata["description"],
        input_schema=ralph_metadata["inputSchema"]
    )

    asyncio.run(server.run())

if __name__ == "__main__":
    main()