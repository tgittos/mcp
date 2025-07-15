You are building an autonomous programming agent called Ralph.

Ralph is implemented in Python and leverages uv to maintain packages and run commands. Use `uv run` to obtain a list of available uv commands.

Study specs/* to learn about the software specifications and FIX_PLAN.md to understand plan so far.

The source code of the software is in src/*. Study it.

First task is to study @FIX_PLAN.md (it may be incorrect) and is to use up to 500 Ralphs to study existing source code in src/ and compare it against the software specifications. From that create/update a @FIX_PLAN.md which is a bullet point list sorted in priority of the items which have yet to be implemeneted. Think extra hard. Consider searching for TODO, minimal implementations and placeholders. Study @FIX_PLAN.md to determine starting point for research and keep it up to date with items considered complete/incomplete using subagents.

When you learn something new about how to run the examples make sure you update @AGENT.md using a subagent but keep it brief. For example if you run commands multiple times before learning the correct command then that file should be updated.

For any bugs you notice, it's important to resolve them or document them in @FIX_PLAN.md to be resolved using a subagent even if it is unrelated to the current piece of work after documenting it in @FIX_PLAN.md

When the tests pass update the @FIX_PLAN.md, then add changed code and @FIX_PLAN.md with "git add -A" via bash then do a "git commit" with a message that describes the changes you made to the code. After the commit do a "git push" to push the changes to the remote repository.

As soon as there are no linting or test errors create a git tag. If there are no git tags start at 0.0.0 and increment patch by 1 for example 0.0.1 if 0.0.0 does not exist.