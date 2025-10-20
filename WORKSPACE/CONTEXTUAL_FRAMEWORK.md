# Contextual Framework for my-tiny-data-collider

**Last Updated:** 2025-10-20  
**Purpose:** Bridge the 45% → 100% contextual understanding gap  
**Audience:** Developers with 89% theoretical knowledge, need practical context

---

## The 45% Gap: What You're Missing

You understand **WHAT** these concepts are (89% clear):
- OpenAPI, API contracts, validators, hooks, helpers
- Local vs global tools, submodules, SDK, ENV variables
- Imports, PATH, endpoints, CLI, HTTP

You're unclear on **HOW THEY FIT TOGETHER** (45% contextual):
- When to use decorators vs manual registration
- Local tools (in agent process) vs global tools (external service)
- SDK (import directly) vs CLI (subprocess) vs HTTP (API calls)
- How your code compares to pydantic-ai patterns
- Import resolution (why remove `src.` prefix, how Python path works)

**This document closes that gap.**

---

## Part 1: Local vs Global Tools (Pydantic AI Context)

### What Pydantic AI Means by "Local" and "Global"

From https://github.com/pydantic/pydantic-ai/issues/58 discussion:

**Local Tools (FunctionToolset)**
```python
# Tools defined IN the agent process
# Agent calls them directly (no network, no subprocess)

from pydantic_ai import Agent, FunctionToolset

toolset = FunctionToolset()

@toolset.tool
def get_temperature(city: str) -> float:
    """This runs IN the agent's Python process"""
    return 21.0

agent = Agent('openai:gpt-4o', toolsets=[toolset])
```

**Global Tools (ExternalToolset or MCP)**
```python
# Tools defined OUTSIDE the agent process
# Agent makes HTTP/RPC calls to external service

from pydantic_ai import Agent, ExternalToolset, ToolDefinition

# Tool definitions (schemas only, no implementation)
external_tools = [
    ToolDefinition(
        name='search_database',
        parameters_json_schema={...},
        description="Search external database via API"
    )
]

toolset = ExternalToolset(external_tools)
agent = Agent('openai:gpt-4o', toolsets=[toolset])

# When agent calls 'search_database':
# 1. Agent run returns DeferredToolRequests
# 2. Your code calls external API
# 3. Pass results back to agent via DeferredToolResults
```

### Your Code: Hybrid Approach

**Your ToolSessionService is GLOBAL-style architecture:**
- Tools registered in `MANAGED_METHODS` registry (centralized)
- Agent calls tools via `ToolSessionService.process_tool_request()` (internal HTTP-like pattern)
- Each tool execution creates `ToolEvent` (audit trail)
- Casefile context links all executions

**But you CAN use it locally too:**
```python
# Option A: Direct import (LOCAL - same process)
from casefileservice.service import CasefileService
request = CheckPermissionRequest(...)
response = await CasefileService().check_permission(request)

# Option B: Via ToolSessionService (GLOBAL-style - internal)
from tool_sessionservice.service import ToolSessionService
tool_request = ToolRequest(tool_name="casefile_check_permission_tool", ...)
response = await ToolSessionService().process_tool_request(tool_request)

# Option C: Via FastAPI (GLOBAL - external HTTP)
import httpx
response = httpx.post("http://localhost:8000/api/v1/tools", json={...})
```

**Design Decision:** You built global-style infrastructure (audit trails, session management, registry) but kept it internal (same codebase) for now. Can expose as HTTP API later without changing service code.

---

## Part 2: Decorators, Validators, Hooks, Helpers

### Decorators (Registration Metadata)

**What they do:** Add metadata to functions for discovery/documentation

**Your @register_service_method:**
```python
@register_service_method(
    name="check_permission",
    description="Check if user has permission",
    service_name="CasefileService",
    classification={...},
    required_permissions=["casefiles:read"]
)
async def check_permission(self, request: CheckPermissionRequest) -> CheckPermissionResponse:
    # Decorator does NOT wrap execution
    # It only registers metadata in MANAGED_METHODS registry
```

**Pydantic AI @toolset.tool:**
```python
@toolset.tool
async def get_temperature(city: str) -> float:
    """Decorator DOES wrap execution for validation"""
    return 21.0

# Pydantic AI auto-generates schema from type hints
# Your approach: Define schema in Pydantic models (BaseRequest/BaseResponse)
```

**Key Difference:**
- Pydantic AI: Decorator wraps execution, generates schema from function signature
- Your approach: Decorator only registers metadata, schema comes from Pydantic models

**Why your approach is better for you:**
- You need Request-Action-Response (RAR) pattern for audit trails
- You need `client_request_id`, `request_id`, `status`, `payload` structure
- Pydantic AI pattern doesn't support this (returns raw data, not wrapped responses)

