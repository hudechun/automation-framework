# Automation Framework Python SDK

Python SDK for the Automation Framework - simplify browser and desktop automation.

## Installation

```bash
pip install automation-framework-sdk
```

## Quick Start

```python
import asyncio
from automation_framework import AutomationClient

async def main():
    # Create client
    async with AutomationClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    ) as client:
        # Create a task
        task = await client.tasks.create(
            name="My First Task",
            description="Navigate to example.com",
            actions=[
                {"type": "goto", "url": "https://example.com"}
            ]
        )
        
        # Execute and wait for completion
        result = await client.tasks.execute_and_wait(task["id"])
        print(f"Task completed: {result['status']}")

asyncio.run(main())
```

## API Reference

### AutomationClient

Main client class for interacting with the API.

**Parameters:**
- `base_url` (str): API base URL (default: "http://localhost:8000")
- `api_key` (str): API key for authentication
- `timeout` (float): Request timeout in seconds (default: 30.0)

### TaskAPI

Task management operations.

**Methods:**
- `create(name, description, actions, **kwargs)`: Create a new task
- `get(task_id)`: Get task details
- `list(skip=0, limit=100, **filters)`: List tasks
- `update(task_id, **updates)`: Update a task
- `delete(task_id)`: Delete a task
- `execute(task_id)`: Execute a task
- `execute_and_wait(task_id, poll_interval=1.0, timeout=None)`: Execute and wait for completion

### SessionAPI

Session management operations.

**Methods:**
- `list(**filters)`: List sessions
- `get(session_id)`: Get session details
- `restore(session_id)`: Restore a session

### HistoryAPI

Execution history operations.

**Methods:**
- `list(skip=0, limit=100, **filters)`: List execution records
- `get(execution_id)`: Get execution details
- `export(format="json", **filters)`: Export history records

### ConfigAPI

Configuration management operations.

**Methods:**
- `list_models()`: List model configurations
- `create_model(**config)`: Create model configuration
- `update_model(config_id, **updates)`: Update model configuration

## Examples

See the `examples/` directory for more examples.

## Error Handling

The SDK raises specific exceptions for different error types:

```python
from automation_framework.sdk.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError,
    ResourceNotFoundError,
    TimeoutError
)

try:
    task = await client.tasks.get("invalid-id")
except ResourceNotFoundError:
    print("Task not found")
except AuthenticationError:
    print("Authentication failed")
except APIError as e:
    print(f"API error: {e}")
```
