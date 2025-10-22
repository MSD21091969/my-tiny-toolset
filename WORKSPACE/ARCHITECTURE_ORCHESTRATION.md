# Architecture & Orchestration Strategy

**Last Updated:** 2025-10-21  
**Status:** Planning & Analysis  
**Priority:** High - Foundation for scalability

---

## Executive Summary

Analysis of current service architecture identifying orchestration concerns scattered across multiple modules. Proposes reorganization into dedicated `orchestrationservice/` and `methodregistryservice/` modules for cleaner separation of concerns.

**Key Issues:**
- RequestHub monolithic (1005 lines) - difficult to test and extend
- Session management split across 3 locations
- Execution/orchestration logic scattered
- Registry/decorator code needs consolidation

**Proposed Solution:**
- New `orchestrationservice/` - workflow engine, hooks, policies
- New `methodregistryservice/` - unified method/tool registry
- Simplified `coreservice/` - utilities only
- 8-12 hour migration roadmap in 4 phases

---

## Current Architecture

### Service Organization

```
src/
├── authservice/           ✅ Authentication & JWT
├── casefileservice/       ✅ Casefile CRUD
├── communicationservice/  ✅ Gmail, Drive, Sheets
├── tool_sessionservice/   ✅ Tool session lifecycle
├── persistence/           ✅ Repository & Firestore
│
└── Integration Layer (SCATTERED)
    ├── coreservice/
    │   ├── request_hub.py           🔴 1005 lines - orchestration
    │   ├── service_container.py     ✅ Dependency injection
    │   ├── context_aware_service.py ✅ Context utilities
    │   ├── policy_patterns.py       ⚠️ Should move
    │   └── ...
    │
    └── pydantic_ai_integration/
        ├── session_manager.py       🔴 Session orchestration
        ├── method_decorator.py      ✅ Method registration
        ├── method_registry.py       ✅ Method registry
        ├── tool_decorator.py        ✅ Tool registration
        ├── tool_definition.py       ✅ Tool definitions
        ├── execution/
        │   └── chain_executor.py    🔴 Multi-method orchestration
        └── registry/
            └── parameter_mapping.py ✅ Validation
```

---

## Problems Identified

### 1. RequestHub Monolith

**File:** `src/coreservice/request_hub.py` (1005 lines)

**Responsibilities:**
- Operation routing (28 operation types)
- Hook execution (metrics, audit, session_lifecycle)
- Context preparation
- Policy loading
- Error handling

**Issues:**
- All 28 operation handlers in one file
- Hard to test individual concerns
- Hard to add new hooks/operations without modification
- Policy engine intertwined with routing
- No clear separation of orchestration vs execution

### 2. Session Management Fragmentation

**Three locations manage sessions:**

1. **ToolSessionService** (`tool_sessionservice/`)
   - `create_session()`, `get_session()`, `close_session()`
   - Tool session CRUD operations

2. **SessionManager** (`pydantic_ai_integration/session_manager.py`)
   - `_find_existing_session()`, `plan_tool_chain()`, `track_tool_execution()`
   - Session orchestration logic

3. **RequestHub** (`coreservice/request_hub.py`)
   - Session lifecycle hook
   - Session context preparation
   - Session error handling

**Issue:** Unclear responsibilities, hard to understand session flow

### 3. Execution/Orchestration Split

**Execution logic scattered across:**

1. **RequestHub** - 22 operation-specific `_execute_*` methods
2. **ChainExecutor** - Multi-method orchestration (`execute_chain`, `_execute_step`)
3. **Tool execution** - Tool wrapper execution, param validation

**Issue:** No clear boundary between "execute single operation" vs "orchestrate workflow"

### 4. Registry Cluster

**Registry code in `pydantic_ai_integration/`:**
- `method_decorator.py` (100+ lines) - Method registration
- `method_registry.py` (300+ lines) - Registry + search
- `tool_decorator.py` (1000+ lines) - Tool registration + wrapper
- `tool_definition.py` (180 lines) - Tool models
- `tool_utils.py` (200+ lines) - Utilities
- `session_manager.py` (200+ lines) - Session logic
- `registry/parameter_mapping.py` (500+ lines) - Validation

**Issue:** Should be consolidated into dedicated service module

---

## Proposed Architecture

### New Service Organization

