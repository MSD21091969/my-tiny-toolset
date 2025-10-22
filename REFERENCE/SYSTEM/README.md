# SYSTEM - Complete System Documentation

**Last updated:** 2025-10-22

---

## Overview

Complete system architecture, specifications, guides, and auto-generated documentation for the Tiny Data Collider application.

---

## Directory Structure

```
SYSTEM/
├── README.md (this file)
├── architecture/        → System design, service overviews
├── guides/              → Request flow, token schemas
├── model-docs/          → Auto-generated Pydantic model docs (121 models)
├── registry/            → Registry consolidation analysis
├── specifications/      → MVP specs, toolset coverage
└── versioning/          → Version strategy, v1 baseline, taxonomy (NEW)
```

---

## Folder Contents

### architecture/
System architecture documentation and service designs.

**Key files:**
- Service architecture overviews
- Component interaction diagrams
- Integration patterns

**Maintenance:** Update when adding/refactoring services

---

### guides/
Operational guides for understanding system behavior.

**Key files:**
- Request flow documentation
- Token schema explanations
- Authentication/authorization guides

**Maintenance:** Update when request flow changes

---

### model-docs/ (Auto-Generated)
**121 Pydantic model markdown files** - automatically generated documentation.

**Generator:** `TOOLSET/documentation-tools/model_docs_generator.py`

**Contents:**
- Field specifications with types, defaults, constraints
- Custom validators and business logic
- Example payloads
- Cross-references to related models

**Regeneration:**
```powershell
python $env:MY_TOOLSET\documentation-tools\model_docs_generator.py . --output-dir REFERENCE/SYSTEM/model-docs
```

**Maintenance:** Regenerate after model changes, commit updates

---

### registry/
Analysis of method registry consolidation.

**Key files:**
- Registry architecture analysis
- Service method mapping
- Registration pattern documentation

**Maintenance:** Update when registry structure changes

---

### specifications/
High-level specifications and coverage reports.

**Key files:**
- MVP specifications
- Toolset coverage analysis
- Feature tracking

**Maintenance:** Update quarterly or at major milestones

---

### versioning/ (NEW - Phase 9)
**Version strategy, baseline snapshots, classification taxonomy.**

**Key files:**
1. **`version_strategy.md`** - Comprehensive versioning policy
   - Infrastructure code vs API contracts separation
   - Version lifecycle (development → production → evolution)
   - Tool recommendations (21 tools → 12 core)
   - File organization strategy
   - Version decision matrix

2. **`v1_baseline_2025-10-22.md`** - v1 baseline snapshot
   - 28 methods inventory
   - 121 models catalog
   - 28 tool YAMLs
   - Known limitations (external API validation, workflow versioning)
   - Validation status and next steps

3. **`classification_taxonomy_v1.yaml`** (copy from app repo)
   - Multi-dimensional classification schema
   - Domains, capabilities, complexity, maturity, integration_tier
   - Validation rules and statistics
   - Evolution policy

**Purpose:**
- Document versioning philosophy (code vs artifacts)
- Capture stable v1 baseline (2025-10-22)
- Define classification taxonomy for method organization
- Track known limitations and future work

**Maintenance:**
- Update `version_strategy.md` when versioning policy changes
- Create new baseline snapshots for v1.1, v2, etc.
- Keep taxonomy synchronized with `config/classification_taxonomy_v1.yaml` in app repo

---

## Quick Navigation

### For Developers
- **Understanding models:** → `model-docs/` (121 auto-generated docs)
- **System architecture:** → `architecture/`
- **Request flow:** → `guides/`

### For Architects
- **Versioning strategy:** → `versioning/version_strategy.md`
- **v1 baseline:** → `versioning/v1_baseline_2025-10-22.md`
- **Method classification:** → `versioning/classification_taxonomy_v1.yaml`
- **Registry design:** → `registry/`

### For Product/PM
- **MVP specifications:** → `specifications/`
- **Feature coverage:** → `specifications/`
- **Known limitations:** → `versioning/v1_baseline_2025-10-22.md` (section 4)

---

## Auto-Generated Content

**Regenerate model docs after Pydantic model changes:**
```powershell
# From application repo root
python $env:MY_TOOLSET\documentation-tools\model_docs_generator.py . --output-dir $env:MY_TOOLSET\REFERENCE\SYSTEM\model-docs
```

**Validate v1 baseline consistency:**
```powershell
# From application repo root
python $env:MY_TOOLSET\validation-tools\drift_detector.py --inventory config/methods_inventory_v1.yaml
python $env:MY_TOOLSET\validation-tools\methodtools_validator.py --inventory config/methods_inventory_v1.yaml --tools-dir config/methodtools_v1
```

---

## Cross-References

**Application Repo (`my-tiny-data-collider`):**
- `config/methods_inventory_v1.yaml` - Method catalog (28 methods)
- `config/classification_taxonomy_v1.yaml` - Source of truth for taxonomy
- `config/methodtools_v1/` - 28 tool YAML files
- `docs/ARCHITECTURE_ORCHESTRATION.md` - Implementation patterns
- `docs/VALIDATION_PATTERNS.md` - Custom types, validators

**Toolset Repo (`my-tiny-toolset`):**
- `TOOLSET/documentation-tools/model_docs_generator.py` - Generate model docs
- `TOOLSET/validation-tools/drift_detector.py` - Detect contract drift
- `TOOLSET/validation-tools/methodtools_validator.py` - Validate tool YAMLs
- `TOOLSET/validation-tools/model_spec_extractor.py` - Extract model specs

---

## Maintenance Schedule

**Daily (during development):**
- Regenerate `model-docs/` after model changes

**Weekly (during active development):**
- Review `versioning/v1_baseline_*.md` for accuracy
- Run drift detection tools

**Monthly:**
- Update `architecture/` with new services/patterns
- Update `guides/` if request flow changes
- Review `specifications/` for feature completion

**Quarterly:**
- Review versioning strategy
- Update classification taxonomy if needed
- Create new baseline snapshot if v1.1 or v2

---

*Part of the my-tiny-toolset knowledge base. See `REFERENCE/README.md` for navigation.*
