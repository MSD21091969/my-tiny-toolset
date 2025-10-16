# Data Intelligence Toolkit - Field Notes

**Last updated:** 2025-10-14

---

## 🎯 Knowledge Base Vision (REFERENCE/ Folder)

The REFERENCE/ folder serves as our consolidated knowledge base covering:

**Core Knowledge Areas:**
- **Science & Engineering** - RAG optimization, MLOps patterns, model tuning strategies
- **Agent Tools & Combinations** - Tool composition patterns, parameter flow design
- **Model Field Mappings** - Complete field inventories, parameter documentation, type hierarchies
- **Audit Trail Integration** - Casefile toolset linkages, data lineage tracking
- **Best Practices** - Engineering patterns, solutions catalog, implementation guides
- **Source Indexes** - Curated links to authoritative references

**Agent Interaction Pattern:**
- RAG system provides: Relevant context + Parameter recommendations
- Agent receives: Pre-reasoned responses, no ReAct loop needed
- Communication focus: Tool relevance, parameter adjustments, execution confidence
- Goal: Minimize reasoning overhead, maximize execution accuracy

**Knowledge Organization:**
- `SUBJECTS/` - Domain expertise (data-engineering, knowledge-graphs, api-design, mlops, documentation)
- `SYSTEM/` - Architecture docs, service specs, registry patterns, request flows
- `INDEX.md` - Master navigation and cross-references
- `GRAND_CLASSIFICATION_PLAN.md` - Classification methodology

**Maintenance Protocol:**
- Move validated knowledge from WORKSPACE/ experiments to REFERENCE/SUBJECTS/
- Keep INDEX.md synchronized with folder structure
- Date stamp all README.md files when updating structure
- Single source of truth - no duplicate information

---

## 🚀 Data Engineering - ETL Patterns & Schema Evolution

### Key Libraries & Tools
- **Apache Airflow** - Workflow orchestration
- **dbt (data build tool)** - Transform data in warehouse
- **Great Expectations** - Data validation framework
- **Pandera** - Pandas data validation
- **SQLAlchemy** - Database ORM with migration support

### Schema Evolution Patterns
- **Backward Compatibility** - Add optional fields, never remove
- **Forward Compatibility** - Handle unknown fields gracefully
- **Schema Registry** - Centralized schema management (Confluent Schema Registry)
- **Migration Scripts** - Automated database schema updates

