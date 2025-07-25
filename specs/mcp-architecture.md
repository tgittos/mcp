# Ralph MCP Server Architecture Specification

## Overview
Ralph uses Model Context Protocol (MCP) servers to provide a distributed, scalable, and secure tool execution environment. This architecture enables recursive agents to share tools while maintaining isolation and fault tolerance.

## MCP Server Organization

### Server Classification
```python
class MCPServerType(Enum):
    CORE_TOOLS = "core_tools"           # Essential file/git operations
    ANALYSIS_TOOLS = "analysis_tools"   # Code analysis and metrics
    WEB_TOOLS = "web_tools"            # Web search and documentation
    AI_TOOLS = "ai_tools"              # LLM calls and embeddings
    SYSTEM_TOOLS = "system_tools"      # System commands and monitoring
    CUSTOM_TOOLS = "custom_tools"      # Project-specific tools

class MCPServerConfig:
    def __init__(self, server_type: MCPServerType):
        self.type = server_type
        self.host = "localhost"
        self.port = self._get_default_port()
        self.max_connections = 50
        self.timeout_seconds = 30
        self.auth_required = True
        self.rate_limits = self._get_default_limits()
    
    def _get_default_port(self) -> int:
        port_mapping = {
            MCPServerType.CORE_TOOLS: 8001,
            MCPServerType.ANALYSIS_TOOLS: 8002,
            MCPServerType.WEB_TOOLS: 8003,
            MCPServerType.AI_TOOLS: 8004,
            MCPServerType.SYSTEM_TOOLS: 8005,
            MCPServerType.CUSTOM_TOOLS: 8006
        }
        return port_mapping[self.type]
```

### Server Responsibilities

#### Core Tools Server (Port 8001)
```python
# Essential tools that every Ralph agent needs
CORE_TOOLS = [
    "read_file",
    "write_file", 
    "list_directory",
    "git_status",
    "git_commit",
    "run_command",
    "create_directory",
    "delete_file"
]
```

#### Analysis Tools Server (Port 8002)
```python
# Code analysis and quality metrics
ANALYSIS_TOOLS = [
    "analyze_code_structure",
    "measure_complexity",
    "find_code_patterns",
    "analyze_dependencies",
    "run_linter",
    "run_type_checker",
    "calculate_test_coverage"
]
```

#### Web Tools Server (Port 8003)
```python
# External research and documentation
WEB_TOOLS = [
    "web_search",
    "fetch_url",
    "parse_documentation",
    "search_stackoverflow",
    "search_github",
    "fetch_api_docs"
]
```

#### AI Tools Server (Port 8004)
```python
# LLM and AI-powered analysis
AI_TOOLS = [
    "generate_code_summary",
    "suggest_improvements",
    "generate_tests",
    "explain_code",
    "translate_code",
    "generate_documentation"
]
```

## Connection Management

### MCP Client Implementation
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from typing import Dict, List, Optional

