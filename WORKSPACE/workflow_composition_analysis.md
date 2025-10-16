# Workflow Composition Analysis

**Date:** 2025-10-15  
**Context:** User wants to generate composite tools for data flows by searching/discovering models and methods  
**Related:** See [ROUNDTRIP_ANALYSIS.md](../../my-tiny-data-collider/ROUNDTRIP_ANALYSIS.md) for Pydantic enhancement phase tracking

---

## Application Purpose

**Understanding:** This application is a data engineering platform for AI/ML workflows with a much broader scope than initially apparent.

**Core Mission:**
- **Data Transfer & Transformation**: Collect data from external sources (Google Workspace, GCS, web APIs, etc.)
- **Metadata Management**: Store structured metadata in Firestore, BigQuery, embeddings for search
- **Dataset Preparation**: Build RAG corpora and fine-tuning datasets for AI models
- **Tool Engineering**: Generate tools through YAML composition by analyzing field mappings and data flows

**Tool Engineering Process:**
1. **Analyze fields**: Compare source output fields → target input fields
2. **Generate YAMLs**: Create tool definitions using different generator approaches
3. **Compose methods**: Chain multiple methods (or even tools) into workflows
4. **Trial & error**: Iterate on field mappings, test data flows
5. **Best practices needed**: Systematic approach to reduce trial-and-error

**Before Phase 2:** Foundation must support moving from simple methodtools (1:1 wrappers) to tool engineering (composed workflows with field mapping intelligence).

---

## User Workflow Example

**Goal:** "Move daily Gmail attachments to GDrive, store Gmail message metadata in casefile"

**Required capabilities:**
1. **Search/Discovery:** Find methods by description, capability, domain
2. **Calculation:** Determine parameter compatibility between methods
3. **Mapping:** Match output fields from one method to input fields of next
4. **Generation:** Create composite tool YAML from discovered methods
5. **Validation:** Verify workflow is executable (params flow, permissions align)

---

## Current State: What EXISTS

### Available Methods (from methods_inventory_v1.yaml)

**Gmail operations:**
- `store_gmail_messages` - Store Gmail messages in casefile
  - Request: StoreGmailMessagesRequest
  - Response: StoreGmailMessagesResponse
  - Complexity: composite
  - Permissions: ["casefiles:write", "workspace:gmail:read"]

**Google Drive operations:**
- `store_drive_files` - Store Google Drive files in casefile
  - Request: StoreDriveFilesRequest
  - Response: StoreDriveFilesResponse
  - Complexity: composite
  - Permissions: ["casefiles:write", "workspace:drive:read"]

**Casefile operations (13 methods):**
- create_casefile, get_casefile, update_casefile, delete_casefile
- list_casefiles, search_casefiles, archive_casefile, restore_casefile
- add_tags, remove_tags, update_metadata, attach_files, store_gmail_messages, store_drive_files, store_sheet_data

### Existing Infrastructure

**Tool generation:**
- ✅ `scripts/generate_method_tools.py` - Generates simple 1:1 tool wrappers
- ✅ Parameter extraction via Pydantic introspection
- ✅ Type validation and normalization
- ✅ 34 tool YAMLs generated

**Validation:**
- ✅ `scripts/validate_registries.py` - Coverage, consistency, drift detection
- ✅ `scripts/validate_parameter_mappings.py` - Type compatibility checking
- ✅ Runtime registration via `register_methods_from_yaml()`, `register_tools_from_yaml()`

**Analysis tools (my-tiny-toolset):**
- ✅ `version_tracker.py` - Full codebase analysis (352 models, 1006 functions)
- ✅ `code_analyzer.py` - Quick structure analysis, CSV exports
- ✅ `mapping_analyzer.py` - Relationship mapping, HTML dashboard
- ✅ `excel_exporter.py` - 5-sheet Excel reports

**Composite tool prototype:**
- ✅ `tests/fixtures/test_composite_tool.py` - Working composite pattern in code
- ✅ YAML schema defined (implementation.type=composite, steps array)
- ❌ No composite tool generator
- ❌ No workflow discovery/composition helper

---

## GAPS: What's MISSING

