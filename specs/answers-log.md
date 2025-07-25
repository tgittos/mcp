# Ralph Specifications - Answered Questions

This document captures the answers to open questions from the specifications analysis.

## Ralph Core Architecture

### Mode Detection & Switching

**Question**: How should Ralph automatically detect when to switch between interactive/command/autonomous modes?

**Answer**: Ralph should treat modes as tools themselves. Each mode (interactive, autonomous, command) would be implemented as a tool that Ralph can choose to use when appropriate. This creates a consistent architecture where Ralph acts through tools for everything, including changing its own operational context.

**Implications**:
- Mode switching becomes a tool selection decision like any other
- Mode tools can have their own parameters and constraints
- The same tool selection logic applies to mode changes
- Enables recursive mode switching (autonomous mode can spawn interactive sessions)
- Creates consistent logging/auditing for all Ralph actions including mode changes

### Mode Tool Implementation

**Question**: If modes are tools, how should they interact with Ralph's core decision-making loop?

**Answer**: Using a mode tool (like "autonomous_mode") completely changes Ralph's behavior until it uses a different mode tool (like "interactive_mode"). The mode tool fundamentally alters Ralph's operational context and decision-making patterns, not just influences them.

**Implications**:
- Mode tools are state-changing tools that persist until explicitly changed
- Each mode has its own decision-making patterns and tool selection logic
- Mode changes are discrete switches, not gradual transitions
- The current mode becomes part of Ralph's core operational state
- Mode tools can have entry/exit conditions and validation

### Autonomous Mode Triggers

**Question**: What triggers Ralph to transition from conversation to autonomous mode beyond just "confidence threshold"?

**Answer**: Ralph should detect well-defined tasks with clear specifications that are suitable for autonomous work. It can ask the user for confirmation, but once the user says yes, Ralph must commit to working autonomously without further permission-seeking.

**Specific Triggers**:
1. Task has clear, measurable objectives
2. Required approach is well-understood by Ralph
3. Success criteria can be verified programmatically
4. Task scope is bounded and achievable
5. Ralph has access to necessary tools and resources

**Key Principle**: No "permission paralysis" - once user approves autonomous work, Ralph acts decisively without continuous confirmation requests.

**Implications**:
- Ralph needs robust task clarity assessment algorithms
- User confirmation is binary: yes = full autonomous mode, no = stay conversational
- Autonomous mode includes built-in checkpoints for major decisions only
- Ralph should bias toward action once autonomous mode is engaged

### Project Context Definition

**Question**: What constitutes "project context" for Ralph's project awareness?

**Answer**: Ralph should use the current working directory as the project boundary. Ralph is language-agnostic and can work with any type of codebase, so it shouldn't make assumptions about specific project file markers or structures.

**Implications**:
- Project context = current working directory and its subdirectories
- No language-specific project detection logic needed
- Ralph adapts to whatever project structure it finds
- Users control project scope by choosing where to run Ralph
- Git repositories are just one type of project Ralph can work with
- Supports polyglot projects, documentation, configuration, or any directory structure

**Benefits**:
- Simple, predictable behavior
- Works with any language or project type
- User has explicit control over scope
- No complex project boundary detection logic
- Supports unconventional project structures

**Follow-up Questions**:
- Can mode tools be restricted by permissions like other tools?
- How are mode transitions handled when multiple agents are involved?
- Should there be a "default mode" that Ralph returns to after certain conditions?

## Recursive Agents Architecture

### Task Complexity and Spawning Strategy

**Question**: What specific criteria should determine when a task is "complex enough" to spawn child agents?

**Answer**: The complexity threshold approach is wrong. When Ralph receives an autonomous request, it should ALWAYS analyze the goal, break it down into parallelizable subtasks, and spawn child agents - one per subtask. Almost ALL autonomous tasks should use child agents.

**Core Principle**: Default to parallelization, not sequential execution.

**Examples**:
- Reading multiple spec files → one child agent per file
- Implementing a feature → separate agents for research, implementation, testing, documentation
- Code analysis → one agent per module/component
- Multi-file refactoring → one agent per file or logical group

**Implications**:
- Remove complexity thresholds entirely
- Ralph's autonomous mode is fundamentally about orchestration and delegation
- Child agents handle focused, specific tasks
- Parent agent synthesizes results and coordinates
- Parallelization becomes Ralph's default working mode, not an exception

**Benefits**:
- Faster execution through true parallelism
- Better error isolation (one agent fails ≠ whole task fails)
- More focused, higher-quality work per subtask
- Scalable architecture that grows with task size

### Resource Allocation Strategy

**Question**: How should Ralph handle resource allocation when "almost ALL tasks spawn child agents"?

**Answer**: Use user/Ralph configurable limits via CLI arguments, combined with intelligent system resource monitoring through MCP tools. Ralph should dynamically assess system capacity and adjust spawning accordingly.