```
src/
├── authservice/            ✅ KEEP - Domain: Authentication
├── casefileservice/        ✅ KEEP - Domain: Casefile management
├── communicationservice/   ✅ KEEP - Domain: Communications
├── tool_sessionservice/    ✅ KEEP - Domain: Session CRUD
├── persistence/            ✅ KEEP - Infrastructure: Data layer
│
├── orchestrationservice/   🆕 NEW - Orchestration layer
│   ├── __init__.py
│   ├── orchestrator.py          (replaces RequestHub - 300 lines)
│   ├── session_orchestrator.py  (replaces SessionManager)
│   ├── chain_executor.py        (move from pydantic_ai_integration/)
│   ├── hook_manager.py          (extracted from RequestHub)
│   ├── policy_engine.py         (replaces policy_patterns)
│   └── README.md
│
├── methodregistryservice/  🆕 NEW - Method/Tool orchestration
│   ├── __init__.py
│   ├── method_registry.py       (move from pydantic_ai_integration/)
│   ├── tool_registry.py         (consolidate tool_decorator + tool_definition)
│   ├── registration.py          (unified @register decorators)
│   ├── parameter_validator.py   (move from pydantic_ai_integration/registry/)
│   └── README.md
│
├── coreservice/            ✅ KEEP (simplified)
│   ├── service_container.py     ✅ Dependency injection
│   ├── context_aware_service.py ✅ Context utilities
│   ├── id_service.py            ✅ ID generation
│   └── README.md
│
├── persistence/            ✅ KEEP - Data layer
├── pydantic_models/        ✅ KEEP - Models & types
└── pydantic_api/           ✅ KEEP - HTTP API
```

---

## Detailed Design

### OrchestrationService (Workflow Engine)

**Purpose:** Central orchestration of operations, hooks, and policies

**Location:** `src/orchestrationservice/`

#### 1. orchestrator.py (300-400 lines)

Replaces RequestHub with cleaner, focused responsibility:

```python
class Orchestrator:
    """Orchestrates single & multi-method operations."""
    
    def __init__(self, 
                 hook_manager: HookManager,
                 policy_engine: PolicyEngine,
                 session_orchestrator: SessionOrchestrator,
                 service_manager: ServiceManager):
        self.hooks = hook_manager
        self.policies = policy_engine
        self.sessions = session_orchestrator
        self.services = service_manager
    
    async def dispatch(self, request: BaseRequest) -> BaseResponse:
        """Single-method orchestration with clear 8-step flow."""
        
        # 1. Get execution directives (controls HOW)
        directives = request.payload.execution_directives
        
        # 2. Get policy
        policy = self.policies.get_policy(request.operation)
        
        # 3. Prepare context
        context = await self._prepare_context(request, policy)
        
        # 4. Filter hooks based on directives
        hooks = self.hooks.filter_hooks(
            policy.hooks,
            skip=directives.skip_hooks if directives else []
        )
        
        # 5. Run pre-hooks
        await self.hooks.run_hooks("pre", request, context, hooks)
        
        # 6. Execute operation (delegate to service)
        response = await self._execute_operation(request, directives)
        
        # 7. Run post-hooks
        await self.hooks.run_hooks("post", request, context, response, hooks)
        
        # 8. Attach metadata
        self._attach_metadata(response, context)
        
        return response
    
    async def _execute_operation(self, request, directives):
        """Delegate to appropriate domain service."""
        operation_type = request.operation.split(".")[0]
        
        if operation_type == "casefile":
            return await self.services.casefile_service.execute(request, directives)
        elif operation_type == "tool_execution":
            return await self.services.tool_session_service.execute(request, directives)
        elif operation_type == "chat":
            return await self.services.communication_service.execute(request, directives)
        # ... etc
```

**Benefits:**
- Clear 8-step orchestration flow
- Hooks are explicit via HookManager
- Policy engine is explicit via PolicyEngine
- Directives are first-class citizens
- Easy to add new operations
- Services handle their own domain logic

#### 2. session_orchestrator.py (200 lines)

Consolidates SessionManager + ToolSessionService orchestration concerns:

```python
class SessionOrchestrator:
    """Orchestrates session lifecycle across chat + tool sessions."""
    
    async def find_or_create_session(self, user_id, casefile_id):
        """Find existing or create new session."""
        pass
    
    async def link_session_to_casefile(self, session_id, casefile_id):
        """Link session to casefile context."""
        pass
    
    async def track_execution(self, session_id, operation, result):
        """Track operation execution in session history."""
        pass
```

**Benefits:**
- Single source of truth for session orchestration
- Clear session lifecycle management
- Separates orchestration from CRUD (ToolSessionService still handles CRUD)

#### 3. hook_manager.py (150 lines)

Extracted from RequestHub for pluggable hook architecture:

