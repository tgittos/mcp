# Ralph MVP Implementation Task List

## Current Implementation Status: ~25-30% Complete

The current Ralph implementation has basic MCP infrastructure and some tools, but is missing critical components for MVP functionality. The execution is currently broken with a `sys.exit(1)` at line 79 of `ralph.py`.

## Task Breakdown by Priority

### CRITICAL TASKS (High Priority) - Week 1-2
Must be completed for basic functionality:

1. **Fix broken execution flow** - remove sys.exit(1) from ralph.py line 79 and complete basic task execution
2. **Replace OpenAI client with LiteLLM integration** - implement RalphLLMClient class with environment variable configuration  
3. **Implement MarkdownStateManager class** - for persistent state in AGENT.md, RALPH_TASKS.md, etc.
4. **Create RalphCoordinator class** - to handle mode routing (interactive vs autonomous) and child agent orchestration

### FOUNDATION TASKS (Medium Priority) - Week 2-3  
Core infrastructure components:

5. **Add git integration tools** - implement git_status, git_add, git_commit functions using GitPython
6. **Refactor child agent spawning** - enhance existing 'ralph' tool with proper context passing and recursion depth limits
7. **Implement ChildAgent class** - with 16k token limits and single-level recursion constraint
8. **Create proper CLI interface** - with argument parsing for interactive/autonomous modes and environment variable setup
9. **Add missing dependencies** - LiteLLM, GitPython, pydantic, click, etc. to requirements.txt

### SELF-ANALYSIS PHASE 2 (Medium Priority) - Week 3-4
Enable Ralph to analyze its own gaps:

10. **Implement SpecificationAnalyzer class** - to compare specs against current implementation
11. **Implement CodeAnalyzer class** - to understand current code structure and patterns  
12. **Implement TaskPrioritizer class** - to rank improvement tasks by impact and feasibility

### SELF-IMPROVEMENT PHASE 3 (Low Priority) - Week 4-5
Enable Ralph to implement missing functionality:

13. **Implement ImplementationPlanner class** - to break down tasks into actionable steps
14. **Implement CodeGenerator class** - to create implementations following existing patterns
15. **Implement TestGenerator class** - to create unit and integration tests for new code

### SELF-VERIFICATION PHASE 4 (Low Priority) - Week 5-6
Enable Ralph to verify its own work:

16. **Implement TestRunner class** - for automated test execution and result analysis
17. **Implement QualityAnalyzer class** - for code quality metrics and improvement suggestions
18. **Implement FailureAnalyzer class** - to diagnose test failures and suggest fixes

### INTEGRATION & VALIDATION (Low Priority) - Week 6-7
Final testing and validation:

19. **Create comprehensive test suite** - with pytest for all implemented functionality
20. **Integrate and test complete self-iteration workflow** - Ralph analyzing and improving its own codebase

## Key Architecture Issues Identified

### Current vs Specified Structure
- **Missing**: Entire `llm/` directory with LiteLLM integration  
- **Missing**: `coordinator.py` and `child_agent.py` classes
- **Missing**: `state/markdown_state.py` for persistence
- **Missing**: Proper `cli.py` implementation
- **Issue**: Wrong LLM integration approach (OpenAI vs LiteLLM)

### Critical Technical Problems
1. **Broken execution flow** - `sys.exit(1)` prevents completion
2. **No state persistence** - Can't track improvements in AGENT.md
3. **Wrong LLM interface** - Not using specified LiteLLM approach
4. **Missing git integration** - Can't commit improvements

## Success Criteria for MVP Completion

Ralph should be able to execute this workflow autonomously:
1. **Self-Assessment**: "Analyze my current capabilities vs. specifications"
2. **Gap Identification**: "What functionality am I missing?"  
3. **Implementation Planning**: "How should I implement the most important missing feature?"
4. **Parallel Implementation**: "Spawn child agents to implement, test, and document"
5. **Quality Verification**: "Do my changes work correctly and improve the system?"
6. **Learning Documentation**: "What did I learn that will help future improvements?"
7. **Iteration**: "What should I work on next?"

## Notes for Implementation

- Focus on **environment variable configuration** over config files for `uv run --with ralph ralph` compatibility
- Maintain **recursion depth = 1** for MVP (only root agent spawns children)
- Use **existing MCP infrastructure** but simplify where needed
- Prioritize **working functionality** over perfect architecture
- Document all improvements in **AGENT.md** as specified

---
*Last updated: 2025-01-23*
*Total estimated effort: 6-7 weeks for complete MVP*