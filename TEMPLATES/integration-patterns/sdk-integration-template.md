# SDK Integration Template

**Last Updated:** 2025-10-20  
**Purpose:** Template for consuming my-tiny-data-collider as Python SDK

---

## Overview

This template shows how to integrate my-tiny-data-collider into your Python application using **direct imports** (SDK pattern).

**Use this when:**
- Consumer is Python
- Need type safety and IDE autocomplete
- Latency critical (microsecond calls)
- Same deployment environment

---

## Installation

### Option A: Install as Package (Recommended)

```powershell
# Install from local directory (editable mode)
pip install -e C:\Users\HP\my-tiny-data-collider

# OR install from Git
pip install git+https://github.com/MSD21091969/my-tiny-data-collider.git

# OR add to requirements.txt
echo "my-tiny-data-collider @ git+https://github.com/MSD21091969/my-tiny-data-collider.git" >> requirements.txt
pip install -r requirements.txt
```

### Option B: Add to PYTHONPATH

```powershell
# Add to environment (temporary - this session only)
$env:PYTHONPATH = "C:\Users\HP\my-tiny-data-collider\src"

# OR add to PowerShell profile (permanent)
Add-Content $PROFILE '$env:PYTHONPATH = "C:\Users\HP\my-tiny-data-collider\src"'

# OR set in python script
import sys
sys.path.insert(0, 'C:/Users/HP/my-tiny-data-collider/src')
```

---

## Basic Usage

### Example 1: Check Permission

```python
# your_app.py
import asyncio
from casefileservice.service import CasefileService
from pydantic_models.operations.casefile_ops import (
    CheckPermissionRequest,
    CheckPermissionPayload
)

async def check_user_access(casefile_id: str, user_id: str, permission: str) -> bool:
    """Check if user has specific permission on casefile"""
    
    # Create service instance
    service = CasefileService()
    
    # Build request
    request = CheckPermissionRequest(
        client_request_id=f"check_{casefile_id}_{user_id}",
        payload=CheckPermissionPayload(
            casefile_id=casefile_id,
            user_id=user_id,
            required_permission=permission
        )
    )
    
    # Execute method
    response = await service.check_permission(request)
    
    # Check response
    if response.status == "success":
        return response.payload.has_required_permission
    else:
        raise Exception(f"Permission check failed: {response.status}")

# Use it
if __name__ == "__main__":
    has_access = asyncio.run(
        check_user_access("cf_abc123", "usr_789", "read")
    )
    print(f"User has access: {has_access}")
```

### Example 2: Create Casefile

```python
from casefileservice.service import CasefileService
from pydantic_models.operations.casefile_ops import (
    CreateCasefileRequest,
    CreateCasefilePayload
)
from pydantic_models.canonical.casefile import CasefileMetadata

async def create_new_casefile(owner_id: str, title: str, description: str) -> str:
    """Create a new casefile and return its ID"""
    
    service = CasefileService()
    
    # Build metadata
    metadata = CasefileMetadata(
        title=title,
        description=description,
        tags=["sdk-created"],
        created_by=owner_id
    )
    
    # Build request
    request = CreateCasefileRequest(
        client_request_id=f"create_{owner_id}",
        payload=CreateCasefilePayload(
            owner_id=owner_id,
            metadata=metadata
        )
    )
    
    # Execute
    response = await service.create_casefile(request)
    
    if response.status == "success":
        return response.payload.casefile.casefile_id
    else:
        raise Exception(f"Creation failed: {response.status}")

# Use it
casefile_id = asyncio.run(
    create_new_casefile("usr_789", "My Casefile", "Created from SDK")
)
print(f"Created casefile: {casefile_id}")
```

### Example 3: Search Gmail Messages

```python
from pydantic_ai_integration.integrations.google_workspace.clients import GmailClient
from pydantic_ai_integration.integrations.google_workspace.models import (
    GmailSearchMessagesRequest
)

async def search_emails(query: str, max_results: int = 10) -> list:
    """Search Gmail messages with semantic query"""
    
    client = GmailClient()
    
    request = GmailSearchMessagesRequest(
        query=query,
        max_results=max_results,
        include_spam_trash=False
    )
    
    response = await client.search_messages(request)
    
    return [
        {
            "id": msg["id"],
            "subject": msg.get("subject"),
            "snippet": msg.get("snippet"),
            "date": msg.get("date")
        }
        for msg in response.messages
    ]

# Use it
emails = asyncio.run(search_emails("user permissions"))
for email in emails:
    print(f"{email['date']}: {email['subject']}")
```