### Validators (Data Validation)

**Pydantic Validators (field-level):**
```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str
    
    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```

**Your Custom Types (reusable validation):**
```python
# In pydantic_models/base/custom_types.py
from typing import Annotated
from pydantic import StringConstraints

# Define once, use everywhere
CasefileId = Annotated[str, StringConstraints(pattern=r'^cf_[a-zA-Z0-9]{6,}$')]

class CheckPermissionPayload(BaseModel):
    casefile_id: CasefileId  # Validation happens automatically
```

**62% code reduction:** Instead of writing `@field_validator` 100 times, you define `CasefileId` once and reuse it.

### Hooks (Lifecycle Events)

**Not in your codebase yet, but planned:**
```python
# Pre-execution hooks (before method runs)
@before_method_execution
async def log_request(request: BaseRequest):
    logger.info(f"Method called: {request.operation}")

# Post-execution hooks (after method runs)
@after_method_execution
async def audit_result(response: BaseResponse):
    await AuditService.log(response)

# RequestHub uses hook-like pattern via detect_hooks_for_method()
# But not exposed as decorators yet
```

### Helpers (Utility Functions)

**Difference between helpers and validators:**
- **Validators:** Check data correctness (raise errors if invalid)
- **Helpers:** Transform or assist (no error raising)

**Your helpers:**
```python
# In pydantic_models/base/validators.py
def extract_user_id_from_token(token: str) -> str:
    """Helper: Extract user ID (doesn't validate token)"""
    return token.split('_')[1]

def validate_token_format(token: str) -> str:
    """Validator: Check token format (raises ValueError)"""
    if not token.startswith('usr_'):
        raise ValueError('Invalid token')
    return token
```

---

## Part 3: SDK vs CLI vs HTTP

### SDK Pattern (Direct Import)

**What it is:** Import Python code directly into your program

```python
# Consumer code (another Python app)
from my_tiny_data_collider.casefileservice import CasefileService
from my_tiny_data_collider.pydantic_models.operations import CheckPermissionRequest

service = CasefileService()
request = CheckPermissionRequest(...)
response = await service.check_permission(request)
```

**Pros:** Fast (no network), type-safe, IDE autocomplete  
**Cons:** Must use Python, must install package, version lock  
**Use when:** Consumer is Python, latency critical, same deployment

### CLI Pattern (Subprocess)

**What it is:** Run your tools as command-line programs

```bash
# Hypothetical CLI wrapper
python -m my_tiny_data_collider.cli check_permission \
  --casefile-id cf_abc123 \
  --user-id user_789 \
  --required-permission write
```

**Implementation (not in your code yet):**
```python
# cli.py
import sys
import json
from casefileservice.service import CasefileService

def main():
    if sys.argv[1] == "check_permission":
        # Parse args, call service, print JSON
        request = CheckPermissionRequest(...)
        response = await CasefileService().check_permission(request)
        print(response.model_dump_json())

if __name__ == "__main__":
    main()
```

**Pros:** Language-agnostic, isolated processes, easy scripting  
**Cons:** Slower (process startup), serialization overhead, no type safety  
**Use when:** Consumer not Python, scripting, CI/CD pipelines

**Your toolset tools already use this:**
```powershell
# TOOLSET/analysis-tools/code_analyzer.bat
python %MY_TOOLSET%\analysis-tools\code_analyzer.py . --json
```

### HTTP API Pattern (FastAPI)

**What it is:** Expose methods as REST endpoints

```python
# api/routes.py (not in your code yet, but planned)
from fastapi import APIRouter, Depends
from pydantic_models.operations import CheckPermissionRequest, CheckPermissionResponse
from casefileservice.service import CasefileService

router = APIRouter()

@router.post("/casefile/check-permission", response_model=CheckPermissionResponse)
async def check_permission(
    request: CheckPermissionRequest,
    service: CasefileService = Depends()
):
    return await service.check_permission(request)
```

**Consumer code (any language):**
```javascript
// JavaScript client
const response = await fetch('http://localhost:8000/api/v1/casefile/check-permission', {
  method: 'POST',
  body: JSON.stringify({
    client_request_id: 'my_check_123',
    payload: {
      casefile_id: 'cf_abc123',
      user_id: 'user_789',
      required_permission: 'write'
    }
  })
});
```

**Pros:** Language-agnostic, scalable, versioned API  
**Cons:** Network overhead, requires server, more complex deployment  
**Use when:** Multiple consumers, different languages, distributed system

---

## Part 4: API Contracts (OpenAPI)

### What is an API Contract?

**API Contract = Schema + Behavior Promise**

