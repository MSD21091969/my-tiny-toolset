# Code Analysis Tools

**Last updated:** 2025-10-16  
**Tools:** 4 (version_tracker, code_analyzer, mapping_analyzer, excel_exporter)

## Purpose

Static analysis and documentation for Python codebases. No application-specific dependencies required.

## Tools

### version_tracker.py
Full code analysis with Git history integration.

**Use for:** Release documentation, version audits, comprehensive analysis  
**Outputs:** JSON, YAML, HTML with Git commit history

```powershell
python version_tracker.py . --version 1.0.0 --json --yaml
```

### code_analyzer.py
Quick structure analysis without Git dependencies.

**Use for:** Daily code review, CI/CD quality gates, fast analysis  
**Outputs:** CSV, JSON (models, functions, endpoints)

```powershell
python code_analyzer.py . --json --csv
```

### mapping_analyzer.py
Relationship and dependency mapping.

**Use for:** Architecture documentation, impact analysis, refactoring planning  
**Outputs:** JSON, HTML dashboard with interactive visualization

```powershell
python mapping_analyzer.py . --html
```

### excel_exporter.py
Consolidated reports in Excel format.

**Use for:** Stakeholder reports, comprehensive reviews, non-technical audiences  
**Outputs:** XLSX with 5 sheets (models, functions, endpoints, relationships, summary)

```powershell
python excel_exporter.py . --output report.xlsx
```

## Batch Wrappers

Windows `.bat` files provided for convenience:

```cmd
code_analyzer.bat . --json
version_tracker.bat . --version 1.0.0
mapping_analyzer.bat . --html
excel_exporter.bat . --output report.xlsx
```

## Output Location

All tools create `.tool-outputs/` in the target directory with subfolders:
- `analysis/` - JSON/YAML/CSV files
- `mappings/` - HTML dashboards
- `excel/` - XLSX reports
- `docs/` - Documentation artifacts
