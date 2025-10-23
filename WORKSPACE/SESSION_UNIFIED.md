# Unified Session Architecture

**Last Updated:** 2025-10-23  
# Unified Session Architecture

**Status:** ✅ Complete (as of 2025-10-23)
**Latest:** PIKE-RAG service integrated with 4 registered methods (2025-10-23)

## Migration Complete

**Date:** October 23, 2025  
**Branch:** feature/orchestration-refactor

### Changes Applied:

1. ✅ **SessionService Integration**
   - Wired CasefileSessionManager for permission validation
   - Integrated with CasefileRepository for ACL checks
   - Added firestore_pool dependency injection
   - Proper get_or_create pattern with permission caching

2. ✅ **Router Updates**
   - Unified session router at `/v1/sessions/*` (priority)
   - Moved dependency injection to `dependencies.py`
   - Added `get_session_service()` dependency
   - Legacy tool_session router commented (deprecated)

3. ✅ **App Configuration**
   - Prioritized unified session router in app.py
   - Legacy routers marked for deprecation
   - All endpoints use SessionService

4. ✅ **Architecture Alignment**
   - Three-layer security (WHO → WHERE → WHAT) fully implemented
   - JWT scope accumulation integrated
   - Casefile-as-router pattern active
   - Per-user AND per-casefile isolation enforced

### What's New:

- **Unified Execution**: Single `/execute` endpoint for tools, agents, workflows
- **Permission Caching**: JWT scopes reduce Firestore queries
- **Auto-Managed Sessions**: Get-or-create pattern, no manual session management
- **Event Tracking**: All operations recorded as ExecutionEvents
- **Type Safety**: Full Pydantic validation throughout

---

Single unified session service replacing separate tool and chat sessions. All operations (tools, agents, workflows, chat) use identical architecture.

---

## Architecture

### Three-Layer Security (WHO → WHERE → WHAT)

1. **WHO**: JWT authentication → user_id, casefile_scopes
2. **WHERE**: CasefileRepository validates casefile exists + user permissions
3. **WHAT**: SessionService executes operations with MDSContext

### Storage Pattern

```
/casefiles/{casefile_id}/
  sessions/{session_id}          # UnifiedSession
    /events/{event_id}           # ExecutionEvent
```

### Session Types

- `interactive` - Manual tool testing (24h TTL)
- `workflow` - Multi-step execution (24h TTL)
- `chat` - Agent conversations (7 day TTL)

### Isolation

- Per-user AND per-casefile
- Query: `WHERE user_id == X AND casefile_id == Y AND active == True`
- Composite index: `(user_id, active, created_at DESC)`

---

## Implementation

### Files (2563 lines total)

- **Models**: `src/pydantic_models/operations/unified_session_ops.py` (588 lines)
- **Repository**: `src/sessionservice/repository.py` (476 lines)
- **Service**: `src/sessionservice/service.py` (1167 lines)
- **Router**: `src/pydantic_api/routers/session.py` (318 lines)
- **Tests**: `tests/unit/sessionservice/` (1331 lines across 4 files)

### Core Models

**UnifiedSession** (replaces ChatSession + ToolSession):
```python
{
  "session_id": "ts_251023_ecoma498_430345",
  "user_id": "sam@example.com",
  "casefile_id": "cf_251023_80a498",
  "session_type": "interactive|workflow|chat",
  "created_at": "2025-10-23T10:00:00Z",
  "updated_at": "2025-10-23T10:30:00Z",
  "active": true,
  "event_count": 5,
  "last_event_at": "2025-10-23T10:30:00Z"
}
```

**ExecutionEvent** (replaces ToolEvent + ChatMessage):
```python
{
  "event_id": "evt_abc",
  "session_id": "ts_xxx",
  "event_type": "tool_execution|agent_response|workflow_step|message",
  "operation_name": "gmail_search",
  "started_at": "2025-10-23T10:00:00Z",
  "completed_at": "2025-10-23T10:00:05Z",
  "duration_ms": 5000,
  "inputs": {"query": "urgent"},
  "outputs": {"messages": [...]},
  "success": true,
  "status": "success"
}
```

---

## Endpoints