class MCPConnectionManager:
    def __init__(self):
        self.connections: Dict[MCPServerType, ClientSession] = {}
        self.server_configs = self._load_server_configs()
        self.connection_pool = ConnectionPool(max_size=10)
    
    async def initialize_connections(self):
        """Initialize connections to all configured MCP servers"""
        connection_tasks = []
        
        for server_type, config in self.server_configs.items():
            task = self._connect_to_server(server_type, config)
            connection_tasks.append(task)
        
        # Connect to all servers concurrently
        results = await asyncio.gather(*connection_tasks, return_exceptions=True)
        
        # Log connection results
        for server_type, result in zip(self.server_configs.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Failed to connect to {server_type}: {result}")
            else:
                logger.info(f"Connected to {server_type}")
    
    async def _connect_to_server(self, server_type: MCPServerType, 
                                config: MCPServerConfig) -> ClientSession:
        try:
            session = ClientSession(
                StdioServerParameters(
                    command=f"ralph-mcp-{server_type.value}",
                    args=["--port", str(config.port)]
                )
            )
            
            await session.initialize()
            self.connections[server_type] = session
            return session
            
        except Exception as e:
            logger.error(f"Failed to connect to {server_type}: {e}")
            raise
    
    async def get_session(self, server_type: MCPServerType) -> Optional[ClientSession]:
        """Get an active session for the specified server type"""
        session = self.connections.get(server_type)
        
        if not session or not session.is_connected():
            # Attempt to reconnect
            config = self.server_configs[server_type]
            session = await self._connect_to_server(server_type, config)
        
        return session
```

### Tool Discovery and Registration
```python
class MCPToolRegistry:
    def __init__(self, connection_manager: MCPConnectionManager):
        self.connection_manager = connection_manager
        self.available_tools: Dict[str, MCPToolInfo] = {}
        self.server_capabilities: Dict[MCPServerType, List[str]] = {}
    
    async def discover_tools(self):
        """Discover all available tools from connected MCP servers"""
        for server_type in MCPServerType:
            session = await self.connection_manager.get_session(server_type)
            if not session:
                continue
            
            try:
                # List available tools from this server
                tools_response = await session.list_tools()
                server_tools = []
                
                for tool in tools_response.tools:
                    tool_info = MCPToolInfo(
                        name=tool.name,
                        description=tool.description,
                        server_type=server_type,
                        input_schema=tool.inputSchema,
                        capabilities=self._analyze_tool_capabilities(tool)
                    )
                    
                    self.available_tools[tool.name] = tool_info
                    server_tools.append(tool.name)
                
                self.server_capabilities[server_type] = server_tools
                logger.info(f"Discovered {len(server_tools)} tools from {server_type}")
                
            except Exception as e:
                logger.error(f"Tool discovery failed for {server_type}: {e}")
    
    def get_tool_server(self, tool_name: str) -> Optional[MCPServerType]:
        """Get the server type that provides a specific tool"""
        tool_info = self.available_tools.get(tool_name)
        return tool_info.server_type if tool_info else None
    
    def list_tools_by_capability(self, capability: str) -> List[str]:
        """List tools that have a specific capability"""
        return [
            name for name, info in self.available_tools.items()
            if capability in info.capabilities
        ]
```

## Permission and Security Model

### Simplified Permission Model
```python
class MCPPermissionManager:
    def __init__(self):
        self.agent_permissions: Dict[str, AgentPermissions] = {}
        self.max_recursion_depth = 3  # Configurable via CLI --max-depth=3
    
    def create_agent_permissions(self, agent_id: str, 
                                parent_agent_id: Optional[str] = None,
                                agent_level: int = 0) -> AgentPermissions:
        """Create permissions for a new agent"""
        
        # Child agents inherit ALL permissions except spawning ability
        if parent_agent_id:
            parent_permissions = self.agent_permissions[parent_agent_id]
            permissions = AgentPermissions(
                allowed_servers=parent_permissions.allowed_servers,
                allowed_tools=parent_permissions.allowed_tools,
                can_spawn_children=(agent_level < self.max_recursion_depth),
                file_access=parent_permissions.file_access,
                network_access=parent_permissions.network_access
            )
        else:
            # Root agent gets full permissions
            permissions = self._create_root_permissions()
        
        self.agent_permissions[agent_id] = permissions
        return permissions

class AgentPermissions:
    def __init__(self):
        self.allowed_servers: Set[MCPServerType] = set()
        self.allowed_tools: Set[str] = set()
        self.can_spawn_children: bool = True  # Only restriction based on recursion depth
        self.file_access: FileAccessPermissions = FileAccessPermissions()
        self.network_access: bool = True
        self.max_tool_execution_time: int = 300  # seconds

# Recursion Control Configuration
RECURSION_LEVELS = {
    0: "Root Ralph agent (can spawn children)",
    1: "First-generation child agents (can spawn children)",
    2: "Second-generation child agents (can spawn children)", 
    3: "Third-generation child agents (CANNOT spawn children)"
}
```

### Security Enforcement
```python
class MCPSecurityEnforcer:
    def __init__(self, permission_manager: MCPPermissionManager):
        self.permission_manager = permission_manager
        self.audit_logger = AuditLogger()
    
    async def execute_tool_with_security(self, agent_id: str, 
                                       tool_name: str, 
                                       arguments: Dict) -> ToolResult:
        # Check permissions
        if not self._check_tool_permission(agent_id, tool_name):
            self.audit_logger.log_permission_denied(agent_id, tool_name)
            raise PermissionDeniedError(f"Agent {agent_id} cannot execute {tool_name}")
        
        # Rate limit check
        if not await self._check_rate_limits(agent_id, tool_name):
            raise RateLimitExceededError(f"Rate limit exceeded for {tool_name}")
        
        # Sanitize arguments
        sanitized_args = self._sanitize_arguments(arguments, tool_name)
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                self._execute_tool(agent_id, tool_name, sanitized_args),
                timeout=self._get_tool_timeout(agent_id, tool_name)
            )
            
            self.audit_logger.log_tool_execution(agent_id, tool_name, result)
            return result
            
        except asyncio.TimeoutError:
            self.audit_logger.log_tool_timeout(agent_id, tool_name)
            raise ToolTimeoutError(f"Tool {tool_name} timed out")
