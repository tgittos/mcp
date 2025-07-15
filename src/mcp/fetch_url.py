#!/usr/bin/env python3
"""
Simple MCP server that fetches URL content and returns it as UTF-8 text.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import httpx
from urllib.parse import urlparse
from html.parser import HTMLParser


class HTMLStripper(HTMLParser):
    """Utility class to strip HTML tags from content"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

    def strip_html(self, html):
        self.feed(html)
        return self.get_data()


class MCPServer:
    """Simple MCP server implementation"""
    
    def __init__(self):
        self.tools = {
            "fetch_url": {
                "name": "fetch_url",
                "description": "Fetch content from a URL and return it as UTF-8 text",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to fetch content from"
                        },
                        "timeout": {
                            "type": "number",
                            "description": "Request timeout in seconds (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["url"]
                }
            }
        }
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    async def _fetch_url_content(self, url: str, timeout: float = 10) -> str:
        """Fetch content from URL, strip HTML, and return as plain text"""
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Try to decode as UTF-8, with fallback handling
                try:
                    content = response.content.decode('utf-8')
                except UnicodeDecodeError:
                    # Try to detect encoding from response headers
                    encoding = response.encoding or 'utf-8'
                    content = response.content.decode(encoding, errors='replace')

                # Strip HTML tags
                stripper = HTMLStripper()
                plain_text = stripper.strip_html(content)

                return plain_text

            except httpx.RequestError as e:
                raise RuntimeError(f"Request failed: {str(e)}")
            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"HTTP error {e.response.status_code}: {e.response.text}")
    
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
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "fetch_url":
                    url = arguments.get("url")
                    timeout = arguments.get("timeout", 10)
                    
                    if not url:
                        raise ValueError("URL is required")
                    
                    content = await self._fetch_url_content(url, timeout)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": content
                                }
                            ]
                        }
                    }
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
            
            elif method == "notifications/initialized":
                # No response needed for notifications
                return None
            
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
    asyncio.run(server.run())



if __name__ == "__main__":
    main()