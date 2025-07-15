# Ralph Agent Documentation

## System Overview
Ralph is a loop-based parallelized autonomous agent system that implements the Ralph Wiggum technique for AI-driven software development.

## Build Process Learnings

### Core Loop
The system operates on a single infinite loop:
```bash
while :; do cat PROMPT.md | npx --yes @sourcegraph/amp ; done
```

### Key Dependencies
- **@sourcegraph/amp**: AI agent execution engine
- **Node.js/npm**: Package management and execution
- **Git**: Version control for state management
- **Python**: MCP client integration

### File Structure
```
.
├── PROMPT.md                    # Current task and context
├── AGENT.md                     # This file - build process learnings
├── IMPLEMENTATION_PLAN.md       # Prioritized task list
├── specs/                       # System specifications
│   ├── ralph-core.md           # Core system specification
│   ├── prompt-engine.md        # Prompt management system
│   ├── subagent-system.md      # Subagent architecture
│   ├── memory-management.md    # Context window handling
│   ├── workflow-phases.md      # Phase definitions
│   ├── file-management.md      # File-based state management
│   ├── mcp-server-tools.md     # MCP server tools specification
│   └── mcp-client-integration.md # MCP client integration specification
└── src/                        # Implementation source code
```

## Memory Management

### Context Window Constraints
- **Primary Context**: ~156kb for main process
- **Subagent Contexts**: ~156kb each with automatic garbage collection
- **Total Memory**: Main + (Number of Subagents × 156kb)

### Memory Allocation Strategies
- **Manual Allocation**: Used during Requirements and Planning phases
- **Automatic Allocation**: Used during Implementation phase for consistency

## Subagent Configuration

### Subagent Types and Limits
1. **Analysis Subagents**: Up to 100 parallel for code analysis
2. **Research Subagents**: Unlimited parallel for external information
3. **Implementation Subagents**: Unlimited parallel for code writing
4. **Build/Test Subagents**: 1 parallel for build and test execution
5. **Documentation Subagents**: Unlimited parallel for documentation

### Subagent Communication
- **Task Assignment**: JSON format with task description and constraints
- **Result Collection**: JSON format with status, results, and learnings
- **Error Handling**: Automatic retry up to 3 times with redistribution

## Workflow Phases

### Phase 1: Requirements Gathering
- **Goal**: Define system requirements and create specifications
- **Memory Strategy**: Manual context window allocation
- **Output**: `specs/*.md` files
- **Completion**: All specifications written and reviewed

### Phase 2: Planning and Analysis
- **Goal**: Analyze requirements and create implementation plan
- **Memory Strategy**: Manual context window allocation
- **Input**: `specs/*.md` files
- **Output**: `IMPLEMENTATION_PLAN.md`
- **Completion**: Implementation plan complete and prioritized

### Phase 3: Incremental Implementation
- **Goal**: Execute implementation plan through continuous loops
- **Memory Strategy**: Automatic context window allocation
- **Input**: `IMPLEMENTATION_PLAN.md`, `PROMPT.md`, `AGENT.md`
- **Output**: Code changes, test results, documentation updates
- **Completion**: 90% project completion achieved

## File Management

### Core Files
- **PROMPT.md**: Current task instructions and context
- **AGENT.md**: Build process learnings (this file)
- **IMPLEMENTATION_PLAN.md**: Prioritized task list
- **specs/**: System specifications directory

### File Operations
- **Atomic Updates**: All file updates are atomic to prevent corruption
- **Version Control**: Automatic git commits after successful tasks
- **Backup Strategy**: Automatic backup of critical files
- **State Synchronization**: File state synchronized with context state

## Error Handling

### Recovery Mechanisms
- **Context Overflow**: Automatic trimming of non-essential content
- **Subagent Failure**: Automatic retry and task redistribution
- **File Corruption**: Detection and recovery from backup
- **Memory Pressure**: Graceful degradation with reduced context

### Error Reporting
- **Logging**: All errors logged with detailed information
- **Notification**: Error notifications with recovery suggestions
- **Analysis**: Error pattern analysis for system improvement

## Performance Optimization

### Context Window Efficiency
- **Essential Content**: Prioritize task description and constraints
- **Optional Content**: Move detailed specifications to separate files
- **Dynamic Loading**: Load specifications on-demand via subagents
- **Compression**: Intelligent compression of non-essential content

### Subagent Optimization
- **Pool Management**: Maintain optimal pool size for different task types
- **Task Batching**: Group similar tasks for efficiency
- **Context Caching**: Cache frequently used context
- **Result Caching**: Cache common results

## Integration Points

### MCP System Integration
- **Compatibility**: Maintain compatibility with existing MCP functionality
- **Seamless Transition**: Smooth transition between Ralph and MCP systems
- **Resource Sharing**: Share resources between systems efficiently
- **Tool Consumption**: Ralph consumes MCP server tools for operations
- **Client-Server Architecture**: Ralph as MCP client, tools as MCP server

### MCP Server Tools
- **File Operations**: read_file, write_file, list_directory, delete_file
- **Web Fetching**: fetch_url, fetch_url_json for research and learning
- **Test Execution**: run_tests, run_build for validation
- **System Commands**: execute_command, check_process for system interaction
- **Git Operations**: git_status, git_commit, git_push for version control

### External Systems
- **Git Integration**: Automatic commits, meaningful messages, tag management
- **Package Management**: npm for @sourcegraph/amp and other dependencies
- **Network Access**: External research and documentation retrieval

## Success Metrics

### Performance Metrics
- **Task Completion Rate**: Percentage of tasks completed successfully
- **Memory Efficiency**: Average context window utilization
- **Parallelization Efficiency**: Effective use of parallel subagents
- **Error Recovery Rate**: Success rate of error recovery

### Quality Metrics
- **Code Quality**: Maintain high code quality standards
- **Test Coverage**: Comprehensive test coverage for all components
- **Documentation Quality**: Complete and up-to-date documentation
- **Specification Compliance**: Implementation matches specifications

## Current Status
- **Phase**: Requirements Gathering (COMPLETED)
- **Next Phase**: Planning and Analysis (IN PROGRESS)
- **Specifications**: All core specifications created
- **Implementation Plan**: Initial plan created and prioritized

## Recent Learnings
- Ralph paradigm requires extreme faith in AI reasoning capabilities
- Deterministic stack allocation is critical for consistent behavior
- File-based state management provides reliable persistence
- Subagent parallelization significantly improves performance
- Phase transitions are file-driven and prompt-based
- MCP server tools provide essential capabilities for Ralph operation
- Tool consumption through MCP client enables autonomous decision making
- Security and sandboxing are critical for tool execution safety

## Optimization Tips
- Keep PROMPT.md focused and concise for optimal context usage
- Use subagents for expensive operations to preserve main context
- Update AGENT.md continuously with new learnings
- Maintain atomic file operations for data integrity
- Monitor context window usage to prevent overflow
- Use MCP tools efficiently to minimize context pollution
- Cache tool results for frequently accessed data
- Implement proper error handling for tool failures
- Validate tool inputs to prevent security issues
