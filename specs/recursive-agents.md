# Ralph Recursive Agent System Specification

## Overview
Ralph's recursive agent system is built on a **parallel-by-default** architecture. When Ralph receives an autonomous request, it ALWAYS analyzes the goal, breaks it down into parallelizable subtasks, and spawns child agents - one per subtask. The coordinator Ralph orchestrates all work while child agents handle focused, specific tasks.

## Architecture

### Agent Hierarchy
```
Parent Agent (Level 0)
├── Child Agent A (Level 1)
│   ├── Grandchild A1 (Level 2)
│   └── Grandchild A2 (Level 2)
└── Child Agent B (Level 1)
    └── Grandchild B1 (Level 2)
```

### Agent Types
- **Parent Agent**: Orchestrates child agents, aggregates results
- **Child Agent**: Executes delegated tasks, can spawn own children
- **Leaf Agent**: Terminal agents that cannot spawn further children

## Spawning Strategy

### Core Principle: Parallel-by-Default
- **Remove complexity thresholds entirely** - they prevent optimal parallelization
- When Ralph enters autonomous mode, it ALWAYS breaks down tasks and spawns child agents
- Almost ALL autonomous tasks should use child agents
- Ralph's autonomous mode is fundamentally about orchestration and delegation

### Spawning Examples
- Reading multiple spec files → one child agent per file (e.g., `read_spec_ralph_core`, `read_spec_mcp_architecture`)
- Implementing a feature → separate agents for research, implementation, testing, documentation
- Code analysis → one agent per module/component
- Multi-file refactoring → one agent per file or logical group

### Benefits
- Faster execution through true parallelism
- Better error isolation (one agent fails ≠ whole task fails)
- More focused, higher-quality work per subtask
- Scalable architecture that grows with task size

## Resource Management

### Dynamic Resource Allocation
- **CLI Configuration**: User-configurable limits via arguments
  - `--max-agents=20` (default: 20)
  - `--max-depth=3` (default: 3) 
  - `--max-children-per-agent=10` (default: 10)
- **Intelligent Monitoring**: Ralph uses MCP system tools to monitor:
  - Current CPU load and available cores
  - Memory usage and available RAM
  - Number of running processes
  - Ralph's own resource consumption

### Adaptive Spawning Logic
1. Ralph analyzes task → identifies N subtasks
2. Checks system resources and configured limits
3. Spawns as many agents as resources allow
4. Queues remaining subtasks for later execution
5. Monitors and adjusts as agents complete work

### Token-Based Resource Management
- **Real Constraint**: LLM token usage, not computational resources
- **Root Ralph Agent**: Full context window (up to 1M tokens)
- **Child Agents**: Limited context (~16k tokens each)
- **Reality Check**: Sub-agents are HTTP API request loops - tool operations are not computationally intensive

### Safety Mechanisms
- **Deadlock Detection**: Monitor for circular dependencies
- **Runaway Prevention**: Kill agents exceeding resource limits
- **Health Monitoring**: Check agent responsiveness
- **Graceful Shutdown**: Clean termination cascade

## Communication System

### Agent Identification
- **Task-Based Naming**: Agent IDs are descriptive of their purpose
- **Format Examples**:
  - `read_spec_ralph_core`
  - `implement_authentication_system`  
  - `test_user_registration`
  - `refactor_database_layer_1`, `refactor_database_layer_2` (indexed for duplicates)
  - `research_oauth_libraries`
  - `update_documentation_api`

### Inter-Agent Messaging
```json
{
  "message_type": "task_delegation|result_report|status_update|error_report",
  "agent_id": "implement_authentication_system",
  "parent_id": "main_ralph_coordinator",
  "timestamp": "iso_timestamp",
  "payload": {...}
}
```

### Communication Channels
- **Task Queue**: Parent → Child task assignments
- **Result Channel**: Child → Parent result reporting
- **Status Updates**: Bidirectional health/progress updates
- **Emergency Channel**: Critical errors and shutdown signals

### Context Sharing
- **Shared State**: Read-only project context for all agents
- **Working Memory**: Agent-specific mutable state
- **Result Cache**: Shared results to avoid duplicate work

## Task Delegation Strategies

### Horizontal Partitioning
```
Large refactoring task:
├── Agent A: Update module X
├── Agent B: Update module Y
└── Agent C: Update module Z
```

### Vertical Decomposition
```
Feature implementation:
├── Agent A: Write specifications
├── Agent B: Implement core logic (waits for A)
├── Agent C: Write tests (waits for B)
└── Agent D: Update documentation (waits for C)
```

### Research Parallelization
```
Research task:
├── Agent A: Search codebase for patterns
├── Agent B: Analyze external documentation
├── Agent C: Review similar implementations
└── Parent: Synthesize findings
```

## Coordination Mechanisms

### Dependency Management
- **Task Dependencies**: Define prerequisite relationships
- **Resource Locks**: Prevent concurrent file modifications
- **Synchronization Points**: Wait for critical tasks to complete

### Result Aggregation
- **Merge Strategies**: Combine results from multiple agents
- **Conflict Resolution**: Handle contradictory findings
- **Quality Assessment**: Validate child agent outputs
- **Consensus Building**: Resolve disagreements between agents

## Error Handling

### Agent Failures
```python
def handle_child_failure(child_id, error):
    # Log failure details
    log_agent_failure(child_id, error)
    
    # Reassign critical tasks
    if task_is_critical(child_id):
        reassign_task_to_backup_agent()
    
    # Update parent state
    mark_child_as_failed(child_id)
    
    # Continue or abort based on failure impact
    assess_continuation_viability()
```

### Cascade Failures
- **Isolation**: Prevent failures from propagating upward
- **Recovery**: Restart failed agent subtrees when possible
- **Fallback**: Graceful degradation to single-agent mode

### Timeout Handling
- **Agent Timeouts**: Kill unresponsive agents
- **Task Timeouts**: Reassign overrunning tasks
- **System Timeouts**: Emergency shutdown procedures

## Monitoring and Observability

### Agent Metrics
- **Performance**: Task completion times and success rates
- **Resource Usage**: CPU, memory, and API consumption
- **Communication**: Message volumes and latencies
- **Health**: Agent responsiveness and error rates

### Debugging Support
- **Agent Tree Visualization**: Show current hierarchy
- **Communication Logs**: Trace message flows
- **Task Timeline**: Visual task execution timeline
- **Resource Graphs**: Monitor resource consumption

## Configuration

### Spawning Policies
```python
SPAWNING_CONFIG = {
    "max_depth": 3,
    "max_children_per_agent": 5,
    "max_total_agents": 20,
    "complexity_threshold": 8,
    "parallel_threshold": 3,
    "resource_limits": {
        "memory_mb": 1024,
        "cpu_percent": 80,
        "api_calls_per_minute": 100
    }
}
```

### Environment Variables
- `RALPH_MAX_AGENTS`: Override system-wide agent limit
- `RALPH_MAX_DEPTH`: Override recursion depth
- `RALPH_DISABLE_SPAWNING`: Disable recursive spawning
- `RALPH_DEBUG_AGENTS`: Enable agent debugging

## Security Considerations

### Sandbox Isolation
- **Process Isolation**: Each agent runs in separate process
- **File System Access**: Restricted file access per agent
- **Network Access**: Controlled external communication
- **Resource Quotas**: Hard limits on resource consumption

### Data Protection
- **Context Isolation**: Sensitive data access controls
- **Communication Security**: Encrypted inter-agent messages
- **Audit Logging**: Complete audit trail of agent actions