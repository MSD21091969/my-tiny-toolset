# OpenAPI Schema Generation

**Last Updated:** 2025-10-20  
**Purpose:** Explain how Pydantic models → JSON Schema → OpenAPI automatically

---

## Overview

**API Contract = Schema + Behavior Documentation**

In my-tiny-data-collider, API contracts are generated automatically from Pydantic models through this flow:

```
Pydantic Models (Python)
    ↓ (Pydantic serialization)
JSON Schema
    ↓ (FastAPI integration)
OpenAPI Specification
    ↓ (Swagger/Redoc rendering)
Interactive API Documentation
```

---

## Part 1: Pydantic Model → JSON Schema

### Your Base Models

```python
# pydantic_models/base/types.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Literal

PayloadT = TypeVar('PayloadT', bound=BaseModel)

class BaseRequest(BaseModel, Generic[PayloadT]):
    """All requests follow this pattern"""
    client_request_id: str = Field(..., description="Client-provided request ID")
    payload: PayloadT = Field(..., description="Request-specific data")

class BaseResponse(BaseModel, Generic[PayloadT]):
    """All responses follow this pattern"""
    request_id: str = Field(..., description="Server-assigned request ID (echoes client_request_id)")
    status: RequestStatus = Field(..., description="Request outcome (success/error/pending)")
    payload: PayloadT = Field(..., description="Response-specific data")
```

### Concrete Example: CheckPermissionRequest

```python
# pydantic_models/operations/casefile_ops.py
class CheckPermissionPayload(BaseModel):
    """Payload for checking if a user has permission."""
    casefile_id: CasefileId = Field(..., description="Casefile ID")
    user_id: UserId = Field(..., description="User ID to check")
    required_permission: PermissionLevel = Field(..., description="Required permission level")

class CheckPermissionRequest(BaseRequest[CheckPermissionPayload]):
    """Request to check if a user has permission."""
    operation: Literal["check_permission"] = "check_permission"
```

### Generated JSON Schema

```json
{
  "CheckPermissionRequest": {
    "type": "object",
    "properties": {
      "client_request_id": {
        "type": "string",
        "description": "Client-provided request ID"
      },
      "payload": {
        "$ref": "#/components/schemas/CheckPermissionPayload"
      },
      "operation": {
        "type": "string",
        "enum": ["check_permission"],
        "const": "check_permission"
      }
    },
    "required": ["client_request_id", "payload"]
  },
  "CheckPermissionPayload": {
    "type": "object",
    "properties": {
      "casefile_id": {
        "type": "string",
        "pattern": "^cf_[a-zA-Z0-9]{6,}$",
        "description": "Casefile ID"
      },
      "user_id": {
        "type": "string",
        "pattern": "^usr_[a-zA-Z0-9]{6,}$",
        "description": "User ID to check"
      },
      "required_permission": {
        "type": "string",
        "enum": ["read", "write", "share", "delete", "admin", "owner"],
        "description": "Required permission level"
      }
    },
    "required": ["casefile_id", "user_id", "required_permission"]
  }
}
```

**Key features:**
- Custom types → pattern validation (`CasefileId` → `pattern: ^cf_...`)
- Literal types → enum constraints (`operation: "check_permission"`)
- Field descriptions → schema descriptions
- Required/optional → required array

---

## Part 2: JSON Schema → OpenAPI (FastAPI Integration)

### FastAPI Endpoint (Hypothetical)

```python
# api/routes/casefile.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic_models.operations.casefile_ops import (
    CheckPermissionRequest,
    CheckPermissionResponse
)
from casefileservice.service import CasefileService

router = APIRouter(prefix="/api/v1/casefile", tags=["casefile"])

@router.post(
    "/check-permission",
    response_model=CheckPermissionResponse,
    summary="Check User Permission",
    description="Check if a user has specific permission level on a casefile"
)
async def check_permission(
    request: CheckPermissionRequest,
    service: CasefileService = Depends(get_casefile_service)
) -> CheckPermissionResponse:
    """
    Check if a user has the required permission level on a casefile.
    
    Returns structured response with permission details:
    - can_read: Whether user can read casefile
    - can_write: Whether user can modify casefile
    - can_share: Whether user can grant permissions
    - can_delete: Whether user can delete casefile
    - has_required_permission: Whether user meets the required level
    
    Raises:
        404: Casefile not found
        403: Requesting user lacks access to check permissions
    """
    try:
        return await service.check_permission(request)
    except CasefileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
```

### Generated OpenAPI Specification

