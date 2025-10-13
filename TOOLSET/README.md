# TOOLSET

Analysis tools for Python code inspection.

**Last updated:** 2025-10-13

## Contents

- `version_tracker.py` - Full analysis with Git history
- `code_analyzer.py` - Quick structure analysis
- `mapping_analyzer.py` - Relationship mapping
- `excel_exporter.py` - Excel report generation
- `*.bat` - Windows command wrappers

## Usage

Run from application repositories:
```powershell
python $env:MY_TOOLSET\version_tracker.py . --version 1.0.0 --json
```

## Output

Tools create `.tool-outputs/` in the directory where executed.

## Maintenance

Read carefully before modifying:
- Update copilot-instructions.md when changing tool behavior
- Maintain backward compatibility in output schemas
- Test against sample code before committing
- Update this README when adding/removing tools

**Date stamp when updating:** Check and update the "Last updated" date above.