**Schema (structure):**
```yaml
# OpenAPI schema auto-generated from your Pydantic models
paths:
  /casefile/check-permission:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CheckPermissionRequest'
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CheckPermissionResponse'

components:
  schemas:
    CheckPermissionRequest:
      type: object
      properties:
        client_request_id:
          type: string
        payload:
          $ref: '#/components/schemas/CheckPermissionPayload'
```

**Behavior promise (documentation):**
- Method will return `200` if user has permission
- Method will return `403` if user lacks permission
- Method will return `404` if casefile doesn't exist
- `request_id` in response matches `client_request_id` in request

**Your code generates contracts automatically:**
- Pydantic models → JSON Schema (FastAPI does this)
- `@register_service_method` → Method metadata → Tool YAML
- Tool YAML → Agent tool definitions

---

## Part 5: Import Resolution (The `src.` Mystery)

### Why Remove `src.` Prefix?

**The problem:**
```python
# This fails:
from src.casefileservice.service import CasefileService
# ModuleNotFoundError: No module named 'src'

# This works:
from casefileservice.service import CasefileService
```

**Why?**

**Python's import system:**
1. Python looks for modules in `sys.path` (list of directories)
2. When you run `python src/main.py`, Python adds `src/` to `sys.path`
3. Now `casefileservice` is importable (it's in `src/` which is in `sys.path`)
4. But `src.casefileservice` is NOT importable (no folder named `src` in `sys.path`)

**Your repo structure:**
```
my-tiny-data-collider/
├── src/                    ← This folder is added to sys.path
│   ├── casefileservice/    ← Importable as: casefileservice
│   ├── tool_sessionservice/← Importable as: tool_sessionservice
│   └── pydantic_models/    ← Importable as: pydantic_models
└── tests/                  ← This folder is added to sys.path (pytest)
    └── unit/               ← Importable as: unit
```

**When `src/` is in path:**
- ✅ `from casefileservice.service import CasefileService`
- ❌ `from src.casefileservice.service import CasefileService`

**When project root is in path (less common):**
- ✅ `from src.casefileservice.service import CasefileService`
- ❌ `from casefileservice.service import CasefileService`

**Your codebase uses first pattern (src/ in path)** because:
- pytest adds `src/` to path automatically
- `pyproject.toml` likely has `[tool.setuptools] packages = ["src"]`
- FastAPI runs from `src/` directory

---

## Part 6: Submodules (Git Context)

### What are Submodules?

**Submodules = Git repos inside Git repos**

**Your toolset repo has submodules:**
```
my-tiny-toolset/
├── PROMPTS/
│   ├── awesome-prompts/     ← Git submodule (external repo)
│   └── edu-prompts/         ← Git submodule (external repo)
├── SCHEMAS/
│   └── schemastore/         ← Git submodule (external repo)
└── EXAMPLES/
    └── public-apis/         ← Git submodule (external repo)
```

**Why use submodules?**
- Reuse external repos without copying code
- Keep them updated independently
- Track specific versions (commit hashes)

**How to update:**
```powershell
# Update all submodules to latest
git submodule update --remote

# Update specific submodule
cd PROMPTS/awesome-prompts
git pull origin main
cd ../..
git add PROMPTS/awesome-prompts
git commit -m "Update awesome-prompts to latest"
```

**Your folder README should point to relevant sections:**
```markdown
# PROMPTS/README.md

**Submodules:**
- `awesome-prompts/` - 🔗 [GitHub](https://github.com/f/awesome-chatgpt-prompts)
  - Relevant: `prompts/coding.md` (code review prompts)
  - Relevant: `prompts/data-analysis.md` (data engineering prompts)
```

---

## Part 7: Your Code vs Pydantic AI Patterns

### Pattern Comparison Table

| Feature | Pydantic AI Pattern | Your Pattern | Why Yours is Different |
|---------|---------------------|--------------|----------------------|
| **Tool Registration** | `@toolset.tool` decorator wraps execution | `@register_service_method` only registers metadata | You need RAR pattern with audit trails |
| **Request/Response** | Functions return raw data | Methods accept `BaseRequest[T]`, return `BaseResponse[T]` | Structured context (request_id, status, payload) |
| **Validation** | Schema from function signature | Schema from Pydantic models | More control, reusable types (62% reduction) |
| **Context Passing** | `ctx: RunContext` parameter | `MDSContext` object with user/casefile/session | Richer context (casefile-centric) |
| **Tool Discovery** | Runtime toolset composition | Static registry + YAML | Supports documentation generation, drift detection |
| **Session Management** | Agent manages internally | Dual-session architecture (chat + tool sessions) | Audit trails, lazy creation, reusable sessions |
| **Error Handling** | Exceptions propagate to agent | `status: RequestStatus` in response | Agents see structured errors, not exceptions |
| **Async Execution** | All tools async | All methods async | Both use async (good!) |

### Example: Same Feature, Different Patterns

**Pydantic AI:**
```python
from pydantic_ai import Agent, RunContext

@agent.tool
async def check_permission(ctx: RunContext, casefile_id: str, user_id: str) -> bool:
    """Returns True/False directly to agent"""
    # No request wrapper, no audit trail, no casefile context
    return True  # Simplified
```

**Your Pattern:**
```python
@register_service_method(
    name="check_permission",
    description="Check if user has permission",
    service_name="CasefileService",
    classification={...}
)
async def check_permission(
    self, 
    request: CheckPermissionRequest
) -> CheckPermissionResponse:
    """Returns structured response with audit info"""
    # Request contains: client_request_id, payload with casefile_id/user_id
    # Response contains: request_id, status, payload with result + metadata
    # ToolEvent created automatically (audit trail)
    # Casefile context preserved
    return CheckPermissionResponse(
        request_id=request.client_request_id,
        status="success",
        payload=PermissionCheckPayload(
            casefile_id=request.payload.casefile_id,
            user_id=request.payload.user_id,
            has_required_permission=True,
            can_read=True,
            can_write=False,
            # ... more metadata
        )
    )
```

**Why your pattern is more complex but necessary:**
- Compliance: Audit trails required for legal/medical data
- Multi-user: Casefile context links related operations
- Debugging: Structured responses easier to trace than raw booleans
- Documentation: Auto-generate API docs from Pydantic models

---

## Part 8: Environment Variables & Paths

### Environment Variables in Your System

**`$env:MY_TOOLSET`** (Windows PowerShell)
```powershell
$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"

# Usage in batch files (TOOLSET/analysis-tools/*.bat)
python %MY_TOOLSET%\analysis-tools\code_analyzer.py . --json
```

**Why use environment variables?**
- Toolset location can change (different machines, CI/CD)
- Consumer repos don't need to know absolute paths
- Easy to override for testing

**Other common environment variables:**
```powershell
# Python path (where Python looks for modules)
$env:PYTHONPATH = "C:\Users\HP\my-tiny-data-collider\src"

# Application config
$env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"

# API keys (never commit these!)
$env:OPENAI_API_KEY = "sk-..."
$env:GOOGLE_API_KEY = "..."
```

### PATH vs PYTHONPATH

**PATH** (system command search):
```powershell
# Directories where Windows looks for executables
$env:PATH = "C:\Python\;C:\Program Files\Git\bin;..."

# When you type 'python', Windows searches PATH for python.exe
python --version
```

**PYTHONPATH** (module search):
```python
# Directories where Python looks for modules
import sys
print(sys.path)
# ['', 'C:\\Users\\HP\\my-tiny-data-collider\\src', ...]

# When you import casefileservice, Python searches sys.path
from casefileservice.service import CasefileService
```

---

## Part 9: Quick Reference Guide

### When to Use Each Pattern

| Scenario | Use This | Example |
|----------|----------|---------|
| **Calling service method directly** | SDK (import) | `from casefileservice import CasefileService; await service.check_permission(request)` |
| **With audit trail** | ToolSessionService | `await ToolSessionService().process_tool_request(ToolRequest(...))` |
| **From another language** | HTTP API (future) | `POST /api/v1/casefile/check-permission` |
| **In CI/CD pipeline** | CLI (future) | `python -m collider check_permission --casefile cf_123` |
| **Agent needs to call** | Register as tool | Already done (28 methods registered) |

### How to Add New Method

1. **Define Request/Response models** (in `pydantic_models/operations/`)
2. **Add method to service** with `@register_service_method` decorator
3. **Decorator auto-registers** in `MANAGED_METHODS`
4. **Regenerate YAML** with `export_registry_to_yaml.py`
5. **Generate tool YAML** with `generate_method_tools.py`
6. **Update model docs** with `model_docs_generator.py`

**No manual YAML editing needed!** (That's the point of decorators)

---

## Part 10: Next Steps to Close Gap Fully

**For EXAMPLES/:**
- Add real pydantic-ai code samples
- Add YOUR code samples side-by-side
- Show pattern differences explicitly

**For SCHEMAS/:**
- Document OpenAPI generation from Pydantic
- Show tool_schema YAML structure
- Explain parameter validation flow

**For CONFIGS/:**
- Document all environment variables
- Show import resolution rules
- Add Python path setup guide

**For TEMPLATES/:**
- Create SDK integration template
- Create CLI wrapper template
- Create HTTP API template
- Create agent tool registration template

**Action:** Update all CAPITAL folders with this contextual knowledge, ensuring REFERENCE/ stays internal-only.

---

**This framework gives you the missing 55% context. Read this, then we'll organize it into CAPITAL folders properly.**
