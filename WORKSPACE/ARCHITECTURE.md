# Casefile-Centric Routing Architecture

**Last Updated:** 2025-10-23 (Added PIKE-RAG service)

## Overview

The system implements a **casefile-as-router** pattern where each casefile defines an isolated workspace with permissions, data context, and user sessions.

---

## Three-Layer Security Model

### Layer 1: WHO (Authentication)
- **Component:** JWT Token (`authservice/token.py`)
- **Validates:** User identity
- **Contains:**
  - `user_id` - User identity
  - `scopes` - Accumulated casefile permissions (cache)
  - `exp` - Token expiration
- **Storage:** Client-side (browser/app)

### Layer 2: WHERE (Authorization & Routing)
- **Component:** CasefileSessionManager (`coreservice/casefile_session_manager.py`)
- **Validates:** 
  - Casefile exists
  - User has permission (owner/editor/viewer)
  - Session context in casefile
- **Routes to:** User's session within the casefile boundary
- **Returns:** Session context with casefile data

### Layer 3: WHAT (Execution)
- **Component:** OrchestrationManager (future) / PydanticAI Agent (current)
- **Receives:** Validated session context
- **Trusts:** SessionManager already validated access
- **Executes:** Tools/chat within casefile data context

---

## Request Flow

```
1. Client Request
   ↓
   POST /v1/chat
   Headers: Authorization: Bearer {JWT}
   Body: {casefile_id, message}

2. Auth Layer (WHO)
   ↓
   get_current_user() decodes JWT
   Returns: {user_id, casefile_scopes}

3. Router Layer (WHERE)
   ↓
   SessionManager.validate_and_get_session()
   - Check JWT scopes cache (fast path)
   - OR validate Firestore (slow path):
     * Casefile exists? → 404 if not
     * User has access? → 403 if not
     * Cache permission in scopes
   - Get/create user's session in casefile
   Returns: {session_id, casefile_id, permission, updated_scopes}

4. Execution Layer (WHAT)
   ↓
   Agent/Tool executes with:
   - Casefile context (gmail_data, drive_data, sheets_data)
   - User's session history
   - Permission level
   Returns: Result

5. Response
   ↓
   Includes updated JWT scopes for client to refresh token
```

---

## Casefile Structure

```
Firestore: /casefiles/{casefile_id}
├── id: "cf_251022_399c7a"
├── metadata:
│   ├── title: "Personal Email Archive"
│   ├── created_by: "sam@example.com"
│   └── created_at: "2025-10-22T10:00:00Z"
├── acl:
│   ├── owner_id: "sam@example.com"
│   └── permissions:
│       └── entries:
│           └── alice@example.com:
│               ├── role: "editor"
│               └── granted_by: "sam@example.com"
├── gmail_data: {messages[], threads[], labels[]}
├── drive_data: {files[]}
├── sheets_data: {sheets[]}
└── subcollections:
    ├── /chat_sessions/
    │   ├── chat_abc123 (sam's session)
    │   └── chat_def456 (alice's session)
    └── /tool_sessions/
        └── ts_xyz789 (sam's session)
```

---

## JWT Scope Accumulation

### Initial Login
```json
{
  "sub": "sam@example.com",
  "scopes": {},
  "exp": 1729800000
}
```

### After Accessing Casefile #1
```json
{
  "sub": "sam@example.com",
  "scopes": {
    "cf_251022_399c7a": "owner"
  },
  "exp": 1729800000
}
```

### After Accessing Casefile #2
```json
{
  "sub": "sam@example.com",
  "scopes": {
    "cf_251022_399c7a": "owner",
    "cf_work_12345": "editor"
  },
  "exp": 1729800000
}
```

### Client Refresh Flow
1. API response includes `metadata.casefile_scopes`
2. Client calls `POST /auth/refresh-scopes` with scopes
3. Receives new JWT with merged scopes
4. Future requests use cached permissions (fast path)

---

## Multi-Casefile Isolation

**Example: User accesses 3 different casefiles**

