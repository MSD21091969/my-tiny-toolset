# Versioning Strategy: Toolset v1

**Last updated:** 2025-10-22  
**Status:** Active  
**Scope:** Methods, Models, Tools, Infrastructure

---

## Overview

**Problem:** Application code, methods, models, and tool YAMLs evolve independently.  
**Solution:** Decouple infrastructure version from API contracts version.

```
Infrastructure Code (git tags)
    ├── v0.5.0 → FastAPI app, services, orchestration
    ├── v0.6.0 → Added workflow engine
    └── v1.0.0 → Production release
        ↓
    Independent from:
        ↓
API Contracts (versioned artifacts)
    ├── methods_inventory_v1.yaml (28 methods, 2025-10-22)
    ├── models_specification_v1.yaml (121 models)
    ├── classification_taxonomy_v1.yaml
    └── methodtools_v1/ (28 tool YAMLs)
```

**Key Insight:** Infrastructure can be v0.6.0 while API contracts are v1 (stable).

---

## Versioning Layers

### Layer 1: Infrastructure Code (Git Tags)
**What:** Python code, FastAPI app, services, persistence, orchestration  
**Versioning:** Semantic versioning via git tags (`v0.5.0`, `v1.0.0`)  
**Changes tracked:** Code structure, dependencies, architecture  
**Rate of change:** High (daily commits during development)

**Example:**
```
v0.5.0 - Initial services
v0.6.0 - Added workflow orchestration
v0.7.0 - Refactored method registry
v1.0.0 - Production release
```

---

### Layer 2: API Contracts (Versioned Artifacts)
**What:** Methods, models, tool YAMLs - the stable API surface  
**Versioning:** Snapshot-based with date stamps  
**Changes tracked:** Method signatures, model fields, tool definitions  
**Rate of change:** Low (monthly/quarterly releases)

**Files:**
```
config/
  ├── methods_inventory_v1.yaml      # Version 1.0.0, date: 2025-10-22
  ├── models_specification_v1.yaml   # Version 1.0.0, date: 2025-10-22
  ├── classification_taxonomy_v1.yaml # Version 1.0.0, date: 2025-10-22
  ├── methodtools_v1/                # 28 tools, version 1.0.0
  │   └── *.yaml
  └── workflows/                     # No version (composition layer)
      └── *.yaml
```

**Version bumping:**
- **v1 → v2:** Breaking changes (remove method, change model signature)
- **v1.1:** Additive changes (new method, new optional field)
- **v1.1.1:** Patch (typo fix, description update)

---

### Layer 3: Classification Metadata
**What:** Domain, subdomain, capability, complexity, maturity, integration_tier  
**Versioning:** Embedded in methods_inventory_v1.yaml  
**Purpose:** Stable taxonomy for method organization  
**Changes:** Rare (only when adding new domains/capabilities)

**Current taxonomy (v1):**
```yaml
domains:
  - workspace        # Casefile, ACL, Google Workspace sync
  - communication    # Chat sessions, Gmail
  - automation       # Tool execution, orchestration

subdomains:
  - casefile, casefile_acl, google_workspace
  - chat_session, chat_processing, gmail
  - tool_execution, tool_session

capabilities:
  - create, read, update, delete, search, process

complexity:
  - atomic, composite, pipeline

maturity:
  - alpha, beta, stable, deprecated

integration_tier:
  - internal, external, hybrid
```

---

## Version Lifecycle

### Phase 1: Development (Infrastructure v0.x + API Contracts v1-draft)
- **Infrastructure:** Rapid iteration (v0.5 → v0.6 → v0.7)
- **API Contracts:** Draft inventory, unstable models
- **Tools used:** 
  - `drift_detector.py` → Track inventory drift
  - `methods_inventory_validator.py` → Catch regressions
  - `model_docs_generator.py` → Document as you go

