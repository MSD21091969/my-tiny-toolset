# Pydantic AI Patterns vs Your Code

**Last Updated:** 2025-10-20  
**Purpose:** Compare pydantic-ai framework patterns with my-tiny-data-collider architecture

---

## Overview

This folder contains **side-by-side comparisons** of:
- **Pydantic AI patterns** (from official docs)
- **Your equivalent patterns** (my-tiny-data-collider implementation)
- **Why your approach differs** (design decisions)

**Read these to understand:**
- How standard pydantic-ai code looks
- How your code achieves the same goals differently
- When to use each pattern

---

## Examples Index

### 01_function_toolset_basic.py
**Pydantic AI:** `@toolset.tool` decorator with local functions  
**Your pattern:** `@register_service_method` with BaseRequest/BaseResponse  
**Key difference:** Your pattern adds audit trails, request tracking, structured responses

**When to read:** Understand basic tool registration differences

---

### 02_toolset_composition.py
**Pydantic AI:** CombinedToolset, filtered(), prefixed(), renamed()  
**Your pattern:** MANAGED_METHODS registry with classification taxonomy  
**Key difference:** Your pattern uses 6-field classification for filtering, not runtime composition

**When to read:** Understand how to combine/filter tools in each approach

---

### 03_external_toolset_rag.py
**Pydantic AI:** ExternalToolset with DeferredToolRequests/Results  
**Your pattern:** Registered service methods with local embeddings (Sentence Transformers)  
**Key difference:** Your pattern keeps RAG internal with privacy-preserving local embeddings

**When to read:** Implementing semantic search, understanding RAG architecture

---

## Pattern Comparison Table

| Feature | Pydantic AI | Your Code | Why Different |
|---------|-------------|-----------|---------------|
| **Tool Registration** | `@toolset.tool` wraps execution | `@register_service_method` registers metadata | Need audit trails, request tracking |
| **Request/Response** | Raw data types | `BaseRequest[T]` / `BaseResponse[T]` | Structured context (request_id, status) |
| **Validation** | Schema from function signature | Schema from Pydantic models | Reusable types (62% code reduction) |
| **Context** | `RunContext` (run_step, deps) | `MDSContext` (user_id, casefile_id, session_id) | Multi-user sessions, casefile-centric |
| **Discovery** | Runtime toolset composition | Static registry (MANAGED_METHODS) | Documentation generation, drift detection |
| **Filtering** | `filtered()`, `prefixed()` | Classification taxonomy | Fine-grained (domain/subdomain/capability) |
| **Error Handling** | Exceptions propagate | `status: RequestStatus` in response | Agents see structured errors |
| **Async** | All async | All async | ✅ Both use async |

---

## When to Use Pydantic AI Patterns

✅ **Use pydantic-ai patterns when:**
- Rapid prototyping (quick experiments)
- Simple tools (no audit requirements)
- External toolsets (MCP servers, LangChain)
- Dynamic loading (plugins, runtime composition)
- Agent-centric (tools only used by agents)

---

## When to Use Your Patterns

✅ **Use your patterns when:**
- Enterprise/production (audit trails required)
- Multi-user systems (casefile context, permissions)
- Compliance (medical/legal data tracking)
- Documentation (auto-generated from registry)
- Direct consumption (SDK, CLI, HTTP - not just agents)
- Privacy (local embeddings, no API calls)
- Cost control (no per-query API fees at scale)

---

## Your Architecture Advantages

**What you have that pydantic-ai doesn't:**

1. **Dual-session architecture**
   - Chat sessions (cs_xxx) for conversations
   - Tool sessions (ts_xxx) for execution audit
   - Lazy creation (reusable across calls)

2. **Request-Action-Response (RAR) pattern**
   - Every call produces `ToolEvent` (audit trail)
   - `client_request_id` → `request_id` tracking
   - Structured `status` field (not exceptions)

3. **Casefile-centric context**
   - Multi-user sessions
   - Document storage (Gmail, Drive, Sheets)
   - Permission-based access

4. **Classification taxonomy**
   - 6-field classification (domain/subdomain/capability/complexity/maturity/tier)
   - Fine-grained filtering
   - Auto-generated documentation

5. **Registry system**
   - Central `MANAGED_METHODS` dictionary
   - Drift detection (YAML vs actual code)
   - Tool catalog generation

---

## Learning Path

**Recommended reading order:**

1. **Start here:** `01_function_toolset_basic.py`
   - Basic decorator patterns
   - Request/Response vs raw data
   - Understand core differences

2. **Then:** `02_toolset_composition.py`
   - Tool filtering and composition
   - Registry-based approach
   - Classification taxonomy

3. **Finally:** `03_external_toolset_rag.py`
   - RAG implementation
   - Local embeddings (Sentence Transformers)
   - Privacy-preserving search

4. **Cross-reference:** `WORKSPACE/CONTEXTUAL_FRAMEWORK.md`
   - Complete contextual guide
   - SDK vs CLI vs HTTP patterns
   - Import resolution, environment variables

---

## External References

**Pydantic AI Documentation:**
- Toolsets: https://ai.pydantic.dev/toolsets/
- Function Tools: https://ai.pydantic.dev/tools/
- Deferred Tools: https://ai.pydantic.dev/deferred-tools/

**Issue Discussions:**
- RAG & Embeddings API: https://github.com/pydantic/pydantic-ai/issues/58
- Sentence Transformers integration discussion

**Your Documentation:**
- User Manual: `REFERENCE/SYSTEM/guides/20251016_user_manual.md`
- Model Docs: `REFERENCE/SYSTEM/model-docs/README.md`
- Validation Patterns: (in my-tiny-data-collider repo)

---

## Contributing

**When adding new examples:**
1. Show pydantic-ai pattern first (commented code from docs)
2. Show your equivalent pattern second (working code)
3. Explain differences in docstring
4. Add to examples index above
5. Update this README

**Format:**
```python
# ============================================================================
# PYDANTIC AI PATTERN: [Pattern name]
# ============================================================================
[Code from pydantic-ai docs]

# ============================================================================
# YOUR EQUIVALENT PATTERN: [Your pattern name]
# ============================================================================
[Your code with full context]

"""
DIFFERENCES:
- Point 1
- Point 2

WHY YOUR PATTERN:
- Reason 1
- Reason 2
"""
```
