# Ralph Core System Specification

## Overview
Ralph is a loop-based parallelized autonomous agent system that implements the Ralph Wiggum technique for AI-driven software development.

## Core Architecture

### Main Loop
- Loop until the task is complete
- Loops can spawn Ralph sub-processes that also loop until the sub-processes task is complete

### Memory Management
- **Primary Context Window**: ~156kb for main process
- **Subagent Context Windows**: ~156kb each with automatic garbage collection
- **Deterministic Allocation**: Same stack allocation every loop iteration

### Single Agent Process
- Monolithic architecture (no multi-agent communication)
- Single repository, single process
- One task per loop iteration
- Autonomous decision making for next priority item

## Core Components

### 1. Prompt Engine
- **File**: `PROMPT.md`
- **Purpose**: Contains current task instructions and context
- **Behavior**: Updated after each loop iteration with learnings
- **Format**: Markdown with clear task definitions

### 2. Agent Documentation
- **File**: `AGENT.md`
- **Purpose**: Stores learnings about build processes, commands, and optimizations
- **Behavior**: Continuously updated with discovered information
- **Format**: Brief, actionable documentation

### 3. Implementation Plan
- **File**: `IMPLEMENTATION_PLAN.md`
- **Purpose**: Prioritized list of tasks to be completed
- **Behavior**: Updated as tasks are completed or new issues discovered
- **Format**: Bullet-point list sorted by priority

### 4. Specifications Directory
- **Directory**: `specs/`
- **Purpose**: Contains all system specifications
- **Behavior**: Read-only during implementation phase
- **Format**: One markdown file per concern/topic

## Subagent Architecture

### Subagent Types
1. **Analysis Subagents**: Study code, specs, and requirements (up to 100 parallel)
2. **Research Subagents**: Load external information and documentation
3. **Implementation Subagents**: Write code and make changes (unlimited parallel)
4. **Build/Test Subagents**: Compile and test code (limited to 1 parallel)
5. **Documentation Subagents**: Update documentation and commit changes

### Subagent Memory Management
- Each subagent gets ~156kb context window
- Automatic garbage collection after task completion
- No state persistence between subagent executions

## Workflow Phases

### Phase 1: Requirements Gathering
- **Goal**: Define system requirements and create specifications
- **Memory Strategy**: Manual context window allocation
- **Output**: `specs/*.md` files
- **Subagents**: Research and specification writing

### Phase 2: Planning and Analysis
- **Goal**: Analyze requirements and create implementation plan
- **Memory Strategy**: Manual context window allocation
- **Input**: `specs/*.md` files
- **Output**: `IMPLEMENTATION_PLAN.md`
- **Subagents**: Code analysis and planning

### Phase 3: Incremental Implementation
- **Goal**: Execute implementation plan through continuous loops
- **Memory Strategy**: Automatic context window allocation
- **Input**: `IMPLEMENTATION_PLAN.md`, `PROMPT.md`, `AGENT.md`
- **Output**: Code changes, test results, documentation updates
- **Subagents**: Implementation, testing, documentation

## Key Principles

### 1. One Task Per Loop
- Each loop iteration handles exactly one task
- Task selection is autonomous based on priority
- No multi-tasking within single iteration

### 2. Deterministic Stack Allocation
- Same core items allocated to context every loop
- Specifications, plan, and current task always present
- Consistent memory layout across iterations

### 3. Trust in AI Reasoning
- Autonomous decision making for task priority
- Self-directed implementation approach
- Minimal human intervention during execution

### 4. Eventual Consistency
- Progress may not be linear
- Failures are learning opportunities
- Continuous refinement through prompt tuning

## File Structure
```
.
├── PROMPT.md                    # Current task and context
├── AGENT.md                     # Build process learnings
├── IMPLEMENTATION_PLAN.md       # Prioritized task list
├── specs/                       # System specifications
│   ├── ralph-core.md           # This file
│   ├── prompt-engine.md        # Prompt management system
│   ├── subagent-system.md      # Subagent architecture
│   ├── memory-management.md    # Context window handling
│   ├── workflow-phases.md      # Phase definitions
│   └── file-management.md      # File-based state management
└── src/                        # Implementation source code
```

## Success Criteria
- System can autonomously implement software projects
- Maintains consistent memory allocation across loops
- Successfully manages subagent parallelization
- Produces working code with tests
- Updates documentation and commits changes automatically
- Achieves 90% completion of greenfield projects 
