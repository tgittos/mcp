software specifications are in ./specs
source code is in ./src
tests are in ./test

when discussing software with the user, suggest ideas and alternatives when appropriate
always document with high level of detail and precision
ensure you understand the context of the documentation you're writing fully, ask questions for clarity

update CLAUDE.md with insights and learnings whenever you find a way to make yourself more efficient

## Current Work Context
- **MVP Task List**: Detailed implementation tasks are documented in `./MVP_TASKS.md`
- **Progress Tracking**: Use TodoWrite tool to track task completion status
- **Current Phase**: Foundation phase - fixing critical architecture gaps
- **Priority Focus**: High-priority tasks (1-4) must be completed for basic functionality

# insights-and-learnings
MCP server architecture is ideal for Ralph's recursive agent system:
- Provides natural isolation between agent levels
- Enables permission inheritance with restrictions
- Allows distributed scaling of tool execution
- Circuit breaker patterns prevent cascade failures
- Tool discovery enables dynamic capability detection

## Open Source Library Preference
ALWAYS prefer existing open source libraries with strong community support over implementing functionality manually:
- Research existing Python libraries thoroughly before writing custom code
- Prioritize libraries with:
  - Active maintenance and recent commits
  - Strong community support (GitHub stars, contributors, issues activity)
  - Good documentation and examples
  - Mature APIs and stable releases
  - Type hints and modern Python practices
- Examples: Use `gitpython` for git operations, `click` for CLI, `pydantic` for validation
- Only implement custom solutions when no suitable library exists or when existing solutions have fundamental limitations
- Document library research process and selection rationale

DO NOT WRITE PLACEHOLDER CODE
DO **NOT** WRITE PLACEHOLDER CODE