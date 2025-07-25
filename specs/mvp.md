# Ralph MVP Specification: Self-Iterating Development System

## Overview

This MVP focuses on creating a minimal but complete Ralph system capable of autonomous self-improvement. The core principle is building the smallest viable system that can read its own specifications, identify gaps, implement improvements, and verify its work - establishing a self-iterating development loop.

## MVP Scope and Philosophy

### Primary Objective
Create a Ralph system that can:
1. **Read and understand its own codebase and specifications**
2. **Identify improvement opportunities autonomously**
3. **Implement changes using child agents**
4. **Verify implementations through testing**
5. **Document improvements in AGENT.md**

### MVP Boundaries
**INCLUDED in MVP:**
- Core agent coordination and child spawning
- Basic file system operations (read, write, edit)
- Git integration for version control
- Python code execution and testing
- LLM integration (Claude + Local LLMs via LM Studio)
- Markdown state management
- Interactive mode for user collaboration

**EXCLUDED from MVP:**
- Web research capabilities
- Complex MCP server architecture (simplified to single process)
- Advanced security sandboxing
- Advanced multi-provider LLM routing and fallback
- Web-based interfaces
- Distributed deployment features

## Core MVP Architecture

### Simplified Component Structure
```
ralph/
├── coordinator.py          # Main Ralph agent coordinator
├── child_agent.py         # Child agent implementation
├── tools/                 # Tool implementations
│   ├── file_tools.py      # File system operations
│   ├── git_tools.py       # Git version control
│   ├── python_tools.py    # Python execution and testing
│   └── agent_tools.py     # Agent spawning and management
├── llm/                   # LLM integration
│   ├── providers/         # LLM provider implementations
│   │   ├── claude_provider.py    # Claude API integration
│   │   ├── local_llm_provider.py # LM Studio/local LLM support
│   │   └── provider_factory.py   # Provider selection logic
│   └── context_manager.py # Context and token management
├── state/                 # State management
│   └── markdown_state.py  # Markdown file state persistence
└── cli.py                 # Command-line interface
```

## MVP Implementation Phases

### Phase 1: Foundation (Self-Reading Capability)
**Goal**: Ralph can read and understand its own codebase

#### Core Components
1. **Basic Coordinator Agent**
   ```python
   class RalphCoordinator:
       def __init__(self, project_path: str = None):
           self.project_path = project_path or os.getcwd()
           self.state_manager = MarkdownStateManager(self.project_path)
           self.llm_client = RalphLLMClient()
           self.tools = ToolRegistry()
           
       async def process_task(self, task: str) -> TaskResult:
           # Determine if task should use autonomous mode
           if self.should_spawn_child_agents(task):
               return await self.execute_autonomous_mode(task)
           else:
               return await self.execute_interactive_mode(task)
   ```

2. **Child Agent Spawning (Single Level Only)**
   ```python
   class ChildAgentSpawner:
       def spawn_agent(self, task_description: str, context: Dict) -> ChildAgent:
           agent_id = self.generate_task_based_id(task_description)
           return ChildAgent(
               agent_id=agent_id,
               task=task_description,
               context=context,
               tools=self.get_child_tool_permissions(),
               max_tokens=16000,  # Child agent token limit
               recursion_depth=1  # MVP: Child agents cannot spawn further children
           )
   ```

3. **Essential Tools**
   - `read_file()` - Read any file in the project
   - `write_file()` - Write/create files
   - `list_directory()` - Directory exploration
   - `run_python()` - Execute Python code
   - `git_status()`, `git_add()`, `git_commit()` - Basic git operations

