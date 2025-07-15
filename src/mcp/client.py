import asyncio
import json
import sys
from typing import Any, Dict
from loguru import logger

class MCPClient:
    """Client for interfacing with the MCP server"""

    def __init__(self, reader=None, writer=None):
        import io

        # Wrap binary streams with TextIOWrapper for consistent handling
        if reader and hasattr(reader, 'fileno'):
            self.reader = io.TextIOWrapper(reader, encoding='utf-8')
        else:
            self.reader = reader if reader else sys.stdin

        if writer and hasattr(writer, 'fileno'):
            self.writer = io.TextIOWrapper(writer, encoding='utf-8')
        else:
            self.writer = writer if writer else sys.stdout

    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server and receive the response"""
        # Write the request as a string
        self.writer.write(json.dumps(request) + "\n")
        self.writer.flush()

        # Read the response
        response_line = await asyncio.get_event_loop().run_in_executor(
            None, self.reader.readline
        )

        # Strip the response
        response_line = response_line.strip()

        return json.loads(response_line)

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