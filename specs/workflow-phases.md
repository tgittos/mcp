# Workflow Phases Specification

## Overview
The Workflow Phases define the conceptual stages through which Ralph progresses during a project lifecycle. These phases are not separate coded processes but different states of the same prompt-driven loop system.

## Phase Architecture

### Phase Definition
A phase is a conceptual stage characterized by:
- **Specific Goals**: Clear objectives for the phase
- **Memory Strategy**: How context window is allocated
- **Input/Output Files**: Which files are consumed and produced
- **Subagent Configuration**: Types and limits of subagents used
- **Success Criteria**: How phase completion is determined

### Phase Transitions
- **File-Driven**: Phases transition through the files they create and consume
- **Prompt-Based**: Phase changes are driven by prompt content changes
- **Autonomous**: Ralph determines when to transition between phases
- **Iterative**: Phases can be revisited as needed

## Phase 1: Requirements Gathering

### Purpose
Define system requirements and create comprehensive specifications without implementation.

### Goals
- Understand project requirements thoroughly
- Research best practices and existing solutions
- Create detailed specifications for all system components
- Establish project scope and constraints

### Memory Strategy
- **Allocation Type**: Manual context window allocation
- **Focus**: Research and specification writing
- **Content Priority**: External information and requirement analysis
- **Space Allocation**: Reserve space for specification generation

### Input Files
- Project requirements (if provided)
- External documentation and research materials
- Existing specifications (if any)

### Output Files
- `specs/*.md` - One specification file per system component
- `AGENT.md` - Initial build process documentation
- `IMPLEMENTATION_PLAN.md` - Preliminary plan structure

### Subagent Configuration
- **Research Subagents**: Unlimited parallel for external information gathering
- **Analysis Subagents**: Up to 50 parallel for requirement analysis
- **Documentation Subagents**: Unlimited parallel for specification writing

### Task Types
1. **Requirement Analysis**: Study and understand project requirements
2. **Research Tasks**: Gather external information and best practices
3. **Specification Writing**: Create detailed specifications for each component
4. **Scope Definition**: Define project boundaries and constraints
5. **Technology Selection**: Research and select appropriate technologies

### Success Criteria
- All system components have detailed specifications
- Requirements are fully understood and documented
- External research is complete and documented
- Project scope is clearly defined
- Technology stack is selected and justified

### Phase Completion
- All specifications are written and reviewed
- Implementation plan structure is created
- Ready to transition to planning phase

## Phase 2: Planning and Analysis

### Purpose
Analyze requirements and existing code to create a detailed implementation plan.

### Goals
- Analyze specifications against existing codebase
- Identify missing implementations and dependencies
- Create prioritized implementation plan
- Establish development strategy and timeline

### Memory Strategy
- **Allocation Type**: Manual context window allocation
- **Focus**: Code analysis and planning
- **Content Priority**: Specifications and existing code analysis
- **Space Allocation**: Reserve space for plan generation

### Input Files
- `specs/*.md` - All system specifications
- Existing source code (if any)
- `AGENT.md` - Build process documentation
- `IMPLEMENTATION_PLAN.md` - Preliminary plan

### Output Files
- `IMPLEMENTATION_PLAN.md` - Detailed, prioritized implementation plan
- Updated `AGENT.md` - Enhanced build process documentation
- `PROMPT.md` - Initial implementation prompt

### Subagent Configuration
- **Analysis Subagents**: Up to 100 parallel for code analysis
- **Research Subagents**: Unlimited parallel for best practice research
- **Planning Subagents**: Up to 50 parallel for plan generation

### Task Types
1. **Code Analysis**: Study existing codebase and identify gaps
2. **Dependency Mapping**: Map dependencies between components
3. **Priority Assessment**: Determine implementation priorities
4. **Resource Planning**: Plan resource requirements and timeline
5. **Risk Assessment**: Identify potential risks and mitigation strategies

### Success Criteria
- Complete analysis of existing codebase
- All missing implementations identified
- Prioritized implementation plan created
- Dependencies and risks documented
- Development strategy established

### Phase Completion
- Implementation plan is complete and prioritized
- All dependencies are mapped
- Ready to transition to implementation phase