```yaml
openapi: 3.1.0
info:
  title: My Tiny Data Collider API
  version: 1.0.0

paths:
  /api/v1/casefile/check-permission:
    post:
      tags:
        - casefile
      summary: Check User Permission
      description: Check if a user has specific permission level on a casefile
      operationId: check_permission_api_v1_casefile_check_permission_post
      
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CheckPermissionRequest'
            examples:
              basic_check:
                summary: Check read permission
                value:
                  client_request_id: "check_001"
                  operation: "check_permission"
                  payload:
                    casefile_id: "cf_abc123"
                    user_id: "usr_789xyz"
                    required_permission: "read"
      
      responses:
        '200':
          description: Permission check completed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CheckPermissionResponse'
              examples:
                has_permission:
                  summary: User has permission
                  value:
                    request_id: "check_001"
                    status: "success"
                    payload:
                      casefile_id: "cf_abc123"
                      user_id: "usr_789xyz"
                      permission: "read"
                      can_read: true
                      can_write: false
                      can_share: false
                      can_delete: false
                      has_required_permission: true
        
        '404':
          description: Casefile not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPError'
        
        '403':
          description: Permission denied
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPError'

components:
  schemas:
    CheckPermissionRequest:
      $ref: '#/components/schemas/CheckPermissionRequest'
    
    CheckPermissionResponse:
      $ref: '#/components/schemas/CheckPermissionResponse'
```

**What FastAPI adds automatically:**
- `operationId` (unique identifier per endpoint)
- HTTP status codes (from response_model + exceptions)
- Request/response examples (from docstrings + Pydantic examples)
- Tags (from router configuration)
- Error schemas (HTTPException → HTTPError schema)

---

## Part 3: Your Tool Schema YAML

### Tool Definition (config/methodtools_v1/)

```yaml
# casefile_check_permission_tool.yaml
name: casefile_check_permission_tool
version: "1.0.0"
description: "Check if a user has permission on a casefile"

classification:
  domain: workspace
  subdomain: casefile
  capability: check_permission
  complexity: atomic
  maturity: stable
  integration_tier: internal

parameters:
  - name: casefile_id
    type: str
    required: true
    description: "Casefile ID to check permission on"
    validation:
      pattern: "^cf_[a-zA-Z0-9]{6,}$"
  
  - name: user_id
    type: str
    required: true
    description: "User ID to check permission for"
    validation:
      pattern: "^usr_[a-zA-Z0-9]{6,}$"
  
  - name: required_permission
    type: str
    required: true
    description: "Permission level to check (read/write/share/delete/admin/owner)"
    validation:
      enum: ["read", "write", "share", "delete", "admin", "owner"]

returns:
  type: CheckPermissionResponse
  description: "Permission check result with detailed capabilities"

examples:
  - name: check_read_permission
    input:
      casefile_id: "cf_abc123"
      user_id: "usr_789xyz"
      required_permission: "read"
    expected_output:
      status: "success"
      payload:
        has_required_permission: true
        can_read: true
        can_write: false

errors:
  - code: 404
    condition: "Casefile not found"
  - code: 403
    condition: "Requesting user lacks access"

implementation:
  service: CasefileService
  method: check_permission
  module: casefileservice.service
```

**Tool schema is agent-focused:**
- Parameters flattened (no nested `payload` object)
- Examples for agent training
- Classification for tool selection
- Error conditions for retry logic

---

## Part 4: BaseRequest/BaseResponse → OpenAPI Mapping

### The Pattern

**Every method follows:**
```python
@register_service_method(...)
async def method_name(
    self,
    request: SomeRequest  # BaseRequest[PayloadT]
) -> SomeResponse:        # BaseResponse[PayloadT]
```

**Maps to OpenAPI:**
```yaml
paths:
  /api/v1/service/method:
    post:
      requestBody:
        schema:
          $ref: '#/components/schemas/SomeRequest'
      responses:
        '200':
          schema:
            $ref: '#/components/schemas/SomeResponse'
```

### Standard Fields (All Requests)

```python
class BaseRequest[T]:
    client_request_id: str  # → OpenAPI: required string
    payload: T              # → OpenAPI: $ref to payload schema
```

**OpenAPI result:**
```json
{
  "client_request_id": {
    "type": "string",
    "description": "Client-provided request ID"
  },
  "payload": {
    "$ref": "#/components/schemas/SpecificPayload"
  }
}
```

### Standard Fields (All Responses)

```python
class BaseResponse[T]:
    request_id: str         # → OpenAPI: required string
    status: RequestStatus   # → OpenAPI: enum (success/error/pending)
    payload: T              # → OpenAPI: $ref to payload schema
```