### 1. Method Discovery Tool
**Need:** Search methods by natural language query
```python
# Example API:
results = search_methods(
    query="gmail attachments",
    capability="read",
    domain="workspace"
)
# Returns: [method_name, description, parameters, dependencies]
```

**Status:** ❌ Not implemented
**Toolset opportunity:** Could be new tool in `my-tiny-toolset/TOOLSET/method_search.py`

### 2. Parameter Compatibility Calculator
**Need:** Check if method outputs can feed into other method inputs
```python
# Example API:
compatibility = check_parameter_flow(
    source_method="get_gmail_messages",
    target_method="store_drive_files"
)
# Returns: {compatible: True, mappings: {...}, warnings: [...]}
```

**Status:** ❌ Not implemented
**Current:** `parameter_mapping.py` only validates tool ↔ method, not method ↔ method

### 3. Workflow Composer
**Need:** Generate composite tool YAML from method sequence
```python
# Example API:
workflow = compose_workflow(
    name="gmail_to_drive_with_casefile",
    steps=[
        {"method": "get_gmail_messages", "params": {...}},
        {"method": "extract_attachments", "params": {...}},
        {"method": "upload_to_drive", "params": {...}},
        {"method": "store_gmail_messages", "params": {...}}
    ]
)
# Returns: Complete composite tool YAML
```

**Status:** ❌ Not implemented
**Pattern exists:** test_composite_tool.py shows the structure, but no generator

### 4. Field Mapper
**Need:** Map output fields from one method to input fields of another
```python
# Example API:
mapping = map_fields(
    source_response="GetGmailMessagesResponse",
    target_request="StoreGmailMessagesRequest"
)
# Returns: {
#   "messages[].id": "payload.message_ids",
#   "messages[].subject": "payload.metadata.subjects"
# }
```

**Status:** ❌ Not implemented
**Toolset opportunity:** Could leverage `code_analyzer.py` model field extraction

### 5. Interactive Workflow Builder
**Need:** CLI tool to interactively build workflows
```bash
python scripts/build_workflow.py

> What's your goal? "Move Gmail attachments to Drive and log in casefile"
> Searching methods... Found:
  1. store_gmail_messages (casefile)
  2. store_drive_files (casefile)
  3. get_gmail_messages (communication)
  
> Building workflow...
  Step 1: get_gmail_messages
  Step 2: extract_attachments (custom logic needed)
  Step 3: upload_to_drive
  Step 4: store_gmail_messages
  Step 5: store_drive_files
  
> Generate YAML? [Y/n] Y
> Created: config/workflows/gmail_to_drive_workflow.yaml
```

**Status:** ❌ Not implemented

---

## Implementation Plan

### Phase 0: Decorator Deployment ✅ **COMPLETE** ("Phase 10")

**Context:** Originally called "Phase 10" in code comments - deploy `@register_service_method` decorator to all 34 service methods. This is the foundation for reliable method discovery and workflow composition.

**Completion Status:**
- ✅ Decorator implemented in `src/pydantic_ai_integration/method_decorator.py`
- ✅ Registry infrastructure in `src/pydantic_ai_integration/method_registry.py`
- ✅ **Applied to all service methods** (completed in Phase 2)
- ✅ Auto-registration at module import via `src/__init__.py`

**Why Do This First:**
1. **Eliminates YAML maintenance** - Code changes auto-register methods
2. **Prevents drift** - Single source of truth (code, not YAML)
3. **Enables accurate discovery** - Workflow tools query fresh data
4. **Required for Phase 1** - Method search needs reliable registry

**Tasks:**

**0.1 Apply Decorators to Services (4 hours)**
```python
# Example: src/casefileservice/casefile_service.py

@register_service_method(
    name="create_casefile",
    description="Create new casefile with metadata",
    service_name="CasefileService",
    service_module="src.casefileservice.service",
    classification={
        "domain": "workspace",
        "subdomain": "casefile",
        "capability": "create",
        "complexity": "atomic",
        "maturity": "stable",
        "integration_tier": "internal"
    },
    required_permissions=["casefiles:write"],
    version="1.0.0"
)
async def create_casefile(self, request: CreateCasefileRequest) -> CreateCasefileResponse:
    # Implementation
```