Base: `/v1/sessions`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/create` | POST | Create session explicitly |
| `/execute` | POST | Execute operation (auto-creates session) |
| `/get` | POST | Retrieve session + events |
| `/list` | POST | List sessions in casefile |
| `/close` | POST | Close session + statistics |

---

## Execute Operation

Universal execution endpoint supporting tools, agents, workflows.

**Request**:
```json
{
  "request_id": "uuid",
  "user_id": "sam@example.com",
  "operation_type": "tool",
  "payload": {
    "casefile_id": "cf_xxx",
    "session_id": null,  // Optional - auto-creates
    "operation": {
      "operation_type": "tool",
      "tool_name": "gmail_search",
      "parameters": {"query": "invoice"}
    }
  }
}
```

**Response**:
```json
{
  "status": "completed",
  "payload": {
    "event_id": "evt_xxx",
    "session_id": "ts_xxx",
    "session_created": true,
    "outputs": {...},
    "user_permission": "owner"
  }
}
```

---

## Features

### Auto-Managed Sessions

- Get-or-create pattern: reuses active session or creates new
- Session touched on each operation (TTL extended)
- No explicit session management needed

### Permission Model

- Owner: Full access (creator of casefile)
- Viewer: Read-only access
- Validated via CasefileRepository on every request

### Event Tracking

- All operations recorded as ExecutionEvents
- Chronological audit trail per session
- Query by type, time range, status

---

## Integration

### Dependencies

```python
def get_session_service(request: Request) -> SessionService:
    firestore_pool = request.app.state.firestore_pool
    session_manager = CasefileSessionManager(firestore_pool=firestore_pool)
    repository = SessionRepository(connection_pool=firestore_pool)
    casefile_repository = CasefileRepository(firestore_pool=firestore_pool)
    return SessionService(
        repository=repository,
        session_manager=session_manager,
        casefile_repository=casefile_repository,
        firestore_pool=firestore_pool
    )
```

### Orchestrator

- Execute operations route through `Orchestrator.execute_operation()`
- Pre-hooks: metrics, auth check
- Post-hooks: audit trail, notifications

### WorkflowEngine

- `SessionService._execute_workflow()` method
- Workflow loading from registry
- DAG execution with step-by-step event recording

---

## Testing

### Test Suite

1331 lines, 39 test methods:
- Repository: 14 tests (CRUD, queries, events)
- Service: 15 tests (lifecycle, execution, validation)
- Router: 10 tests (endpoints, auth, errors)

**Coverage**: ~80% overall (target 85%+)

**Run**:
```powershell
python tests/run_tests.py
python tests/run_tests.py --coverage
pytest tests/unit/sessionservice/ -v
```

### Live Integration

All endpoints tested with running server (USE_MOCKS=true):

1. ✅ Create Casefile → `cf_251023_80a498`
2. ✅ Create Session → `ts_251023_ecoma498_430345`
3. ✅ Get Session → Retrieved with events
4. ✅ List Sessions → Found sessions
5. ✅ Close Session → Closed with statistics
6. ✅ Execute Operation → Structure validated

---

## Quick Start

### Start Server

```powershell
cd c:\Users\HP\my-tiny-data-collider
# VS Code task configured with USE_MOCKS=true
```

### Create Session Flow

```powershell
# Create casefile
$case = Invoke-WebRequest -Uri "http://127.0.0.1:8000/v1/casefiles?title=Test" -Method POST
$caseId = ($case.Content | ConvertFrom-Json).payload.casefile_id

# Create session
$body = @{
    request_id = [guid]::NewGuid()
    user_id = "sam@example.com"
    payload = @{
        casefile_id = $caseId
        session_type = "interactive"
        metadata = @{}
    }
} | ConvertTo-Json

$sess = Invoke-WebRequest -Uri "http://127.0.0.1:8000/v1/sessions/create" -Method POST -Body $body -ContentType "application/json"
$sessionId = ($sess.Content | ConvertFrom-Json).payload.session_id

# Get session
$getBody = @{
    request_id = [guid]::NewGuid()
    user_id = "sam@example.com"
    payload = @{
        session_id = $sessionId
        include_events = $true
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/v1/sessions/get" -Method POST -Body $getBody -ContentType "application/json"
```

---

## Deployment Notes

### Mock Firestore Enhancements

Added to `src/persistence/mock_firestore_pool.py`:
- `order_by()` support on MockQuery and MockCollection
- Sorting with ASCENDING/DESCENDING
- Proper chaining: `.where().order_by().limit()`

### Environment Variables

```powershell
$env:USE_MOCKS="true"         # Use mock Firestore
$env:SKIP_AUTO_INIT="true"    # Skip auto-initialization
```

### VS Code Task

```json
{
  "label": "Start FastAPI (Uvicorn)",
  "command": "uvicorn src.pydantic_api.app:app --host 127.0.0.1 --port 8000 --log-level info",
  "env": {
    "USE_MOCKS": "true",
    "SKIP_AUTO_INIT": "true"
  }
}
```

---

## Migration Path (NOT IMPLEMENTED)

Old → New mapping:
- `ToolSession` → `UnifiedSession(session_type="interactive")`
- `ChatSession` → `UnifiedSession(session_type="chat")`
- `ToolEvent` → `ExecutionEvent(event_type="tool_execution")`
- `ChatMessage` → `ExecutionEvent(event_type="agent_message")`

Migration script would:
- Copy `/tool_sessions/` → `/casefiles/{id}/sessions/`
- Copy `/chat_sessions/` → `/casefiles/{id}/sessions/`
- Transform session data to UnifiedSession schema
- Preserve event history

---

## Related Files

- **Architecture**: `ARCHITECTURE.md` (three-layer security)
- **Tests**: `tests/TEST_DOCUMENTATION.md` (test guide)
- **Models**: `src/pydantic_models/operations/unified_session_ops.py`
- **Service**: `src/sessionservice/service.py`
- **Repository**: `src/sessionservice/repository.py`
- **Router**: `src/pydantic_api/routers/session.py`
