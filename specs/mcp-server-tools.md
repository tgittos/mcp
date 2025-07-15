# MCP Server Tools Specification

## Overview
The MCP Server Tools provide Ralph with essential capabilities for file operations, web content fetching, test execution, and system interaction. These tools are exposed through an MCP server that Ralph can consume to perform various tasks during its autonomous operation.

## Core Requirements

### Essential Tools for Ralph Operation
1. **File Operations**: Read, write, and manage files
2. **Web Content Fetching**: Fetch and parse web content for research
3. **Test Execution**: Run tests and collect results
4. **System Commands**: Execute shell commands and scripts
5. **Git Operations**: Version control operations
6. **Process Management**: Monitor and manage system processes

## Tool Specifications

### 1. File Operations Tools

#### 1.1 read_file
- **Purpose**: Read file content for analysis and processing
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to the file to read"
      },
      "encoding": {
        "type": "string",
        "description": "File encoding (default: utf-8)",
        "default": "utf-8"
      },
      "start_line": {
        "type": "integer",
        "description": "Start line number (1-indexed, optional)"
      },
      "end_line": {
        "type": "integer", 
        "description": "End line number (1-indexed, optional)"
      }
    },
    "required": ["path"]
  }
  ```
- **Output**: File content as text
- **Error Handling**: File not found, permission denied, encoding errors

#### 1.2 write_file
- **Purpose**: Write content to files
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to the file to write"
      },
      "content": {
        "type": "string",
        "description": "Content to write to the file"
      },
      "mode": {
        "type": "string",
        "description": "Write mode: 'w' (overwrite) or 'a' (append)",
        "default": "w"
      },
      "encoding": {
        "type": "string",
        "description": "File encoding (default: utf-8)",
        "default": "utf-8"
      }
    },
    "required": ["path", "content"]
  }
  ```
- **Output**: Success status and file metadata
- **Error Handling**: Permission denied, disk space issues, invalid path

#### 1.3 list_directory
- **Purpose**: List directory contents for navigation and discovery
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Directory path to list"
      },
      "recursive": {
        "type": "boolean",
        "description": "List recursively (default: false)",
        "default": false
      },
      "include_hidden": {
        "type": "boolean",
        "description": "Include hidden files (default: false)",
        "default": false
      }
    },
    "required": ["path"]
  }
  ```
- **Output**: List of files and directories with metadata
- **Error Handling**: Directory not found, permission denied

#### 1.4 delete_file
- **Purpose**: Delete files and directories
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path to file or directory to delete"
      },
      "recursive": {
        "type": "boolean",
        "description": "Delete recursively for directories (default: false)",
        "default": false
      }
    },
    "required": ["path"]
  }
  ```
- **Output**: Success status
- **Error Handling**: File not found, permission denied, directory not empty

### 2. Web Content Fetching Tools

#### 2.1 fetch_url (Existing)
- **Purpose**: Fetch content from URLs for research and information gathering
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "The URL to fetch content from"
      },
      "timeout": {
        "type": "number",
        "description": "Request timeout in seconds (default: 10)",
        "default": 10
      },
      "strip_html": {
        "type": "boolean",
        "description": "Strip HTML tags (default: true)",
        "default": true
      }
    },
    "required": ["url"]
  }
  ```
- **Output**: Fetched content as plain text
- **Error Handling**: Network errors, HTTP errors, timeout

#### 2.2 fetch_url_json
- **Purpose**: Fetch JSON content from URLs
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "The URL to fetch JSON from"
      },
      "timeout": {
        "type": "number",
        "description": "Request timeout in seconds (default: 10)",
        "default": 10
      }
    },
    "required": ["url"]
  }
  ```
- **Output**: Parsed JSON object
- **Error Handling**: Network errors, invalid JSON, timeout

### 3. Test Execution Tools

#### 3.1 run_tests
- **Purpose**: Execute test suites and collect results
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "Test command to execute"
      },
      "timeout": {
        "type": "number",
        "description": "Test timeout in seconds (default: 300)",
        "default": 300
      },
      "working_directory": {
        "type": "string",
        "description": "Working directory for test execution"
      }
    },
    "required": ["command"]
  }
  ```
- **Output**: Test results including pass/fail status, output, and timing
- **Error Handling**: Test failures, timeout, command not found

#### 3.2 run_build
- **Purpose**: Execute build processes
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "Build command to execute"
      },
      "timeout": {
        "type": "number",
        "description": "Build timeout in seconds (default: 600)",
        "default": 600
      },
      "working_directory": {
        "type": "string",
        "description": "Working directory for build execution"
      }
    },
    "required": ["command"]
  }
  ```
- **Output**: Build results including success/failure status and output
- **Error Handling**: Build failures, timeout, dependency issues

### 4. System Commands Tools