**Services to Update:**
- `CasefileService` - 13 methods (2 hours)
- `ToolSessionService` - 9 methods (1 hour)
- `ChatSessionService` - 6 methods (45 min)
- `GmailService`, `DriveService`, `SheetsService` - 6 methods (45 min)

**0.2 Update Startup Registration (1 hour)**
```python
# src/main.py or initialization module

# OLD (YAML-based):
from src.pydantic_ai_integration.method_decorator import register_methods_from_yaml
register_methods_from_yaml("config/methods_inventory_v1.yaml")

# NEW (Decorator-based):
# Import services to trigger decorator registration
from src.casefileservice.service import CasefileService
from src.tool_sessionservice.service import ToolSessionService
# ... decorators auto-register at import

# OPTIONAL: Keep YAML for documentation/reference
# Mark as read-only, generate from registry
```

**0.3 Validation & Testing (2 hours)** ✅ Complete
- Run `scripts/validate_registries.py --strict`
- Verify all 34 methods registered
- Check parameter extraction works
- Run full test suite (169 tests: 126 pydantic + 43 registry)
- Fix any registration issues

**0.4 Update YAML to Read-Only Documentation (30 min)**
```yaml
# config/methods_inventory_v1.yaml (header update)

# ⚠️ THIS FILE IS NOW DOCUMENTATION ONLY
# Methods auto-register via @register_service_method decorator
# Do NOT edit manually - regenerate via export_methods_to_yaml()
# Last regenerated: 2025-10-15
```

**Deliverable:** ✅ All 34 methods auto-register via decorators, YAML is documentation-only

**Impact on Workflow Composition (Now Available):**
- ✅ Method search can query live registry
- ✅ Parameter flow analysis uses fresh data
- ✅ No YAML drift concerns
- ✅ Code changes immediately available to tools

**Status:** Complete as of Phase 2 (Oct 15, 2025). Ready for workflow composition tool development.

---

### Phase 1: Discovery Tools (4-6 hours)

**1.1 Method Search Script**
```python
# scripts/search_methods.py
"""
Search methods inventory by keyword, domain, capability.

Usage:
    python scripts/search_methods.py "gmail" --capability read
    python scripts/search_methods.py --domain workspace --json
"""
```

**Features:**
- Text search in name/description
- Filter by domain, subdomain, capability, complexity
- JSON/CSV output for piping to other tools
- Shows parameters, permissions, dependencies

**1.2 Model Field Searcher**
```python
# scripts/search_model_fields.py
"""
Search model fields across all Pydantic models.

Usage:
    python scripts/search_model_fields.py "email"
    python scripts/search_model_fields.py --type EmailAddress --json
"""
```

**Features:**
- Search field names/types
- Show which models contain field
- Export field inventory
- Integration with code_analyzer.py CSV output

### Phase 2: Compatibility Analysis (4-6 hours)

**2.1 Parameter Flow Validator**
```python
# scripts/validate_parameter_flow.py
"""
Check if outputs from one method can flow to inputs of another.

Usage:
    python scripts/validate_parameter_flow.py \
        --source GetGmailMessagesResponse \
        --target StoreGmailMessagesRequest
"""
```

**Features:**
- Compare response fields to request fields
- Identify missing fields (need manual mapping)
- Suggest field transformations
- Output compatibility score

**2.2 Workflow Validator**
```python
# scripts/validate_workflow.py
"""
Validate complete workflow before generation.

Usage:
    python scripts/validate_workflow.py workflow_spec.yaml
"""
```

**Features:**
- Check all methods exist
- Validate parameter flow between steps
- Check permission accumulation
- Detect circular dependencies
- Estimate execution time/cost

### Phase 3: Workflow Generation (6-8 hours)

**3.1 Composite Tool Generator**
```python
# scripts/generate_composite_tool.py
"""
Generate composite tool YAML from workflow specification.

Usage:
    python scripts/generate_composite_tool.py workflow_spec.yaml
"""
```

**Features:**
- Read workflow specification (simple format)
- Generate full composite tool YAML (test_composite_tool.py schema)
- Include error handling (on_success/on_failure branching)
- Add parameter validation
- Generate documentation

