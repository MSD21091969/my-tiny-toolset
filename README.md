# My Tiny Toolset - Extended Laboratory 

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

`powershell
# Install dependencies
pip install PyYAML openpyxl

# Analyze any project
cd your-fastapi-project
python $env:USERPROFILE\my-tiny-toolset\tools\version_tracker.py . --version 1.0.0 --json --yaml
`

## Tools

| Tool | Purpose | Output |
|------|---------|--------|
| 	ools/version_tracker.py | Version tracking + Git + Mapping | JSON, YAML, Manifests, HTML Report |
| 	ools/code_analyzer.py | Quick analysis | CSV, JSON, Excel |
| 	ools/mapping_analyzer.py | Model relationships | JSON, HTML Dashboard |
| 	ools/excel_exporter.py | Excel export | XLSX (5 sheets) |

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
