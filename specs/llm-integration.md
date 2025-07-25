# Ralph LLM Provider Integration Specification

## Overview
Ralph's LLM integration system provides a flexible, extensible framework for interacting with language models. Initially focused on Anthropic Claude, the system is designed to support multiple providers while maintaining consistent behavior and optimal performance.

## Provider Architecture

### LLM Provider Interface
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncGenerator

class LLMProvider(ABC):
    def __init__(self, config: Dict):
        self.config = config
        self.name = self.get_provider_name()
        self.models = self.get_available_models()
    
    @abstractmethod
    async def generate_response(self, 
                               messages: List[Dict], 
                               model: str = None,
                               **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    async def stream_response(self, 
                             messages: List[Dict], 
                             model: str = None,
                             **kwargs) -> AsyncGenerator[str, None]:
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        pass
    
    @abstractmethod
    def get_context_limit(self, model: str) -> int:
        pass
```

### Claude Provider Implementation
```python
import anthropic

class ClaudeProvider(LLMProvider):
    def __init__(self, config: Dict):
        super().__init__(config)
        self.client = anthropic.Anthropic(
            api_key=config.get('api_key'),
            base_url=config.get('base_url')
        )
        self.default_model = config.get('default_model', 'claude-3-5-sonnet-20241022')
    
    async def generate_response(self, 
                               messages: List[Dict], 
                               model: str = None,
                               **kwargs) -> LLMResponse:
        model = model or self.default_model
        
        try:
            response = await self.client.messages.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.7),
                tools=kwargs.get('tools', []),
                **kwargs
            )
            
            return LLMResponse(
                content=response.content,
                model=model,
                usage=response.usage,
                stop_reason=response.stop_reason
            )
            
        except anthropic.APIError as e:
            raise LLMError(f"Claude API error: {e}")
    
    async def stream_response(self, 
                             messages: List[Dict], 
                             model: str = None,
                             **kwargs) -> AsyncGenerator[str, None]:
        model = model or self.default_model
        
        async with self.client.messages.stream(
            model=model,
            messages=messages,
            max_tokens=kwargs.get('max_tokens', 4096),
            **kwargs
        ) as stream:
            async for chunk in stream:
                if chunk.type == 'content_block_delta':
                    yield chunk.delta.text
    
    def get_available_models(self) -> List[str]:
        return [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-haiku-20241022',
            'claude-3-opus-20240229'
        ]
    
    def estimate_tokens(self, text: str) -> int:
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def get_context_limit(self, model: str) -> int:
        limits = {
            'claude-3-5-sonnet-20241022': 200000,
            'claude-3-5-haiku-20241022': 200000,
            'claude-3-opus-20240229': 200000
        }
        return limits.get(model, 200000)