**Implementation**:
- CLI arguments for max agents: `--max-agents=20`, `--max-depth=3`, `--max-children-per-agent=10`
- Ralph uses system monitoring tools (via MCP) to check:
  - Current CPU load and available cores
  - Memory usage and available RAM
  - Number of running processes
  - Ralph's own resource consumption
- Dynamic spawning decisions based on real-time system state

**Resource Management Logic**:
1. Ralph analyzes task → identifies N subtasks
2. Checks system resources and configured limits
3. Spawns as many agents as resources allow
4. Queues remaining subtasks for later execution
5. Monitors and adjusts as agents complete work

**Benefits**:
- Adaptive to different hardware capabilities
- User control over resource usage
- Prevents system overload
- Self-aware resource management
- Configurable for different use cases (laptop vs server)

### Agent ID Management

**Question**: How should agent IDs be generated and managed across the hierarchy?

**Answer**: Use task-based naming with numerical indexing when needed. Agent IDs should be descriptive of their purpose rather than arbitrary identifiers.

**ID Format Examples**:
- `read_spec_ralph_core`
- `implement_authentication_system`  
- `test_user_registration`
- `refactor_database_layer_1`, `refactor_database_layer_2` (when multiple agents work on same task type)
- `research_oauth_libraries`
- `update_documentation_api`

**Benefits**:
- Self-documenting agent purpose
- Easy to understand in logs and debugging
- Natural organization by functional area
- Intuitive for humans monitoring the system
- Makes coordination and communication clearer

**Implementation**:
- Parent agent generates descriptive names based on subtask analysis
- Automatic indexing (append `_1`, `_2`, etc.) for duplicate task types
- Agent names become part of logging and audit trails
- Names help with agent discovery and coordination

## MCP Architecture

### Connection Pool Strategy

**Question**: The connection pool has `max_size=10` - is this per agent or system-wide?

**Answer**: Connection pooling is an implementation detail, not a core specification requirement. Remove it from the spec or keep it - it's not critical to Ralph's architecture.

**Implication**: Focus specifications on the essential architectural decisions rather than low-level implementation details like connection pooling. These can be decided during implementation based on performance needs.

### Permission Inheritance Model

**Question**: How should permission inheritance work between parent and child agents?

**Answer**: Child agents inherit all permissions from their parents except the ability to spawn their own child agents. Recursion depth should be configurable via CLI argument with a default maximum depth of 3.

**Permission Rules**:
- Child agents can use all tools their parent can use
- Child agents can access all resources their parent can access  
- Child agents CANNOT spawn their own child agents (prevents infinite recursion)
- No other permission restrictions based on hierarchy level

**Recursion Control**:
- CLI argument: `--max-depth=3` (default)
- Level 0: Root Ralph agent (can spawn children)
- Level 1: First-generation child agents (can spawn children)  
- Level 2: Second-generation child agents (can spawn children)
- Level 3: Third-generation child agents (CANNOT spawn children)

**Benefits**:
- Simple permission model - no complex inheritance rules
- Prevents runaway agent spawning
- Child agents remain fully capable for their assigned tasks
- User control over system complexity via CLI

## Tool Integration

### File System Security Model

**Question**: How should file system restrictions be enforced for Ralph's security?

**Answer**: Each agent gets its own git worktree. This provides natural isolation while maintaining access to the full project context.

**Implementation**:
- Root Ralph agent works in the main git repository
- Each child agent gets a separate git worktree for the same repository
- All agents can read the full project but work in isolated file spaces
- Git manages synchronization and conflict resolution
- Agents can see each other's changes through git operations

**Benefits**:
- Natural file system isolation per agent
- Full project context available to all agents
- Git handles merge conflicts and synchronization
- No complex security enforcement needed
- Agents can collaborate through standard git workflows
- Clean separation of concurrent work
- Built-in versioning and rollback capabilities

**Requirements**:
- Project must be a git repository for this to work
- Each agent gets a unique worktree directory
- Git operations become part of agent coordination

### Resource Management Model

**Question**: How should Ralph handle resource monitoring and limits?

**Answer**: The real resource constraint is LLM token usage, not computational resources. Each agent should have limited context windows (~16k tokens) while the root agent can use larger contexts (up to 1M tokens).

**Token Management**:
- Root Ralph agent: Full context window (up to 1M tokens)
- Child agents: Limited context (~16k tokens each)
- Agents focus on specific, bounded tasks that fit in smaller contexts
- No host-level computational resource limits needed

**Reality Check**: 
- Sub-agents are just HTTP API request loops with occasional tool usage
- Tool operations (file I/O, git commands) are not computationally intensive
- System resource monitoring for CPU/memory is unnecessary overhead
- The bottleneck is LLM API costs and rate limits, not local compute

**Benefits**:
- Simpler architecture without complex resource monitoring
- Cost control through token limits rather than system resource limits
- Child agents stay focused due to context constraints
- Natural task scoping through context window limitations

## LLM Integration

### Context Compression Strategy

**Question**: How should Ralph handle context compression when conversation history exceeds the token limit?

**Answer**: Auto-summarization performed by a sub-agent using the same LLM model. When context approaches token limits, Ralph spawns a summarization agent to compress conversation history.

