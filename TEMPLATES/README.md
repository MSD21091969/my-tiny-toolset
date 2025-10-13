# TEMPLATES - Project Templates

**Last updated:** 2025-10-14

## Purpose

Boilerplate code and integration templates for scaffolding projects and integrating the toolset into application repositories.

## Contents

### [app-integration/](app-integration/)
Templates for integrating my-tiny-toolset into application repositories:
- `copilot-instructions-template.md` - AI assistant configuration template
- `tasks-template.json` - VS Code tasks for running toolset commands
- `gitignore-additions.txt` - Gitignore patterns for tool outputs
- `README.md` - Integration instructions

**See:** [app-integration/README.md](app-integration/README.md) for detailed usage

### [cookiecutter/](cookiecutter/)
Project scaffolding templates (submodule):
- Python package templates
- FastAPI application templates
- Data science project structures
- Documentation templates

**Source:** https://github.com/cookiecutter/cookiecutter

**Update submodule:**
```powershell
git submodule update --remote cookiecutter
```

## Template Categories

### Application Integration
- Toolset setup for new repositories
- VS Code workspace configuration
- CI/CD integration patterns

### Project Scaffolding
- Python package structure
- FastAPI application boilerplate
- Documentation site setup
- Testing framework setup

## Usage

### Integrate Toolset into Existing App
```powershell
# See app-integration/README.md for full instructions
cd your-application
# Copy and customize templates
```

### Create New Project from Template
```powershell
# Using cookiecutter templates
cookiecutter path/to/template
```

## Maintenance

**Update when:**
- Adding new integration templates
- Changing toolset integration process
- Adding new project scaffolding templates
- Updating template documentation

**Keep synchronized with:**
- Tool requirements (update when tools change)
- Best practices (update patterns as they evolve)
- Application repo needs

**Date stamp:**
- Update when adding/removing templates
- Major template changes
- Integration process updates