```python
class HookManager:
    """Manages hook execution (metrics, audit, session_lifecycle)."""
    
    async def run_hooks(self, stage: Literal["pre", "post"], ...):
        """Execute hooks for given stage."""
        pass
    
    def filter_hooks(self, hooks, skip_list, execution_mode):
        """Filter hooks based on execution directives."""
        pass
    
    def register_hook(self, name: str, handler: HookHandler):
        """Register custom hook handler."""
        pass
```

**Benefits:**
- Pluggable hook architecture
- Easy to add new hooks without modifying Orchestrator
- Clear hook lifecycle management

#### 4. policy_engine.py (200 lines)

Moved from `coreservice/policy_patterns.py`:

```python
# Move existing policy_patterns.py here
# Clearer naming and focused responsibility
```

#### 5. chain_executor.py

Moved from `pydantic_ai_integration/execution/`:

```python
# Move existing chain_executor.py here
# Update imports to use new service structure
```

---

### MethodRegistryService (Method/Tool Registration)

**Purpose:** Unified registry for methods and tools

**Location:** `src/methodregistryservice/`

#### 1. method_registry.py

Moved from `pydantic_ai_integration/`:

```python
# Keep mostly as-is with clean imports
```

#### 2. tool_registry.py

Consolidates `tool_decorator.py` + `tool_definition.py`:

```python
class ToolRegistry:
    """Unified tool registry with lazy loading."""
    
    def register_tool(self, name, method_name, ...):
        """Register tool definition."""
        pass
    
    def get_tool(self, tool_name):
        """Retrieve tool by name."""
        pass
    
    def list_tools(self, category=None, domain=None, ...):
        """List tools with optional filtering."""
        pass
```

**Benefits:**
- Consolidates tool registration logic
- Provides clean public API
- Supports lazy loading

#### 3. registration.py

Unified decorator interface:

```python
@register_method(name="create_casefile", ...)
def create_casefile_method(...):
    pass

@register_tool(name="Create Casefile Tool", method_name="create_casefile", ...)
def create_casefile_tool(...):
    pass
```

**Benefits:**
- Single decorator interface
- Both methods and tools in one place
- Clear registration contract

#### 4. parameter_validator.py

Moved from `pydantic_ai_integration/registry/parameter_mapping.py`:

```python
class ParameterValidator:
    """Validates method parameters against tool definitions."""
    
    def validate_tool_to_method_mapping(self, tool_def, method_def):
        """Validate tool params map to method signature."""
        pass
    
    def validate_execution_parameters(self, tool_name, params):
        """Validate runtime parameters."""
        pass
```

---

### Simplified CoreService

**Purpose:** Core utilities only (no orchestration)

**Keep:**
- `service_container.py` ✅ - Dependency injection (already good)
- `context_aware_service.py` ✅ - Context utilities (already good)
- `id_service.py` ✅ - ID generation (already good)

**Move Out:**
- `policy_patterns.py` → `orchestrationservice/policy_engine.py`
- `service_metrics.py` → `orchestrationservice/hook_manager.py` (as metrics hook)
- `test_autonomous.py` → `tests/`

---

## Migration Roadmap

### Phase 1: Create MethodRegistryService (2-3 hours)

1. Create `methodregistryservice/` directory structure
2. Move `method_registry.py` (mostly as-is)
3. Consolidate `tool_decorator` + `tool_definition` → `tool_registry.py`
4. Create `registration.py` with unified decorators
5. Move `parameter_mapping.py` → `parameter_validator.py`
6. Update imports in affected files
7. Run tests to verify

### Phase 2: Create OrchestrationService (3-4 hours)

1. Create `orchestrationservice/` directory structure
2. Extract RequestHub `_execute_*` methods → `orchestrator.py`
3. Move `SessionManager` → `session_orchestrator.py`
4. Extract hooks → `hook_manager.py`
5. Move `policy_patterns.py` → `policy_engine.py`
6. Move `ChainExecutor` (update imports)
7. Update service_container to wire new services
8. Run tests to verify

### Phase 3: Update Imports & References (2-3 hours)

1. Update all imports across codebase
2. Update routers in `pydantic_api/`
3. Update tests to use new locations
4. Fix circular import issues
5. Run full test suite

### Phase 4: Clean Up & Documentation (1-2 hours)

1. Delete old files (after verification)
2. Create README files in each new service
3. Update architecture documentation
4. Update ROUNDTRIP_ANALYSIS.md
5. Final test run

**Total Estimated Time: 8-12 hours**

---

