# Code Analyzer - Request/Response Model Mapping

Python toolkit for analyzing code models, functions, and methods. Exports to CSV, Excel, or JSON for request/response mapping analysis.

## Features

- Extract classes/models (Pydantic, dataclasses, regular classes)
- Analyze functions/methods with signatures and decorators
- Detect request/response model patterns and API endpoints
- Export to CSV (4 files), Excel (5 sheets), or JSON

## Installation

```bash
# Basic (CSV/JSON only, no dependencies)
python code_analyzer.py

# With Excel support
pip install openpyxl
```

## Usage

### Quick Commands

```bash
# Analyze current directory, export all formats
python example_usage.py

# Command line options
python code_analyzer.py                                    # Summary only
python code_analyzer.py --csv                              # Export CSV
python code_analyzer.py --json                             # Export JSON
python code_analyzer.py /path/to/code --csv --json         # Specify path
python code_analyzer.py --csv --output-dir my_output       # Custom output
```

### Python API

```python
from code_analyzer import CodeAnalyzer
from excel_exporter import export_to_excel

# Analyze
analyzer = CodeAnalyzer('.')
analyzer.analyze_directory(exclude_patterns=['venv', 'tests'])
analyzer.print_summary()

# Export
analyzer.export_to_csv('analysis_output')
analyzer.export_to_json('analysis.json')
export_to_excel(analyzer, 'analysis.xlsx')

# Access data
pydantic_models = [m for m in analyzer.models if m.is_pydantic]
async_funcs = [f for f in analyzer.functions if f.is_async]

for model in analyzer.models:
    print(f"{model.name}: {len(model.fields)} fields")
```

## Output Files

All files created in `analysis_output/` folder:

### CSV (4 files)

- `models_[timestamp].csv` - All models (name, path, line, type, field count)
- `model_fields_[timestamp].csv` - All fields (model, field name, type, default)
- `functions_[timestamp].csv` - All functions (name, path, params, return type, async)
- `req_resp_mappings_[timestamp].csv` - API mappings (endpoint, HTTP method, request/response models)

### Excel (1 file, 5 sheets)

- **Summary** - Statistics and overview
- **Models** - All models (green highlight = Pydantic)
- **Model Fields** - Field details per model
- **Functions** - All functions (blue highlight = async)
- **API Mappings** - Request/response (color-coded HTTP methods)

### JSON (1 file)

- `analysis.json` - Complete structured data with all models, functions, mappings, and statistics

## Common Tasks

**Map API endpoints to models:** Open `req_resp_mappings_*.csv`

**List Pydantic models:** Filter `models_*.csv` where `is_pydantic` = Yes

**Find model fields:** Filter `model_fields_*.csv` by `model_name`

**Find async functions:** Filter `functions_*.csv` where `is_async` = Yes

**Excel analysis:** Use filters, pivot tables, or sort on any column

## Advanced Usage

### Custom Filtering

```python
# Filter by decorator
api_functions = [f for f in analyzer.functions 
                 if any(d in ['get', 'post'] for d in f.decorators)]

# Find models with specific field
user_models = [m for m in analyzer.models 
               if any(f['name'] == 'user_id' for f in m.fields)]

# Analyze specific files only
from pathlib import Path
analyzer = CodeAnalyzer('.')
for file in Path('.').glob('api/**/*.py'):
    analyzer.analyze_file(file)
```

### Pandas Integration

```python
import pandas as pd

models_df = pd.DataFrame([{
    'name': m.name,
    'fields': len(m.fields),
    'type': 'Pydantic' if m.is_pydantic else 'Dataclass' if m.is_dataclass else 'Class'
} for m in analyzer.models])
```

## Supported Frameworks

- **Pydantic** - BaseModel detection
- **Dataclasses** - @dataclass decorator
- **FastAPI** - @app.get/post/put/delete decorators
- **Flask** - @app.route decorator
- **Type hints** - Full Python type annotation support

## Using in Other Repositories

### Setup Once: Push to GitHub

```bash
cd C:\Users\Geurt\Sam
git init
git add .
git commit -m "Code analyzer tools"
git remote add origin https://github.com/yourusername/code-analyzer.git
git push -u origin main
```

### Then on ANY Workstation:

**Clone once:**
```bash
# Clone to standard location on new machine
cd ~
git clone https://github.com/yourusername/code-analyzer.git
```

**Use anywhere:**

### Option 1: Direct Path (Simple)
```bash
# From any repository on any machine (Windows)
python %USERPROFILE%\code-analyzer\code_analyzer.py . --csv --json

# Linux/Mac
python ~/code-analyzer/code_analyzer.py . --csv --json
```

### Option 2: VS Code Task
Add to `.vscode/tasks.json` in any project:
```json
{
  "label": "Analyze Code",
  "type": "shell",
  "command": "python",
  "args": ["${userHome}/code-analyzer/code_analyzer.py", "${workspaceFolder}", "--csv"]
}
```
Run with: `Terminal → Run Task → Analyze Code`

### Option 3: Add to PATH
Windows: Add `%USERPROFILE%\code-analyzer` to PATH
Linux/Mac: Add `~/code-analyzer` to PATH

Then use from anywhere:
```bash
cd any-project
python code_analyzer.py . --csv
```

### Option 4: VS Code Multi-root Workspace
Create `my-workspace.code-workspace`:
```json
{
  "folders": [
    { "path": "${userHome}/code-analyzer", "name": "🔧 Tools" },
    { "path": "C:\\path\\to\\project1", "name": "Project 1" },
    { "path": "C:\\path\\to\\project2", "name": "Project 2" }
  ],
  "settings": {
    "python.analysis.extraPaths": ["${userHome}/code-analyzer"]
  }
}
```
Open with: `File → Open Workspace from File`

Now import works directly in any project folder:
```python
from code_analyzer import CodeAnalyzer
analyzer = CodeAnalyzer('.')
```

## Troubleshooting

**No models found:** Check file paths and exclude patterns
**Excel export failed:** Run `pip install openpyxl`
**Import errors:** Ensure correct working directory
**CSV won't open:** Use Excel → Open → select "All Files" → choose CSV
