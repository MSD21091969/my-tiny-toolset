# User Manual: Building AI Systems with Data-First Architecture

**Date:** 2025-10-17  
**Context:** Post-test suite validation and cleanup  
**Author:** Sessions with MSD21091969

---

## Executive Summary

This manual documents the strategic decision to build custom session management, context orchestration, and audit trails instead of relying on agent framework context systems (e.g., Google ADK). **Key insight:** When data modeling, object orientation, and validation are foundational requirements, building your own context management yields superior results for RAG optimization, compliance, and maintainability.

---

## 1. The Two-Repository Architecture

### my-tiny-data-collider (Application)
**What it is:** FastAPI data integration platform with structured persistence, validation, and tool execution orchestration.

**Core capabilities:**
- 28 registered service methods across 6 services (casefile, communication, core, Gmail, Drive, Sheets)
- 37 Pydantic models with custom validation framework (30 custom types, 12 reusable validators)
- Dual-session architecture: Chat sessions (cs_xxx) for agents, Tool sessions (ts_xxx) for execution
- Casefile-centric audit trails with ToolEvent objects
- Firestore + Redis persistence with content splitting
- RAR (Request-Action-Response) pattern for all tool calls

**Strategic design:** Tool infrastructure exists independently of agent frameworks. Agents are just the UI layer that forwards tool_calls to the backend.

### my-tiny-toolset (Meta-Tools + Knowledge Base)
**What it is:** 17 analysis tools + curated knowledge repository for code inspection and architectural guidance.

**Core capabilities:**
- Code analysis: version_tracker, code_analyzer, mapping_analyzer, excel_exporter
- Workflow composition: method_search, parameter_flow_validator, composite_tool_generator
- Documentation generation: json_schema_examples, model_docs_generator, field_usage_analyzer
- Knowledge base: REFERENCE/ (patterns, architecture, guides), WORKSPACE/ (research notes)

**Usage pattern:** Application repos reference toolset via `$env:MY_TOOLSET` environment variable. Tools run FROM application directories, analyze structure, generate reports to `.tool-outputs/`.

---

## 2. Session Architecture: Dual-Context Design

### Why Two Session Types?

**Chat Sessions (CommunicationService):**
- **Purpose:** Conversation continuity for agents
- **ID pattern:** `cs_xxx`
- **Contains:** Messages, turn history, agent state
- **Lifecycle:** Created when agent conversation starts, closed when conversation ends
- **Persistence:** Firestore `chat_sessions` collection

**Tool Sessions (ToolSessionService):**
- **Purpose:** Tool execution audit trail with casefile linkage
- **ID pattern:** `ts_xxx`
- **Contains:** ToolEvents (request → action → response), chain_id, reasoning, metadata
- **Lifecycle:** Lazy creation—only created when tools are actually executed
- **Persistence:** Firestore `tool_sessions` collection + Redis cache

**How they link:** Through `user_id` and `casefile_id` context, NOT direct references. Tool session's `session_request_id` appears in chat session response metadata for tracking.

### Lazy Creation Pattern

**Problem:** Creating tool sessions upfront wastes resources if agent never executes tools.

**Solution:** SessionManager with automatic session finding/creation:

```python
# SessionManager.ensure_session_context()
# 1. Try to find existing session by user_id + casefile_id
existing = await self._find_existing_session(user_id, casefile_id)
if existing:
    return (MDSContext with existing session, was_created=False)

# 2. Create new session only if none found
new_session = await ToolSessionService.create_session(...)
return (MDSContext with new session, was_created=True)
```

**Benefit:** Sessions are reused across multiple tool calls within same user/casefile context. Audit trail continuity without manual session management.

---

## 3. RAR Pattern: Request-Action-Response