## Benefits Analysis

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Clarity** | RequestHub unclear (1005 lines) | Orchestrator focused (300 lines) |
| **Modularity** | Sessions split 3 ways | SessionOrchestrator unified |
| **Testing** | Hard to test RequestHub | Easy to test Orchestrator |
| **Extensibility** | Hard to add hooks/operations | Plugin architecture with HookManager |
| **Organization** | Services mixed with integration | Clear service boundaries |
| **Scalability** | Monolithic RequestHub | Microservice-ready architecture |

---

## RequestHub vs Orchestrator Comparison

### Current RequestHub (1005 lines)

```python
class RequestHub:
    async def dispatch(request):
        # 1. Routing logic (handlers dict)
        # 2. Hook preparation
        # 3. Policy loading
        # 4. 28 operation handlers (handlers._execute_*)
        # 5. Hook execution
        # 6. Error handling
        # 7. Response attachment
```

**Issues:**
- All 28 operation handlers in one file
- Hooks mixed with business logic
- Policy engine intertwined
- Hard to understand flow

### Proposed Orchestrator (300 lines)

**8-Step Clear Flow:**
1. Get execution directives (controls HOW)
2. Get policy
3. Prepare context
4. Filter hooks based on directives
5. Run pre-hooks
6. Execute operation (delegate to service)
7. Run post-hooks
8. Attach metadata

**Benefits:**
- Clear step-by-step flow
- Hooks explicit via HookManager
- Policy explicit via PolicyEngine
- Directives first-class
- Easy to add operations
- Services own domain logic

---

## Risk Analysis

### Low Risk ✅
- New services don't break existing functionality
- Imports can be gradually migrated
- Old files can coexist during transition

### Medium Risk ⚠️
- Circular imports between services
- Tests need updating
- ServiceContainer needs rewiring

### Mitigation Strategy
- Use dependency injection (already in place)
- Create services incrementally
- Run full test suite after each phase
- Create migration guide

---

## Decision Points

**Q1: Move RequestHub completely or run in parallel?**
- **Decision:** Run both during transition, gradually migrate routers
- **Timeline:** 2-3 weeks

**Q2: Merge ToolSessionService with SessionOrchestrator?**
- **Decision:** Keep ToolSessionService for CRUD, SessionOrchestrator for orchestration
- **Rationale:** Separation of concerns (data vs behavior)

**Q3: Create separate MethodService or just reorganize?**
- **Decision:** Create `methodregistryservice/` with unified interface
- **Rationale:** Cleaner separation, better isolation

---

## Next Steps

1. ✅ **Analysis Complete** - This document
2. **Phase 1** - Create `methodregistryservice/`
3. **Phase 2** - Create `orchestrationservice/`
4. **Phase 3** - Migrate imports & references
5. **Phase 4** - Clean up & document

---

## Future: Workflow Orchestration API (Post-Refactor)

**Status:** 📋 Proposed - After orchestration refactor complete

---

## Terminology: SDK vs API vs Package vs Library

**Understanding the distinctions for Python developers:**

### SDK (Software Development Kit)
**What:** Complete package with tools, libraries, docs, examples for building with a platform
**Install:** External via PyPI
```bash
pip install boto3  # AWS SDK
pip install stripe  # Stripe SDK
pip install openai  # OpenAI SDK
```
**Import:**
```python
import boto3  # From site-packages/
client = boto3.client('s3')
```
**Characteristics:**
- Installed in virtual environment (`venv/lib/python3.x/site-packages/`)
- Has its own version (e.g., `boto3==1.28.0`)
- Published to PyPI repository
- External dependency in `requirements.txt`
- Includes: client library + docs + CLI tools + examples

**Real-world SDK structure:**
```
site-packages/boto3/
├── __init__.py
├── session.py
├── resources/
├── docs/
└── examples/
```

---

### API (Application Programming Interface)
**What:** Contract for how to interact with code (internal or external)
**Install:** NOT installed - it's part of YOUR codebase
```python
# No pip install - it's in your src/ folder
from orchestrationservice import WorkflowBuilder  # From YOUR code
```
**Import:**
```python
from orchestrationservice.workflow_builder import WorkflowBuilder
# Imports from src/orchestrationservice/workflow_builder.py
```
**Characteristics:**
- Lives in your project's `src/` directory
- Same version as your application
- NOT in requirements.txt (it IS the application)
- Part of your git repository
- Changes when you edit code

**Your application structure:**
```
my-tiny-data-collider/
├── src/
│   ├── orchestrationservice/
│   │   ├── workflow_builder.py  # ← Internal API
│   │   └── workflow_engine.py
│   └── ...
└── requirements.txt  # Does NOT include orchestrationservice
```