**3.2 Interactive Workflow Builder**
```python
# scripts/build_workflow.py
"""
Interactive CLI for building workflows from natural language.

Usage:
    python scripts/build_workflow.py --interactive
"""
```

**Features:**
- Natural language goal input
- Method discovery and suggestion
- Step-by-step workflow construction
- Parameter mapping assistance
- YAML generation
- Validation before save

### Phase 4: Toolset Integration (2-4 hours)

**4.1 Add to my-tiny-toolset**

Move mature tools to toolset:
```
my-tiny-toolset/TOOLSET/
  method_search.py          # Search methods/models
  workflow_validator.py     # Validate workflows
  composite_generator.py    # Generate composite YAMLs
```

**4.2 Update copilot-instructions.md**

Document new capabilities in both repos

---

## Quick Win: Immediate Implementation

**Most valuable first step: Method Search Tool**

Create `scripts/search_methods.py` to enable discovery:

```python
#!/usr/bin/env python3
"""
Search methods inventory by keyword, domain, capability.
"""
import argparse
import yaml
from pathlib import Path
from typing import List, Dict, Any

def load_methods() -> Dict:
    """Load methods from inventory."""
    with open("config/methods_inventory_v1.yaml") as f:
        return yaml.safe_load(f)

def search_methods(
    inventory: Dict,
    query: str = None,
    domain: str = None,
    capability: str = None,
    complexity: str = None
) -> List[Dict[str, Any]]:
    """Search methods with filters."""
    results = []
    
    for service in inventory.get('services', []):
        for method in service.get('methods', []):
            # Text search
            if query:
                query_lower = query.lower()
                if query_lower not in method['name'].lower() and \
                   query_lower not in method['description'].lower():
                    continue
            
            # Domain filter
            if domain:
                if method['classification']['domain'] != domain:
                    continue
            
            # Capability filter
            if capability:
                if method['classification']['capability'] != capability:
                    continue
            
            # Complexity filter
            if complexity:
                if method['classification']['complexity'] != complexity:
                    continue
            
            results.append({
                'name': method['name'],
                'description': method['description'],
                'domain': method['classification']['domain'],
                'capability': method['classification']['capability'],
                'complexity': method['classification']['complexity'],
                'request': method['models']['request'],
                'response': method['models']['response'],
                'permissions': method.get('business_rules', {}).get('required_permissions', []),
                'dependencies': method.get('dependencies', [])
            })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Search methods inventory')
    parser.add_argument('query', nargs='?', help='Search query (name or description)')
    parser.add_argument('--domain', help='Filter by domain')
    parser.add_argument('--capability', help='Filter by capability (read, update, create, etc)')
    parser.add_argument('--complexity', help='Filter by complexity (atomic, composite, pipeline)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    inventory = load_methods()
    results = search_methods(
        inventory,
        query=args.query,
        domain=args.domain,
        capability=args.capability,
        complexity=args.complexity
    )
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(f"\nFound {len(results)} methods:\n")
        for i, method in enumerate(results, 1):
            print(f"{i}. {method['name']}")
            print(f"   Description: {method['description']}")
            print(f"   Domain: {method['domain']} | Capability: {method['capability']}")
            print(f"   Request: {method['request']}")
            print(f"   Response: {method['response']}")
            if method['permissions']:
                print(f"   Permissions: {', '.join(method['permissions'])}")
            if method['dependencies']:
                print(f"   Dependencies: {', '.join(method['dependencies'])}")
            print()

if __name__ == '__main__':
    main()
```

**Usage example:**
```bash
# Your use case:
python scripts/search_methods.py "gmail" --domain workspace

# Output:
Found 1 methods:

1. store_gmail_messages
   Description: Store Gmail messages in casefile
   Domain: workspace | Capability: update
   Request: StoreGmailMessagesRequest
   Response: StoreGmailMessagesResponse
   Permissions: casefiles:write, workspace:gmail:read
   Dependencies: GmailClient
```

---

## Answer to Your Question

**Can you generate tools for data flows by searching models/methods?**

