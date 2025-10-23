# AI Instructions - Toolset Repository

**Last Updated:** 2025-10-23

## 1. What is "my-tiny-toolset"

**What:**
- Meta-analysis toolset for Python code inspection (models, functions, endpoints, relationships)
- 13 analysis, workflow, and documentation tools
- Outputs: JSON, YAML, CSV, Excel, HTML reports for documentation and CI/CD integration
- Knowledge base: Architecture, science, engineering, patterns, best practices

**External MCP Tools:**
- **Context7**: Up-to-date library documentation via MCP server (use for framework/library references)

**Who:**
- Used by: AI coding assistants (Copilot, agents), developers, CI/CD pipelines
- Maintained by: MSD21091969
- Consumers: Application repositories (like my-tiny-data-collider) that need code structure analysis

**Where:**
- GitHub: https://github.com/MSD21091969/my-tiny-toolset.git
- Tools location: `TOOLSET/` (executable Python scripts in 3 category folders)
- Knowledge base structure:
  1. `TOOLSET/` - 13 analysis/documentation/workflow tools
  2. `REFERENCE/` - Knowledge base (science, engineering, architecture, guides, best practices)
  3. `WORKSPACE/` - Research sandbox (field notes, experiments, drafts)
  4. `CONFIGS/` - Configuration templates
  5. `PROMPTS/` - AI prompt collections (submodules: awesome-prompts, edu-prompts)
  6. `SCHEMAS/` - JSON/YAML schemas (submodule: schemastore)
  7. `TEMPLATES/` - Project templates and boilerplates
  8. `EXAMPLES/` - Code examples and references (submodule: public-apis, pydantic-ai-patterns)
- Each capital folder has dated `README.md`

**How:**
- Application repos reference this toolset via Git clone or direct download
- Tools run FROM application directories: `python path/to/TOOLSET/tool.py . --version X`
- Environment variable: `$env:MY_TOOLSET` points to local clone TOOLSET folder
- CI/CD clones on-demand, runs analysis, uploads artifacts

---

## 2. Practices

**Communication:**
- Chat responses: Short, dry, no emojis (developers, not managers)
- Report in chat during work, summarize at completion
- Update existing documents, do not create new ones without approval

**Code Maintenance:**
- Test tool changes against sample code before committing
- Maintain backward compatibility in tool outputs (JSON/YAML schemas)
- Update tool inventory table when adding/modifying tools

**Documentation:**
- Update existing MD files only (no new files unless requested)
- Use subfolder README.md for detailed docs (e.g., `REFERENCE/README.md`)
- **All README.md files MUST include "Last updated: YYYY-MM-DD" at top**
- Single source of truth: no duplicate information across files
- AI should read folder README first, then update it when content changes

---

## 3. Tool Inventory (Updated Oct 22)

**Total:** 13 tools implemented (3 categories: analysis, workflow, documentation)

### Analysis Tools (4) - `TOOLSET/analysis-tools/`
| Tool | Purpose | Outputs |
|------|---------|---------| 
| `version_tracker.py` | Full analysis + Git history | JSON, YAML, HTML |
| `code_analyzer.py` | Quick structure analysis | CSV, JSON, Excel |
| `mapping_analyzer.py` | Relationship mapping | JSON, HTML dashboard |
| `excel_exporter.py` | Report generation | XLSX (5 sheets) |

**Batch wrappers:** `.bat` files for Windows command line

### Workflow Tools (7) - `TOOLSET/workflow-tools/`
| Tool | Purpose | Typical Use |
|------|---------|-------------|
| `method_search.py` | Method discovery | Find methods by domain/capability |
| `model_field_search.py` | Field search & mapping | Map response→request fields |
| `parameter_flow_validator.py` | Workflow validation | Detect missing/incompatible fields |
| `workflow_validator.py` | Comprehensive validation | Orchestrate all checks |
| `composite_tool_generator.py` | Workflow generation | Generate YAML workflows |
| `workflow_builder.py` | Interactive builder | Build from goals |
| `data_flow_analyzer.py` | Data lineage tracking | Flow visualization |

### Documentation Tools (6) - `TOOLSET/documentation-tools/`
| Tool | Purpose | Typical Use |
|------|---------|-------------|
| `json_schema_examples.py` | Example generation | OpenAPI enhancement |
| `deprecated_fields.py` | Deprecation tracking | Migration planning |
| `response_variations.py` | Response variants | API variant design |
| `schema_validator.py` | Schema validation | Test schema correctness |
| `model_docs_generator.py` | Model documentation | Auto-generate docs (121 models) |
| `field_usage_analyzer.py` | Field analytics | Find unused fields |