**OpenAPI result:**
```json
{
  "request_id": {
    "type": "string",
    "description": "Server-assigned request ID"
  },
  "status": {
    "type": "string",
    "enum": ["success", "error", "pending"],
    "description": "Request outcome"
  },
  "payload": {
    "$ref": "#/components/schemas/SpecificPayload"
  }
}
```

---

## Part 5: Custom Types → Schema Constraints

### Your Custom Types

```python
# pydantic_models/base/custom_types.py
from typing import Annotated
from pydantic import StringConstraints

CasefileId = Annotated[
    str, 
    StringConstraints(
        pattern=r'^cf_[a-zA-Z0-9]{6,}$',
        min_length=9
    )
]

UserId = Annotated[
    str,
    StringConstraints(
        pattern=r'^usr_[a-zA-Z0-9]{6,}$',
        min_length=10
    )
]

PermissionLevel = Literal["read", "write", "share", "delete", "admin", "owner"]
```

### Generated Schema Constraints

```json
{
  "casefile_id": {
    "type": "string",
    "pattern": "^cf_[a-zA-Z0-9]{6,}$",
    "minLength": 9,
    "description": "Casefile ID"
  },
  "user_id": {
    "type": "string",
    "pattern": "^usr_[a-zA-Z0-9]{6,}$",
    "minLength": 10,
    "description": "User ID"
  },
  "required_permission": {
    "type": "string",
    "enum": ["read", "write", "share", "delete", "admin", "owner"],
    "description": "Permission level"
  }
}
```

**Benefits:**
- Client SDKs enforce patterns (TypeScript regex, Python validation)
- API documentation shows valid formats
- Frontend forms use constraints (input masks, dropdowns)
- Agents understand valid values (fewer invalid tool calls)

---

## Part 6: Generating OpenAPI Docs

### Manual Generation (for SDK clients)

```python
# scripts/generate_openapi_spec.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import json

app = FastAPI()

# Import all routers
from api.routes import casefile_router, communication_router, tool_router
app.include_router(casefile_router)
app.include_router(communication_router)
app.include_router(tool_router)

# Generate OpenAPI spec
openapi_spec = get_openapi(
    title="My Tiny Data Collider API",
    version="1.0.0",
    description="Data integration platform with structured persistence",
    routes=app.routes
)

# Save to file
with open("openapi.json", "w") as f:
    json.dump(openapi_spec, f, indent=2)

print("OpenAPI spec generated: openapi.json")
```

### Runtime Documentation (Swagger/Redoc)

```python
# main.py
from fastapi import FastAPI

app = FastAPI(
    title="My Tiny Data Collider API",
    version="1.0.0",
    docs_url="/api/docs",        # Swagger UI
    redoc_url="/api/redoc",      # ReDoc
    openapi_url="/api/openapi.json"
)

# Access at:
# - http://localhost:8000/api/docs (interactive Swagger UI)
# - http://localhost:8000/api/redoc (documentation-focused ReDoc)
# - http://localhost:8000/api/openapi.json (raw JSON spec)
```

---

## Part 7: Schema Validation Flow

### Request Validation

```
1. Client sends JSON
   ↓
2. FastAPI deserializes to Pydantic model
   ↓
3. Pydantic validates:
   - Required fields present
   - Types correct (str, int, etc.)
   - Constraints satisfied (pattern, enum, etc.)
   - Custom validators pass
   ↓
4. If valid: Call service method
   If invalid: Return 422 Unprocessable Entity
```

### Response Validation

```
1. Service returns Pydantic model
   ↓
2. Pydantic validates response:
   - All required fields present
   - Types correct
   - Matches response_model schema
   ↓
3. FastAPI serializes to JSON
   ↓
4. Client receives validated response
```

### Why This Matters

**Type safety:** Both ends validated (client send + server return)  
**Documentation:** Schema = single source of truth  
**SDK generation:** OpenAPI → TypeScript/Python/Go/etc. clients  
**Agent integration:** Schema → tool definitions → agent understands parameters

---

## Summary

**Your architecture generates 3 schema formats:**

1. **JSON Schema** (from Pydantic models)
   - Used by: Validation, documentation, SDK generation
   - Format: JSON Schema Draft 2020-12

2. **OpenAPI Specification** (from FastAPI + Pydantic)
   - Used by: API docs, client SDKs, testing tools
   - Format: OpenAPI 3.1.0

3. **Tool YAML** (from @register_service_method)
   - Used by: Agent tool definitions, registry, catalog
   - Format: Custom YAML (your format)

**All 3 generated from same source:** Pydantic models + decorators

**Benefits:**
- Single source of truth (DRY principle)
- Automatic updates (change model → all schemas update)
- Type safety (validated at runtime + compile time)
- Documentation (auto-generated, always current)