4. **Unified LLM Integration via LiteLLM**
   ```python
   import litellm
   import os
   from typing import List, Dict, Optional
   
   class RalphLLMClient:
       def __init__(self):
           self.setup_providers()
           
       def setup_providers(self):
           """Configure LLM providers via environment variables"""
           # LiteLLM reads these environment variables automatically:
           # ANTHROPIC_API_KEY - Claude API key
           # OPENAI_API_KEY - OpenAI API key  
           # LM_STUDIO_API_BASE - Local LM Studio endpoint (default: http://localhost:1234)
           # OLLAMA_API_BASE - Ollama endpoint (default: http://localhost:11434)
           
           # Set defaults for local providers if not configured
           if not os.environ.get("LM_STUDIO_API_BASE"):
               os.environ["LM_STUDIO_API_BASE"] = "http://localhost:1234"
           if not os.environ.get("OLLAMA_API_BASE"):  
               os.environ["OLLAMA_API_BASE"] = "http://localhost:11434"
           
           # Enable debug mode via environment variable
           litellm.set_verbose = os.environ.get("RALPH_DEBUG", "false").lower() == "true"
           
       async def generate_response(self, messages: List[Dict], 
                                  provider: str = None,
                                  tools: List[Dict] = None,
                                  **kwargs) -> Dict:
           """Generate response using specified provider with automatic fallbacks"""
           
           # Default provider from environment variable
           if provider is None:
               provider = os.environ.get("RALPH_DEFAULT_PROVIDER", "claude")
           
           # Provider to model mapping (customizable via env vars)
           provider_models = {
               "claude": os.environ.get("RALPH_CLAUDE_MODEL", "anthropic/claude-3-5-sonnet-20241022"),
               "local": os.environ.get("RALPH_LOCAL_MODEL", "lm_studio/auto"),
               "ollama": os.environ.get("RALPH_OLLAMA_MODEL", "ollama/llama2"),
               "openai": os.environ.get("RALPH_OPENAI_MODEL", "openai/gpt-4")
           }
           
           model = provider_models.get(provider, provider_models["claude"])
           
           try:
               # Check tool support for this provider
               if tools and not litellm.supports_function_calling(model):
                   # Fallback to text-based tool simulation
                   tools = None
                   
               response = await litellm.acompletion(
                   model=model,
                   messages=messages,
                   tools=tools,
                   temperature=kwargs.get("temperature", float(os.environ.get("RALPH_TEMPERATURE", "0.7"))),
                   max_tokens=kwargs.get("max_tokens", int(os.environ.get("RALPH_MAX_TOKENS", "4096"))),
                   **kwargs
               )
               
               return self._format_response(response)
               
           except Exception as e:
               # Automatic fallback to next available provider
               return await self._fallback_completion(messages, tools, **kwargs)
               
       def _format_response(self, response) -> Dict:
           """Convert LiteLLM response to Ralph's standard format"""
           return {
               "content": response.choices[0].message.content,
               "tool_calls": getattr(response.choices[0].message, "tool_calls", None),
               "model": response.model,
               "usage": response.usage.dict() if response.usage else None
           }
           
       async def _fallback_completion(self, messages: List[Dict], 
                                    tools: List[Dict] = None, **kwargs):
           """Try fallback providers in order"""
           fallback_order = os.environ.get("RALPH_FALLBACK_ORDER", "claude,local").split(",")
           
           for provider in fallback_order:
               try:
                   return await self.generate_response(
                       messages, provider, tools, **kwargs
                   )
               except Exception as e:
                   continue
                   
           raise Exception("All LLM providers failed")
   ```

5. **Markdown State Management**
   ```python
   class MarkdownStateManager:
       def __init__(self, project_path: str):
           self.project_path = project_path
           
       def save_agent_state(self, state: Dict):
           # Update AGENT.md with improvements
           
       def load_project_context(self) -> Dict:
           # Read existing Ralph state files
   ```

#### Success Criteria for Phase 1
- Ralph can spawn child agents to read all files in its own codebase
- Each child agent can report on the purpose and structure of assigned files
- Results are aggregated by the coordinator
- State is preserved in markdown files
- Basic git operations work

### Phase 2: Self-Analysis (Gap Identification)
**Goal**: Ralph can identify missing functionality by comparing codebase to specifications

