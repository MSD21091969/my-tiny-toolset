# CONFIGS - Configuration Templates

# CONFIGS

**Last updated:** 2025-10-16

## Purpose

Configuration templates and examples for integrating the toolset into application repositories and CI/CD pipelines.

## Contents

### [gitignore-templates/](gitignore-templates/)
`.gitignore` patterns for different project types:
- Python projects
- Node.js projects
- Tool output exclusions

## Usage

Copy relevant patterns to your application's `.gitignore`:

```powershell
# Add tool outputs to gitignore
Get-Content $env:MY_TOOLSET\..\CONFIGS\gitignore-templates\tool-outputs.txt | Add-Content .gitignore
```

## Planned Additions

- **fastapi-configs/** - FastAPI-specific configuration templates
- **vscode-configs/** - VS Code workspace and task configurations
- **ci-cd-configs/** - GitHub Actions, GitLab CI templates
- **env-templates/** - Environment variable templates

## Maintenance

**Update when:**
- Adding new configuration templates
- Tools require new gitignore patterns
- Integration patterns change

**Date stamp:**
- Update when adding/removing template categories
- Major template changes
