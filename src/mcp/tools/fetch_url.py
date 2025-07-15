#!/usr/bin/env python3
"""
Simple URL fetcher that retrieves content from a given URL and returns it as plain UTF-8 text.
"""

import httpx
from urllib.parse import urlparse
from html.parser import HTMLParser


class HTMLStripper(HTMLParser):
    """Utility class to strip HTML tags from content"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def reset(self):
        """Reset the parser state"""
        super().reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return ''.join(self.fed)

    def strip_html(self, html):
        """Strip HTML tags and return plain text"""
        self.reset()  # Reset state before processing
        self.feed(html)
        self.close()  # Close the parser
        return self.get_data()


async def fetch_url_tool(arguments):
    """Tool function for fetching URL content"""
    url = arguments.get("url")
    timeout = arguments.get("timeout", 10)

    def is_valid_url(url: str) -> bool:
        """Basic URL validation"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    if not url or not is_valid_url(url):
        raise ValueError("Invalid or missing URL")

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

            return {
                "content": [
                    {
                        "type": "text",
                        "text": plain_text
                    }
                ]
            }

        except httpx.RequestError as e:
            raise RuntimeError(f"Request failed: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error {e.response.status_code}: {e.response.text}")

# Tool metadata for registration
fetch_url_metadata = {
    "name": "fetch_url",
    "description": "Fetch content from a URL, strip HTML tags, and return it as plain UTF-8 text",
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
