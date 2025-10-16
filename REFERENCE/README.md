# REFERENCE - Knowledge Base

**Last updated:** 2025-10-16

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
- **registry/** - Registry consolidation analysis and summaries
- **specifications/** - MVP specs, toolset coverage documentation
- **model-docs/** - Auto-generated Pydantic model documentation (37 models) ✅

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

## Workflow

1. **Research** → Explore in WORKSPACE/, take field notes in FIELDNOTES.md
2. **Experiment** → Validate concepts in WORKSPACE/experiments/
3. **Draft** → Structure findings in WORKSPACE/drafts/
4. **Publish** → Move validated knowledge here to SUBJECTS/
5. **Update** → Keep this README synchronized with folder structure

## Maintenance

**Update this README when:**
- Adding new subject areas
- Restructuring hierarchy
- Moving content between sections
- Adding major reference documents
- Changing folder structure
- Updating knowledge base vision

**Date stamp protocol:**
- Update date when changing structure
- Major content reorganization requires date update
- Keep synchronized with folder structure
