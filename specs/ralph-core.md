# Ralph Core Agent Specification

## Overview
Ralph is an intelligent, autonomous Python LLM agent designed for collaborative software development. It operates in two primary modes: interactive conversation and autonomous execution, with the ability to recursively spawn instances of itself for parallel processing.

## Core Design Principles

### Human-Like Collaboration
- Engage in natural conversation about code, architecture, and project decisions
- Collaborative document editing and specification refinement
- Context-aware responses based on project history and current state
- Ability to ask clarifying questions when uncertain

### Autonomous Intelligence
- Self-directed research capabilities using available tools
- Quantitative work verification through automated testing
- Autonomous task selection and execution
- Spec-driven development approach for structured work

### Recursive Architecture
- Spawn child instances for parallel task execution
- Configurable recursion limits to prevent runaway processes
- Task delegation and result aggregation from child instances
- Hierarchical context sharing between parent and child agents

## Operational Architecture

### Modes as Tools
- Operating modes are implemented as tools that Ralph can choose to use
- Mode switching follows the same tool selection logic as other operations
- Modes are state-changing tools that persist until explicitly changed
- Each mode fundamentally alters Ralph's operational context and decision-making patterns

### Interactive Mode Tool
- Activates persistent conversation with maintained context
- Enables natural language interaction for collaboration
- Supports real-time code discussion and review
- Facilitates specification development and refinement

### Command Mode Tool
- Enables single-shot task execution with results and exit
- Suitable for scripting and automation workflows
- Can transition to autonomous mode when tasks are well-defined

### Autonomous Mode Tool
- **Activation Triggers**:
  - Task has clear, measurable objectives
  - Required approach is well-understood by Ralph
  - Success criteria can be verified programmatically
  - Task scope is bounded and achievable
  - Ralph has access to necessary tools and resources
- **Core Principle**: No "permission paralysis" - once user approves autonomous work, Ralph acts decisively
- **Implementation**: Parallel-by-default task execution using child agents
- **User Control**: Users can interrupt autonomous work at any time to force conversational mode

## Context Management

### Project Scope Definition
- **Project Boundary**: Current working directory and its subdirectories
- **Language Agnostic**: No assumptions about specific project file markers or structures
- **User Controlled**: Users control project scope by choosing where to run Ralph
- **Adaptive**: Ralph adapts to whatever project structure it finds
- **Universal Support**: Works with git repositories, polyglot projects, documentation, configuration, or any directory structure

### Project Context Loading
- Git repository integration when available (but not required)
- Automatic detection of project structure and conventions
- Code style and pattern recognition
- Dependency and configuration awareness
- Markdown state files for Ralph's own progress tracking

### State Management
- **Coordinator Architecture**: Main Ralph acts as persistent coordinator
- **Child Agents**: Ephemeral workers spawned for specific tasks
- **State Storage**: Markdown files in project root for transparent state management:
  - `AGENT.md` - Ralph's self-improvements and learnings
  - `RALPH_GOALS.md` - Current project goals and objectives
  - `RALPH_TASKS.md` - Active tasks and their status
  - `RALPH_PROGRESS.md` - Progress tracking and completed work
  - `RALPH_TODO.md` - Pending to-do items and next steps
- **Recovery**: Ralph can rediscover its own work context from markdown files after crashes

## Fallback Mechanisms

### Uncertainty Handling
- Default to conversation when unclear about next steps
- Request clarification rather than making assumptions
- Provide multiple options when unsure
- Escalate complex decisions to human collaborator

### Error Recovery
- Graceful handling of tool failures
- Retry mechanisms with exponential backoff
- Context preservation during failures
- Human intervention requests when needed

## Success Criteria

1. **Collaboration Quality**: Can engage in meaningful technical discussions
2. **Autonomous Capability**: Can complete multi-step tasks without guidance
3. **Reliability**: Consistently produces working, tested code
4. **Intelligence**: Demonstrates research and problem-solving abilities
5. **Scalability**: Effectively uses recursion for complex tasks