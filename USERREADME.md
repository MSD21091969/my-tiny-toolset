e# My Tiny Toolset - Extended Laboratory 

This repository contains my personal extended toolset and collections for development work, including Python tools for analyzing FastAPI applications with version tracking and CI/CD integration.

## Structure

- TOOLSET/ - Core development tools and analyzers
- PROMPTS/ - Collections of AI prompts and templates
- SCHEMAS/ - Schema definitions and OpenAPI examples
- TEMPLATES/ - Project templates and boilerplates
- CONFIGS/ - Configuration templates and examples
- EXAMPLES/ - Code examples and API references
- 	ools/ - Python analysis tools (legacy location)
- classification/ - Legacy insights & analysis patterns
- docs/ - Documentation

## Quick Start

```powershell
# Install dependencies
pip install PyYAML openpyxl

# Analyze any project
cd your-fastapi-project
python $env:USERPROFILE\my-tiny-toolset\TOOLSET\version_tracker.py . --version 1.0.0 --json --yaml
```

## 🚀 Quick Deploy (For Occasional Use Elsewhere)

**Need tools on a different workstation? One command gets you started:**

```powershell
# Download single tool instantly (5 seconds)
iwr -useb https://raw.githubusercontent.com/MSD21091969/my-tiny-toolset/main/TOOLSET/version_tracker.py -o version_tracker.py

# Use immediately
python version_tracker.py . --version 1.0.0
```

**Or lightweight clone (no big collections):**
```powershell
# Quick 5MB download (no submodules)
git clone --depth 1 --no-recurse-submodules https://github.com/MSD21091969/my-tiny-toolset.git temp-tools
python temp-tools\TOOLSET\version_tracker.py . --version 1.0.0
# Delete when done: rm -rf temp-tools
```

**Available tools for quick download:**
- `version_tracker.py` - Version tracking + Git + Mapping
- `code_analyzer.py` - Quick analysis  
- `mapping_analyzer.py` - Model relationships
- `excel_exporter.py` - Excel export

## Tools

| Tool | Purpose | Output |
|------|---------|--------|
| `TOOLSET/version_tracker.py` | Version tracking + Git + Mapping | JSON, YAML, Manifests, HTML Report |
| `TOOLSET/code_analyzer.py` | Quick analysis | CSV, JSON, Excel |
| `TOOLSET/mapping_analyzer.py` | Model relationships | JSON, HTML Dashboard |
| `TOOLSET/excel_exporter.py` | Excel export | XLSX (5 sheets) |

## Extended Collections Usage

Clone with submodules:
`ash
git clone --recursive https://github.com/MSD21091969/my-tiny-toolset.git
`

Update all submodules:
`ash
git submodule update --remote --recursive
`

Update specific submodule:
`ash
git submodule update --remote PROMPTS/awesome-prompts
`

## Submodule Management

Each collection is a git submodule pointing to external repositories. This allows:
- Clean separation of concerns
- Easy updates from upstream sources
- Tracking specific versions of each collection
- Minimal storage overhead

To add new collections, use:
`ash
git submodule add <repository-url> <path>
`

## Author

Geurt - [MSD21091969](https://github.com/MSD21091969)