---

## With Type Safety

### Using Type Hints

```python
from typing import Optional
from casefileservice.service import CasefileService
from pydantic_models.operations.casefile_ops import (
    GetCasefileRequest,
    GetCasefileResponse
)
from pydantic_models.canonical.casefile import CasefileModel

async def get_casefile(
    casefile_id: str,
    requesting_user_id: str
) -> Optional[CasefileModel]:
    """Get casefile with full type safety"""
    
    service: CasefileService = CasefileService()
    
    request: GetCasefileRequest = GetCasefileRequest(
        client_request_id=f"get_{casefile_id}",
        payload=GetCasefilePayload(
            casefile_id=casefile_id,
            requesting_user_id=requesting_user_id
        )
    )
    
    response: GetCasefileResponse = await service.get_casefile(request)
    
    if response.status == "success":
        casefile: CasefileModel = response.payload.casefile
        # IDE knows all fields: casefile.metadata.title, casefile.acl.owner_id, etc.
        return casefile
    else:
        return None

# Full autocomplete in IDE
casefile = await get_casefile("cf_abc123", "usr_789")
if casefile:
    print(casefile.metadata.title)  # ← IDE autocompletes 'title'
    print(casefile.acl.owner_id)    # ← IDE autocompletes 'owner_id'
```

### Using Pydantic Validation

```python
from pydantic import BaseModel, Field, validator
from pydantic_models.base.custom_types import CasefileId, UserId

class CasefileAccessRequest(BaseModel):
    """Your app's request model (validates at edge)"""
    casefile_id: CasefileId  # ← Auto-validates format
    user_id: UserId          # ← Auto-validates format
    permission: str = Field(..., pattern="^(read|write|admin)$")
    
    @validator('permission')
    def normalize_permission(cls, v):
        return v.lower()

async def check_access(request: CasefileAccessRequest) -> bool:
    """Your app validates at edge, then calls service"""
    # If we got here, casefile_id and user_id are valid
    # (Pydantic already validated them)
    
    service = CasefileService()
    check_request = CheckPermissionRequest(
        client_request_id=f"check_{request.casefile_id}",
        payload=CheckPermissionPayload(
            casefile_id=request.casefile_id,
            user_id=request.user_id,
            required_permission=request.permission
        )
    )
    
    response = await service.check_permission(check_request)
    return response.payload.has_required_permission

# Validation happens automatically
try:
    request = CasefileAccessRequest(
        casefile_id="cf_abc123",  # ✅ Valid
        user_id="usr_789",        # ✅ Valid
        permission="READ"         # ✅ Normalized to "read"
    )
    has_access = await check_access(request)
except ValueError as e:
    print(f"Invalid request: {e}")
```

---

## Error Handling

### Response Status Checking

```python
async def safe_get_casefile(casefile_id: str, user_id: str) -> Optional[CasefileModel]:
    """Handle all error cases"""
    
    service = CasefileService()
    request = GetCasefileRequest(...)
    
    try:
        response = await service.get_casefile(request)
        
        # Check status field
        if response.status == "success":
            return response.payload.casefile
        elif response.status == "error":
            print(f"Error: {response.payload}")  # Error details in payload
            return None
        elif response.status == "pending":
            print("Request is pending (async operation)")
            return None
        else:
            print(f"Unknown status: {response.status}")
            return None
    
    except Exception as e:
        # Network errors, validation errors, etc.
        print(f"Exception: {type(e).__name__}: {e}")
        return None
```

### Exception Handling

```python
from casefileservice.exceptions import (
    CasefileNotFoundError,
    PermissionDeniedError,
    ValidationError
)

async def get_casefile_with_exceptions(casefile_id: str, user_id: str) -> CasefileModel:
    """Raise exceptions for error cases"""
    
    service = CasefileService()
    request = GetCasefileRequest(...)
    
    try:
        response = await service.get_casefile(request)
        
        if response.status == "success":
            return response.payload.casefile
        else:
            # Convert response error to exception
            raise RuntimeError(f"Request failed: {response.status}")
    
    except CasefileNotFoundError:
        print(f"Casefile {casefile_id} not found")
        raise
    except PermissionDeniedError:
        print(f"User {user_id} lacks access")
        raise
    except ValidationError as e:
        print(f"Invalid request: {e}")
        raise

# Use with try/except
try:
    casefile = await get_casefile_with_exceptions("cf_abc123", "usr_789")
    print(f"Got casefile: {casefile.metadata.title}")
except CasefileNotFoundError:
    print("Casefile doesn't exist")
except PermissionDeniedError:
    print("Access denied")
```

