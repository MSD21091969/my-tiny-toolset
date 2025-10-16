# Workflow Composition Tools

**Last updated:** 2025-10-16  
**Tools:** 7 (method search, field search, validators, generators, builder, analyzer)

## Purpose

Service method discovery, workflow validation, and composite tool generation for FastAPI applications.

**Requires:** `$env:COLLIDER_PATH` pointing to application repository with registered service methods.

## Tools

### method_search.py (349 lines)
Search and filter service methods by keyword, domain, capability.

**Use for:** Method discovery, capability search, domain filtering  
**Outputs:** Text table, JSON

```powershell
python method_search.py "gmail"
python method_search.py --domain workspace --json
python method_search.py --capability "create" --output methods.json
```

### model_field_search.py (403 lines)
Search models for fields and map response→request compatibility.

**Use for:** Field discovery, compatibility mapping, field tracking  
**Outputs:** Text table, JSON

```powershell
python model_field_search.py --field casefile_id
python model_field_search.py --map-from CreateCasefileResponse --map-to UpdateCasefileRequest
```

### parameter_flow_validator.py (469 lines)
Validate workflow chains for parameter compatibility.

**Use for:** Workflow validation, missing field detection, incompatibility warnings  
**Outputs:** Text validation report, JSON

```powershell
python parameter_flow_validator.py create_casefile grant_permission
python parameter_flow_validator.py method1 method2 method3 --json
```

### workflow_validator.py (525 lines)
Comprehensive workflow validation orchestrating all checks.

**Use for:** Complete workflow validation, fix suggestions, detailed analysis  
**Outputs:** Text report with suggestions, JSON

```powershell
python workflow_validator.py create_casefile add_session grant_permission
python workflow_validator.py method1 method2 --suggest-fixes --json
```

### composite_tool_generator.py (477 lines)
Generate composite YAML workflows from method sequences.

**Use for:** Workflow automation, YAML generation, field auto-mapping  
**Outputs:** YAML workflow files, JSON mapping reports

```powershell
python composite_tool_generator.py create_casefile list_casefiles --auto-map
python composite_tool_generator.py method1 method2 --validate --output workflow.yaml
python composite_tool_generator.py method1 method2 method3 --auto-map --detailed
```

### workflow_builder.py (337 lines)
Interactive CLI to build workflows from natural language goals.

**Use for:** Goal-based workflow design, interactive building, method suggestions  
**Outputs:** YAML workflows, interactive prompts

```powershell
python workflow_builder.py  # Interactive mode
python workflow_builder.py --goal "Create casefile and grant permission"
python workflow_builder.py --methods create_casefile grant_permission --output workflow.yaml
```

### data_flow_analyzer.py (463 lines)
Track data lineage and flow across method workflows.

**Use for:** Data lineage tracking, flow visualization, confidence scoring  
**Outputs:** ASCII flow diagrams, JSON flow reports

```powershell
python data_flow_analyzer.py create_casefile grant_permission
python data_flow_analyzer.py method1 method2 method3 --full-lineage
python data_flow_analyzer.py workflow --export flow.json
```

## Workflow

**Typical workflow composition process:**

1. **Discover methods** → `method_search.py "gmail"` 
2. **Check compatibility** → `model_field_search.py --map-from ResponseModel --map-to RequestModel`
3. **Validate workflow** → `parameter_flow_validator.py method1 method2 method3`
4. **Generate composite** → `composite_tool_generator.py method1 method2 --auto-map --output workflow.yaml`

**Or use interactive builder:**

```powershell
python workflow_builder.py --goal "Your workflow goal"
```

## Prerequisites

Set `$env:COLLIDER_PATH` before running any tool:

```powershell
$env:COLLIDER_PATH = "C:\path\to\my-tiny-data-collider"
cd $env:MY_TOOLSET\workflow-tools
```

Tools require:
- Collider application with `@register_service_method` decorators
- Pydantic models in `src/pydantic_models/`
- Method registry in `src/pydantic_ai_integration/method_registry.py`
