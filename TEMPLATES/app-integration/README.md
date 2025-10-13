# Application Integration Setup

This folder contains templates for integrating my-tiny-toolset into application repositories.

## Files

1. **`copilot-instructions-template.md`**
   - Template for `.github/copilot-instructions.md` in app repos
   - Replace `[PROJECT_NAME]` and `[placeholders]` with actual values
   - Tells AI how to use toolset in that specific app

2. **`tasks-template.json`**
   - VS Code tasks for running toolset commands
   - Copy to `.vscode/tasks.json` in app repo (or merge with existing)
   - Provides quick commands for analysis

3. **`gitignore-additions.txt`**
   - Lines to add to app's `.gitignore`
   - Ensures tool outputs aren't committed
   - Copy relevant lines to app's `.gitignore`

4. **`.tool-outputs-README.md`** (in parent TEMPLATES folder)
   - Auto-copied to `.tool-outputs/` when tools run
   - Explains output structure to users

## Usage

### Manual Integration

```powershell
# In your application repository
cd C:\Projects\your-app

# 1. Copy and customize copilot instructions
Copy-Item path\to\toolset\TEMPLATES\app-integration\copilot-instructions-template.md .github\copilot-instructions.md
# Edit: Replace [PROJECT_NAME] and other placeholders

# 2. Merge VS Code tasks
# Copy content from tasks-template.json into your .vscode/tasks.json

# 3. Update .gitignore
Get-Content path\to\toolset\TEMPLATES\app-integration\gitignore-additions.txt | Add-Content .gitignore

# 4. Set environment variable (if not done)
[Environment]::SetEnvironmentVariable("MY_TOOLSET", "C:\path\to\toolset\TOOLSET", "User")

# 5. Test
python $env:MY_TOOLSET\version_tracker.py . --version 1.0.0 --json
```

### Automated Integration (TODO)

Create `setup-app-integration.ps1` script for one-command setup.

## Example Application Structure After Integration

```
your-application/
├── .github/
│   └── copilot-instructions.md    ← From template
├── .vscode/
│   └── tasks.json                 ← Contains toolset tasks
├── .gitignore                     ← Updated with tool outputs
├── src/
│   └── ...
└── .tool-outputs/                 ← Created by tools (gitignored)
    ├── analysis/
    ├── mappings/
    ├── docs/
    ├── excel/
    └── README.md                  ← Auto-generated
```

## Notes

- Templates are generic - customize per application
- Environment variable `$env:MY_TOOLSET` must point to toolset TOOLSET folder
- Each app repo gets its own copilot-instructions.md (different from toolset's)
- Output folder `.tool-outputs/` is per-repo, gitignored