#### New Components
1. **Specification Analyzer**
   ```python
   class SpecificationAnalyzer:
       def analyze_spec_coverage(self, spec_files: List[str], 
                                code_files: List[str]) -> AnalysisResult:
           # Compare specs against implementation
           # Identify missing features, incomplete implementations
           
       def generate_improvement_tasks(self, gaps: List[Gap]) -> List[Task]:
           # Convert identified gaps into actionable tasks
   ```

2. **Code Structure Analyzer**
   ```python
   class CodeAnalyzer:
       def analyze_architecture(self, code_files: List[str]) -> ArchitectureReport:
           # Understand current code structure
           # Identify coupling, missing abstractions, etc.
   ```

3. **Task Prioritizer**
   ```python
   class TaskPrioritizer:
       def prioritize_tasks(self, tasks: List[Task]) -> List[PrioritizedTask]:
           # Rank tasks by impact, effort, dependencies
           # Focus on foundational improvements first
   ```

#### Implementation Approach
- Spawn child agents to analyze each specification file
- Spawn child agents to analyze each source code file  
- Coordinator aggregates findings and identifies gaps
- Generate prioritized task list for improvements

#### Success Criteria for Phase 2
- Ralph can identify at least 5 concrete gaps between specs and implementation
- Tasks are prioritized by feasibility and impact
- Improvement tasks are documented in RALPH_TASKS.md
- Ralph can explain its analysis process to users

### Phase 3: Self-Improvement (Implementation Capability) 
**Goal**: Ralph can implement missing functionality autonomously

#### New Components
1. **Implementation Planner**
   ```python
   class ImplementationPlanner:
       def create_implementation_plan(self, task: Task) -> ImplementationPlan:
           # Break down implementation into steps
           # Identify required tools and dependencies
           # Plan verification approach
   ```

2. **Code Generator**
   ```python
   class CodeGenerator:
       def generate_implementation(self, plan: ImplementationPlan) -> CodeChanges:
           # Generate code based on specifications
           # Follow existing code patterns and conventions
           # Include appropriate error handling and documentation
   ```

3. **Test Generator**
   ```python
   class TestGenerator:
       def generate_tests(self, implementation: CodeChanges) -> TestSuite:
           # Generate unit tests for new functionality
           # Create integration tests where appropriate
   ```

#### Implementation Approach
- For each prioritized task, spawn child agents:
  - **Planning Agent**: Create detailed implementation plan
  - **Implementation Agent**: Write the actual code
  - **Testing Agent**: Create comprehensive tests
  - **Documentation Agent**: Update relevant documentation
- Coordinator validates and integrates results
- Automated verification before committing changes

#### Success Criteria for Phase 3
- Ralph can implement at least one missing feature end-to-end
- Generated code follows existing project conventions
- Implementation includes appropriate tests
- Changes are committed to git with descriptive messages
- AGENT.md is updated with learnings from the implementation

### Phase 4: Self-Verification (Quality Assurance)
**Goal**: Ralph can verify its own work and iterate on failures

#### New Components
1. **Automated Test Runner**
   ```python
   class TestRunner:
       def run_test_suite(self) -> TestResults:
           # Run all tests and capture results
           # Provide detailed failure analysis
           
       def run_specific_tests(self, test_patterns: List[str]) -> TestResults:
           # Run targeted tests for specific functionality
   ```

2. **Code Quality Analyzer**
   ```python
   class QualityAnalyzer:
       def analyze_code_quality(self, files: List[str]) -> QualityReport:
           # Check code style, complexity, maintainability
           # Identify potential improvements
   ```

3. **Failure Analyzer**
   ```python
   class FailureAnalyzer:
       def analyze_test_failures(self, failures: List[TestFailure]) -> AnalysisReport:
           # Understand why tests failed
           # Suggest fixes and improvements
   ```

#### Implementation Approach
- After each implementation, run comprehensive verification
- If tests fail, spawn child agents to analyze and fix issues
- Iterate until quality thresholds are met
- Document successful patterns in AGENT.md