### Phase 2: Stabilization (Infrastructure v1.0-rc + API Contracts v1)
- **Infrastructure:** Feature freeze, bug fixes
- **API Contracts:** Lock v1 snapshot (methods_inventory_v1.yaml)
- **Baseline:** 2025-10-22 snapshot (28 methods, 121 models)
- **Tools used:**
  - `model_spec_extractor.py` → Generate models_specification_v1.yaml
  - `methodtools_validator.py` → Validate all 28 tool YAMLs

### Phase 3: Production (Infrastructure v1.0+ + API Contracts v1)
- **Infrastructure:** Patch releases (v1.0.1, v1.0.2)
- **API Contracts:** Frozen v1 (no changes without v2)
- **CI/CD:** `drift_detector.py --ci-mode` fails if contracts drift

### Phase 4: Evolution (Infrastructure v1.1+ + API Contracts v1.1 or v2)
- **Minor changes (v1 → v1.1):**
  - Add new methods
  - Add optional fields to models
  - New domains/subdomains in taxonomy
  - **Backward compatible** with v1
  
- **Major changes (v1 → v2):**
  - Remove methods
  - Change required fields
  - Break existing tool YAMLs
  - **Not backward compatible**

---

## Versioning Best Practices

### 1. **Separate Infrastructure from Contracts**

**❌ Don't do this:**
```
v0.7.0 infrastructure → v0.7.0 API contracts
v0.8.0 infrastructure → v0.8.0 API contracts
```
Every infrastructure change forces contract version bump.

**✅ Do this:**
```
v0.7.0 infrastructure → v1 API contracts (stable)
v0.8.0 infrastructure → v1 API contracts (still stable)
v1.0.0 infrastructure → v1 API contracts (ready for prod)
v1.1.0 infrastructure → v1.1 API contracts (additive changes)
```

---

### 2. **Date Stamp All Contract Snapshots**

```yaml
# methods_inventory_v1.yaml
version: "1.0.0"
date: "2025-10-22"
description: "Baseline: 28 methods, 17 internal + 6 external + 5 hybrid"
```

**Why:** Git history shows infrastructure changes, date stamp shows contract freeze point.

---

### 3. **Use Drift Detection in CI/CD**

```yaml
# .github/workflows/validate-contracts.yml
- name: Detect contract drift
  run: |
    python $TOOLSET/validation-tools/drift_detector.py \
      --inventory config/methods_inventory_v1.yaml \
      --ci-mode
  # Fails if methods added/removed/changed (forces v1.1 or v2)
```

---

### 4. **Version Tool YAMLs with Inventory**

```
methodtools_v1/  ← Matches methods_inventory_v1.yaml
methodtools_v2/  ← Matches methods_inventory_v2.yaml
```

**Don't:** Create `methodtools_v1.1/` for minor changes  
**Do:** Keep same folder, tools inherit version from inventory

---

### 5. **Document Breaking Changes**

```
CHANGELOG-v2.md
===============
## Breaking Changes
- Removed: `process_chat_request` (deprecated since v1.5)
- Changed: `CreateCasefileRequest.title` now required (was optional)
- Renamed: `integration_tier` → `tier_type`

## Migration Guide
1. Update tool YAMLs to reference new method names
2. Add `title` field to all casefile creation calls
3. Replace `integration_tier` with `tier_type` in classification
```

---

## Tool Recommendations

### For Development Phase
Use **all 21 tools** for comprehensive analysis:

**Code Analysis (4):**
- `code_analyzer.py` - Daily structure checks
- `version_tracker.py` - Release documentation
- `mapping_analyzer.py` - Architecture docs
- `excel_exporter.py` - Stakeholder reports

**Workflow Tools (7):**
- `method_search.py` - Discover methods by domain
- `model_field_search.py` - Map field compatibility
- `parameter_flow_validator.py` - Validate chains
- `workflow_validator.py` - Comprehensive validation
- `composite_tool_generator.py` - Generate workflows
- `workflow_builder.py` - Interactive builder
- `data_flow_analyzer.py` - Lineage tracking