**Usage from application repos:**
```powershell
# Code analysis (no dependencies)
python $env:MY_TOOLSET\analysis-tools\version_tracker.py . --version 1.0.0 --json

# Workflow tools (requires $env:COLLIDER_PATH)
$env:COLLIDER_PATH = "C:\path\to\application"
python $env:MY_TOOLSET\workflow-tools\method_search.py "gmail"
```

**Output location:**
- Tools create `.tool-outputs/` in application workspace
- Structure: `analysis/`, `mappings/`, `docs/`, `excel/`
- Auto-generates README.md explaining contents
- Application repos should gitignore: `.tool-outputs/`

**Usage from application repos:**
```powershell
# Code analysis (no dependencies)
python $env:MY_TOOLSET\analysis-tools\version_tracker.py . --version 1.0.0 --json

# Workflow tools (requires $env:COLLIDER_PATH)
$env:COLLIDER_PATH = "C:\path\to\application"
python $env:MY_TOOLSET\workflow-tools\method_search.py "gmail"
```

**Output location:**
- Tools create `.tool-outputs/` in application workspace
- Structure: `analysis/`, `mappings/`, `docs/`, `excel/`
- Auto-generates README.md explaining contents
- Application repos should gitignore: `.tool-outputs/`

---

## 4. Maintenance Protocol

**When updating tools:**
1. Update tool code in `TOOLSET/`
2. Update tool inventory table above
3. Update `README.md` if interface changed
4. Regenerate batch wrappers if needed

**When updating repository folders:**
1. Update content in respective folder (`REFERENCE/`, `CONFIGS/`, `PROMPTS/`, etc.)
2. **Always update folder's `README.md` with new date stamp** if structure changed
3. Keep folder README current with content changes
4. Test changes don't break tool integrations

**Document format rules:**
- No duplicate information across files
- Single source of truth per topic
- Markdown only (no PDFs, no Word docs)
- Keep under 500 lines per file

---

## 5. Integration Context

**Environment:**
- Variable: `$env:MY_TOOLSET` → `C:\Users\HP\my-tiny-toolset\TOOLSET`
- Git: `https://github.com/MSD21091969/my-tiny-toolset.git`
- Size: ~5MB core, ~500MB with submodules

**Application repos use this via:**
- Reference (not copy)
- Environment variable
- Git submodule (optional)
- Direct clone for CI/CD

**Each application repo has own `.github/copilot-instructions.md` with different content.**

---

## 6. Capital Folders Reference

**Critical: Every folder README.md must include date stamp at top: `**Last updated:** YYYY-MM-DD`**

### TOOLSET/ - Analysis Tools
**Purpose:** Meta-tools for Python code analysis and FastAPI application development  
**Organization:** 3 category folders with 17 total tools

**Structure:**
- `analysis-tools/` - 4 tools: Code analysis without dependencies (code_analyzer, version_tracker, mapping_analyzer, excel_exporter)
- `workflow-tools/` - 7 tools: Method discovery, workflow validation, composite generation (requires COLLIDER_PATH)
- `documentation-tools/` - 6 tools: API docs, field analytics, schema validation (requires COLLIDER_PATH)
- `integration-templates/` - Templates for app integration
- `*.bat` - Windows command wrappers (in analysis-tools/)

**README.md:** Master guide with all 17 tools, usage examples, category descriptions  
**Update when:** Adding/modifying tools, changing CLI interfaces, reorganizing categories  
**Template:** Use as model for other folder READMEs (structured, dated, comprehensive)

---

### REFERENCE/ - Knowledge Base
**Purpose:** Consolidated knowledge repository (science, engineering, patterns, architecture)  
**Structure:**
- `README.md` - Master navigation and index
- `SUBJECTS/` - Domain expertise areas (data-engineering, mlops, api-design, etc.)
  - `shared-patterns/` - Reusable code patterns (Pydantic types, validators, utilities)
- `SYSTEM/` - Complete system architecture documentation
  - `architecture/` - Service overviews, system architecture (11 service docs)
  - `guides/` - Request flow, token schemas
  - `registry/` - Registry consolidation analysis
  - `specifications/` - MVP specs, toolset coverage
  - `model-docs/` - Auto-generated Pydantic model documentation (121 models)

**Knowledge Base Scope:**
- RAG optimization patterns and agent tool combinations
- Model field mappings and parameter documentation
- Audit trail integration with casefile toolsets
- Best practices, solutions, indexes to relevant sources
- Engineering patterns (MLOps, model tuning, schema evolution)
- **Agent interaction:** RAG provides responses + parameters (no reasoning/ReAct needed)
- Communication focus: Relevance, tool selection, parameter adjustment