**Current state:**
- ❌ **Direct generation:** No - composite workflow generator doesn't exist yet
- ✅ **Building blocks exist:** Yes - all pieces are there (methods, models, validation, test pattern)
- ✅ **Simple tools work:** Yes - 34 atomic tools generated and validated
- ✅ **Method registry:** Yes - decorator-based registration deployed (Phase 2 complete)
- ✅ **Search foundation:** Yes - live registry available for discovery tools
- ❌ **Search tools:** No - need to build method/model search CLI
- ✅ **Parameter validation:** Yes - tool↔method validation working
- ❌ **Parameter flow:** No - method↔method compatibility not implemented

**To make your workflow work, you need:**

1. **Search tool** (search_methods.py) - 2 hours to build
2. **Parameter flow validator** - 4 hours to build
3. **Composite generator** - 6 hours to build
4. **Workflow spec format** - 2 hours to design

**Total effort: ~14-20 hours to full working system** (decorator deployment already complete)

**Interim solution (today):**
Manually compose in YAML using test_composite_tool.py schema:

```yaml
name: gmail_to_drive_workflow
description: "Move Gmail attachments to Drive and log in casefile"
category: automation
implementation:
  type: composite
  steps:
    - name: fetch_messages
      tool: get_gmail_messages_tool
      inputs:
        query: "has:attachment after:{{today}}"
      on_success: extract_attachments
      on_failure: log_error
    
    - name: extract_attachments
      tool: extract_attachments_tool  # Custom logic needed
      inputs:
        messages: "$context.fetch_messages.messages"
      on_success: upload_files
      on_failure: log_error
    
    - name: upload_files
      tool: store_drive_files_tool
      inputs:
        casefile_id: "$context.casefile_id"
        files: "$context.extract_attachments.files"
      on_success: store_metadata
      on_failure: log_error
    
    - name: store_metadata
      tool: store_gmail_messages_tool
      inputs:
        casefile_id: "$context.casefile_id"
        message_ids: "$context.fetch_messages.message_ids"
      on_success: complete
      on_failure: log_error
```

**Bottom line:** Infrastructure exists, automation tools need to be built. Toolset can help with discovery/analysis, but workflow composition requires new scripts in application repo.

---

## Integration with Pydantic Enhancement Work

**Current State:** See [ROUNDTRIP_ANALYSIS.md](../../my-tiny-data-collider/ROUNDTRIP_ANALYSIS.md) for complete phase tracking.

**Completed Foundation (52 hours):**
- ✅ **Phase 1 (32h):** Validation foundation - Custom types, validators, test suite
- ✅ **Phase 2 (20h):** Classification & mapping - Decorator registration, custom type application, import fixes

**Critical Enabler - Decorator Registration:**
The `@register_service_method` decorator (originally "Phase 10") is now **✅ DEPLOYED** across all service methods. This provides the live method registry that workflow composition tools require.

**Workflow Composition Readiness:**

```
Foundation Complete (Phase 1 + 2) ✅
    ↓
Decorator Registration ✅ DEPLOYED
    ↓
┌─────────────────────────┬──────────────────────────┐
│ PYDANTIC Next Phases    │ WORKFLOW COMPOSITION     │
│ (Documentation/polish)  │ (Tool engineering)       │
├─────────────────────────┼──────────────────────────┤
│ Phase 3: OpenAPI (19h)  │ Phase 1: Discovery (4-6h)│
│ Phase 4: Advanced (30h) │ Phase 2: Compatibility   │
│ Phase 5: Migration (12h)│ Phase 3: Generation      │
│                         │ Phase 4: Integration     │
└─────────────────────────┴──────────────────────────┘
```

**Why Workflow Composition Can Start Now:**
- ✅ Method registry is live and accurate (decorator-based)
- ✅ 34 methods registered with full metadata
- ✅ Parameter extraction from Pydantic models working
- ✅ Type validation infrastructure in place
- ✅ Test suite validates registry consistency

**Dependencies Met:**
- Method discovery tools can query live registry
- Parameter flow analysis can introspect request/response models
- Composite tool generator has validated patterns to follow
- No YAML drift concerns (single source of truth in code)

**Recommended Approach:**
Start with **Workflow Phase 1 (Discovery Tools)** in parallel with data-collider **Phase 3 (OpenAPI Enhancement)**. Discovery tools operate on existing registry and don't require additional model enhancements.

---

**Last updated:** 2025-10-15