### References
- [The Data Engineering Cookbook](https://github.com/andkret/Cookbook)
- [Awesome Data Engineering](https://github.com/igorbarinov/awesome-data-engineering)
- [dbt Learn](https://docs.getdbt.com/docs/learn)

---

## 🕸️ Knowledge Graphs - Entity Relationships & RAG Optimization

### Core Technologies
- **Neo4j** - Graph database
- **NetworkX** - Python graph analysis
- **RDFLib** - RDF/SPARQL for Python
- **spaCy** - NLP for entity extraction
- **LangChain** - RAG framework integration

### RAG Enhancement Patterns
- **Hierarchical Indexing** - Multi-level document structure
- **Hybrid Search** - Vector + keyword search
- **Graph-RAG** - Entity relationships in retrieval
- **Contextual Compression** - Smart chunk selection

### References
- [Neo4j Graph Academy](https://graphacademy.neo4j.com/)
- [Advanced RAG Techniques](https://github.com/microsoft/graphrag)
- [Knowledge Graph Construction](https://github.com/IBM/kg-construction)

---

## 🔌 API Design - Pydantic → OpenAPI Workflows

### FastAPI Ecosystem
- **FastAPI** - Auto OpenAPI generation from Pydantic
- **Pydantic V2** - Enhanced validation & serialization
- **OpenAPI Generator** - Client SDK generation
- **Redoc/Swagger** - Interactive API documentation

### Design Patterns
- **Schema-First Design** - Define models before endpoints
- **Version Compatibility** - API versioning strategies  
- **Response Models** - Separate input/output schemas
- **Dependency Injection** - Reusable validation logic

### References
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)

---

## 📚 Documentation Engineering - Auto-Generated Docs

### Documentation Tools
- **MkDocs** - Markdown-based site generator
- **Sphinx** - Python documentation standard
- **autodoc** - Auto-generate from docstrings
- **pydantic-docs** - Model documentation generation
- **JSON Schema Docs** - Schema to documentation

### Automation Patterns
- **Pre-commit Hooks** - Doc validation on commit
- **CI/CD Integration** - Auto-deploy docs
- **Living Documentation** - Code-driven doc updates
- **API Documentation** - OpenAPI to static docs

### References
- [Write the Docs](https://www.writethedocs.org/)
- [Documentation Driven Development](https://gist.github.com/zsup/9434452)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

---

## 🤖 MLOps - Model Versioning & Data Lineage

### MLOps Stack
- **MLflow** - Model lifecycle management
- **DVC** - Data version control
- **Weights & Biases** - Experiment tracking
- **Apache Airflow** - ML pipeline orchestration
- **Great Expectations** - Data quality monitoring

### Lineage Tracking
- **Data Lineage** - Track data flow through transformations
- **Model Lineage** - Track model training dependencies
- **Feature Stores** - Centralized feature management
- **Experiment Tracking** - Reproducible ML experiments

### References
- [MLOps Principles](https://ml-ops.org/)
- [Awesome MLOps](https://github.com/visenger/awesome-mlops)
- [Data Version Control (DVC)](https://dvc.org/doc)

---

## 🧮 Math/Graph Toolset Ideas

### Toolset 2: Network Analysis
```python
# Field relationship graphs
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

# Correlation analysis
import pandas as pd
import seaborn as sns
import scipy.stats as stats

# Data flow visualization  
import plotly.graph_objects as go
from plotly.subplots import make_subplots
```

### Graph Analysis Patterns
- **Field Dependencies** - Which fields depend on others
- **Data Flow Graphs** - Visualize transformation pipelines  
- **Correlation Matrices** - Statistical relationships
- **Usage Frequency** - Most/least used fields
- **Schema Evolution** - Track changes over time

### References
- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [Graph Analysis with Python](https://github.com/practical-python/graphs)
- [Data Visualization Best Practices](https://github.com/cxli233/FriendsDontLetFriends)

---

## 🎯 Prompt Collection Focus Areas

### Data Transformation Prompts
- Schema mapping between systems
- Data validation rule generation
- ETL pipeline documentation
- Error handling strategies

### Schema Analysis Prompts  
- Field relationship discovery
- Data type optimization
- Constraint generation
- Migration planning

### Documentation Generation Prompts
- API documentation from code
- Schema documentation
- User guide generation
- Technical specification writing

### Code Review/Refactoring Prompts
- Pydantic model optimization
- Performance improvement suggestions
- Security vulnerability detection
- Code quality assessment

### Business → Technical Prompts
- Requirements to technical specs
- User stories to data models
- Business rules to validation logic
- Process flows to API design

---

## 📁 Collection Structure

```
/TOOLSET/           # Your analysis tools
/PROMPTS/           # AI prompt collections  
  /awesome-prompts/ # General purpose prompts
  /edu-prompts/     # Educational prompts
  /gpt3-prompts/    # GPT-specific prompts
/SCHEMAS/           # JSON/YAML schemas
  /schemastore/     # Common schema patterns
  /openapi-examples/# API schema examples
/TEMPLATES/         # Code/doc templates
  /cookiecutter/    # Project templates
  /fastapi-stack/   # Full-stack templates  
/CONFIGS/           # Configuration patterns
  /gitignore-templates/
  /fastapi-configs/
/EXAMPLES/          # Sample transformations
  /public-apis/     # API examples
  /pydantic-examples/
```

## 🎛️ Workflow Commands

- **"Get my tools"** → Run "Complete Toolset Setup"
- **"Get collections"** → Run "Get All Collections"  
- **Outputs** → `C:\Users\HP\Desktop\krabbel\tool-outputs\`
- **Docs** → `tool-outputs\docs\` (auto-copied MDs)

---

## 🔧 Tool Engineering Focus

### YAML-Driven Development
- **Models defined in Pydantic** → Exported to YAML
- **Tools defined in YAML** → Validated against methods
- **Parameters mapped automatically** → Type-checked
- **Changes in code** → Registry drift detection

### Custom Tool Functions
- Build reusable validators (9 functions so far)
- Create custom types (20+ types so far)
- Generic helpers for audit, session management
- All validated with comprehensive tests

### Problem-Solving Workflow
1. Define problem (Git issue or ROUNDTRIP_ANALYSIS.md action item)
2. Check existing solutions (REFERENCE/SUBJECTS/)
3. Implement solution using custom types/validators
4. Validate with tests (159+ tests framework)
5. Document pattern if reusable (WORKSPACE/ → REFERENCE/)
6. Update tool YAMLs if new parameters added

---

## 🔄 Data Workflow Cycle (RAG/Tuning)

### Transfer
- Gmail/Drive/Sheets → Casefile storage
- Structured data models (GmailMessage, DriveFile, SheetData)
- Audit trail: session_id → casefile_id hierarchy

### Transformation
- Pydantic validation ensures data quality
- Custom types enforce constraints
- Validators check business rules

### Analysis
- Code analysis tools from toolset
- Parameter mapping validation
- Registry drift detection

### RAG Integration
- Casefile as context storage
- Session management for conversation continuity
- Tool execution history for learning

### Tuning Cycle
- Validation errors → Improve models
- Parameter mismatches → Update tool YAMLs
- Test failures → Refine validation logic
- Repeat cycle iteratively

---

*Happy data engineering! 🚀*