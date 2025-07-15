#!/usr/bin/env python3
"""
Tool for writing content to a file.
"""

async def write_file_tool(arguments):
    """Tool function for writing content to a file"""
    file_path = arguments.get("file_path")
    content = arguments.get("content")

    if not file_path or content is None:
        raise ValueError("Missing file path or content")

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        return {
            "status": "success",
            "message": f"Content written to {file_path}"
        }
    except Exception as e:
        raise RuntimeError(f"Error writing to file: {str(e)}")

# Tool metadata for registration
write_file_metadata = {
    "name": "write_file",
    "description": "Write content to a file",
    "inputSchema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to write to"
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file"
            }
        },
        "required": ["file_path", "content"]
    }
}
