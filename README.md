# My Tiny Toolset 🛠️

Python tools for analyzing FastAPI applications with version tracking and CI/CD integration.

## Quick Start

```powershell
# Install dependencies
pip install PyYAML openpyxl

# Analyze any project
cd your-fastapi-project
python $env:USERPROFILE\my-tiny-toolset\tools\version_tracker.py . --version 1.0.0 --json --yaml
```

## Tools

| Tool | Purpose | Output |
|------|---------|--------|
| `tools/version_tracker.py` | Version tracking + Git + Mapping | JSON, YAML, Manifests, HTML Report |
| `tools/code_analyzer.py` | Quick analysis | CSV, JSON, Excel |
| `tools/mapping_analyzer.py` | Model relationships | JSON, HTML Dashboard |
| `tools/excel_exporter.py` | Excel export | XLSX (5 sheets) |

## Documentation

- 📖 **[docs/README.md](docs/README.md)** - Full documentation
- 📊 **[docs/OUTPUT_REFERENCE.md](docs/OUTPUT_REFERENCE.md)** - Output examples
- 📋 **[docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md)** - Model mapping & versioning guide

## Project Structure

```
my-tiny-toolset/
├── tools/                      # Python analysis tools
│   ├── code_analyzer.py
│   └── version_tracker.py
├── docs/                       # Documentation
│   ├── README.md
│   ├── OUTPUT_REFERENCE.md
│   ├── BEST_PRACTICES.md
│   └── requirements.txt
└── awesome-copilot/            # Copilot chat modes & prompts
```

## Author

Geurt - [MSD21091969](https://github.com/MSD21091969)