**Documentation Tools (6):**
- `model_docs_generator.py` - **ESSENTIAL** - Auto-generate model docs
- `json_schema_examples.py` - OpenAPI examples
- `deprecated_fields.py` - Track deprecations
- `response_variations.py` - API variant design
- `schema_validator.py` - Validate schemas
- `field_usage_analyzer.py` - Find unused fields

**Validation Tools (4):**
- `methods_inventory_validator.py` - **ESSENTIAL** - Validate inventory
- `drift_detector.py` - **ESSENTIAL** - CI/CD drift checks
- `methodtools_validator.py` - **ESSENTIAL** - Validate tool YAMLs
- `model_spec_extractor.py` - Generate model specs

---

### For Production Phase
**Essential tools only (reduce maintenance overhead):**

**Must-have (5):**
1. `model_docs_generator.py` - Keep docs current
2. `methods_inventory_validator.py` - Pre-commit validation
3. `drift_detector.py` - CI/CD gate
4. `methodtools_validator.py` - Tool YAML validation
5. `code_analyzer.py` - Quick structure analysis

**Optional (use as needed):**
- `version_tracker.py` - Release documentation
- `workflow_validator.py` - Complex workflow validation
- `schema_validator.py` - Schema correctness testing

**Deprecate (move to archive):**
- `deprecated_fields.py` - Use model docs instead
- `response_variations.py` - Manual process better
- `field_usage_analyzer.py` - One-time analysis tool

---

## File Organization

### Recommended Structure

```
my-tiny-data-collider/                # Infrastructure code
├── src/                              # Git versioned (v0.x, v1.x)
├── config/                           # API contracts (separate versioning)
│   ├── methods_inventory_v1.yaml     # Version: 1.0.0, Date: 2025-10-22
│   ├── models_specification_v1.yaml  # Generated from code
│   ├── classification_taxonomy_v1.yaml
│   ├── methodtools_v1/               # 28 tool YAMLs
│   └── workflows/                    # No version (dynamic)
└── docs/
    └── CHANGELOG-v1.md               # Contract evolution log

my-tiny-toolset/                      # Analysis tools (separate repo)
├── TOOLSET/                          # 21 tools
│   ├── analysis-tools/
│   ├── workflow-tools/
│   ├── documentation-tools/
│   └── validation-tools/
└── REFERENCE/
    └── SYSTEM/
        ├── model-docs/               # Auto-generated (121 models)
        └── versioning/
            ├── v1_baseline_2025-10-22.md    # Snapshot documentation
            └── version_strategy.md          # This file
```

---

## Version Decision Matrix

| Change Type | Infrastructure | API Contracts | Tool Action |
|-------------|---------------|---------------|-------------|
| Add service class | v1.0 → v1.1 | v1 (no change) | None |
| Add method | v1.0 → v1.1 | v1 → v1.1 | Add to inventory + tool YAML |
| Add optional field | v1.0 → v1.1 | v1 → v1.1 | Update model spec |
| Change required field | v1.0 → v1.1 | v1 → v2 | ❌ Breaking change |
| Remove method | v1.0 → v1.1 | v1 → v2 | ❌ Breaking change |
| Refactor service | v1.0 → v1.1 | v1 (no change) | Update if service name changed |
| Bug fix | v1.0 → v1.0.1 | v1 (no change) | None |
| Performance optimization | v1.0 → v1.0.1 | v1 (no change) | None |

---

## Recommendations

### 1. **Lock v1 Baseline Today (2025-10-22)**

**Action items:**
- ✅ `methods_inventory_v1.yaml` exists (28 methods)
- ⏳ Generate `models_specification_v1.yaml` via `model_spec_extractor.py`
- ⏳ Create `classification_taxonomy_v1.yaml` (formalize current taxonomy)
- ✅ Validate all 28 methodtools_v1/ YAMLs
- ⏳ Document snapshot in `v1_baseline_2025-10-22.md`