#### Success Criteria for Phase 4
- Ralph can run its own test suite and interpret results
- Test failures trigger automatic debugging and fixing attempts
- Quality improvements are measured and tracked
- Ralph can explain what it learned from fixing its own bugs

## MVP Validation Strategy

### Self-Iteration Test
The ultimate MVP validation is Ralph successfully improving itself:

1. **Start with incomplete implementation** (missing 2-3 specified features)
2. **Ralph analyzes its own codebase** and identifies missing features
3. **Ralph implements missing features** using child agents
4. **Ralph tests its own implementations** and fixes any issues
5. **Ralph documents improvements** in AGENT.md
6. **Repeat the cycle** - Ralph finds new improvement opportunities

### Success Metrics
- **Completeness**: % of specification features implemented
- **Quality**: Test coverage and pass rate
- **Autonomy**: % of improvements made without human intervention
- **Self-Awareness**: Accuracy of Ralph's self-analysis
- **Learning**: Quality of insights documented in AGENT.md

## Required Dependencies

### Python Libraries
```python
# requirements.txt
litellm>=1.0.0             # Unified LLM provider interface (includes Claude, OpenAI, local LLMs)
aiohttp>=3.8.0             # Async HTTP client
pydantic>=2.0.0            # Data validation and settings
asyncio                    # Async programming support
gitpython>=3.1.0           # Git integration
click>=8.0.0               # CLI framework
markdown>=3.4.0            # Markdown processing
pyyaml>=6.0                # YAML configuration
pytest>=7.0.0              # Testing framework
black>=23.0.0              # Code formatting
mypy>=1.0.0                # Type checking

# Optional dependencies for specific providers (auto-installed by litellm as needed)
# anthropic                # Claude (installed automatically)
# openai                   # OpenAI/Local LLMs (installed automatically)
```

### Environment Variable Configuration

Ralph uses environment variables for zero-config deployment and `uv run --with ralph ralph` compatibility:

```bash
# Required for specific providers
export ANTHROPIC_API_KEY="sk-ant-..."        # Claude API key
export OPENAI_API_KEY="sk-..."               # OpenAI API key

# Local LLM endpoints (auto-detected if not set)
export LM_STUDIO_API_BASE="http://localhost:1234"    # LM Studio endpoint
export OLLAMA_API_BASE="http://localhost:11434"      # Ollama endpoint

# Ralph behavior configuration
export RALPH_DEFAULT_PROVIDER="claude"               # Primary provider: claude, local, openai, ollama
export RALPH_FALLBACK_ORDER="claude,local,ollama"    # Comma-separated fallback order
export RALPH_DEBUG="false"                           # Enable detailed logging

# Model selection (optional - uses sensible defaults)
export RALPH_CLAUDE_MODEL="anthropic/claude-3-5-sonnet-20241022"
export RALPH_LOCAL_MODEL="lm_studio/auto"            # Uses loaded LM Studio model
export RALPH_OPENAI_MODEL="openai/gpt-4"
export RALPH_OLLAMA_MODEL="ollama/llama2"

# Generation parameters (optional)
export RALPH_TEMPERATURE="0.7"                       # Response creativity (0.0-1.0)
export RALPH_MAX_TOKENS="4096"                       # Maximum response length
```

### Zero-Config Deployment Examples

```bash
# Use Claude (requires API key)
export ANTHROPIC_API_KEY="sk-ant-..."
uv run --with ralph ralph "analyze this codebase"

# Use local LM Studio (requires LM Studio running on localhost:1234)
export RALPH_DEFAULT_PROVIDER="local"
uv run --with ralph ralph "refactor this function"

# Use with fallback (tries Claude, then local)
export ANTHROPIC_API_KEY="sk-ant-..."
export RALPH_FALLBACK_ORDER="claude,local"
uv run --with ralph ralph "implement new feature X"

# Complete offline mode (Ollama only)
export RALPH_DEFAULT_PROVIDER="ollama"
export RALPH_FALLBACK_ORDER="ollama"
uv run --with ralph ralph "review this code"
```

