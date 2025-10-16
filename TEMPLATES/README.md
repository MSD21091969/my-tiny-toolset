# TEMPLATES - Project Templates

**Last updated:** 2025-10-16

## Purpose

External project scaffolding templates for creating new projects from boilerplate.

## Contents

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

## Usage

### Create New Project from Template
```powershell
# Using cookiecutter templates
cookiecutter path/to/template
```

## Note

**For toolset integration templates**, see `TOOLSET/integration-templates/` - those are for integrating this toolset into existing applications, not for creating new projects.

## Maintenance

**Update when:**
- Adding new external template sources
- Updating template documentation
- Changing recommended templates

**Date stamp:**
- Update when adding/removing template sources
