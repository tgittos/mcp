import asyncio
import json
import sys
from typing import Any, Dict

class MCPClient:
    """Client for interfacing with the MCP server"""

    def __init__(self):
        self.reader = sys.stdin
        self.writer = sys.stdout

    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server and receive the response"""
        self.writer.write(json.dumps(request) + "\n")
        self.writer.flush()

        response_line = await asyncio.get_event_loop().run_in_executor(
            None, self.reader.readline
        )

        return json.loads(response_line.strip())

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from the server"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }
        return await self.send_request(request)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool on the server"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 2
        }
        return await self.send_request(request)