**Universal execution flow** for both user direct calls and agent-forwarded calls:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ToolRequest (from user OR from agent's tool_calls)       │
│    - tool_name: str                                          │
│    - payload: Dict[str, Any]  ← Parameters extracted here   │
│    - context: MDSContext (user_id, casefile_id, session_id) │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Action (ToolSessionService.process_tool_request)         │
│    - Lookup tool in MANAGED_TOOLS registry                  │
│    - Execute: result = await tool.function(**payload)       │
│    - Record ToolEvent with chain_id, reasoning, metadata    │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ToolResponse (structured, validated)                     │
│    - success: bool                                           │
│    - result: Any (validated Pydantic model)                 │
│    - error: Optional[str]                                    │
│    - metadata: execution_time, session_request_id           │
└─────────────────────────────────────────────────────────────┘
```

**Key insight:** Agent doesn't make decisions about tool execution. It only provides `tool_calls` array from LLM response. Backend executes, validates, records audit trail, returns structured response.

---

## 4. Why Not Use Agent Framework Context?

### The ADK Experiment

**What was tested:**
- Google ADK's InvocationContext, CallbackContext, ToolContext
- Session management via ADK's context system
- Integration with existing Firestore persistence

**What was discovered:**

| Your Architecture | Google ADK |
|-------------------|------------|
| **Context:** MDSContext with typed fields (user_id, casefile_id, session_id, metadata) | **Context:** state: Dict[str, Any] (flat untyped dictionary) |
| **Audit:** ToolEvent objects (chain_id, request, response, reasoning, metadata) | **Audit:** Events with nested GenAI SDK types (Event→Content→Parts→Part.text) |
| **Validation:** Pydantic models throughout | **Validation:** Manual type checking or none |
| **Persistence:** Content split by your persistence service (structured) | **Persistence:** State dict in ADK's session store |
| **RAG:** Query by casefile, user, tool name, date range (optimized) | **RAG:** Query flat state dict (not optimized) |
| **Compliance:** Casefile-centric audit trail with full lineage | **Compliance:** Event history without casefile linkage |

### The 50-Cent Return Problem

**Investment:**
- Built full Firestore integration with structured sessions
- Chat sessions + Tool sessions linked via casefiles
- ToolEvent audit trails with proper object models
- Content persistence with validation
- Clean separation: data → models → validation → persistence

**ADK Return:**
- Flat state dictionary (loses your validation)
- Nested extraction patterns (Event→Content→Parts→Part)
- Session management you already had
- Need to bridge between their unstructured state and your structured audit trail

**Conclusion:** When you value **data modeling, object orientation, and validation as foundation for AI**, you should build context management yourself. ADK's context is for simple state passing, not compliance audit trails or RAG-optimized structured events.

---

## 5. Tool Infrastructure: Agent-Agnostic Design

### Current State

**Tool Registry:** 28 methods registered via `@register_service_method` decorator
- Auto-registration at import (no manual YAML edits)
- Classification extracted from decorator parameters
- Input/output models extracted from function signature

**Tool YAMLs:** 34 YAML files in `config/methodtools_v1/` (generated from methods_inventory_v1.yaml)
- RAR pattern: Request-Action-Response structure
- Parameters extracted from `payload` field
- Type normalization (list[str] → array, generic type detection)

**Agent Runtime:** Stub only (`src/pydantic_ai_integration/tools/agents/base.py`)
- AgentRuntime class exists with minimal implementation
- No active agent imports in CommunicationService (commented out)
- `tool_calls` field in ChatMessagePayload prepared for future integration

### Strategic Advantage

**Tool-first, agent-agnostic architecture means:**
1. Tool infrastructure validated before adding agent complexity
2. Registry system works independently of agent framework choice
3. Audit trails optimized for your requirements (compliance, RAG)
4. When agent is added, it's just a forwarding layer (provides tool_calls, backend executes)

**Contrast with agent-first approach:**
- Would have discovered context mismatch AFTER building tools around framework
- Would need to retrofit casefile audit trails into framework's state model
- Would lose validation and structured persistence advantages

---

## 6. Casefile-Centric Audit Trail

### Why Casefiles Are Central

**Casefile concept:** Container for related work (documents, communications, tool executions)

**Benefits:**
- **Compliance:** Every tool execution can link to casefile for audit trail
- **Context:** Tools executed within same casefile share context (user, purpose, lineage)
- **RAG optimization:** Query by casefile returns all related tool executions, reasoning, metadata
- **Multi-session orchestration:** Multiple chat/tool sessions can contribute to same casefile

### ToolEvent Structure

```python
class ToolEvent(BaseModel):
    event_id: str
    tool_name: str
    chain_id: str              # Links related tool calls
    request: ToolRequest       # Original request with context
    response: ToolResponse     # Structured validated response
    reasoning: Optional[str]   # Why this tool was called (from agent)
    metadata: Dict[str, Any]   # execution_time, session_request_id, etc.
    created_at: IsoTimestamp
```

**RAG queries enabled:**
- "Show all Gmail operations for casefile_123"
- "Find tool failures in last 30 days for user_456"
- "Get reasoning chain for sheet_export tools in session_ts_789"

**Contrast with flat state dict:** Cannot structure queries by domain concepts (casefile, tool category, user). Must scan entire state history.

---

## 7. Validation Framework

### Custom Types (30 types)

**Location:** `src/pydantic_models/base/custom_types.py`

**Categories:**
- **IDs:** CasefileId, UserId, SessionId, GmailMessageId, DriveFileId, SheetId, EventId, ResourceId, ToolRequestId, ChainId (10 types)
- **Strings:** ShortString, MediumString, LongString, Description, NonEmptyString, TrimmedString, ResourceName (7 types)
- **Numbers:** PositiveInt, NonNegativeInt, PositiveFloat, NonNegativeFloat, PortNumber (5 types)
- **Email/URL:** EmailString, UrlString, HttpsUrl (3 types)
- **Timestamps:** IsoTimestamp, UtcDatetime, DateString, TimeString, UnixTimestamp (5 types)

**Usage pattern:**
```python
from src.pydantic_models.base.custom_types import CasefileId, ShortString, IsoTimestamp

class MyModel(BaseModel):
    id: CasefileId              # UUID validation + lowercase
    title: ShortString          # 1-200 characters
    created_at: IsoTimestamp    # ISO 8601 format
```

### Reusable Validators (12 functions)

**Location:** `src/pydantic_models/base/validators.py`

**Functions:**
- `validate_timestamp_order` - Ensure created_at < updated_at
- `validate_at_least_one` - At least one field required
- `validate_mutually_exclusive` - Only one field allowed
- `validate_conditional_required` - If field A set, field B required
- `validate_list_not_empty` - List must have items
- `validate_list_unique` - No duplicates in list
- `validate_range` - Value within min/max
- `validate_string_length` - String length bounds
- `validate_depends_on` - Field B depends on field A
- `validate_timestamp_in_range` - Timestamp within time window
- `validate_email_domain` - Email from allowed domains
- `validate_url_domain` - URL from allowed domains

**Full guide:** `docs/VALIDATION_PATTERNS.md` (Phase 1 reference)

---

## 8. Testing & Validation

### Registry Validation
```powershell
# Full validation (methods + parameter mappings)
python scripts/validate_registries.py --strict --verbose

# Parameter mapping only
python scripts/validate_parameter_mappings.py --verbose
```

**Current status:**
- 28 methods / 28 tools registered (drift detection disabled)
- All parameter mappings validated
- Generic type detection working (list[str] → array)

### Test Suites

**Current Status (2025-10-17):**
- ✅ **Unit Tests:** 179 passed, 0 warnings, 0 failures (2.76s)
- ⚠️ **Integration Tests:** 11 passed, 18 skipped, 5 failed (tool registry issues - expected)

```powershell
# All unit tests (179 total)
pytest tests/unit/ -v

# All integration tests (34 total)
pytest tests/integration/ -v

# By category
pytest tests/unit/pydantic_models/ -v      # Model validation tests
pytest tests/unit/registry/ -v             # Registry loader/validator tests
pytest tests/unit/coreservice/ -v          # Core service tests
pytest tests/unit/casefileservice/ -v      # Repository tests

# With coverage
pytest --cov=src --cov-report=html

# Quiet mode (summary only)
pytest tests/unit/ -q
```

### VS Code Tasks

**Available tasks** (`.vscode/tasks.json`):
- `Validate Registries` - Full registry + parameter validation
- `Run Tests` - Complete test suite
- `Quick Analysis` - Run code_analyzer.py on codebase
- `Full Analysis` - Run version_tracker.py + mapping_analyzer.py
- `Pre-commit Checks` - Sequential validation + tests

**Usage:** VS Code Task Runner or `run_task` tool

---

## 9. Toolset Integration

### Environment Setup
```powershell
$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"
```

### Code Analysis Tools (4 tools)

| Tool | Purpose | Command |
|------|---------|---------|
| `code_analyzer.py` | Quick structure analysis | `python $env:MY_TOOLSET\analysis-tools\code_analyzer.py . --json --csv` |
| `version_tracker.py` | Full analysis + Git history | `python $env:MY_TOOLSET\analysis-tools\version_tracker.py . --version 1.0.0 --json --yaml` |
| `mapping_analyzer.py` | Relationship mapping | `python $env:MY_TOOLSET\analysis-tools\mapping_analyzer.py . --html` |
| `excel_exporter.py` | Report generation | `python $env:MY_TOOLSET\analysis-tools\excel_exporter.py . --output report.xlsx` |

### Workflow Composition Tools (7 tools)

**Requires:** `$env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"`

| Tool | Purpose |
|------|---------|
| `method_search.py` | Find methods by domain/capability |
| `model_field_search.py` | Map response→request fields |
| `parameter_flow_validator.py` | Detect missing/incompatible fields |
| `workflow_validator.py` | Comprehensive validation |
| `composite_tool_generator.py` | Generate YAML workflows |
| `workflow_builder.py` | Interactive workflow builder |
| `data_flow_analyzer.py` | Data lineage tracking |

### Documentation Tools (6 tools)

| Tool | Purpose |
|------|---------|
| `json_schema_examples.py` | OpenAPI enhancement |
| `deprecated_fields.py` | Deprecation tracking |
| `response_variations.py` | API variant design |
| `schema_validator.py` | Schema validation |
| `model_docs_generator.py` | Auto-generate model docs |
| `field_usage_analyzer.py` | Find unused fields |

**Output location:** `.tool-outputs/` in application workspace (gitignored)

---

## 10. Knowledge Base Structure

### REFERENCE/ - Consolidated Knowledge

**Structure:**
- `SUBJECTS/` - Domain expertise (data-engineering, mlops, api-design, tool-engineering)
  - `shared-patterns/` - Reusable code patterns (Pydantic types, validators)
- `SYSTEM/` - Complete system architecture
  - `architecture/` - Service overviews, system architecture
  - `guides/` - Request flow, token schemas
  - `registry/` - Registry consolidation analysis
  - `specifications/` - MVP specs, toolset coverage
  - `model-docs/` - Auto-generated Pydantic model documentation (37 models)

**Knowledge scope:**
- RAG optimization patterns and agent tool combinations
- Model field mappings and parameter documentation
- Audit trail integration with casefile toolsets
- Best practices, engineering patterns (MLOps, schema evolution)
- **Agent interaction:** RAG provides responses + parameters (no reasoning/ReAct needed)

### WORKSPACE/ - Research Sandbox

**Contents:**
- `FIELDNOTES.md` - Research findings, domain references, workflow commands
- Daily research notes, experiments, drafts

**Workflow:** Explore → Note → Experiment → Draft → Publish to REFERENCE/

---

## 11. Lessons Learned: Data-First AI Architecture

### Strategic Insights

**1. Build tool infrastructure before choosing agent framework**
- Validate registry system, audit trails, persistence independently
- Agent becomes just a forwarding layer (provides tool_calls, backend executes)
- Avoid retrofitting structured audit trails into framework's state model

**2. Control your response structure**
- Agent framework responses (Event→Content→Parts→Part) require deep API knowledge to extract
- Custom ToolResponse structure enables clean debugging and direct field access
- Structured responses optimize RAG queries (query by casefile, tool, user, date)

**3. When data modeling matters, build context management yourself**
- Pydantic validation throughout ensures data integrity
- Structured audit trails (ToolEvent objects) beat flat state dictionaries for RAG
- Casefile-centric design enables compliance and multi-session orchestration

**4. Session context is not magic—it's just state management**
- MDSContext (user_id, casefile_id, session_id, metadata) is 4 fields
- SessionManager (find existing or create new) is 100 lines
- Worth building yourself when you need casefile linkage and validated audit trails

### Cost-Benefit Analysis

**Framework Context (ADK):**
- ✅ Faster initial setup (provided by framework)
- ✅ Standard patterns for simple use cases
- ❌ Flat state dict (no validation)
- ❌ Nested extraction patterns (complex)
- ❌ Not optimized for your requirements (compliance, RAG, casefiles)

**Custom Context (Your Architecture):**
- ⚠️ More upfront work (build SessionManager, MDSContext, persistence)
- ✅ Pydantic validation throughout
- ✅ Structured audit trails (ToolEvent objects)
- ✅ Casefile-centric design (compliance + RAG)
- ✅ Clean response structure (direct field access)
- ✅ Agent-agnostic (can swap frameworks without changing tools)

**Verdict:** When data modeling, validation, and audit trails are foundational requirements, custom context yields superior results. **You put in 1 dollar of upfront work, you get 2 dollars of long-term value.**

---

## 12. Future Roadmap

### Phase 1: Agent Integration (When Ready)
- Add PydanticAI agent runtime (replace stub)
- Uncomment agent imports in CommunicationService
- Agent provides `tool_calls` array, backend executes via ToolSessionService
- Test lazy session creation with real agent workflows

### Phase 2: RAG Optimization
- Query ToolEvents by casefile, user, tool name, date range
- Build vector embeddings from reasoning + metadata fields
- Test retrieval performance for compliance queries

### Phase 3: Workflow Composition
- Use toolset workflow tools to generate composite tool YAMLs
- Validate parameter flow across multi-step workflows
- Test data lineage tracking with data_flow_analyzer.py

### Phase 4: Performance Testing
- Load test with concurrent tool executions
- Measure session reuse efficiency (lazy creation)
- Optimize Redis caching strategy

---

## 13. Quick Reference

### Session Startup Checklist

**Every new session:**
1. Set toolset environment: `$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"`
2. Check Git branch: `git status` (current work on `main`)
3. Read system state: Open `ROUNDTRIP_ANALYSIS.md` for current progress
4. Validate registries: Run task "Validate Registries" OR `python scripts/validate_registries.py --strict`
5. Run test suite: Run task "Run Tests" OR `pytest tests/unit/ -q` (expect 179/179 passing)
6. Review tasks: Check `.vscode/tasks.json` for available tasks

### Key Documents

**Application (my-tiny-data-collider):**
- `ROUNDTRIP_ANALYSIS.md` - ⭐ PRIMARY REFERENCE - System state, action plan, progress tracking
- `docs/VALIDATION_PATTERNS.md` - Custom types & validators reference
- `README.md` - Project overview, quick start
- `.vscode/tasks.json` - Executable tasks

**Toolset (my-tiny-toolset):**
- `.github/copilot-instructions.md` - Toolset instructions for AI assistant
- `TOOLSET/README.md` - Master guide with all 17 tools
- `REFERENCE/README.md` - Knowledge base navigation
- `WORKSPACE/FIELDNOTES.md` - Research findings, domain references

### Command Patterns

```powershell
# Validation
python scripts/validate_registries.py --strict --verbose
python scripts/validate_parameter_mappings.py --verbose

# Testing
pytest tests/unit/ -v                      # Unit tests (179)
pytest tests/integration/ -v               # Integration tests (34)
pytest tests/unit/ -q                      # Quick summary (no verbose)
pytest --cov=src --cov-report=html         # With coverage

# Code Analysis (from application directory)
python $env:MY_TOOLSET\analysis-tools\code_analyzer.py . --json
python $env:MY_TOOLSET\analysis-tools\version_tracker.py . --version 1.0.0
python $env:MY_TOOLSET\analysis-tools\mapping_analyzer.py . --html

# Tool Generation
python scripts/generate_method_tools.py --verbose
python scripts/generate_method_tools.py --dry-run
```

---

## Conclusion

You built a **validated data platform** that happens to execute tools. The session context, MDSContext, casefile linking, ToolEvents—those are the real value. The agent is just the UI layer on top.

**Strategic advantage:** Tool infrastructure exists independently of agent frameworks. When data modeling, object orientation, and validation are foundational, building your own context management yields superior ROI for compliance, RAG optimization, and maintainability.

**You didn't just avoid vendor lock-in—you built a better foundation.**

---

## 14. Test Suite Architecture (2025-10-17 Update)

### Critical Discovery: Test Directory Structure

**Problem:** Pytest 8.x had import issues despite correct package installation and imports working from Python CLI.

**Root Cause:** Test directories with `__init__.py` files caused pytest to treat test directories as Python packages matching source code structure. This created namespace confusion where pytest tried importing `casefileservice.test_memory_repository` instead of importing from the installed `casefileservice` package.

**Solution:** **Test directories must NOT have `__init__.py` files** when using `package-dir = {"": "src"}` in `pyproject.toml`.

### Fixed Import Pattern

```python
# ✅ Correct (after fix)
from casefileservice.repository import CasefileRepository
from pydantic_models.base.types import RequestStatus

# ❌ Wrong (caused circular imports)
from src.casefileservice.repository import CasefileRepository
```

**Files Fixed:**
- Removed 3 test directory `__init__.py` files
- Fixed 81 "from src." import statements (77 in source + 4 in tests)
- Renamed `test_validators.py` → `test_registry_validators.py` (filename collision)
- Fixed 3 `datetime.utcnow()` deprecations → `datetime.now(UTC)`
- Fixed 8 test return value warnings (changed `return True` to `assert`)

### Test Organization

```
tests/
├── conftest.py              # Root pytest configuration (KEEP)
├── unit/                    # 179 tests, all passing ✅
│   ├── casefileservice/     # NO __init__.py
│   ├── coreservice/         # NO __init__.py
│   ├── pydantic_models/     # NO __init__.py
│   └── registry/            # NO __init__.py
├── integration/             # 34 tests (11 pass, 18 skip, 5 fail)
│   ├── conftest.py          # Integration fixtures (KEEP)
│   └── test_*.py            # Core test suites
└── fixtures/                # Test data

**Rule:** Tests are NOT packages—they import from the installed package.
```

### Pytest Configuration

**Root `conftest.py` (essential):**
```python
def pytest_load_initial_conftests(early_config, parser, args):
    """Ensure src/ is in sys.path before test collection."""
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
```

**Why this hook:** Runs early enough to fix imports for pytest 8.x's assertion rewriting phase.

### Lessons Learned

1. **Empty `__init__.py` files are not harmless** - They change how pytest interprets directory structure
2. **Pytest 8.x requires early sys.path setup** - Use `pytest_load_initial_conftests` hook
3. **Test filename uniqueness matters** - Two `test_validators.py` in different directories caused import conflicts
4. **Import consistency is critical** - Mix of "from src." and direct imports created circular dependencies

---

**Last Updated:** 2025-10-17