**Freeze policy:**
- No changes to v1 contracts without v1.1 or v2 bump
- CI/CD fails if drift detected (`drift_detector.py --ci-mode`)
- All new methods go to v1.1 draft (not v1)

---

### 2. **Clean Up Toolset (Reduce from 21 → 12 Core)**

**Keep (production-critical):**
- 4 analysis-tools (all useful for different use cases)
- 3 workflow-tools: `method_search`, `workflow_validator`, `composite_tool_generator`
- 1 documentation-tool: `model_docs_generator` (auto-updates docs)
- 4 validation-tools (all essential for CI/CD)
- **Total: 12 tools**

**Archive (move to `/archive/` folder):**
- `model_field_search.py` - Replaced by workflow_validator
- `parameter_flow_validator.py` - Replaced by workflow_validator
- `workflow_builder.py` - Manual interactive tool (not CI/CD)
- `data_flow_analyzer.py` - One-time analysis
- `json_schema_examples.py` - Manual enhancement tool
- `deprecated_fields.py` - Use model docs grep instead
- `response_variations.py` - Manual design tool
- `schema_validator.py` - Redundant with Pydantic validation
- `field_usage_analyzer.py` - One-time analysis
- **Total: 9 tools archived**

---

### 3. **Documentation Location Strategy**

**Infrastructure Docs (application repo):**
- `docs/ARCHITECTURE.md` - System design
- `docs/API_REFERENCE.md` - Generated from OpenAPI
- `README.md` - Quick start

**Contract Docs (application repo config/):**
- `config/methods_inventory_v1.yaml` - Method catalog
- `config/models_specification_v1.yaml` - Model field specs
- `config/classification_taxonomy_v1.yaml` - Taxonomy definitions
- `config/README.md` - Config overview

**Generated Docs (toolset repo):**
- `REFERENCE/SYSTEM/model-docs/` - 121 model markdown files (auto-generated)
- `REFERENCE/SYSTEM/versioning/v1_baseline_2025-10-22.md` - Snapshot doc
- `REFERENCE/SYSTEM/versioning/version_strategy.md` - This file

**Why separate?**
- Application repo: Contracts + infrastructure
- Toolset repo: Analysis + generated docs + knowledge base

---

### 4. **Version Both Repos Independently**

**Application repo tags:**
```
v0.5.0 - Initial implementation
v0.6.0 - Added workflow engine
v1.0.0 - Production release with v1 API contracts
```

**Toolset repo tags:**
```
v1.0.0 - Initial toolset release (21 tools)
v1.1.0 - Added validation-tools (Phase 9)
v2.0.0 - Cleaned up to 12 core tools
```

**No coupling:** Application v1.0.0 can use toolset v1.1.0 or v2.0.0.

---

## Next Steps (Phase 9 Completion)

1. **Generate missing artifacts:**
   - Run `model_spec_extractor.py` → `models_specification_v1.yaml`
   - Create `classification_taxonomy_v1.yaml` manually
   - Test all 4 validation tools against current inventory

2. **Document v1 baseline:**
   - Create `v1_baseline_2025-10-22.md` with snapshot summary
   - List all 28 methods with classification
   - Document known limitations (external API validation gap)

3. **Clean up toolset:**
   - Move 9 tools to `/archive/`
   - Update `TOOLSET/README.md` with 12 core tools
   - Create `TOOLSET/archive/README.md` explaining archived tools

4. **Setup CI/CD validation:**
   - Add `drift_detector.py --ci-mode` to GitHub Actions
   - Add `methodtools_validator.py` to pre-commit hooks
   - Document validation workflow

5. **Tag releases:**
   - Application repo: No tag yet (wait for v1.0.0)
   - Toolset repo: Tag `v1.1.0` for Phase 9 completion

---

*Last updated: 2025-10-22 - Part of Phase 9 (Toolset v1 Baseline)*
