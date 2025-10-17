# REFERENCE - Knowledge Base

**Last updated:** 2025-10-17

## Purpose

Consolidated knowledge repository covering science, engineering, architecture, best practices, and reference materials for data engineering, RAG optimization, agent tooling, and system architecture.

## Contents

### Core Documents
- **GRAND_CLASSIFICATION_PLAN.md** - Moved to WORKSPACE/ (research/planning document)

### Knowledge Areas

#### [SUBJECTS/](SUBJECTS/)
Domain expertise organized by area:
- **[shared-patterns/](SUBJECTS/shared-patterns/)** - Reusable code patterns (Pydantic types, validators, utilities) ✅
- **data-engineering/** - ETL patterns, schema evolution (planned)
- **knowledge-graphs/** - RAG optimization, entity relationships (planned)
- **api-design/** - Pydantic → OpenAPI workflows (planned)
- **documentation/** - Auto-generated docs, living documentation (planned)
- **mlops/** - Model versioning, data lineage (planned)

#### [SYSTEM/](SYSTEM/)
Complete system architecture and documentation:
- **architecture/** - Service overviews, system architecture documents
- **guides/** - Request flows, token schemas, integration patterns, best practices
  - **20251016_user_manual.md** - ⭐ **PRIMARY MANUAL** - Data-first AI architecture guide (updated 2025-10-17)
  - Covers: Two-repository architecture, session design, RAR pattern, validation framework, test suite architecture
- **registry/** - Registry consolidation analysis and summaries
- **specifications/** - MVP specs, toolset coverage documentation
- **[model-docs/](SYSTEM/model-docs/)** - Auto-generated Pydantic model documentation ✅
  - **37 core models documented** (public API surface)
  - Organized by architecture layer: canonical (9), operations (12), views (3), workspace (13)
  - Covers 78 total models in codebase
  - Model hierarchy, validation patterns, quick reference guides

## Knowledge Base Vision

**Agent Interaction Pattern:**
- RAG provides: Relevant context + Parameter recommendations
- Agent receives: Pre-reasoned responses (no ReAct loop needed)
- Communication focus: Tool relevance, parameter adjustment, execution confidence

**Scope:**
- RAG optimization patterns and agent tool combinations
- Model field mappings and parameter documentation
- Audit trail integration with casefile toolsets
- Best practices, solutions catalog, implementation guides
- Engineering patterns (MLOps, model tuning, schema evolution)

## Quick Start

**New to the project?** Read these in order:
1. **SYSTEM/guides/20251016_user_manual.md** - Complete system architecture and philosophy
2. **SYSTEM/model-docs/README.md** - Model documentation index with architecture layers and hierarchy
3. **SUBJECTS/shared-patterns/** - Reusable code patterns (Pydantic types, validators)

**For AI assistants:** Primary reference is `SYSTEM/guides/20251016_user_manual.md` for system context and architectural decisions.

## Workflow

1. **Research** → Explore in WORKSPACE/, take field notes in FIELDNOTES.md
2. **Experiment** → Validate concepts in WORKSPACE/experiments/
3. **Draft** → Structure findings in WORKSPACE/drafts/
4. **Publish** → Move validated knowledge here to SUBJECTS/ or SYSTEM/
5. **Update** → Keep this README synchronized with folder structure

## Recent Updates

**2025-10-17:**
- **Systematized model documentation** - Reorganized model-docs README with architecture layers
  - Added model statistics: 37 documented / 78 total models
  - Created model hierarchy diagram (CasefileModel → children)
  - Organized by layer: domain entities, DTOs, views, workspace models
  - Added quick reference by use case and validation framework section
- Removed tool-engineering-workflow.md from SUBJECTS/ (consolidated into user manual)
- Updated user manual with test suite architecture section (Section 14)
- Documented pytest 8.x import resolution discovery (no `__init__.py` in test dirs)
- Updated test counts: 179 unit tests (all passing), 34 integration tests
- Fixed import patterns throughout codebase (removed "from src." pattern)

**2025-10-16:**
- Added 20251016_user_manual.md covering complete data-first AI architecture
- Documented two-repository architecture, session design, RAR pattern
- Added validation framework documentation with 30 custom types, 12 validators
- Covered ADK experiment findings and strategic decisions

## Maintenance

**Update this README when:**
- Adding new subject areas or major documents
- Restructuring hierarchy
- Moving content between sections
- Changing folder structure
- Major updates to primary documents (user manual, guides)

**Date stamp protocol:**
- Update date when changing structure or adding major content
- Document significant updates in Recent Updates section
- Keep synchronized with actual folder structure
