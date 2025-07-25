# Ralph Tool Integration Specification

## Overview
Ralph's tool system provides a comprehensive set of capabilities for file manipulation, code execution, research, version control, and system interaction. Tools are organized into categories and executed with appropriate security and error handling.

## Tool Categories

### File System Tools
```python
class FileSystemTools:
    def read_file(self, path: str, encoding: str = 'utf-8') -> str
    def write_file(self, path: str, content: str, encoding: str = 'utf-8') -> bool
    def append_file(self, path: str, content: str) -> bool
    def delete_file(self, path: str) -> bool
    def list_directory(self, path: str, recursive: bool = False) -> List[str]
    def create_directory(self, path: str, parents: bool = True) -> bool
    def copy_file(self, src: str, dst: str) -> bool
    def move_file(self, src: str, dst: str) -> bool
    def get_file_info(self, path: str) -> FileInfo
    def search_files(self, pattern: str, path: str = ".") -> List[str]
```

### Code Execution Tools
```python
class CodeExecutionTools:
    def run_python(self, code: str, timeout: int = 30) -> ExecutionResult
    def run_shell_command(self, command: str, timeout: int = 60) -> ExecutionResult
    def run_tests(self, test_pattern: str = None) -> TestResults
    def run_linter(self, files: List[str] = None) -> LintResults
    def run_type_checker(self, files: List[str] = None) -> TypeCheckResults
    def run_formatter(self, files: List[str] = None) -> FormatResults
    def install_package(self, package: str, version: str = None) -> bool
    def create_virtual_environment(self, path: str) -> bool
```

### Version Control Tools
```python
class GitTools:
    def git_status(self) -> GitStatus
    def git_log(self, limit: int = 10) -> List[GitCommit]
    def git_diff(self, staged: bool = False) -> str
    def git_add(self, files: List[str]) -> bool
    def git_commit(self, message: str) -> bool
    def git_push(self, remote: str = "origin", branch: str = None) -> bool
    def git_pull(self, remote: str = "origin", branch: str = None) -> bool
    def git_branch(self, action: str, branch_name: str = None) -> GitBranchResult
    def git_checkout(self, branch_or_commit: str) -> bool
    def git_stash(self, action: str = "push") -> bool
    def git_merge(self, branch: str) -> MergeResult
```

### Web Research Tools
```python
class WebTools:
    def web_search(self, query: str, num_results: int = 10) -> List[SearchResult]
    def fetch_url(self, url: str, timeout: int = 30) -> WebContent
    def parse_documentation(self, url: str) -> Documentation
    def search_stackoverflow(self, query: str) -> List[StackOverflowResult]
    def search_github(self, query: str, language: str = None) -> List[GitHubResult]
    def fetch_api_docs(self, library: str, version: str = None) -> APIDocumentation
```

### Agent Management Tools
```python
class AgentTools:
    def spawn_child_agent(self, task: str, context: Dict) -> AgentHandle
    def get_agent_status(self, agent_id: str) -> AgentStatus
    def send_message_to_agent(self, agent_id: str, message: Dict) -> bool
    def terminate_agent(self, agent_id: str) -> bool
    def list_active_agents(self) -> List[AgentInfo]
    def aggregate_agent_results(self, agent_ids: List[str]) -> AggregatedResults
```

### Analysis Tools
```python
class AnalysisTools:
    def analyze_code_structure(self, path: str) -> CodeStructure
    def find_code_patterns(self, pattern: str, path: str = ".") -> List[Match]
    def analyze_dependencies(self, path: str = ".") -> DependencyGraph
    def measure_code_complexity(self, files: List[str]) -> ComplexityMetrics
    def find_similar_code(self, code_snippet: str) -> List[SimilarCode]
    def analyze_performance(self, profiling_data: str) -> PerformanceAnalysis
```

## Tool Execution Framework

### Tool Interface
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.usage_count = 0
        self.success_rate = 0.0
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        pass
    
    def get_help(self) -> str:
        pass

class ToolResult:
    def __init__(self, success: bool, data: Any, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.execution_time = 0.0
        self.resource_usage = {}
```

### Tool Registry
```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.categories = {}
    
    def register_tool(self, tool: Tool, category: str):
        self.tools[tool.name] = tool
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool.name)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)
    
    def list_tools(self, category: str = None) -> List[str]:
        if category:
            return self.categories.get(category, [])
        return list(self.tools.keys())
    
    def search_tools(self, query: str) -> List[Tool]:
        # Search by name, description, or functionality
        pass
```

### Tool Execution Engine
```python
class ToolExecutor:
    def __init__(self):
        self.registry = ToolRegistry()
        self.security_manager = SecurityManager()
        self.resource_manager = ResourceManager()
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        # Security validation
        if not self.security_manager.validate_tool_execution(tool_name, kwargs):
            return ToolResult(False, None, "Security validation failed")
        
        # Resource check
        if not self.resource_manager.can_execute(tool_name):
            return ToolResult(False, None, "Resource limits exceeded")
        
        # Get and execute tool
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return ToolResult(False, None, f"Tool '{tool_name}' not found")
        
        try:
            # Parameter validation
            if not tool.validate_parameters(**kwargs):
                return ToolResult(False, None, "Invalid parameters")
            
            # Execute with monitoring
            with self.resource_manager.monitor_execution():
                result = await tool.execute(**kwargs)
            
            # Update metrics
            tool.usage_count += 1
            if result.success:
                tool.success_rate = (tool.success_rate * (tool.usage_count - 1) + 1) / tool.usage_count
            
            return result
            
        except Exception as e:
            return ToolResult(False, None, str(e))
