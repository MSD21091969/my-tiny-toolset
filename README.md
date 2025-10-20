# my-tiny-toolset

Meta-tools repository for Python code analysis and FastAPI application development.

**Last Updated:** 2025-10-21  
**Repository:** https://github.com/MSD21091969/my-tiny-toolset.git

---

## What is this?

A collection of **meta-tools** for analyzing, documenting, and designing Python applications. These tools help you understand code structure, validate workflows, and generate documentation **before** building features.

**Key insight:** Analyze first, build second. These tools help you discover patterns, detect issues, and plan workflows before writing application code.

---

## Repository Structure

```
my-tiny-toolset/
├── TOOLSET/                    # 17 production-ready meta-tools ⭐
│   ├── analysis-tools/         # 4 tools: code analysis, version tracking
│   ├── workflow-tools/         # 7 tools: method search, workflow validation
│   ├── documentation-tools/    # 6 tools: API docs, field analytics
│   └── README.md               # Tool usage guide
│
├── REFERENCE/                  # Knowledge base (curated)
│   ├── SUBJECTS/               # Domain expertise (data-eng, MLOps, APIs)
│   └── SYSTEM/                 # Architecture, specs, guides
│
├── WORKSPACE/                  # Research sandbox (messy by design)
│   └── FIELDNOTES.md           # Research findings, workflow commands
│
├── CONFIGS/                    # Configuration templates
├── PROMPTS/                    # AI prompt collections (submodules)
├── SCHEMAS/                    # JSON/YAML schemas (submodule)
├── TEMPLATES/                  # Project templates
└── EXAMPLES/                   # Code examples (submodule)
```

**Critical:** Every folder with capital letters MUST have a dated `README.md`.

---

## Quick Start

### 1. Set Environment Variable

```powershell
$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"
```

### 2. Use Tools

**Code Analysis (no dependencies):**
```powershell
# Quick analysis
python $env:MY_TOOLSET\analysis-tools\code_analyzer.py . --json

# Full version analysis
python $env:MY_TOOLSET\analysis-tools\version_tracker.py . --version 1.0.0
```

**Workflow Tools (requires `$env:COLLIDER_PATH`):**
```powershell
$env:COLLIDER_PATH = "C:\path\to\application"

# Find methods
python $env:MY_TOOLSET\workflow-tools\method_search.py "gmail"

# Build workflow
python $env:MY_TOOLSET\workflow-tools\workflow_builder.py --goal "Your goal"
```

**Documentation Tools (requires `$env:COLLIDER_PATH`):**
```powershell
# Generate docs
python $env:MY_TOOLSET\documentation-tools\model_docs_generator.py --generate-all

# Analyze field usage
python $env:MY_TOOLSET\documentation-tools\field_usage_analyzer.py --analyze
```

### 3. Read Documentation

- **Tool guide:** `TOOLSET/README.md` - Comprehensive usage guide
- **Category guides:** Each tool folder has its own README
- **Knowledge base:** `REFERENCE/INDEX.md` - Master navigation

---

## Tool Categories

### Code Analysis (4 tools)
No application dependencies. Analyze any Python codebase.

- `version_tracker.py` - Full analysis with Git history
- `code_analyzer.py` - Quick structure analysis
- `mapping_analyzer.py` - Relationship mapping
- `excel_exporter.py` - Excel reports

### Workflow Composition (7 tools)
Requires FastAPI application with `@register_service_method` decorators.

- `method_search.py` - Method discovery
- `model_field_search.py` - Field search & mapping
- `parameter_flow_validator.py` - Workflow validation
- `workflow_validator.py` - Comprehensive validation
- `composite_tool_generator.py` - YAML workflow generation
- `workflow_builder.py` - Interactive workflow builder
- `data_flow_analyzer.py` - Data lineage tracking

### Documentation (6 tools)
Requires Pydantic models and service methods.

- `json_schema_examples.py` - Example generator
- `deprecated_fields.py` - Deprecation tracking
- `response_variations.py` - Response variant suggestions
- `schema_validator.py` - JSON schema validation
- `model_docs_generator.py` - Auto-generate model docs
- `field_usage_analyzer.py` - Field usage analytics

---

## Integration Pattern

**Application repos use this toolset via:**

1. **Environment variable:** `$env:MY_TOOLSET` points to `TOOLSET/` folder
2. **Git submodule** (optional): Clone into application repo
3. **Direct clone:** CI/CD clones on-demand for analysis
4. **Reference only:** No code copying, tools run from central location

**Each application repo has its own `.github/copilot-instructions.md` with application-specific context.**

---

## Knowledge Base

The `REFERENCE/` folder contains curated knowledge:

- **SUBJECTS/** - Domain expertise (data engineering, MLOps, API design)
- **SYSTEM/** - Complete system architecture documentation
  - `architecture/` - Service overviews
  - `guides/` - Request flow, token schemas
  - `registry/` - Registry consolidation
  - `specifications/` - MVP specs, toolset coverage

**Workflow:** Explore in `WORKSPACE/` → Validate → Move to `REFERENCE/`

---

## Development Practices

**Communication:**
- Short, dry, no emojis (developers, not managers)
- Update existing docs only (no new files without approval)

**Documentation:**
- Single source of truth: No duplicate information
- Date stamp all major docs: `**Last Updated:** YYYY-MM-DD`
- Update folder README when structure changes

**Tool Maintenance:**
- Test against sample code before committing
- Maintain backward compatibility in outputs
- Update tool inventory when adding/modifying tools

---

## Status

**Tools:** ✅ 17/17 complete and production-ready (71h actual work)  
**Tests:** 263/263 passing in collider application  
**Documentation:** ✅ Comprehensive with usage examples  
**Organization:** ✅ 3 category folders with individual READMEs

**Last major update:** 2025-10-16 - Organized tools into category folders

---

## Related Repositories

- **my-tiny-data-collider** - FastAPI application using this toolset
  - 34 service methods with decorator registration
  - 37 Pydantic models
  - Tools analyze this application for workflow composition

---

## License

See repository LICENSE file.

## Maintainer

MSD21091969
