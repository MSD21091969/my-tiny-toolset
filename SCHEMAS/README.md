# SCHEMAS - Schema Definitions

**Last updated:** 2025-10-16

## Purpose

JSON/YAML schema patterns for validation, API design, and data structure documentation.

## Contents

### [schemastore/](schemastore/)
Comprehensive collection of JSON schemas for common file formats and configurations:
- Package managers (package.json, requirements.txt, pyproject.toml)
- Configuration files (tsconfig.json, .eslintrc, etc.)
- CI/CD configs (GitHub Actions, GitLab CI, etc.)
- API specifications (OpenAPI, AsyncAPI, GraphQL)

**Source:** https://github.com/SchemaStore/schemastore

**Update submodule:**
```powershell
git submodule update --remote schemastore
```

## Schema Use Cases

### Validation Examples
- JSON Schema validation with Python (jsonschema library)
- YAML schema validation with pykwalify
- Pydantic model generation from JSON Schema
- OpenAPI schema validation

### Integration Patterns
- Using schemas for API contract testing
- Schema-driven code generation
- Documentation generation from schemas
- Schema evolution and versioning

## Relevant Schema Types

For toolset and application development:

- **OpenAPI/Swagger** - API specification and documentation
- **JSON Schema** - Data validation and structure definition
- **Pydantic** - Python data validation schemas
- **YAML** - Configuration and data serialization
- **pyproject.toml** - Python project configuration
- **GitHub Actions** - CI/CD workflow schemas

## Usage

Reference schemas when:
- Validating configuration files
- Generating API documentation
- Creating Pydantic models
- Setting up IDE validation/autocomplete

## Maintenance

**Update when:**
- Adding custom schemas
- Changing validation approaches
- Updating submodule to latest schemas
- Documenting schema patterns

**Cross-reference:**
- Link schemas to REFERENCE/SUBJECTS/ when relevant
- Document schema patterns in WORKSPACE/FIELDNOTES.md

**Date stamp:**
- Update when adding custom schemas
- Major organizational changes