**Types of APIs:**
1. **Internal API** (our case): For developers working ON this codebase
   ```python
   from orchestrationservice import WorkflowBuilder  # Internal
   ```

2. **HTTP API** (external): For clients calling our server
   ```bash
   curl -X POST http://api.example.com/v1/workflows
   ```

3. **Library API** (external): Public interface of installed package
   ```python
   import requests  # Library's public API
   requests.get(url)
   ```

---

### Package
**What:** Distributable unit of Python code (folder with `__init__.py`)
**Install:** Via pip (if published) or local install
```bash
# Published package
pip install requests

# Local package (development mode)
pip install -e .
```
**Import:**
```python
# Published package
import requests  # From site-packages/

# Your local package (if installed with pip install -e .)
from src.orchestrationservice import WorkflowBuilder
# OR just:
from orchestrationservice import WorkflowBuilder  # If using package layout
```
**Characteristics:**
- Can be internal (part of your app) OR external (published)
- Has `__init__.py` to mark it as a package
- May have `setup.py` or `pyproject.toml` for publishing

**Package types:**

1. **Application package** (our case):
   ```
   src/
   ├── __init__.py
   ├── orchestrationservice/
   │   ├── __init__.py  # Makes it a package
   │   └── workflow_builder.py
   └── casefileservice/
       ├── __init__.py
       └── service.py
   ```
   Not meant to be published - it IS the application

2. **Installed package** (from PyPI):
   ```
   venv/lib/python3.11/site-packages/
   ├── requests/
   │   ├── __init__.py
   │   └── api.py
   └── boto3/
       ├── __init__.py
       └── session.py
   ```
   Installed via pip, lives in site-packages

---

### Library
**What:** Reusable code collection (usually a published package)
**Install:** Via pip from PyPI
```bash
pip install requests  # HTTP library
pip install pydantic  # Data validation library
pip install sqlalchemy  # Database library
```
**Import:**
```python
import requests  # Library
from pydantic import BaseModel  # From library
```
**Characteristics:**
- Published to PyPI
- Installed in site-packages
- Version-managed (in requirements.txt)
- Designed for reuse across projects
- Examples: requests, pandas, numpy, pydantic

**Library vs SDK:**
- **Library:** Single-purpose tool (requests = HTTP only)
- **SDK:** Complete platform toolkit (boto3 = AWS everything)

---

### Real-World Python Developer Workflow

**Installing external dependencies:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install external packages (SDKs/libraries)
pip install boto3      # AWS SDK → venv/lib/python3.11/site-packages/boto3/
pip install pydantic   # Library → venv/lib/python3.11/site-packages/pydantic/
pip install requests   # Library → venv/lib/python3.11/site-packages/requests/

# Your application code
python src/main.py
```

**Import resolution:**
```python
# Python looks in this order:
# 1. Built-in modules (sys, os, json)
import sys

# 2. Current directory / PYTHONPATH
from src.orchestrationservice import WorkflowBuilder  # Your code

# 3. site-packages (installed packages)
import boto3  # From venv/lib/python3.11/site-packages/boto3/
from pydantic import BaseModel  # From site-packages/pydantic/
```

**Where code lives:**
```
my-tiny-data-collider/
├── src/                          # ← YOUR application code (internal API)
│   └── orchestrationservice/
│       └── workflow_builder.py
├── venv/                         # ← Virtual environment
│   └── lib/python3.11/
│       └── site-packages/        # ← Installed packages (external)
│           ├── boto3/            # SDK
│           ├── pydantic/         # Library
│           └── requests/         # Library
└── requirements.txt              # Lists external dependencies only
```

**requirements.txt:**
```txt
# External dependencies ONLY
boto3==1.28.0
pydantic==2.5.0
requests==2.31.0

# DOES NOT include your own code:
# orchestrationservice  ❌ NOT here
# casefileservice       ❌ NOT here
```

---

### Our Case: Workflow Orchestration API

**What we're building:**
```python
from orchestrationservice import WorkflowBuilder, WorkflowEngine
# ↑ Internal API - part of YOUR application in src/
```

**NOT an SDK because:**
- ❌ Not installed via pip
- ❌ Not in site-packages
- ❌ Not published to PyPI
- ❌ Not external dependency

**It IS an internal API because:**
- ✅ Lives in `src/orchestrationservice/`
- ✅ Part of application codebase
- ✅ Same version as application
- ✅ Changes with application development
- ✅ In same git repository

**Developer experience:**
```python
# When you write application code:
from orchestrationservice.workflow_builder import WorkflowBuilder
# ↑ Imports from src/orchestrationservice/workflow_builder.py (YOUR code)

