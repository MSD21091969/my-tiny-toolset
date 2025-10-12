# My Tiny Toolset - Extended Laboratory

This repository contains my personal extended toolset and collections for development work.

## Structure

- `TOOLSET/` - Core development tools and analyzers
- `PROMPTS/` - Collections of AI prompts and templates
- `SCHEMAS/` - Schema definitions and OpenAPI examples
- `TEMPLATES/` - Project templates and boilerplates
- `CONFIGS/` - Configuration templates and examples
- `EXAMPLES/` - Code examples and API references

## Usage

Clone with submodules:
```bash
git clone --recursive https://github.com/MSD21091969/my-tiny-toolset.git
```

Update all submodules:
```bash
git submodule update --remote --recursive
```

Update specific submodule:
```bash
git submodule update --remote PROMPTS/awesome-prompts
```

## Submodule Management

Each collection is a git submodule pointing to external repositories. This allows:
- Clean separation of concerns
- Easy updates from upstream sources
- Tracking specific versions of each collection
- Minimal storage overhead

To add new collections, use:
```bash
git submodule add <repository-url> <path>
```