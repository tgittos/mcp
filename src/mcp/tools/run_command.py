#!/usr/bin/env python3
"""
Tool for running shell commands and returning their output.
"""

async def run_command_tool(arguments):
    """Tool function for running shell commands"""
    command = arguments.get("command")

    if not command:
        raise ValueError("Missing command")

    try:
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        return {
            "output": [
                {
                    "type": "text",
                    "text": result.stdout
                }
            ],
            "error": result.stderr
        }
    except Exception as e:
        raise RuntimeError(f"Error running command: {str(e)}")

# Tool metadata for registration
run_command_metadata = {
    "name": "run_command",
    "description": "Run a shell command and return its output",
    "inputSchema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute"
            }
        },
        "required": ["command"]
    }
}