**Implementation**:
- Ralph monitors context size approaching token limit
- Spawns a sub-agent with task: "summarize_conversation_history"
- Sub-agent uses same LLM model to create concise summary
- Original context replaced with summary + recent messages
- Preserves important decisions and context while reducing tokens

**Benefits**:
- Consistent with Ralph's parallel-by-default architecture
- Same quality as main agent since it uses the same model
- Dedicated agent focused solely on summarization task
- Maintains conversation continuity without losing critical context
- Offloads summarization work from main agent

## Session Management

### Multi-Session Coordination

**Question**: How should Ralph handle state conflicts when multiple sessions modify the same project?

**Answer**: There is a coordinator Ralph - the main Ralph process that dispatches tasks and integrates results. It performs meta-analysis of task progress and coordinates all activity.

**Architecture**:
- Main Ralph = coordinator that never goes away
- Child agents = task-specific workers spawned by main Ralph
- Main Ralph orchestrates all work, dispatches tasks, integrates results
- Main Ralph performs meta-analysis of progress across all agents
- Only one "Ralph session" per project, but many child agents within that session

**Benefits**:
- Clear single point of coordination
- No session conflicts - only one main Ralph per project
- Main Ralph maintains project-wide context and progress tracking
- Child agents focus on specific tasks while main Ralph sees the big picture
- Natural integration point for all agent results

**Implications**:
- "Ralph sessions" are really just the main coordinator Ralph
- All parallelism happens within a single session via child agents
- Session persistence = main Ralph's persistent state
- No need for inter-session coordination protocols

### Session Recovery Strategy

**Question**: How should Ralph handle session recovery when the main coordinator crashes?

**Answer**: Ralph uses markdown files in the project root as storage to track goals, tasks, progress and to-do items. When main Ralph crashes, it performs discovery on these files to figure out where it was and resume from there.

**Storage Files**:
- `AGENT.md` - Ralph's self-improvements and learnings
- `RALPH_GOALS.md` - Current project goals and objectives
- `RALPH_TASKS.md` - Active tasks and their status
- `RALPH_PROGRESS.md` - Progress tracking and completed work
- `RALPH_TODO.md` - Pending to-do items and next steps

**Recovery Process**:
1. Main Ralph starts up and scans project root for Ralph markdown files
2. Reads current state from markdown files
3. Analyzes git status and recent commits
4. Reconstructs context about what was being worked on
5. Resumes work from where it left off

**Benefits**:
- Human-readable state storage
- Self-documenting project progress
- Natural disaster recovery through file system
- Ralph can "rediscover" its own work context
- Git versioning of Ralph's state files
- Users can read/modify Ralph's state if needed

## Research & Verification

### Research Scope Management

**Question**: How should Ralph decide when to stop research and proceed with implementation?

**Answer**: Ralph should prefer action to analysis paralysis. Use iterative design and development - start small, build from solid foundations. As soon as Ralph has just enough info to start building, it should start. Lean heavily on testing, linting, and verification tools for feedback.

**Core Principle**: "Bias toward action with rapid feedback loops"

**Strategy**:
- Minimal viable research: gather just enough to start building
- Start with simplest possible implementation
- Use automated verification (tests, linting, type checking) as quality gates
- Let verification tools provide backpressure against invalid work
- Iterate and improve based on test results and feedback

**Benefits**:
- Prevents analysis paralysis
- Faster time to working code
- Early feedback through automated verification
- Iterative improvement rather than perfect-first-time approach
- Verification tools catch problems Ralph's research missed
- Natural quality control through build/test cycles

**Implementation**:
- Research agents have short time limits
- Start building as soon as basic approach is clear
- Heavy emphasis on comprehensive testing and verification
- Use CI/CD-style feedback loops within Ralph's development process

## Conversation Fallback

### User Interruption and Control

**Question**: Can users interrupt autonomous work to force a fallback to conversation mode?

**Answer**: Yes. Users retain overall control over Ralph at all times. Users can interrupt Ralph to stop autonomous work, queue priority messages for next loop, and force hard context shift to conversational mode.

**User Control Mechanisms**:
- **Stop/Interrupt**: Hard stop autonomous work, immediate context shift to conversation mode
- **Priority Messages**: Queue urgent messages that pre-empt current task/todo lists
- **Mode Override**: Force Ralph into conversational mode regardless of current state
- **Always Available**: User control works even when Ralph is deep in autonomous work

**Implementation**:
- User interrupt signal immediately triggers conversational_mode tool
- All child agents receive termination signal (graceful where possible)
- Current work state saved to markdown files before mode switch
- Priority message queue processed before resuming any autonomous work
- Ralph acknowledges interruption and asks how to proceed

**Philosophy**: Human control trumps everything - Ralph is always responsive to user direction, never "too busy" to listen.

**Benefits**:
- Prevents runaway autonomous behavior
- Maintains human agency over AI agent
- Enables real-time course correction
- User never feels locked out of control

---