from pydantic import BaseModel
# ↑ Imports from venv/lib/python3.11/site-packages/pydantic/ (EXTERNAL)

# Build workflow using YOUR internal API
workflow = WorkflowBuilder("setup").add_step(...).build()

# Execute using YOUR internal API
engine = WorkflowEngine()
result = await engine.execute(workflow)
```

**If we WERE to publish as SDK (future possibility):**
```bash
# Hypothetical future:
pip install my-tiny-data-collider-sdk

# Then in external projects:
from my_tiny_data_collider import WorkflowBuilder
client = ColliderClient(api_key="...")
```

But for now: **Internal orchestration API**, not external SDK.

---

### Quick Reference Table

| Term | Location | Install? | Import From | Example |
|------|----------|----------|-------------|---------|
| **SDK** | site-packages/ | `pip install boto3` | `import boto3` | AWS SDK, Stripe SDK |
| **Library** | site-packages/ | `pip install requests` | `import requests` | requests, pandas, numpy |
| **Internal API** | src/ | No (it's your code) | `from src.module import Class` | Our WorkflowBuilder |
| **HTTP API** | Remote server | No (call via HTTP) | N/A (use requests) | REST endpoints |
| **Package** | Either | Depends | Depends | Any folder with `__init__.py` |

---

### Vision: Developer-Facing Workflow Orchestration API

Enable developers to orchestrate tools in Python using a fluent, type-safe API:

```python
from my_tiny_data_collider import WorkflowBuilder, WorkflowEngine

# Define workflow with fluent API
workflow = (
    WorkflowBuilder("casefile_setup")
    .add_step(
        "create_casefile",
        params={
            "title": "Legal Case #12345",
            "description": "Client intake for Smith vs. Jones",
            "metadata": {"case_type": "civil", "priority": "high"}
        }
    )
    .add_step(
        "create_session",
        params={"casefile_id": "${steps.create_casefile.casefile_id}"},
        depends_on=["create_casefile"]
    )
    .add_step(
        "store_gmail_messages",
        params={
            "casefile_id": "${steps.create_casefile.casefile_id}",
            "query": "from:client@example.com subject:case"
        },
        depends_on=["create_session"]
    )
    .with_execution_mode("sequential")
    .with_error_handling("stop_on_failure")
    .build()
)

# Execute workflow
engine = WorkflowEngine()
result = await engine.execute(
    workflow,
    user_id="u_abc123",
    context={"case_id": "12345"}
)

# Access results
if result.success:
    casefile_id = result.steps["create_casefile"].output.casefile_id
    messages_count = result.steps["store_gmail_messages"].output.messages_stored
```

### Required Models

**1. Workflow Definition Models** (`pydantic_models/operations/workflow_ops.py`):

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

class StepDefinition(BaseModel):
    """Single step in workflow."""
    step_id: str
    tool_name: str  # References MANAGED_METHODS
    parameters: Dict[str, Any]
    depends_on: List[str] = Field(default_factory=list)
    timeout: Optional[int] = None  # seconds
    retry_policy: Optional[RetryPolicy] = None
    
class WorkflowDefinition(BaseModel):
    """Complete workflow specification."""
    workflow_id: str
    name: str
    description: Optional[str] = None
    steps: List[StepDefinition]
    execution_mode: Literal["sequential", "parallel", "dag"] = "sequential"
    error_handling: Literal["stop_on_failure", "continue_on_failure"] = "stop_on_failure"
    timeout: Optional[int] = None  # Overall workflow timeout
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StepResult(BaseModel):
    """Result of single step execution."""
    step_id: str
    status: Literal["pending", "running", "success", "failed", "skipped"]
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

class WorkflowResult(BaseModel):
    """Result of complete workflow execution."""
    workflow_id: str
    status: Literal["pending", "running", "success", "failed", "partial"]
    steps: Dict[str, StepResult]  # step_id -> result
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
```

**2. Workflow Request/Response** (for API exposure):

```python
class WorkflowRequestPayload(BaseModel):
    """Request to execute workflow."""
    workflow_definition: WorkflowDefinition
    context: Dict[str, Any] = Field(default_factory=dict)
    execution_directives: Optional[ExecutionDirective] = None

class WorkflowResponsePayload(BaseModel):
    """Response from workflow execution."""
    result: WorkflowResult
    execution_log: List[str] = Field(default_factory=list)
```

