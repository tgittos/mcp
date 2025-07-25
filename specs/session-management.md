# Ralph Session Management Specification

## Overview
Ralph's session management system handles persistent interactions, context maintenance, and seamless transitions between conversation and autonomous work modes.

## Session Types

### Interactive Sessions (`ralph chat`)
- **Initialization**: Detect project context from current directory
- **State Persistence**: Maintain conversation history and project state
- **Context Loading**: Load relevant project files, git status, and previous sessions
- **Exit Handling**: Gracefully save state and provide session summary

### Command Sessions (`ralph "task"`)
- **Quick Execution**: Single-shot command processing
- **Context Inference**: Automatically load minimal required context
- **Result Output**: Structured response format for scripting
- **State Preservation**: Update project state without persistent session

## Context Management

### Project Context Detection
```
On session start:
1. Detect git repository (if any)
2. Identify project type (Python, Node.js, etc.)
3. Load project configuration files
4. Analyze directory structure
5. Check for existing Ralph state/memory
```

### Conversation Context
- **Message History**: Store complete conversation with metadata
- **Decision Trail**: Track important decisions and their rationale  
- **Code Changes**: Link conversations to actual file modifications
- **Reference Tracking**: Maintain references between related discussions

### Working Memory
- **Active Files**: Files currently being discussed or modified
- **Task Queue**: Pending tasks and their priorities
- **Research Notes**: Information gathered during autonomous research
- **Test Results**: Verification outcomes and metrics

## State Persistence

### Markdown State Storage
Ralph uses human-readable markdown files in the project root for transparent state management:

- **`AGENT.md`** - Ralph's self-improvements and learnings
- **`RALPH_GOALS.md`** - Current project goals and objectives  
- **`RALPH_TASKS.md`** - Active tasks and their status
- **`RALPH_PROGRESS.md`** - Progress tracking and completed work
- **`RALPH_TODO.md`** - Pending to-do items and next steps

### Benefits of Markdown Storage
- **Human-readable**: Users can read and understand Ralph's state
- **Version controlled**: Git tracks changes to Ralph's state files
- **Self-documenting**: Project progress is automatically documented
- **Disaster recovery**: Ralph can rediscover context from files
- **Transparent**: No hidden or binary state storage
- **Editable**: Users can modify Ralph's state if needed

## Coordinator Architecture

### Single Session Model
- **Main Ralph**: Persistent coordinator that orchestrates all work
- **Child Agents**: Ephemeral workers spawned by main Ralph for specific tasks
- **No Multi-Session Conflicts**: Only one main Ralph per project
- **Session = Coordinator**: "Ralph sessions" are really just the main coordinator Ralph
- **All Parallelism**: Happens within a single session via child agents

### Session Recovery Process
1. **Startup Discovery**: Main Ralph scans project root for Ralph markdown files
2. **State Reconstruction**: Reads current state from markdown files
3. **Git Analysis**: Analyzes git status and recent commits
4. **Context Rebuilding**: Reconstructs what was being worked on
5. **Resume Operation**: Continues work from where it left off

### User Interruption System
- **Always Available**: Users can interrupt Ralph at any time
- **Hard Stop**: Immediate context shift to conversational mode
- **Priority Queue**: Users can queue urgent messages that pre-empt current work
- **State Preservation**: Current work state saved to markdown files before mode switch
- **Human Control**: User control trumps everything - Ralph never "too busy" to listen

## State Recovery

### Crash Recovery Strategy
- **Automatic Discovery**: Ralph rediscovers its own work context from markdown files
- **No Complex Checkpoints**: State is continuously maintained in markdown files
- **Self-Documenting Recovery**: Ralph can understand what it was doing from its own documentation
- **Git Integration**: Recent commits provide additional context about work state

### Recovery Advantages
- **Transparent Recovery**: Users can see exactly what Ralph recovers
- **Manual Override**: Users can edit markdown files to guide recovery
- **Natural Backup**: Git provides versioning of Ralph's state files
- **No Data Loss**: Human-readable state means nothing is hidden in binary formats

## Multi-Session Coordination

### Parallel Sessions
- Session isolation to prevent conflicts
- Shared project state with conflict resolution
- Cross-session communication for coordination

### Session Handoff
- Transfer context between sessions
- Merge conversation histories
- Consolidate project state changes

## Performance Considerations

### Context Window Management
- Intelligent context pruning
- Relevance-based history selection
- Efficient encoding of project state

### Memory Usage
- Configurable history retention
- Lazy loading of large context
- Garbage collection of unused data

## Error Handling

### Session Corruption
- Backup and restore mechanisms
- Graceful degradation when state is lost
- User notification and recovery options

### Resource Exhaustion
- Memory limits and cleanup
- Disk space monitoring
- Performance degradation handling