#### 4.1 execute_command
- **Purpose**: Execute shell commands and scripts
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "Command to execute"
      },
      "timeout": {
        "type": "number",
        "description": "Command timeout in seconds (default: 60)",
        "default": 60
      },
      "working_directory": {
        "type": "string",
        "description": "Working directory for command execution"
      },
      "capture_output": {
        "type": "boolean",
        "description": "Capture command output (default: true)",
        "default": true
      }
    },
    "required": ["command"]
  }
  ```
- **Output**: Command execution results including exit code, stdout, stderr
- **Error Handling**: Command not found, permission denied, timeout

#### 4.2 check_process
- **Purpose**: Check if a process is running
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "process_name": {
        "type": "string",
        "description": "Name of the process to check"
      },
      "pid": {
        "type": "integer",
        "description": "Process ID to check (optional)"
      }
    }
  }
  ```
- **Output**: Process status including running state and metadata
- **Error Handling**: Process not found, permission denied

### 5. Git Operations Tools

#### 5.1 git_status
- **Purpose**: Check git repository status
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "repository_path": {
        "type": "string",
        "description": "Path to git repository (default: current directory)",
        "default": "."
      }
    }
  }
  ```
- **Output**: Git status including modified files, branches, and commits
- **Error Handling**: Not a git repository, permission denied

#### 5.2 git_commit
- **Purpose**: Commit changes to git repository
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "Commit message"
      },
      "files": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Files to commit (default: all staged files)"
      },
      "repository_path": {
        "type": "string",
        "description": "Path to git repository (default: current directory)",
        "default": "."
      }
    },
    "required": ["message"]
  }
  ```
- **Output**: Commit hash and metadata
- **Error Handling**: No changes to commit, invalid message, git errors

#### 5.3 git_push
- **Purpose**: Push commits to remote repository
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "remote": {
        "type": "string",
        "description": "Remote name (default: origin)",
        "default": "origin"
      },
      "branch": {
        "type": "string",
        "description": "Branch name (default: current branch)",
        "default": "current"
      },
      "repository_path": {
        "type": "string",
        "description": "Path to git repository (default: current directory)",
        "default": "."
      }
    }
  }
  ```
- **Output**: Push results and metadata
- **Error Handling**: No commits to push, authentication errors, network issues

## MCP Server Implementation

### Server Architecture
- **Protocol**: MCP (Model Context Protocol) 2024-11-05
- **Transport**: JSON-RPC over stdin/stdout
- **Language**: Python 3.13+
- **Dependencies**: httpx, asyncio, json, pathlib

### Server Structure
```
src/mcp/
├── __init__.py
├── server.py              # Main MCP server implementation
├── tools/
│   ├── __init__.py
│   ├── file_ops.py        # File operation tools
│   ├── web_fetch.py       # Web content fetching tools
│   ├── test_runner.py     # Test execution tools
│   ├── system_cmd.py      # System command tools
│   └── git_ops.py         # Git operation tools
└── utils/
    ├── __init__.py
    ├── error_handler.py   # Error handling utilities
    └── validators.py      # Input validation utilities
```

### Tool Registration
- **Dynamic Registration**: Tools registered at server startup
- **Plugin Architecture**: Modular tool implementation
- **Error Handling**: Consistent error handling across all tools
- **Logging**: Comprehensive logging for debugging and monitoring

## Integration with Ralph

### Tool Consumption
- **MCP Client**: Ralph uses MCP client to consume tools
- **Tool Discovery**: Ralph discovers available tools at startup
- **Tool Invocation**: Ralph invokes tools as needed during operation
- **Result Processing**: Ralph processes tool results for decision making

### Tool Usage Patterns
1. **File Analysis**: Read files for code analysis and understanding
2. **Content Research**: Fetch web content for research and learning
3. **Test Execution**: Run tests to validate implementations
4. **Build Management**: Execute builds to verify system functionality
5. **Version Control**: Manage code changes and commits
6. **System Monitoring**: Check system status and processes

### Error Handling Integration
- **Tool Failures**: Ralph handles tool failures gracefully
- **Retry Logic**: Automatic retry for transient failures
- **Fallback Strategies**: Alternative approaches when tools fail
- **Error Reporting**: Comprehensive error reporting and logging

## Security Considerations

### Input Validation
- **Path Validation**: Validate file paths to prevent directory traversal
- **URL Validation**: Validate URLs to prevent malicious requests
- **Command Validation**: Validate commands to prevent injection attacks
- **Permission Checks**: Check permissions before file operations

### Sandboxing
- **Process Isolation**: Isolate tool execution from main process
- **Resource Limits**: Limit resource usage for tool execution
- **Timeout Enforcement**: Enforce timeouts to prevent hanging
- **Error Containment**: Contain errors to prevent system impact

## Performance Optimization

### Tool Efficiency
- **Async Operations**: Use async/await for I/O operations
- **Caching**: Cache frequently accessed data
- **Connection Pooling**: Pool HTTP connections for web requests
- **Resource Management**: Efficient resource allocation and cleanup

### Monitoring and Metrics
- **Tool Usage**: Track tool usage patterns
- **Performance Metrics**: Monitor tool performance
- **Error Rates**: Track error rates and types
- **Resource Usage**: Monitor resource consumption

## Success Criteria
- [ ] All essential tools implemented and functional
- [ ] MCP server properly exposes tools to Ralph
- [ ] Error handling robust and comprehensive
- [ ] Performance meets Ralph's requirements
- [ ] Security measures implemented and tested
- [ ] Integration with Ralph seamless and reliable 