### WorkflowEngine Implementation

**Location:** `src/orchestrationservice/workflow_engine.py`

```python
class WorkflowEngine:
    """Execute multi-step workflows with dependency management."""
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        method_registry: MethodRegistry
    ):
        self.orchestrator = orchestrator
        self.registry = method_registry
    
    async def execute(
        self,
        workflow: WorkflowDefinition,
        user_id: str,
        context: Dict[str, Any] = None
    ) -> WorkflowResult:
        """Execute workflow with dependency resolution."""
        
        result = WorkflowResult(
            workflow_id=workflow.workflow_id,
            status="running",
            steps={},
            started_at=datetime.now(UTC)
        )
        
        try:
            if workflow.execution_mode == "sequential":
                await self._execute_sequential(workflow, result, user_id, context)
            elif workflow.execution_mode == "parallel":
                await self._execute_parallel(workflow, result, user_id, context)
            elif workflow.execution_mode == "dag":
                await self._execute_dag(workflow, result, user_id, context)
            
            result.status = "success"
        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            if workflow.error_handling == "stop_on_failure":
                raise
        finally:
            result.completed_at = datetime.now(UTC)
            result.duration_ms = (
                result.completed_at - result.started_at
            ).total_seconds() * 1000
        
        return result
    
    async def _execute_sequential(
        self,
        workflow: WorkflowDefinition,
        result: WorkflowResult,
        user_id: str,
        context: Dict[str, Any]
    ):
        """Execute steps in order."""
        step_outputs = {}
        
        for step in workflow.steps:
            step_result = await self._execute_step(
                step, user_id, context, step_outputs
            )
            result.steps[step.step_id] = step_result
            
            if step_result.status == "failed":
                if workflow.error_handling == "stop_on_failure":
                    raise WorkflowExecutionError(
                        f"Step {step.step_id} failed: {step_result.error}"
                    )
            else:
                step_outputs[step.step_id] = step_result.output
    
    async def _execute_dag(
        self,
        workflow: WorkflowDefinition,
        result: WorkflowResult,
        user_id: str,
        context: Dict[str, Any]
    ):
        """Execute steps respecting dependencies (topological sort)."""
        # Build dependency graph
        graph = self._build_dependency_graph(workflow.steps)
        
        # Topological sort
        execution_order = self._topological_sort(graph)
        
        step_outputs = {}
        for step_id in execution_order:
            step = next(s for s in workflow.steps if s.step_id == step_id)
            
            # Wait for dependencies
            await self._wait_for_dependencies(step, result)
            
            step_result = await self._execute_step(
                step, user_id, context, step_outputs
            )
            result.steps[step.step_id] = step_result
            
            if step_result.status != "failed":
                step_outputs[step.step_id] = step_result.output
    
    async def _execute_step(
        self,
        step: StepDefinition,
        user_id: str,
        context: Dict[str, Any],
        step_outputs: Dict[str, Any]
    ) -> StepResult:
        """Execute single workflow step."""
        step_result = StepResult(
            step_id=step.step_id,
            status="running",
            started_at=datetime.now(UTC)
        )
        
        try:
            # Resolve parameter references (e.g., ${steps.create_casefile.casefile_id})
            resolved_params = self._resolve_parameters(
                step.parameters, step_outputs, context
            )
            
            # Build request for method
            method_def = self.registry.get_method(step.tool_name)
            request = self._build_request(
                method_def, resolved_params, user_id
            )
            
            # Execute via orchestrator
            response = await self.orchestrator.dispatch(request)
            
            step_result.status = "success"
            step_result.output = response.payload.model_dump()
            
        except Exception as e:
            step_result.status = "failed"
            step_result.error = str(e)
        finally:
            step_result.completed_at = datetime.now(UTC)
            step_result.duration_ms = (
                step_result.completed_at - step_result.started_at
            ).total_seconds() * 1000
        
        return step_result
    
    def _resolve_parameters(
        self,
        params: Dict[str, Any],
        step_outputs: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve ${...} references in parameters."""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${"):
                # Parse reference: ${steps.step_id.field} or ${context.key}
                resolved[key] = self._resolve_reference(
                    value, step_outputs, context
                )
            else:
                resolved[key] = value
        return resolved
```

### WorkflowBuilder Helper

**Location:** `src/orchestrationservice/workflow_builder.py`

