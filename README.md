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

## 💡 Copy-Worthy Insights from Legacy Analysis

Best practices extracted from legacy classification tools for building robust analysis systems:

### 🔍 **Systematic Auto-Discovery vs Hardcoded Paths**
- **Pattern**: Auto-discover directories instead of maintaining hardcoded lists
- **Implementation**: Scan source trees dynamically, include new directories automatically
- **Benefit**: Never miss new modules/models when codebase evolves
- **Example**: `Path('src/models').glob('**/*.py')` vs hardcoded category lists

### 🔄 **Verification Loops - Compare Source vs Exports**
- **Pattern**: Always verify completeness after processing
- **Implementation**: Compare extracted data against source files for missing items
- **Benefit**: Catch missing exports, ensure 100% coverage
- **Example**: Count models in source files vs exported CSV entries

### 📊 **Metrics-Driven Analysis - Quantify System Health**
- **Pattern**: Generate comprehensive metrics for system understanding
- **Implementation**: Version distribution, category coverage, completeness ratios
- **Benefit**: Objective system health assessment, identify patterns
- **Example**: "94.4% method integration rate, 2 orphaned tools detected"

### 🗺️ **Relationship Mapping - Tools ↔ Methods Coverage**
- **Pattern**: Map bidirectional relationships between components
- **Implementation**: Track which tools reference which methods, identify orphans
- **Benefit**: Ensure architectural consistency, prevent technical debt
- **Example**: Tool coverage analysis, method-to-tool mapping verification

### ⚠️ **Drift Detection - YAML vs Code Synchronization**
- **Pattern**: Detect when configuration diverges from implementation
- **Implementation**: Compare registry files against actual code definitions
- **Benefit**: Prevent configuration drift, maintain consistency
- **Example**: "34 methods in YAML but not in code" alerts

### 🎯 **Application to Modern Toolset**
These patterns should be implemented in new analysis tools to ensure:
- **Robust discovery** mechanisms
- **Quality assurance** loops
- **Comprehensive metrics** collection
- **Relationship integrity** validation
- **Configuration consistency** monitoring

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
├── classification/             # Legacy insights & analysis patterns
│   ├── docs/                   # Classification methodology docs
│   ├── exports/                # Output format examples
│   └── README.md               # Classification system overview
└── awesome-copilot/            # Copilot chat modes & prompts
```

## Author

Geurt - [MSD21091969](https://github.com/MSD21091969)
