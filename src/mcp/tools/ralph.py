"""
Tool for starting multiple Ralph subprocesses with given user messages.
"""

import asyncio
import sys

async def ralph(arguments):
    """Tool function for starting Ralph subprocesses."""
    messages = arguments.get("messages")

    if not messages or not isinstance(messages, list):
        raise ValueError("Missing or invalid messages list")

    if len(messages) > 500:
        raise ValueError("Number of messages exceeds the limit of 500")

    results = {}

    async def run_ralph(message):
        """Run a single Ralph subprocess and collect its output."""
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "src/ralph/ralph.py",
            message,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return stderr.decode("utf-8")

        return stdout.decode("utf-8")

    tasks = [run_ralph(message) for message in messages]
    outputs = await asyncio.gather(*tasks)

    for message, output in zip(messages, outputs):
        results[message] = output

    return {
        "result": results
    }

# Tool metadata for registration
ralph_metadata = {
    "name": "ralph",
    "description": "Starts a Ralph with a given task, one per Ralph",
    "inputSchema": {
        "type": "object",
        "properties": {
            "messages": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of tasks to pass to Ralph subprocesses, one per Ralph subprocess."
            }
        },
        "required": ["messages"]
    }
}