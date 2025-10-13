# Reference Guide Index

Living reference guide for data engineering, API design, and knowledge management.

## Core Reference Documents

- **[FIELD_REFERENCES.md](FIELD_REFERENCES.md)** - Subject area overview and key patterns
- **[GRAND_CLASSIFICATION_PLAN.md](GRAND_CLASSIFICATION_PLAN.md)** - Classification methodology
- **[USERREADME.md](USERREADME.md)** - User-facing documentation

## Subject Areas

### [Data Engineering](SUBJECTS/data-engineering/)
ETL patterns, schema evolution, data validation frameworks

### [Knowledge Graphs](SUBJECTS/knowledge-graphs/)
Entity relationships, RAG optimization, graph databases

### [API Design](SUBJECTS/api-design/)
Pydantic → OpenAPI workflows, FastAPI patterns, versioning

### [Documentation](SUBJECTS/documentation/)
Automated docs, living documentation, doc-driven development

### [MLOps](SUBJECTS/mlops/)
Model versioning, data lineage, experiment tracking

## Cross-Cutting Concerns

### [Patterns](PATTERNS/)
Reusable patterns across subject areas

### [Decisions](DECISIONS/)
Architecture decisions and rationale

## System Architecture

### [SYSTEM/](SYSTEM/)
Core service architecture, registry patterns, integration points

---

## Research Workflow

1. **Explore** → Use submodules in PROMPTS/, SCHEMAS/, etc.
2. **Note** → Capture findings in WORKSPACE/field-notes/
3. **Experiment** → Test ideas in WORKSPACE/experiments/
4. **Distill** → Move validated knowledge to SUBJECTS/
5. **Reference** → Update this index and cross-references

*Updated: $(Get-Date -Format 'yyyy-MM-dd')*