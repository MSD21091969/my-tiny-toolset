# Subject Areas

**Last updated:** 2025-10-16

This directory organizes knowledge by domain expertise areas.

## Current Subjects

| Subject | Focus | Key Tools/Patterns |
|---------|-------|-------------------|
| **[tool-engineering-workflow.md](tool-engineering-workflow.md)** | AI + Human Collaboration | Tool design Q&A, implementation workflow ✅ |
| **[shared-patterns/](shared-patterns/)** | Reusable Code Patterns | Pydantic types, validators, utilities ✅ |
| **[data-engineering/](data-engineering/)** | ETL, Schema Evolution | Airflow, dbt, Great Expectations |
| **[knowledge-graphs/](knowledge-graphs/)** | Entity Relations, RAG | Neo4j, NetworkX, LangChain |
| **[api-design/](api-design/)** | Pydantic → OpenAPI | FastAPI, OpenAPI Generator |
| **[documentation/](documentation/)** | Auto-generated Docs | MkDocs, Sphinx, autodoc |
| **[mlops/](mlops/)** | Model/Data Versioning | MLflow, DVC, Airflow |

## Adding New Subjects

1. Create subject directory
2. Add README.md with overview
3. Include key patterns, tools, references
4. Update this index
5. Cross-reference from main INDEX.md

## Subject Structure Template

```
subject-name/
├── README.md           # Overview, key concepts
├── patterns/           # Common patterns
├── tools/              # Tool-specific guides
├── examples/           # Code examples
└── references/         # External links, papers
```

---

*This index auto-updates when subjects are added/modified*