**README.md:** Master index and navigation document  
**Update when:** Adding subjects, restructuring hierarchy, moving content, adding model-docs  
**Maintenance:** Keep synchronized with folder structure, update when SYSTEM/ contents change

---

### WORKSPACE/ - Research Sandbox
**Purpose:** Personal exploration area (messy by design)  
**Structure:**
- `FIELDNOTES.md` - Research findings, domain references, workflow commands
- `field-notes/` - Daily research notes (planned)
- `experiments/` - Test code, POCs (planned)
- `drafts/` - WIP documents before moving to REFERENCE/ (planned)

**Workflow:** Explore → Note → Experiment → Draft → Publish to REFERENCE/  
**README.md:** Explains sandbox purpose and workflow  
**Update when:** Changing research workflow, adding structure  
**Maintenance:** Keep messy but move validated knowledge to REFERENCE/

---

### CONFIGS/ - Configuration Templates
**Purpose:** Configuration examples for integration  
**Contents:**
- `gitignore-templates/` - .gitignore patterns for different project types

**README.md:** Inventory of config types, usage instructions  
**Update when:** Adding new configuration templates  
**Maintenance:** Ensure templates stay current with tool requirements

---

### PROMPTS/ - AI Prompt Collections
**Purpose:** Curated prompt libraries (external submodules)  
**Submodules:**
- `awesome-prompts/` - General purpose prompt engineering
- `edu-prompts/` - Educational and learning prompts

**README.md:** Index of prompt categories, submodule descriptions, update instructions  
**Update when:** Adding submodules, categorizing prompts, updating submodules  
**Maintenance:** Keep submodules current, document useful prompt patterns in FIELDNOTES

---

### SCHEMAS/ - Schema Definitions
**Purpose:** JSON/YAML schema patterns (external submodule)  
**Submodule:**
- `schemastore/` - Common schema patterns (JSON Schema store)

**README.md:** Schema catalog, validation examples, integration patterns  
**Update when:** Adding schemas, changing validation approaches  
**Maintenance:** Reference schemas in REFERENCE/SUBJECTS/ when relevant

---

### TEMPLATES/ - Project Templates
**Purpose:** Boilerplate code and integration templates  
**Contents:**
- `app-integration/` - Templates for integrating toolset into app repos
  - `copilot-instructions-template.md` - AI session instructions template
  - `tasks-template.json` - VS Code tasks for running analysis
  - `gitignore-additions.txt` - Tool output exclusions
- `cookiecutter/` - Project scaffolding templates (submodule)
- `integration-patterns/` - SDK integration patterns

**README.md:** Template inventory, usage instructions, integration guide  
**Update when:** Adding templates, changing integration process  
**Maintenance:** Keep templates synchronized with tool requirements

---

### EXAMPLES/ - Code Examples
**Purpose:** Reference implementations and patterns  
**Contents:**
- `public-apis/` - Public API examples and patterns (submodule)
- `pydantic-ai-patterns/` - PydanticAI integration patterns (3 examples + README)

**README.md:** Example catalog, usage patterns, integration examples  
**Update when:** Adding examples, documenting patterns  
**Maintenance:** Cross-reference examples in REFERENCE/SUBJECTS/

---

### Folder Maintenance Rules

**Every README.md MUST have:**
```markdown
**Last updated:** YYYY-MM-DD

## Contents
[List of files/folders]

## Purpose
[Why this folder exists]

## Maintenance
[Update rules]
```

**Update frequency:**
- TOOLSET/ - Every tool change
- REFERENCE/ - Every knowledge addition/restructure
- WORKSPACE/ - As needed (informal)
- CONFIGS/, PROMPTS/, SCHEMAS/, TEMPLATES/, EXAMPLES/ - When content changes

**Date stamp protocol:**
- Update date when changing structure or adding/removing content
- Small edits to existing content: optional date update
- Major reorganization: MUST update date



## 7. Auto-Approved Operations

**Analysis Tool Execution** (no ask, proceed directly):
- Running any TOOLSET analysis scripts with `python TOOLSET/analysis-tools/*.py`
- Workflow composition and validation tools
- Documentation generation tools
- All tool output to `.tool-outputs/`

**Meta-Tool Test Files** (create/run without approval):
- Test files in TOOLSET for validating tool functionality
- Diagnostic scripts for tool integration testing
- Validation scripts checking tool outputs

**Documentation Updates** (no ask, proceed):
- Updating folder README.md files with `Last updated: YYYY-MM-DD`
- Adding/removing items from tool inventory table
- Updating integration examples in REFERENCE/ or EXAMPLES/

---
