# Development Instructions

## Available Toolset

This project has access to custom analysis tools via the `my-tiny-toolset` repository.

### Code Analyzer Tool

**Repository:** https://github.com/MSD21091969/my-tiny-toolset.git

**Purpose:** Analyze Python code to extract models, functions, and request/response mappings. Exports to CSV, Excel, and JSON.

**Setup (once per machine):**
```bash
git clone https://github.com/MSD21091969/my-tiny-toolset.git ~/my-tiny-toolset
```

**Usage:**
```bash
# From this project directory
python ~/my-tiny-toolset/code_analyzer.py . --csv --json
```

**Capabilities:**
- Extract Pydantic models and dataclasses
- Analyze function signatures and decorators
- Detect API endpoint patterns (FastAPI, Flask)
- Map request/response models
- Export to CSV (4 files), Excel (5 sheets), or JSON

**When to suggest:**
- User asks about analyzing models or code structure
- Need to map API endpoints to request/response models
- Creating documentation for models or APIs
- Code review or migration planning
- Understanding project architecture

**Python API:**
```python
from code_analyzer import CodeAnalyzer
from excel_exporter import export_to_excel

analyzer = CodeAnalyzer('.')
analyzer.analyze_directory()
analyzer.export_to_csv('analysis_output')
export_to_excel(analyzer, 'analysis.xlsx')
```

**Output:** Creates `analysis_output/` folder with timestamped CSV files, Excel workbook, and JSON.

## Setup Required

If tools aren't available yet:
```bash
git clone https://github.com/MSD21091969/my-tiny-toolset.git ~/my-tiny-toolset
pip install openpyxl  # For Excel export
```