```python
class WorkflowBuilder:
    """Fluent API for building workflows."""
    
    def __init__(self, name: str):
        self._workflow = WorkflowDefinition(
            workflow_id=f"wf_{generate_id()}",
            name=name,
            steps=[]
        )
    
    def add_step(
        self,
        tool_name: str,
        params: Dict[str, Any],
        step_id: Optional[str] = None,
        depends_on: List[str] = None
    ) -> "WorkflowBuilder":
        """Add step to workflow."""
        step = StepDefinition(
            step_id=step_id or f"step_{len(self._workflow.steps) + 1}",
            tool_name=tool_name,
            parameters=params,
            depends_on=depends_on or []
        )
        self._workflow.steps.append(step)
        return self
    
    def with_execution_mode(
        self,
        mode: Literal["sequential", "parallel", "dag"]
    ) -> "WorkflowBuilder":
        """Set execution mode."""
        self._workflow.execution_mode = mode
        return self
    
    def with_error_handling(
        self,
        strategy: Literal["stop_on_failure", "continue_on_failure"]
    ) -> "WorkflowBuilder":
        """Set error handling strategy."""
        self._workflow.error_handling = strategy
        return self
    
    def with_timeout(self, seconds: int) -> "WorkflowBuilder":
        """Set overall workflow timeout."""
        self._workflow.timeout = seconds
        return self
    
    def build(self) -> WorkflowDefinition:
        """Build final workflow definition."""
        return self._workflow
```

### Integration with Orchestrator

The WorkflowEngine delegates individual step execution to the existing Orchestrator:

```python
# Workflow step execution flow:
WorkflowEngine.execute()
  → WorkflowEngine._execute_step()
    → Orchestrator.dispatch()  # Single operation execution
      → Hook execution
      → Policy application
      → Service method invocation
```

**Benefits:**
- Workflows use existing orchestration infrastructure
- Hooks and policies apply to workflow steps
- Consistent error handling and context management

### Use Cases

**1. Casefile Setup Workflow:**
```python
workflow = (
    WorkflowBuilder("casefile_setup")
    .add_step("create_casefile", {...})
    .add_step("create_session", {...}, depends_on=["create_casefile"])
    .add_step("store_gmail_messages", {...}, depends_on=["create_session"])
    .build()
)
```

**2. Parallel Data Collection:**
```python
workflow = (
    WorkflowBuilder("gather_evidence")
    .add_step("search_gmail", {...})
    .add_step("list_drive_files", {...})
    .add_step("batch_get_sheets", {...})
    .with_execution_mode("parallel")  # All run concurrently
    .build()
)
```

**3. Complex DAG:**
```python
workflow = (
    WorkflowBuilder("complex_analysis")
    .add_step("fetch_data", step_id="fetch", ...)
    .add_step("process_emails", depends_on=["fetch"], ...)
    .add_step("process_files", depends_on=["fetch"], ...)
    .add_step("merge_results", depends_on=["process_emails", "process_files"], ...)
    .with_execution_mode("dag")
    .build()
)
```

### Implementation Roadmap

**After orchestration refactor (Phase 1-4 complete):**

**Phase 5: Workflow Orchestration API (8-10 hours)**
1. Create workflow models (`workflow_ops.py`) - 2h
2. Implement WorkflowEngine - 3h
3. Implement WorkflowBuilder - 1h
4. Add parameter resolution (${...} syntax) - 2h
5. Add DAG execution support - 2h
6. Write tests and documentation - 2h

**Phase 6: API Exposure (2-3 hours)**
1. Add workflow endpoints to API - 1h
2. Add workflow status/cancel endpoints - 1h
3. Update OpenAPI documentation - 1h

**Total: 10-13 hours**

### Comparison with Industry Tools

| Feature | Our API | Prefect | Temporal | LangChain |
|---------|---------|---------|----------|-----------|
| Fluent API | ✅ | ✅ | ❌ | ✅ (LCEL) |
| Type Safety | ✅ Pydantic | ✅ | ✅ | ❌ |
| DAG Support | ✅ | ✅ | ✅ | ❌ |
| Hook Integration | ✅ | ✅ | ❌ | ✅ |
| Parameter References | ✅ `${...}` | ✅ | ✅ | ❌ |
| Casefile Context | ✅ Native | ❌ | ❌ | ❌ |

---

## References

- Current codebase: `src/coreservice/request_hub.py` (1005 lines)
- Session management: `src/pydantic_ai_integration/session_manager.py`
- Registry code: `src/pydantic_ai_integration/` (multiple files)
- Test suite: `tests/` (179 unit + 11 integration tests passing)
- Workflow inspiration: Prefect, Temporal, LangChain LCEL

---