---

## With Tool Session (Audit Trail)

### Using ToolSessionService

```python
from tool_sessionservice.service import ToolSessionService
from pydantic_models.workspace.tool_ops import ToolRequest

async def check_permission_with_audit(
    casefile_id: str,
    user_id: str,
    permission: str
) -> bool:
    """Check permission and create audit trail"""
    
    service = ToolSessionService()
    
    # Build tool request (wraps method call)
    request = ToolRequest(
        user_id=user_id,
        payload={
            "tool_name": "casefile_check_permission_tool",
            "parameters": {
                "casefile_id": casefile_id,
                "user_id": user_id,
                "required_permission": permission
            },
            "casefile_id": casefile_id  # Links to casefile
        }
    )
    
    # Execute through tool session (creates ToolEvent)
    response = await service.process_tool_request_with_session_management(request)
    
    # Response is ToolResponse (wraps method response)
    if response.status == "success":
        # Extract actual result from nested payload
        result = response.result.get("payload", {}).get("has_required_permission", False)
        return result
    else:
        raise Exception(f"Tool execution failed: {response.status}")

# Audit trail created automatically
has_access = await check_permission_with_audit("cf_abc123", "usr_789", "read")

# Can retrieve audit trail later
from tool_sessionservice.service import ToolSessionService
session_service = ToolSessionService()
events = await session_service.get_tool_events_for_casefile("cf_abc123")
for event in events:
    print(f"{event.timestamp}: {event.tool_name} - {event.result_status}")
```

---

## Configuration

### Environment Variables

```python
# config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Google Workspace
    google_credentials_path: str = os.getenv(
        'GOOGLE_APPLICATION_CREDENTIALS',
        'creds/service-account.json'
    )
    
    # Firestore
    firestore_project_id: str = os.getenv('FIRESTORE_PROJECT_ID', 'my-project')
    
    # Redis
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    
    class Config:
        env_file = '.env'

settings = Settings()

# Use in services
from casefileservice.service import CasefileService
service = CasefileService(
    firestore_project=settings.firestore_project_id
)
```

---

## Testing

### Unit Tests

```python
# tests/test_sdk_integration.py
import pytest
from casefileservice.service import CasefileService
from pydantic_models.operations.casefile_ops import CheckPermissionRequest

@pytest.mark.asyncio
async def test_check_permission():
    """Test SDK usage"""
    service = CasefileService()
    
    request = CheckPermissionRequest(...)
    response = await service.check_permission(request)
    
    assert response.status == "success"
    assert response.payload.has_required_permission is True
```

### Mocking

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    """Mock service calls"""
    with patch('casefileservice.service.CasefileService.check_permission') as mock:
        # Setup mock
        mock.return_value = AsyncMock(
            status="success",
            payload={"has_required_permission": True}
        )
        
        # Test your code
        has_access = await check_user_access("cf_123", "usr_789", "read")
        assert has_access is True
        
        # Verify mock called
        mock.assert_called_once()
```

---

## Summary

**SDK Pattern Advantages:**
- ⚡ Fast (microsecond calls, no network)
- ✅ Type-safe (full IDE support)
- 🐛 Debuggable (step through code)
- 📝 Validated (Pydantic models)

**When to Use:**
- Python consumer applications
- Jupyter notebooks
- Internal microservices (same cluster)
- Latency-critical operations

**When NOT to Use:**
- Non-Python consumers → Use HTTP API
- External consumers → Use HTTP API
- Isolated processes → Use CLI pattern
- Different deployment → Use HTTP API

**See Also:**
- CLI Template: `TEMPLATES/integration-patterns/cli-integration-template.md`
- HTTP Template: `TEMPLATES/integration-patterns/http-api-template.md`
- Agent Template: `TEMPLATES/integration-patterns/agent-tool-template.md`
