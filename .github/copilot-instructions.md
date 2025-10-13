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
  2. `CLASSIFICATION/` - Model/method/tool definitions (Pydantic schemas, reference when user asks about classification system)
  3. `DOCS/` - Documentation and guides
  4. `CONFIGS/` - Configuration templates and examples
  5. `PROMPTS/` - AI prompt collections (reference when user asks for prompt patterns or AI interaction examples)
  6. `SCHEMAS/` - JSON/YAML schemas (reference when user asks about data structure validation or API schemas)
  7. `TEMPLATES/` - Project templates and boilerplates (reference when user asks to scaffold new projects)
  8. `EXAMPLES/` - Code examples and references (reference when user needs implementation patterns)
- Each capital folder has `README.md` with curated index/pointers (read and update as needed)
- Submodules contain external knowledge (folder README points to relevant sections)

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
- Use subfolder README.md for detailed docs (e.g., `DOCS/README.md`)
- Single source of truth: no duplicate information across files
- AI should read folder README first, then update it when content changes
- README structure: Same sections as copilot-instructions.md but more explicit (AI updates these)
- USERREADME.md: Human-facing project description (do not auto-update)

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
1. Update content in respective folder (`CLASSIFICATION/`, `CONFIGS/`, `PROMPTS/`, etc.)
2. Update folder's `README.md` if structure changed
3. Keep main `README.md` in sync if visibility changed
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

## 6. Quick Reference

**If user asks to analyze project:** → Wrong repo, open application repo instead  
**If user asks to improve tool:** → This is correct repo, proceed  
**If unclear which repo:** → Check for `TOOLSET/` folder presence