## Phase 3: Incremental Implementation

### Purpose
Execute the implementation plan through continuous loops, building the system incrementally.

### Goals
- Implement system components according to plan
- Maintain code quality and test coverage
- Update documentation and commit changes
- Achieve 90% project completion

### Memory Strategy
- **Allocation Type**: Automatic context window allocation
- **Focus**: Task execution and implementation
- **Content Priority**: Current task and implementation context
- **Space Allocation**: Consistent allocation for reliable execution

### Input Files
- `IMPLEMENTATION_PLAN.md` - Current implementation plan
- `PROMPT.md` - Current task instructions
- `AGENT.md` - Build process documentation
- `specs/*.md` - System specifications

### Output Files
- Source code files
- Test files
- Updated `AGENT.md` - Enhanced build process documentation
- Updated `IMPLEMENTATION_PLAN.md` - Progress tracking
- Updated `PROMPT.md` - Next task instructions
- Git commits and documentation

### Subagent Configuration
- **Implementation Subagents**: Unlimited parallel for code writing
- **Build/Test Subagents**: 1 parallel for build and test execution
- **Documentation Subagents**: Unlimited parallel for documentation updates
- **Analysis Subagents**: Up to 100 parallel for code analysis

### Task Types
1. **Code Implementation**: Write source code for features
2. **Test Creation**: Create and update tests
3. **Build Execution**: Compile and build the system
4. **Documentation Updates**: Update documentation and commit changes
5. **Bug Fixes**: Fix issues discovered during development
6. **Refactoring**: Improve code quality and structure

### Success Criteria
- All planned features implemented
- All tests passing
- Documentation complete and up-to-date
- Code quality standards met
- 90% project completion achieved

### Phase Completion
- Implementation plan is complete
- All tests are passing
- Documentation is complete
- System is functional and ready for deployment

## Phase Transitions

### Requirements → Planning
- **Trigger**: All specifications are complete
- **Process**: Update prompt to focus on analysis and planning
- **Files**: `specs/*.md` → `IMPLEMENTATION_PLAN.md`

### Planning → Implementation
- **Trigger**: Implementation plan is complete and prioritized
- **Process**: Update prompt to focus on implementation tasks
- **Files**: `IMPLEMENTATION_PLAN.md` → `PROMPT.md`

### Implementation → Implementation (Iteration)
- **Trigger**: Current task completed
- **Process**: Select next priority task from plan
- **Files**: Update `PROMPT.md` with next task

## Phase Monitoring and Control

### Progress Tracking
- **Requirements Phase**: Track specification completion
- **Planning Phase**: Track analysis completion and plan generation
- **Implementation Phase**: Track task completion and plan progress

### Quality Assurance
- **Requirements Phase**: Validate specification completeness and clarity
- **Planning Phase**: Validate plan feasibility and completeness
- **Implementation Phase**: Validate code quality and test coverage

### Phase Optimization
- **Performance Monitoring**: Track phase efficiency and completion time
- **Resource Optimization**: Optimize subagent usage and memory allocation
- **Process Improvement**: Refine phase processes based on learnings

## Integration with Other Systems

### Prompt Engine Integration
- **Phase-Specific Prompts**: Generate appropriate prompts for each phase
- **Context Management**: Manage context allocation for each phase
- **Task Selection**: Select appropriate tasks for each phase

### Subagent System Integration
- **Phase-Specific Subagents**: Configure subagents for phase requirements
- **Resource Allocation**: Allocate resources based on phase needs
- **Result Processing**: Process results according to phase goals

### Memory Management Integration
- **Phase-Specific Allocation**: Allocate memory according to phase strategy
- **Context Optimization**: Optimize context for phase requirements
- **Memory Monitoring**: Monitor memory usage during each phase

## Success Metrics
- **Phase Completion Rate**: Percentage of phases completed successfully
- **Phase Efficiency**: Time to complete each phase
- **Quality Metrics**: Quality of outputs from each phase
- **Resource Utilization**: Efficient use of resources during each phase
- **Transition Smoothness**: Smoothness of transitions between phases 
