#!/usr/bin/env python3
"""
Tool for listing files in a directory, optionally recursively.
"""

import os
import json

async def list_files_tool(arguments):
    """Tool function for listing files in a directory"""
    directory_path = arguments.get("directory_path")
    recursive = arguments.get("recursive", False)

    if not directory_path:
        raise ValueError("Missing directory path")

    try:
        if recursive:
            file_list = [
                os.path.join(root, file)
                for root, _, files in os.walk(directory_path)
                for file in files
            ]
        else:
            file_list = [
                os.path.join(directory_path, file)
                for file in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, file))
            ]

        return json.dumps(file_list)
    except FileNotFoundError:
        raise RuntimeError(f"Directory not found: {directory_path}")
    except Exception as e:
        raise RuntimeError(f"Error listing files: {str(e)}")

# Tool metadata for registration
list_files_metadata = {
    "name": "list_files",
    "description": "List files in a directory, optionally recursively",
    "inputSchema": {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "The path to the directory to list files from"
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to list files recursively"
            }
        },
        "required": ["directory_path"]
    }
}