```python
# Request 1: Personal casefile
POST /v1/chat
{
  "casefile_id": "cf_personal_abc",
  "message": "Find my tax documents"
}
→ Routes to: Sam's chat_session_1 in cf_personal_abc
→ Context: Personal gmail_data only
→ Isolation: Cannot see work or project data

# Request 2: Work casefile
POST /v1/chat
{
  "casefile_id": "cf_work_def",
  "message": "Find Q3 reports"
}
→ Routes to: Sam's chat_session_2 in cf_work_def
→ Context: Work gmail_data only
→ Isolation: Cannot see personal or project data

# Request 3: Shared project (viewer permission)
POST /v1/tools/execute
{
  "casefile_id": "cf_project_ghi",
  "tool": "analyze_sheet"
}
→ Routes to: Sam's tool_session_3 in cf_project_ghi
→ Context: Project sheets_data only
→ Permission: "viewer" (read-only)
→ Isolation: Cannot see personal or work data
```

---

## Key Components

### 1. CasefileSessionManager
**File:** `src/coreservice/casefile_session_manager.py`

**Primary Method:**
```python
async def validate_and_get_session(
    user_id: str,
    casefile_id: str,
    session_type: Literal["tool", "chat"],
    cached_scopes: dict = None
) -> dict:
    """
    Validates access and returns session context.
    
    This is the WHERE layer - routing validation.
    """
```

**Responsibilities:**
- Permission validation (casefile ACL check)
- Session lifecycle (get/create/touch)
- Scope caching (JWT optimization)
- Error handling (404/403)

### 2. Chat Router
**File:** `src/pydantic_api/routers/chat_simple.py`

**Endpoint:** `POST /v1/chat`

**Responsibilities:**
- HTTP interface only
- Extract request parameters
- Call SessionManager for validation
- Execute agent with context
- Return response with updated scopes

### 3. Auth Service
**File:** `src/authservice/token.py`

**Key Methods:**
- `create_token()` - Create JWT with scopes
- `decode_token()` - Validate and extract JWT
- `get_current_user()` - FastAPI dependency

**Endpoint:** `POST /auth/refresh-scopes`

**Responsibilities:**
- Token creation/refresh
- Scope accumulation
- JWT lifecycle management

---

## Benefits

1. **User-Defined Routing** - Each casefile is a custom workspace
2. **Permission Boundaries** - ACL enforced at casefile level
3. **Data Isolation** - Gmail/Drive/Sheets scoped to casefile
4. **Session Isolation** - Tool/chat history per casefile per user
5. **Multi-Tenancy** - Each user's casefiles are isolated
6. **Collaboration** - Share casefile = grant router access
7. **Performance** - JWT caching reduces Firestore queries
8. **Scalability** - Stateless server, horizontal scaling

---

## Error Handling

| Error | HTTP Code | Cause | Solution |
|-------|-----------|-------|----------|
| Casefile not found | 404 | Invalid casefile_id | Check casefile exists |
| No access | 403 | User not in ACL | Request permission from owner |
| Invalid token | 401 | JWT expired/invalid | Refresh or re-login |
| Invalid casefile_id format | 400 | Pydantic validation | Use cf_* format |

---

## Future Enhancements

1. **OrchestrationManager** - Dedicated execution layer
2. **Redis Cache** - Server-side permission cache
3. **Webhook Integration** - Real-time permission updates
4. **Audit Trail** - Log all access attempts
5. **Rate Limiting** - Per-casefile quotas
6. **LRU Scope Eviction** - Keep JWT size bounded

---

## Implementation Status

✅ **Completed:**
- JWT authentication with scope accumulation
- CasefileSessionManager with validation
- Chat router with casefile context (legacy, being migrated)
- Tool router with casefile context (legacy, being migrated)
- Permission caching in JWT
- Token refresh endpoint
- Multi-casefile isolation
- **Unified SessionService with 5 endpoints (NEW)**
- **SessionRepository with Firestore subcollections (NEW)**
- **Integration with CasefileSessionManager for validation (NEW)**
- **Tool/Agent/Workflow execution in unified architecture (NEW)**

⚠️ **In Progress:**
- Migration of legacy routers to unified sessions
- Removal of ToolSessionService + CommunicationService (being replaced)

❌ **Pending:**
- Redis cache layer
- Audit trail
- Rate limiting