### LiteLLM Integration Benefits
- **Unified Interface**: Single API for 100+ LLM providers including local models
- **Automatic Fallbacks**: Seamless switching between providers on failure
- **Native Tool Support**: Function calling works across compatible providers
- **Cost Optimization**: Easy switching for cost comparison and budget management  
- **Future-Proof**: Add new providers without code changes
- **Local Privacy**: Support for completely offline inference via LM Studio/Ollama
- **Enterprise Ready**: Built-in rate limiting, error handling, and monitoring

## Technical Implementation Details

### Child Agent Architecture
```python
class ChildAgent:
    def __init__(self, agent_id: str, task: str, context: Dict):
        self.agent_id = agent_id
        self.task = task
        self.context = context
        self.max_tokens = 16000
        self.recursion_depth = 1  # MVP: Cannot spawn children
        self.tools = self.get_permitted_tools()
        
    async def execute(self) -> AgentResult:
        # Execute assigned task within token limits
        # Use available tools to complete work
        # Return structured results to coordinator
        # NOTE: Cannot spawn child agents (max depth = 1)
```

### State Persistence
```python
class StateManager:
    def update_agent_md(self, improvement: Improvement):
        # Add improvement to AGENT.md with structured format:
        # ## [Timestamp] - [Improvement Type]
        # **What**: Brief description
        # **Why**: Reasoning and context  
        # **How**: Implementation approach
        # **Results**: Measurable outcomes
        # **Learning**: Key insights for future work
```

### Tool Permission Model (Simplified)
```python
CHILD_AGENT_TOOLS = [
    'read_file', 'write_file', 'list_directory',
    'run_python', 'run_tests',
    'git_status', 'git_add', 'git_commit'
    # NOTE: Child agents cannot spawn other agents in MVP (max depth = 1)
]

ROOT_AGENT_TOOLS = CHILD_AGENT_TOOLS + [
    'spawn_child_agent', 'terminate_agent'
]

# MVP recursion limit: only root agent can spawn children
MAX_RECURSION_DEPTH = 1  # Root (0) -> Child (1), no further nesting
```

## MVP Development Approach

### Bootstrap Strategy
1. **Manual Bootstrap**: Initially implement core coordinator manually
2. **First Self-Iteration**: Use incomplete Ralph to implement first missing feature
3. **Iterative Completion**: Each iteration adds more capabilities
4. **Full Autonomy**: Eventually Ralph manages its own development completely

### Risk Mitigation
- **Git Safety**: All changes committed with clear messages and reversible
- **Test Safety**: Never commit changes that break existing tests
- **Human Override**: User can interrupt and take control at any time
- **Incremental Progress**: Small, verifiable improvements rather than large rewrites
- **Simplified Recursion**: Single-level agent hierarchy reduces complexity and debugging overhead

### Development Timeline
- **Week 1-2**: Phase 1 (Foundation)
- **Week 3**: Phase 2 (Self-Analysis) 
- **Week 4-5**: Phase 3 (Self-Improvement)
- **Week 6**: Phase 4 (Self-Verification)
- **Week 7**: Integration testing and refinement
- **Week 8**: MVP validation and documentation

## Success Definition

The MVP is complete when Ralph can execute this workflow autonomously:

1. **Self-Assessment**: "Analyze my current capabilities vs. specifications"
2. **Gap Identification**: "What functionality am I missing?"
3. **Implementation Planning**: "How should I implement the most important missing feature?"
4. **Parallel Implementation**: "Spawn child agents to implement, test, and document"
5. **Quality Verification**: "Do my changes work correctly and improve the system?"
6. **Learning Documentation**: "What did I learn that will help future improvements?"
7. **Iteration**: "What should I work on next?"

When Ralph can execute this cycle reliably and produce measurable improvements to its own codebase, the MVP is successful and ready for expansion into the full specification.