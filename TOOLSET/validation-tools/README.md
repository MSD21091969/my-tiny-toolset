# Validation Tools

**Last updated:** 2025-10-22  
**Tools:** 4 (model spec extractor, inventory validator, drift detector, methodtools validator)

## Purpose

Validate methods_inventory_v1.yaml against code, detect drift, and ensure tool YAMLs stay synchronized.

**Part of:** Phase 9 - Toolset v1 Baseline (2025-10-22)

## Tools

### model_spec_extractor.py
Extract field specifications from Pydantic models → `models_specification_v1.yaml`.

**Use for:** Generate versioned model specs, document request/response fields  
**Outputs:** YAML/JSON model specifications

```powershell
# Generate full model spec
python model_spec_extractor.py --output models_specification_v1.yaml

# Output as JSON
python model_spec_extractor.py --json

# Extract specific model
python model_spec_extractor.py --model CreateCasefileRequest
```

**Output format:**
```yaml
version: 1.0.0
date: 2025-10-22
description: Code-fresh model specifications
methods:
  create_casefile:
    request_model: CreateCasefileRequest
    response_model: CreateCasefileResponse
    request_fields:
      - name: payload
        type: CreateCasefilePayload
        required: true
    response_fields:
      - name: payload
        type: CreateCasefileResponsePayload
        required: true
```

---

### methods_inventory_validator.py
Cross-check `methods_inventory_v1.yaml` against code (MANAGED_METHODS + service_module_map).

**Use for:** Validate inventory correctness, find mismatches  
**Outputs:** Text validation report, JSON results

```powershell
# Validate inventory
python methods_inventory_validator.py --inventory path/to/methods_inventory_v1.yaml

# JSON output
python methods_inventory_validator.py --inventory inventory.yaml --json
```

**Checks:**
- Internal methods (integration_tier: internal) → MANAGED_METHODS
- External methods (integration_tier: external) → service_module_map
- Hybrid methods → both registries
- Model existence (request/response models)
- Classification alignment

**Exit codes:**
- 0: Valid (warnings OK)
- 1: Errors detected

---

### drift_detector.py
Detect drift between inventory and current code state.

**Use for:** CI/CD drift checks, inventory maintenance  
**Outputs:** Text drift report, JSON analysis

```powershell
# Detect drift
python drift_detector.py --inventory path/to/methods_inventory_v1.yaml

# JSON output
python drift_detector.py --inventory inventory.yaml --json

# CI/CD mode (exit 1 if drift)
python drift_detector.py --inventory inventory.yaml --ci-mode
```

**Detects:**
- **New methods:** In code but not inventory
- **Deleted methods:** In inventory but not code (internal only)
- **Changed signatures:** Request/response model changes
- **Changed classification:** Domain, subdomain, capability, etc.
- **Version changes:** Method version updates

**Drift severity:**
- None: 0 changes
- Low: 1-3 changes
- Medium: 4-10 changes
- High: 11+ changes

**Use in CI/CD:**
```yaml
# .github/workflows/validate-inventory.yml
- name: Check drift
  run: python drift_detector.py --inventory config/methods_inventory_v1.yaml --ci-mode
```

---

### methodtools_validator.py
Validate tool YAMLs against `methods_inventory_v1.yaml`.

**Use for:** Ensure tool YAMLs reference valid methods with correct models  
**Outputs:** Text validation report, JSON results

```powershell
# Validate all tools in directory
python methodtools_validator.py --inventory inventory.yaml --tools path/to/methodtools_v1/

# Validate single tool
python methodtools_validator.py --inventory inventory.yaml --tool single_tool.yaml

# JSON output
python methodtools_validator.py --inventory inventory.yaml --tools tools/ --json
```

**Checks:**
- Method exists in inventory
- Request/response models match
- Classification aligns (domain, subdomain, capability, integration_tier)
- Implementation reference correct (service.method)
- Version compatibility (informational)

**Exit codes:**
- 0: Valid or warnings only
- 1: Errors detected

---

## Validation Workflow

**Complete validation flow:**

1. **Validate inventory** → `methods_inventory_validator.py`
2. **Check drift** → `drift_detector.py`
3. **Extract model specs** → `model_spec_extractor.py`
4. **Validate tools** → `methodtools_validator.py`

**Example script:**
```powershell
$inventory = "c:\path\to\config\methods_inventory_v1.yaml"
$tools = "c:\path\to\config\methodtools_v1"

# 1. Validate inventory against code
python methods_inventory_validator.py --inventory $inventory

# 2. Check for drift
python drift_detector.py --inventory $inventory

# 3. Generate model specs
python model_spec_extractor.py --output models_specification_v1.yaml

# 4. Validate tool YAMLs
python methodtools_validator.py --inventory $inventory --tools $tools
```

---

## Prerequisites

**No COLLIDER_PATH required** - tools auto-detect application repo in parent directory.

**Expected structure:**
```
my-tiny-toolset/
  TOOLSET/validation-tools/  ← Run from here
my-tiny-data-collider/         ← Auto-detected
  config/methods_inventory_v1.yaml
  config/methodtools_v1/
  src/methodregistryservice/   ← MANAGED_METHODS
```

**Python requirements:**
- PyYAML
- Pydantic (imported from application repo)

---

## Integration with Phase 9

These tools support the **Toolset v1 Baseline** (2025-10-22):

**Baseline files:**
- `config/methods_inventory_v1.yaml` - Validated by inventory_validator + drift_detector
- `config/models_specification_v1.yaml` - Generated by model_spec_extractor
- `config/methodtools_v1/*.yaml` - Validated by methodtools_validator

**Validation layers:**
1. **Design time:** methodtools_validator (tool YAMLs → inventory)
2. **Commit time:** drift_detector (inventory → code)
3. **Runtime:** MANAGED_METHODS (internal methods)

**CI/CD integration:**
```yaml
# Validate on PR
validation:
  steps:
    - name: Check inventory drift
      run: python drift_detector.py --inventory config/methods_inventory_v1.yaml --ci-mode
    
    - name: Validate tools
      run: python methodtools_validator.py --inventory config/methods_inventory_v1.yaml --tools config/methodtools_v1
```

---

## Output Location

All tools output to stdout by default.

**File outputs:**
- `model_spec_extractor.py --output` → Writes YAML/JSON to specified path
- Other tools → JSON via `--json` flag to stdout (redirect to file if needed)

**Recommended output location:**
```
my-tiny-data-collider/
  config/
    methods_inventory_v1.yaml          ← Source of truth
    models_specification_v1.yaml       ← Generated
    classification_taxonomy_v1.yaml    ← Manual (Phase 9)
    methodtools_v1/                    ← Validated
```

---

*Part of Toolset v1 Baseline - 2025-10-22*
