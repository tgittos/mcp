# Prompt Engine Specification

## Overview
The Prompt Engine is the central nervous system of Ralph, managing the `PROMPT.md` file and orchestrating task execution through the main loop.

## Core Components

### PROMPT.md File
- **Purpose**: Contains current task instructions and context for the main loop
- **Format**: Markdown with structured sections
- **Update Frequency**: After each loop iteration
- **Size Constraint**: Must fit within ~156kb context window

### Prompt Structure
```markdown
# Current Task: [Task Name]

## Context
- Current phase: [Requirements|Planning|Implementation]
- Priority level: [High|Medium|Low]
- Estimated complexity: [Simple|Moderate|Complex]

## Task Description
[Detailed description of what needs to be accomplished]

## Input Files
- specs/*.md: [List of relevant specification files]
- IMPLEMENTATION_PLAN.md: [Current plan status]
- AGENT.md: [Build process learnings]

## Constraints
- Memory limit: ~156kb for main process
- Subagent limit: [Number] parallel subagents allowed
- Time limit: [Optional time constraint]

## Expected Output
- Files to create/modify: [List]
- Tests to run: [List]
- Documentation to update: [List]

## Success Criteria
- [ ] [Specific success condition 1]
- [ ] [Specific success condition 2]
- [ ] [Specific success condition 3]
```

## Prompt Management System

### 1. Task Selection Engine
- **Purpose**: Automatically select next priority task from IMPLEMENTATION_PLAN.md
- **Algorithm**: 
  - Read current plan
  - Filter by dependencies and prerequisites
  - Select highest priority available task
  - Update PROMPT.md with task details

### 2. Context Allocation Manager
- **Purpose**: Ensure deterministic stack allocation every loop
- **Required Items**:
  - Current task description
  - Relevant specification files
  - Current implementation plan
  - Agent documentation
  - Previous iteration learnings

### 3. Learning Integration System
- **Purpose**: Incorporate learnings from previous iterations
- **Process**:
  - Extract key learnings from last execution
  - Update AGENT.md with new information
  - Refine task description based on discoveries
  - Adjust constraints and expectations

## Prompt Types

### 1. Requirements Gathering Prompt
```markdown
# Current Task: Define System Requirements

## Context
- Phase: Requirements Gathering
- Goal: Create comprehensive system specifications

## Task Description
Study the project requirements and create detailed specifications for:
- [Component 1]
- [Component 2]
- [Component 3]

Use subagents to research best practices and gather external information.
```

### 2. Planning Prompt
```markdown
# Current Task: Create Implementation Plan

## Context
- Phase: Planning and Analysis
- Goal: Generate prioritized implementation plan

## Task Description
Analyze specifications and existing code to create:
- Prioritized task list
- Dependency mapping
- Resource requirements
- Timeline estimates
```

### 3. Implementation Prompt
```markdown
# Current Task: Implement [Specific Feature]

## Context
- Phase: Incremental Implementation
- Goal: Complete specific implementation task

## Task Description
Implement [specific feature] according to specifications:
- Write code in [language/framework]
- Create/update tests
- Update documentation
- Run build and test suite
```

## Subagent Integration

### Prompt-to-Subagent Communication
- **Task Delegation**: Main prompt delegates specific tasks to subagents
- **Context Sharing**: Relevant context passed to subagents
- **Result Aggregation**: Subagent results integrated back into main context

### Subagent Prompt Templates
```markdown
# Subagent Task: [Specific Task]

## Context
- Parent task: [Main task reference]
- Available memory: ~156kb
- Time limit: [Duration]

## Task Description
[Specific subagent task with clear boundaries]

## Input
- Files: [List of relevant files]
- Context: [Relevant context from parent]

## Expected Output
- Result: [Expected result format]
- Files: [Files to create/modify]
- Status: [Success/failure with details]
```

## Error Handling

### Prompt Validation
- **Syntax Check**: Ensure markdown format is valid
- **Size Check**: Verify prompt fits within context window
- **Dependency Check**: Ensure all referenced files exist
- **Logic Check**: Verify task dependencies are satisfied

### Recovery Mechanisms
- **Task Failure**: Update prompt with error details and retry strategy
- **Context Overflow**: Automatically trim non-essential content
- **Missing Dependencies**: Create placeholder tasks for missing prerequisites

## Performance Optimization

### Context Window Efficiency
- **Essential Content**: Prioritize task description and constraints
- **Optional Content**: Move detailed specifications to separate files
- **Dynamic Loading**: Load specifications on-demand via subagents

### Prompt Caching
- **Template Caching**: Cache common prompt templates
- **Context Caching**: Cache frequently used context elements
- **Result Caching**: Cache successful prompt patterns

## Integration Points

### With IMPLEMENTATION_PLAN.md
- Read current plan for task selection
- Update plan with completed tasks
- Add new tasks discovered during execution

### With AGENT.md
- Read build process learnings
- Update with new discoveries
- Optimize future prompts based on learnings

### With Specifications
- Load relevant specification files
- Validate implementation against specs
- Update specs when inconsistencies found

## Success Metrics
- **Task Completion Rate**: Percentage of tasks completed successfully
- **Context Efficiency**: Average context window utilization
- **Learning Integration**: Speed of incorporating new learnings
- **Error Recovery**: Time to recover from task failures
- **Prompt Quality**: Clarity and completeness of task descriptions 