```

## Response Management

### Response Data Structure
```python
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class LLMResponse:
    content: List[Dict]  # Message content blocks
    model: str
    usage: Dict[str, int]  # Token usage information
    stop_reason: str
    tool_calls: Optional[List[Dict]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LLMError(Exception):
    message: str
    error_code: Optional[str] = None
    retry_after: Optional[int] = None
```

### Tool Integration
```python
class ToolMessage:
    def __init__(self, tool_name: str, parameters: Dict):
        self.tool_name = tool_name
        self.parameters = parameters
    
    def to_anthropic_format(self) -> Dict:
        return {
            "type": "tool_use",
            "id": f"tool_{uuid.uuid4()}",
            "name": self.tool_name,
            "input": self.parameters
        }

class ToolResult:
    def __init__(self, tool_call_id: str, result: Any, error: str = None):
        self.tool_call_id = tool_call_id
        self.result = result
        self.error = error
    
    def to_anthropic_format(self) -> Dict:
        return {
            "type": "tool_result",
            "tool_use_id": self.tool_call_id,
            "content": str(self.result) if not self.error else f"Error: {self.error}"
        }
```

## Context Management

### Context Window Optimization
```python
class ContextManager:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.context_limit = provider.get_context_limit()
        self.reserve_tokens = 2000  # Reserve for response
    
    def optimize_context(self, messages: List[Dict], model: str) -> List[Dict]:
        available_tokens = self.context_limit - self.reserve_tokens
        current_tokens = sum(self.provider.estimate_tokens(self._message_to_text(msg)) 
                           for msg in messages)
        
        if current_tokens <= available_tokens:
            return messages
        
        # Context compression strategies
        return self._compress_context(messages, available_tokens)
    
    def _compress_context(self, messages: List[Dict], target_tokens: int) -> List[Dict]:
        # Strategy 1: Keep system message and recent messages
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        user_messages = [msg for msg in messages if msg.get('role') != 'system']
        
        # Strategy 2: Summarize middle conversations
        if len(user_messages) > 10:
            recent_messages = user_messages[-5:]  # Keep last 5 exchanges
            old_messages = user_messages[:-5]
            
            summary = self._summarize_conversation(old_messages)
            summary_message = {
                "role": "user", 
                "content": f"[Previous conversation summary: {summary}]"
            }
            
            compressed_messages = system_messages + [summary_message] + recent_messages
        else:
            compressed_messages = messages
        
        return compressed_messages
    
    def _summarize_conversation(self, messages: List[Dict]) -> str:
        # Spawn a sub-agent to handle summarization
        from agent_spawner import spawn_child_agent
        
        summarization_agent = spawn_child_agent(
            agent_id="summarize_conversation_history",
            task="Summarize the provided conversation history, preserving key decisions and context",
            context={'messages': messages}
        )
        
        return summarization_agent.execute()
```

### Memory and State Management
```python
class ConversationMemory:
    def __init__(self, max_history: int = 50):
        self.messages = []
        self.max_history = max_history
        self.important_messages = []  # Messages marked as important
        self.project_context = {}
    
    def add_message(self, message: Dict, important: bool = False):
        self.messages.append(message)
        if important:
            self.important_messages.append(message)
        
        # Trim history if too long
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_context_messages(self, include_important: bool = True) -> List[Dict]:
        context = self.messages.copy()
        
        if include_important:
            # Ensure important messages are included
            for msg in self.important_messages:
                if msg not in context:
                    context.insert(-1, msg)  # Insert before last message
        
        return context
    
    def clear_history(self, keep_important: bool = True):
        if keep_important:
            self.messages = self.important_messages.copy()
        else:
            self.messages = []
            self.important_messages = []
```

## Rate Limiting and Error Handling

### Rate Limiter
```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60, tokens_per_minute: int = 100000):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_times = deque()
        self.token_usage = deque()
    
    async def acquire(self, estimated_tokens: int = 1000):
        await self._wait_for_request_limit()
        await self._wait_for_token_limit(estimated_tokens)
        
        now = datetime.now()
        self.request_times.append(now)
        self.token_usage.append((now, estimated_tokens))
    
    async def _wait_for_request_limit(self):
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Remove old requests
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()
        
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = (self.request_times[0] + timedelta(minutes=1) - now).total_seconds()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def _wait_for_token_limit(self, tokens: int):
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Remove old token usage
        while self.token_usage and self.token_usage[0][0] < cutoff:
            self.token_usage.popleft()
        
        current_tokens = sum(usage[1] for usage in self.token_usage)
        
        if current_tokens + tokens > self.tokens_per_minute:
            # Wait until oldest usage expires
            if self.token_usage:
                sleep_time = (self.token_usage[0][0] + timedelta(minutes=1) - now).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
```

### Error Handling and Retry Logic
```python
import asyncio
from typing import Callable

class LLMErrorHandler:
    def __init__(self):
        self.retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
        self.max_retries = 3
    
    async def with_retry(self, func: Callable, *args, **kwargs):
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                
                if attempt == self.max_retries:
                    break
                
                if self._should_retry(e):
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    await asyncio.sleep(delay)
                else:
                    break
        
        raise last_error
    
    def _should_retry(self, error: Exception) -> bool:
        # Retry on rate limits, network errors, temporary server errors
        if isinstance(error, anthropic.RateLimitError):
            return True
        if isinstance(error, anthropic.APIConnectionError):
            return True
        if isinstance(error, anthropic.InternalServerError):
            return True
        return False
