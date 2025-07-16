import sys
import subprocess
from dataclasses import dataclass
import dotenv
import os
import asyncio
import json
from typing import List

from openai import OpenAI
from loguru import logger
from mcp.client import MCPClient

dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time} {level} {message}")

def llm_completion(messages, model="gpt-4o-mini", temperature=0.0, functions=[]):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        functions=functions,
    )
    return response.choices[0].message

class Ralph:
    def __init__(self, agent: str, message: str, server_stdin=None, server_stdout=None):
        self.agent = agent
        self.message = message
        self.mcp_client = MCPClient(reader=server_stdout, writer=server_stdin)
        self.plan_file = "fix_plan.md"
        self.impl_plan_file = "IMPLEMENTATION_PLAN.md"

    async def read_file(self, path: str) -> str:
        try:
            resp = await self.mcp_client.call_tool("read_file", {"path": path})
            return resp.get("result", {}).get("content", "")
        except Exception as e:
            logger.warning(f"Could not read {path}: {e}")
            return ""

    async def read_plan(self) -> List[str]:
        content = await self.read_file(self.plan_file)
        return [line.strip() for line in content.splitlines() if line.strip()]

    async def write_plan(self, items: List[str]):
        content = "\n".join(items) + "\n"
        await self.mcp_client.call_tool("write_file", {"path": self.plan_file, "content": content})

    def select_top_item(self, items: List[str]) -> int:
        for idx, item in enumerate(items):
            if not item.lstrip().startswith("[x] "):
                return idx
        return -1

    def mark_item_done(self, items: List[str], idx: int) -> List[str]:
        if 0 <= idx < len(items):
            item = items[idx]
            if not item.lstrip().startswith("[x] "):
                stripped = item.lstrip('-* ').strip()
                items[idx] = f"[x] {stripped}"
        return items

    def plan_needs_update(self, items: List[str]) -> bool:
        return not items or all(item.lstrip().startswith("[x] ") for item in items)

    async def gather_context(self, narrow_to_files: List[str] = None) -> str:
        context_parts = []
        paths = [self.plan_file, self.impl_plan_file]

        for path in paths:
            content = await self.read_file(path)
            if content:
                context_parts.append(f"--- {path} ---\n{content}")

        try:
            resp = await self.mcp_client.call_tool("list_files", {"path": "specs"})
            for f in resp.get("result", {}).get("files", []):
                if f.endswith(".md") and (not narrow_to_files or f"specs/{f}" in narrow_to_files):
                    spec_content = await self.read_file(f"specs/{f}")
                    context_parts.append(f"--- specs/{f} ---\n{spec_content}")
        except Exception as e:
            logger.warning(f"Failed to load specs: {e}")

        return "\n\n".join(context_parts)

    async def spawn_subralphs(self, jobs: list[dict]) -> list[dict]:
        return await asyncio.gather(*[
            self.mcp_client.call_tool("ralph", {
                "messages": [job["task"]],
                "context": job.get("context", ""),
                "metadata": job.get("metadata", {})
            }) for job in jobs
        ])

    async def verify_code(self) -> bool:
        lint = subprocess.run(["ruff", "."], capture_output=True, text=True)
        if lint.returncode != 0:
            logger.error("Ruff failed:\n" + lint.stdout)
            return False

        test = subprocess.run(["pytest"], capture_output=True, text=True)
        if test.returncode != 0:
            logger.error("Pytest failed:\n" + test.stdout)
            return False

        return True

    async def plan_subtasks(self, goal: str, context: str) -> List[str]:
        messages = [
            {"role": "system", "content": self.agent},
            {"role": "user", "content": f"Given the goal:\n{goal}\n\nAnd context:\n{context}\n\nBreak the goal into specific implementation subtasks. Return a bullet list."}
        ]
        reply = llm_completion(messages)
        content = reply.get("content", "")
        return [line.strip("-* ").strip() for line in content.splitlines() if line.strip().startswith(("-", "*"))]

    async def git_commit_and_push(self, message: str):
        subprocess.run(["git", "add", "-A"])
        subprocess.run(["git", "commit", "-m", message])
        subprocess.run(["git", "push"])

    async def git_tag_and_push(self):
        tags = subprocess.run(["git", "tag"], capture_output=True, text=True).stdout.splitlines()
        if not tags:
            next_tag = "0.0.0"
        else:
            parts = [int(p) for p in tags[-1].strip().split(".")]
            parts[-1] += 1
            next_tag = ".".join(str(p) for p in parts)
        subprocess.run(["git", "tag", next_tag])
        subprocess.run(["git", "push", "--tags"])

    async def plan_mode(self):
        logger.info("Running Ralph in PLAN mode")
        context = await self.gather_context()

        logger.info("Dispatching sub-Ralphs to analyze specs and implementation...")

        spec_jobs = [
            {"task": "Extract all requirements from spec specs/" + f, "context": context}
            for f in os.listdir("specs") if f.endswith(".md")
        ]
        impl_jobs = [
            {"task": "Analyze all implemented features in src/" + f, "context": context}
            for f in os.listdir("src") if f.endswith(".py")
        ]
        await self.spawn_subralphs(spec_jobs + impl_jobs)

        planning_messages = [
            {"role": "system", "content": self.agent},
            {"role": "user", "content": f"Study the specs and implementation code. Return a prioritized task list for fix_plan.md.

Context:
{context}"}
        ]
        reply = llm_completion(planning_messages)
        content = reply.get("content", "")
        new_items = [line.strip("-* ").strip() for line in content.splitlines() if line.strip().startswith(("-", "*"))]

        existing_items = await self.read_plan()
        completed_items = [item for item in existing_items if item.startswith("[x] ")]
        incomplete_items = [item for item in existing_items if not item.startswith("[x] ")]

        merged = completed_items[:]
        seen = set(line.lstrip("[x] -* ").strip() for line in completed_items + incomplete_items)
        for item in new_items:
            if item not in seen:
                merged.append(item)
                seen.add(item)

        await self.write_plan(merged)
        logger.info("Plan written to fix_plan.md")

    async def execute(self):
        try:
            plan_items = await self.read_plan()
            if self.plan_needs_update(plan_items):
                logger.info("Plan missing, empty, or complete. Triggering plan mode.")
                await self.plan_mode()
                plan_items = await self.read_plan()

            idx = self.select_top_item(plan_items)
            if idx == -1:
                logger.info("All plan items complete.")
                return

            goal = plan_items[idx]
            logger.info(f"Working on: {goal}")

            context = await self.gather_context()

            

            logger.info("Creating subtask plan...")
            sub_tasks = await self.plan_subtasks(goal, context)
            if not sub_tasks:
                logger.warning("No subtasks generated.")
                return

            logger.info("Dispatching sub-Ralphs to implement subtasks...")
            await self.spawn_subralphs([
                {"task": task, "context": context} for task in sub_tasks
            ])

            if await self.verify_code():
                plan_items = self.mark_item_done(plan_items, idx)
                await self.write_plan(plan_items)
                await self.git_commit_and_push(f"Completed: {goal}")
                await self.git_tag_and_push()

        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ralph.py <message>")
        sys.exit(1)

    agent = "You are Ralph, an autonomous agent that specifies, plans, writes, and fixes software."
    message = sys.argv[1]
    if os.path.exists("AGENT.md"):
        with open("AGENT.md", "r") as f:
            agent = f.read()

    mcp_server_process = subprocess.Popen(
        [sys.executable, "src/mcp/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    ralph = Ralph(agent, message, server_stdin=mcp_server_process.stdin, server_stdout=mcp_server_process.stdout)
    asyncio.run(ralph.execute())

    mcp_server_process.terminate()
    mcp_server_process.wait()
    sys.exit(0)

if __name__ == "__main__":
    main()