```

## Security Framework

### Permission System
```python
class PermissionManager:
    def __init__(self):
        self.permissions = {
            'file_read': ['read_file', 'list_directory', 'get_file_info'],
            'file_write': ['write_file', 'append_file', 'create_directory'],
            'file_modify': ['delete_file', 'move_file', 'copy_file'],
            'code_execution': ['run_python', 'run_shell_command'],
            'network_access': ['web_search', 'fetch_url'],
            'git_operations': ['git_status', 'git_commit', 'git_push'],
            'agent_spawn': ['spawn_child_agent'],
        }
    
    def check_permission(self, agent_id: str, tool_name: str) -> bool:
        agent_permissions = self.get_agent_permissions(agent_id)
        required_permission = self.get_required_permission(tool_name)
        return required_permission in agent_permissions
```

### Git Worktree Isolation
- **Root Agent**: Works in the main git repository directory
- **Child Agents**: Each gets a separate git worktree for the same repository
- **Benefits**:
  - Natural file system isolation per agent
  - Full project context available to all agents
  - Git handles merge conflicts and synchronization
  - Agents can collaborate through standard git workflows
  - Clean separation of concurrent work
  - Built-in versioning and rollback capabilities
- **Requirements**: Project must be a git repository
- **Implementation**: Each agent gets a unique worktree directory based on agent ID

### Audit Logging
```python
class AuditLogger:
    def log_tool_execution(self, agent_id: str, tool_name: str, 
                          parameters: Dict, result: ToolResult):
        log_entry = {
            'timestamp': datetime.utcnow(),
            'agent_id': agent_id,
            'tool_name': tool_name,
            'parameters': self.sanitize_parameters(parameters),
            'success': result.success,
            'execution_time': result.execution_time,
            'error': result.error
        }
        self.write_audit_log(log_entry)
```

## Resource Management

### Simplified Resource Model
- **Reality Check**: Sub-agents are HTTP API request loops with occasional tool usage
- **Primary Constraint**: LLM token usage and API rate limits, not local compute
- **No Host-Level Limits**: Tool operations (file I/O, git commands) are not computationally intensive
- **Token Management**:
  - Root Ralph agent: Full context window (up to 1M tokens)
  - Child agents: Limited context (~16k tokens each)
  - Natural task scoping through context window limitations

### Resource Monitoring (Simplified)
```python
class TokenResourceManager:
    def __init__(self):
        self.agent_token_limits = {
            'root_agent': 1000000,  # 1M tokens
            'child_agent': 16000    # 16k tokens
        }
    
    def check_token_limit(self, agent_id: str, estimated_tokens: int) -> bool:
        agent_type = 'root_agent' if agent_id == 'main_ralph_coordinator' else 'child_agent'
        limit = self.agent_token_limits[agent_type]
        return estimated_tokens <= limit
    
    def get_token_limit(self, agent_id: str) -> int:
        agent_type = 'root_agent' if agent_id == 'main_ralph_coordinator' else 'child_agent'
        return self.agent_token_limits[agent_type]
```

## Tool Configuration

### Tool Settings
```python
TOOL_CONFIG = {
    'file_operations': {
        'max_file_size_mb': 10,
        'allowed_extensions': ['.py', '.md', '.txt', '.json', '.yaml'],
        'forbidden_paths': ['/etc', '/usr', '/var']
    },
    'code_execution': {
        'timeout_seconds': 30,
        'memory_limit_mb': 256,
        'allowed_commands': ['python', 'pip', 'pytest', 'black', 'mypy']
    },
    'web_requests': {
        'timeout_seconds': 10,
        'max_response_size_mb': 5,
        'allowed_domains': ['*.github.com', '*.stackoverflow.com', '*.python.org']
    }
}
```

### Environment Variables
- `RALPH_TOOLS_CONFIG`: Path to tool configuration file
- `RALPH_SANDBOX_MODE`: Enable strict sandboxing
- `RALPH_AUDIT_LOG_PATH`: Path for audit logs
- `RALPH_RESOURCE_LIMITS`: Override resource limits

## Error Handling and Recovery

### Tool Failure Strategies
```python
class ToolFailureHandler:
    def handle_failure(self, tool_name: str, error: Exception, context: Dict):
        if isinstance(error, TimeoutError):
            return self.handle_timeout(tool_name, context)
        elif isinstance(error, PermissionError):
            return self.handle_permission_error(tool_name, context)
        elif isinstance(error, NetworkError):
            return self.handle_network_error(tool_name, context)
        else:
            return self.handle_generic_error(tool_name, error, context)
    
    def handle_timeout(self, tool_name: str, context: Dict):
        # Retry with increased timeout or alternative approach
        pass
    
    def handle_permission_error(self, tool_name: str, context: Dict):
        # Request elevated permissions or find alternative
        pass
```

### Fallback Mechanisms
- **Tool Alternatives**: Use backup tools when primary fails
- **Degraded Mode**: Continue with limited functionality
- **Manual Intervention**: Request human assistance for critical failures
- **State Recovery**: Restore consistent state after failures

## Extensibility

### Plugin System
```python
class ToolPlugin:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    
    def register_tools(self, registry: ToolRegistry):
        # Register plugin tools
        pass
    
    def initialize(self, config: Dict):
        # Plugin initialization
        pass
```

### Custom Tool Development
- **Tool Template**: Base class for custom tools
- **Registration API**: Easy tool registration process
- **Testing Framework**: Tools for testing custom tools
- **Documentation Generator**: Auto-generate tool documentation