```

## Model Selection and Configuration

### Model Selector
```python
class ModelSelector:
    def __init__(self):
        self.model_capabilities = {
            'claude-3-5-sonnet-20241022': {
                'context_length': 200000,
                'cost_per_1k_input': 0.003,
                'cost_per_1k_output': 0.015,
                'capabilities': ['reasoning', 'coding', 'analysis', 'creativity']
            },
            'claude-3-5-haiku-20241022': {
                'context_length': 200000,
                'cost_per_1k_input': 0.00025,
                'cost_per_1k_output': 0.00125,
                'capabilities': ['speed', 'efficiency', 'basic_reasoning']
            }
        }
    
    def select_model(self, task_type: str, context_size: int, budget_priority: bool = False) -> str:
        suitable_models = []
        
        for model, specs in self.model_capabilities.items():
            if context_size <= specs['context_length']:
                if task_type in specs['capabilities'] or 'reasoning' in specs['capabilities']:
                    suitable_models.append((model, specs))
        
        if not suitable_models:
            return 'claude-3-5-sonnet-20241022'  # Default fallback
        
        if budget_priority:
            # Choose cheapest suitable model
            return min(suitable_models, key=lambda x: x[1]['cost_per_1k_input'])[0]
        else:
            # Choose most capable model
            return max(suitable_models, key=lambda x: len(x[1]['capabilities']))[0]
```

## Cost Tracking and Optimization

### Usage Tracker
```python
class UsageTracker:
    def __init__(self):
        self.usage_log = []
        self.daily_costs = {}
        self.monthly_budget = None
    
    def log_usage(self, model: str, input_tokens: int, output_tokens: int):
        cost_info = self.model_selector.model_capabilities[model]
        input_cost = (input_tokens / 1000) * cost_info['cost_per_1k_input']
        output_cost = (output_tokens / 1000) * cost_info['cost_per_1k_output']
        total_cost = input_cost + output_cost
        
        usage_entry = {
            'timestamp': datetime.now(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': total_cost
        }
        
        self.usage_log.append(usage_entry)
        
        today = datetime.now().date()
        if today not in self.daily_costs:
            self.daily_costs[today] = 0
        self.daily_costs[today] += total_cost
    
    def get_daily_usage(self, date: datetime.date = None) -> Dict:
        date = date or datetime.now().date()
        return {
            'cost': self.daily_costs.get(date, 0),
            'entries': [entry for entry in self.usage_log 
                       if entry['timestamp'].date() == date]
        }
    
    def check_budget_alert(self) -> bool:
        if not self.monthly_budget:
            return False
        
        current_month_cost = sum(
            cost for date, cost in self.daily_costs.items()
            if date.month == datetime.now().month
        )
        
        return current_month_cost > (self.monthly_budget * 0.8)  # 80% threshold
```

## Configuration

### Provider Configuration
```yaml
# ralph_config.yaml
llm:
  provider: "claude"
  api_key: "${ANTHROPIC_API_KEY}"
  default_model: "claude-3-5-sonnet-20241022"
  rate_limits:
    requests_per_minute: 60
    tokens_per_minute: 100000
  context:
    max_history_messages: 50
    reserve_tokens: 2000
  cost_tracking:
    monthly_budget: 100.0
    alert_threshold: 0.8
  retry:
    max_attempts: 3
    backoff_multiplier: 2
```

### Environment Variables
- `ANTHROPIC_API_KEY`: API key for Claude
- `RALPH_LLM_MODEL`: Override default model
- `RALPH_LLM_BUDGET`: Monthly budget limit
- `RALPH_LLM_DEBUG`: Enable detailed logging