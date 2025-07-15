#!/usr/bin/env python3
"""
Tool for reading file content and returning it as plain UTF-8 text.
"""

async def read_file_tool(arguments):
    """Tool function for reading file content"""
    file_path = arguments.get("file_path")

    if not file_path:
        raise ValueError("Missing file path")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        return {
            "content": [
                {
                    "type": "text",
                    "text": content
                }
            ]
        }
    except FileNotFoundError:
        raise RuntimeError(f"File not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading file: {str(e)}")

# Tool metadata for registration
read_file_metadata = {
    "name": "read_file",
    "description": "Read content from a file and return it as plain UTF-8 text",
    "inputSchema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read"
            }
        },
        "required": ["file_path"]
    }
}