```

## Load Balancing and Scaling

### Server Load Management
```python
class MCPLoadBalancer:
    def __init__(self):
        self.server_instances: Dict[MCPServerType, List[ServerInstance]] = {}
        self.load_metrics: Dict[str, ServerMetrics] = {}
        self.health_checker = HealthChecker()
    
    async def get_optimal_server(self, server_type: MCPServerType) -> ServerInstance:
        """Select the best server instance based on current load"""
        instances = self.server_instances.get(server_type, [])
        
        if not instances:
            raise NoServerAvailableError(f"No {server_type} servers available")
        
        # Filter healthy instances
        healthy_instances = [
            instance for instance in instances
            if self.health_checker.is_healthy(instance)
        ]
        
        if not healthy_instances:
            raise NoHealthyServerError(f"No healthy {server_type} servers")
        
        # Select instance with lowest load
        return min(healthy_instances, 
                  key=lambda x: self.load_metrics[x.id].current_load)
    
    async def scale_servers(self, server_type: MCPServerType, 
                          target_instances: int):
        """Scale server instances up or down"""
        current_instances = len(self.server_instances.get(server_type, []))
        
        if target_instances > current_instances:
            # Scale up
            for _ in range(target_instances - current_instances):
                await self._start_server_instance(server_type)
        elif target_instances < current_instances:
            # Scale down
            instances_to_remove = current_instances - target_instances
            await self._graceful_shutdown_instances(server_type, instances_to_remove)
