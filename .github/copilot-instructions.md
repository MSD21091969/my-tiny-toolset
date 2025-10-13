# AI Instructions - Toolset Repository

## 1. What is "my-tiny-toolset"

**What:**
- Analysis toolset for Python code inspection (models, functions, endpoints, relationships)
- Four core tools: version_tracker, code_analyzer, mapping_analyzer, excel_exporter
- Outputs: JSON, YAML, CSV, Excel, HTML reports for documentation and CI/CD integration

**Who:**
- Used by: AI coding assistants (Copilot, agents), developers, CI/CD pipelines
- Maintained by: MSD21091969
- Consumers: Application repositories that need code structure analysis

**Where:**
- GitHub: https://github.com/MSD21091969/my-tiny-toolset.git
- Cloud deployment: Clone from Git when needed, local clone optional for speed
- Tools location: `TOOLSET/*.py` (executable Python scripts)
- Knowledge base structure:
  1. `TOOLSET/` - Analysis tools (Python scripts, batch wrappers)
  2. `REFERENCE/` - Knowledge base (science, engineering, architecture, guides, best practices)
  3. `WORKSPACE/` - Research sandbox (field notes, experiments, drafts)
  4. `CONFIGS/` - Configuration templates and examples
  5. `PROMPTS/` - AI prompt collections (submodules: awesome-prompts, edu-prompts)
  6. `SCHEMAS/` - JSON/YAML schemas (submodule: schemastore)
  7. `TEMPLATES/` - Project templates and boilerplates (app-integration, cookiecutter)
  8. `EXAMPLES/` - Code examples and references (submodule: public-apis)
- **Each capital folder MUST have dated `README.md`** with curated index/pointers
- Submodules contain external knowledge (folder README points to relevant sections)
- See section 7 "Capital Folders Reference" for detailed structure

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
- README structure: Same sections as copilot-instructions.md but more explicit (AI updates these)
- USERREADME.md: Human-facing project description (do not auto-update)
- Use TOOLSET/README.md as template for structured, dated documentation

---

## 3. Tool Inventory

| Tool | Purpose | Outputs |
|------|---------|---------|
| `version_tracker.py` | Full analysis + Git history | JSON, YAML, HTML |
| `code_analyzer.py` | Quick structure analysis | CSV, JSON, Excel |
| `mapping_analyzer.py` | Relationship mapping | JSON, HTML dashboard |
| `excel_exporter.py` | Report generation | XLSX (5 sheets) |

**Usage from application repos:**
```powershell
python $env:MY_TOOLSET\version_tracker.py . --version 1.0.0 --json
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
5. See section 7 for folder-specific maintenance rules

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
**Purpose:** Core Python analysis scripts  
**Contents:**
- `version_tracker.py` - Full analysis + Git history
- `code_analyzer.py` - Quick structure analysis  
- `mapping_analyzer.py` - Relationship mapping
- `excel_exporter.py` - Report generation
- `*.bat` - Windows command wrappers

**README.md:** Tool inventory, usage examples, maintenance warnings  
**Update when:** Adding/modifying tools, changing CLI interfaces  
**Template:** Use as model for other folder READMEs (structured, dated)

---

### REFERENCE/ - Knowledge Base
**Purpose:** Consolidated knowledge repository (science, engineering, patterns, architecture)  
**Structure:**
- `INDEX.md` - Master navigation document
- `USERREADME.md` - Human-facing overview (do not auto-update)
- `GRAND_CLASSIFICATION_PLAN.md` - Classification methodology
- `SUBJECTS/` - Domain expertise areas (data-engineering, mlops, api-design, etc.)
- `SYSTEM/` - Complete system architecture documentation
  - `architecture/` - Service overviews, system architecture
  - `guides/` - Request flow, token schemas
  - `registry/` - Registry consolidation analysis
  - `specifications/` - MVP specs, toolset coverage

**Knowledge Base Scope:**
- RAG optimization patterns and agent tool combinations
- Model field mappings and parameter documentation
- Audit trail integration with casefile toolsets
- Best practices, solutions, indexes to relevant sources
- Engineering patterns (MLOps, model tuning, schema evolution)
- **Agent interaction:** RAG provides responses + parameters (no reasoning/ReAct needed)
- Communication focus: Relevance, tool selection, parameter adjustment

**README.md:** Currently `INDEX.md` serves as master index  
**Update when:** Adding subjects, restructuring hierarchy, moving content  
**Maintenance:** Keep INDEX.md synchronized with folder structure

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
  - `copilot-instructions-template.md`
  - `tasks-template.json`
  - `gitignore-additions.txt`
- `cookiecutter/` - Project scaffolding templates (submodule)

**README.md:** Template inventory, usage instructions, integration guide  
**Update when:** Adding templates, changing integration process  
**Maintenance:** Keep templates synchronized with tool requirements

---

### EXAMPLES/ - Code Examples
**Purpose:** Reference implementations and patterns  
**Submodule:**
- `public-apis/` - Public API examples and patterns

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

---

## 7. Quick Reference

**If user asks to analyze project:** → Wrong repo, open application repo instead  
**If user asks to improve tool:** → This is correct repo, proceed  
**If unclear which repo:** → Check for `TOOLSET/` folder presence
