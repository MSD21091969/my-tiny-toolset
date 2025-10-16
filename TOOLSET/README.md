# TOOLSET

Analysis and workflow tools for Python code inspection and FastAPI development.

**Last updated:** 2025-10-16  
**Total Tools:** 17 (4 code analysis + 7 workflow + 6 documentation)  
**Organization:** Tools organized in 3 category folders

## Tool Categories

### 1. Code Analysis Tools (`analysis-tools/`)
Static analysis and documentation for Python codebases.

| Tool | Purpose | Typical Use |
|------|---------|-------------|
| `version_tracker.py` | Full analysis with Git history | Release documentation, version audits |
| `code_analyzer.py` | Quick structure analysis | Daily code review, CI/CD quality gates |
| `mapping_analyzer.py` | Relationship mapping | Architecture docs, impact analysis |
| `excel_exporter.py` | Consolidated reports (XLSX) | Stakeholder reports, comprehensive reviews |

**Usage:**
```powershell
# Quick analysis
python $env:MY_TOOLSET\analysis-tools\code_analyzer.py . --json

# Full version analysis
python $env:MY_TOOLSET\analysis-tools\version_tracker.py . --version 1.0.0 --yaml

# Relationship mapping
python $env:MY_TOOLSET\analysis-tools\mapping_analyzer.py . --html
```

### 2. Workflow Composition Tools (`workflow-tools/`)
Service method discovery and workflow validation (requires `COLLIDER_PATH`).

| Tool | Purpose | Typical Use |
|------|---------|-------------|
| `method_search.py` | Method discovery & classification | Find methods by domain/capability |
| `model_field_search.py` | Field search & compatibility | Map response→request fields |
| `parameter_flow_validator.py` | Workflow chain validation | Detect missing/incompatible fields |
| `workflow_validator.py` | Comprehensive validation | Orchestrate all validation checks |
| `composite_tool_generator.py` | Composite workflow generator | Generate YAML workflows from method sequences |
| `workflow_builder.py` | Interactive workflow builder | Build workflows from goals interactively |
| `data_flow_analyzer.py` | Data flow & lineage tracker | Track data flow across methods with confidence scoring |

**Usage:**
```powershell
$env:COLLIDER_PATH = "C:\path\to\my-tiny-data-collider"
cd $env:MY_TOOLSET\workflow-tools

# Find gmail methods
python method_search.py "gmail"

# Check field compatibility
python model_field_search.py --map-from CreateCasefileResponse --map-to UpdateCasefileRequest

# Validate workflow
python parameter_flow_validator.py create_casefile add_session_to_casefile grant_permission

# Comprehensive validation
python workflow_validator.py method1 method2 method3 --suggest-fixes

# Generate composite workflows
python composite_tool_generator.py create_casefile list_casefiles --auto-map
python composite_tool_generator.py method1 method2 --validate --output workflow.yaml

# Interactive workflow builder
python workflow_builder.py  # Interactive mode
python workflow_builder.py --goal "Create casefile and grant permission"
python workflow_builder.py --methods create_casefile grant_permission --output workflow.yaml

# Data flow analysis
python data_flow_analyzer.py create_casefile grant_permission
python data_flow_analyzer.py method1 method2 method3 --full-lineage --export flow.json
```
```

### 3. Documentation Tools (`documentation-tools/`)
API documentation enhancement and quality metrics (requires `COLLIDER_PATH`).

| Tool | Purpose | Typical Use |
|------|---------|-------------|
| `json_schema_examples.py` | Example generator & coverage | Enhance OpenAPI docs, track coverage |
| `deprecated_fields.py` | Deprecation tracking | Migration planning, API evolution |
| `response_variations.py` | Response model variations | Design API variants (summary/detailed/error/pending/partial) |
| `schema_validator.py` | JSON schema validation | Test schema correctness, validate roundtrips |
| `model_docs_generator.py` | Model documentation | Auto-generate markdown docs for all models |
| `field_usage_analyzer.py` | Field usage analytics | Analyze field usage patterns, find unused fields |

**Usage:**
```powershell
$env:COLLIDER_PATH = "C:\path\to\my-tiny-data-collider"
cd $env:MY_TOOLSET\documentation-tools

# Coverage reports
python json_schema_examples.py --report
python response_variations.py --coverage

# Generate examples/suggestions
python json_schema_examples.py --model CreateCasefileRequest
python response_variations.py --model CreateCasefileResponse --suggest

# Code templates
python response_variations.py --model CreateCasefileResponse --template summary

# Validate schemas
python schema_validator.py --test-all
python schema_validator.py --model CreateCasefileRequest

# Generate documentation
python model_docs_generator.py --generate-all
python model_docs_generator.py --model CreateCasefileRequest --with-examples
python model_docs_generator.py --index

# Field usage analytics
python field_usage_analyzer.py --analyze
python field_usage_analyzer.py --unused
python field_usage_analyzer.py --co-occurrence

# Deprecated fields
python deprecated_fields.py --list
python deprecated_fields.py --report
```

### 4. Integration Templates
- `integration-templates/` - Templates for integrating toolset into application repos
  - `copilot-instructions-template.md`
  - `tasks-template.json`
  - `gitignore-additions.txt`
  - `README.md`

### 5. Windows Wrappers
- `*.bat` - Batch files for convenient tool execution on Windows

## Quick Start

### For Code Analysis (any Python project)
```powershell
# Set environment variable (one-time)
$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"

# Run from your project
cd C:\path\to\your-project
python $env:MY_TOOLSET\code_analyzer.py . --json
```

### For Workflow Tools (FastAPI + Pydantic projects)
```powershell
# Set collider path
$env:COLLIDER_PATH = "C:\path\to\my-tiny-data-collider"

# Search methods
python $env:MY_TOOLSET\method_search.py --domain workspace

# Validate workflow
python $env:MY_TOOLSET\workflow_validator.py method1 method2 --full-report
```

## Output Structure

Tools create `.tool-outputs/` in the directory where executed:
```
.tool-outputs/
  ├── analysis/      # Code analysis results (JSON, YAML, CSV)
  ├── mappings/      # Relationship maps, HTML dashboards
  ├── docs/          # Generated documentation
  └── excel/         # Excel reports
```

## Tool Summary

| Category | Tools | Environment |
|----------|-------|-------------|
| **Code Analysis** | 4 tools | Any Python project |
| **Workflow Composition** | 7 tools | Requires COLLIDER_PATH |
| **Documentation** | 6 tools | Requires COLLIDER_PATH |
| **Total** | **17 tools** | |

## Dependencies

**Code Analysis Tools:**
- Python 3.10+
- Standard library only

**Workflow & Documentation Tools:**
- Python 3.10+
- Pydantic 2.x
- FastAPI application structure (my-tiny-data-collider)

## Maintenance

**Before modifying tools:**
1. Test changes against sample code
2. Maintain backward compatibility in output schemas
3. Update this README when adding/removing tools
4. Update `.github/copilot-instructions.md` for behavior changes
5. Regenerate batch wrappers if needed

**Adding new tools:**
1. Create tool in `TOOLSET/` directory
2. Add to appropriate category in this README
3. Update tool inventory table
4. Update date stamp at top
5. Test with both standalone and environment variable execution

**Date stamp protocol:** Update "Last updated" date when:
- Adding/removing tools
- Changing tool interfaces
- Major documentation updates

## Contributing

See parent repository documentation for:
- Tool design patterns
- Output format standards
- Testing requirements
- Integration guidelines