```

### Auto-scaling Policies
```python
AUTOSCALING_POLICIES = {
    MCPServerType.CORE_TOOLS: {
        'min_instances': 2,
        'max_instances': 10,
        'scale_up_threshold': 0.8,    # CPU usage > 80%
        'scale_down_threshold': 0.3,  # CPU usage < 30%
        'scale_up_cooldown': 300,     # 5 minutes
        'scale_down_cooldown': 600    # 10 minutes
    },
    MCPServerType.AI_TOOLS: {
        'min_instances': 1,
        'max_instances': 5,
        'scale_up_threshold': 0.9,    # Higher threshold for expensive AI tools
        'scale_down_threshold': 0.2,
        'scale_up_cooldown': 600,     # 10 minutes
        'scale_down_cooldown': 1200   # 20 minutes
    }
}
```

## Fault Tolerance and Recovery

### Circuit Breaker Pattern
```python
class MCPCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
    
    async def execute_with_circuit_breaker(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### Fallback Tool Execution
```python
class MCPFallbackManager:
    def __init__(self):
        self.fallback_strategies = {
            'server_unavailable': self._handle_server_unavailable,
            'tool_timeout': self._handle_tool_timeout,
            'permission_denied': self._handle_permission_denied,
            'rate_limit_exceeded': self._handle_rate_limit_exceeded
        }
    
    async def execute_with_fallback(self, agent_id: str, 
                                  tool_name: str, 
                                  arguments: Dict) -> ToolResult:
        primary_strategy = self._get_primary_execution_strategy(tool_name)
        
        try:
            return await primary_strategy.execute(agent_id, tool_name, arguments)
        except Exception as e:
            # Determine appropriate fallback
            fallback_strategy = self._select_fallback_strategy(e, tool_name)
            
            if fallback_strategy:
                logger.info(f"Using fallback strategy for {tool_name}: {fallback_strategy}")
                return await fallback_strategy.execute(agent_id, tool_name, arguments)
            else:
                # No fallback available, re-raise the exception
                raise
```

## Configuration and Deployment

### Server Configuration
```yaml
# ralph_mcp_config.yaml
mcp_servers:
  core_tools:
    enabled: true
    port: 8001
    max_connections: 50
    instances: 2
    health_check_interval: 30
    tools:
      - read_file
      - write_file
      - git_status
      - run_command
    
  analysis_tools:
    enabled: true
    port: 8002  
    max_connections: 20
    instances: 1
    tools:
      - analyze_code_structure
      - measure_complexity
      - run_linter
    
  web_tools:
    enabled: true
    port: 8003
    max_connections: 30
    rate_limits:
      requests_per_minute: 100
      requests_per_hour: 1000
    tools:
      - web_search
      - fetch_url

permissions:
  default_agent:
    allowed_servers: [core_tools, analysis_tools]
    dangerous_operations: false
  
  level_1_child:
    allowed_servers: [core_tools]  
    network_access: false
    rate_limit_factor: 0.5
  
  level_2_child:
    allowed_servers: [core_tools]
    file_write_access: false
    rate_limit_factor: 0.25
```

### Deployment Scripts
```python
class MCPDeploymentManager:
    def __init__(self):
        self.server_processes: Dict[str, subprocess.Popen] = {}
        self.config = self._load_config()
    
    async def deploy_all_servers(self):
        """Deploy all configured MCP servers"""
        deployment_tasks = []
        
        for server_type, config in self.config.items():
            if config.get('enabled', True):
                task = self._deploy_server(server_type, config)
                deployment_tasks.append(task)
        
        await asyncio.gather(*deployment_tasks)
        logger.info("All MCP servers deployed successfully")
    
    async def _deploy_server(self, server_type: str, config: Dict):
        """Deploy a single MCP server with specified configuration"""
        instances = config.get('instances', 1)
        
        for i in range(instances):
            instance_id = f"{server_type}_{i}"
            port = config['port'] + i
            
            process = await self._start_server_process(
                server_type, port, instance_id, config
            )
            
            self.server_processes[instance_id] = process
            logger.info(f"Started {instance_id} on port {port}")
```

## Monitoring and Observability

### Metrics Collection
```python
class MCPMetricsCollector:
    def __init__(self):
        self.metrics = {
            'tool_execution_count': Counter(),
            'tool_execution_duration': Histogram(),
            'server_connections': Gauge(),
            'error_count': Counter(),
            'rate_limit_hits': Counter()
        }
    
    def record_tool_execution(self, server_type: str, tool_name: str, 
                            duration: float, success: bool):
        labels = {'server': server_type, 'tool': tool_name, 'success': success}
        
        self.metrics['tool_execution_count'].inc(labels)
        self.metrics['tool_execution_duration'].observe(duration, labels)
        
        if not success:
            self.metrics['error_count'].inc(labels)
```

This MCP architecture provides Ralph with a robust, scalable foundation for tool execution while maintaining security and fault tolerance across recursive agent hierarchies.

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"id": "1", "content": "Define core Ralph CLI agent specifications", "status": "completed", "priority": "high"}, {"id": "2", "content": "Specify interactive session management", "status": "completed", "priority": "high"}, {"id": "3", "content": "Define tool integration and capabilities", "status": "completed", "priority": "medium"}, {"id": "4", "content": "Specify LLM provider integration", "status": "completed", "priority": "medium"}, {"id": "5", "content": "Define recursive agent spawning system", "status": "completed", "priority": "high"}, {"id": "6", "content": "Specify autonomous research and verification capabilities", "status": "completed", "priority": "high"}, {"id": "7", "content": "Define conversation-driven fallback system", "status": "completed", "priority": "medium"}, {"id": "8", "content": "Define MCP server architecture for tool integration", "status": "completed", "priority": "high"}]