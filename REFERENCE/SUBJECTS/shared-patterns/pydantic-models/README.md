# Pydantic Model Patterns

**Last updated:** 2025-10-16

## Purpose

Validated Pydantic model patterns from `my-tiny-data-collider` ready for extraction to shared library.

## Validated Patterns

### Custom Annotated Types

**Source:** `my-tiny-data-collider/src/pydantic_models/base/custom_types.py`

**20+ types implemented:**
- ID types: `CasefileId`, `ToolSessionId`, `ChatSessionId`, `SessionId`
- String types: `NonEmptyString`, `ShortString`, `MediumString`, `LongString`
- Numeric types: `PositiveInt`, `NonNegativeInt`, `PositiveFloat`, `NonNegativeFloat`
- Specialized: `EmailAddress`, `UrlString`, `IsoTimestamp`, `TagList`, `EmailList`

**Pattern:**
```python
from typing import Annotated
from pydantic import Field, BeforeValidator

def validate_lowercase_uuid(v: str) -> str:
    return v.lower()

CasefileId = Annotated[
    str,
    Field(pattern=r'^[0-9a-f-]{36}$'),
    BeforeValidator(validate_lowercase_uuid)
]
```

**When to extract:** Already mature, 159 tests passing

### Base Model Classes

**Pattern:** Common fields with inheritance
```python
class TimestampedModel(BaseModel):
    created_at: IsoTimestamp
    updated_at: IsoTimestamp | None = None

class IdentifiedModel(BaseModel):
    id: CasefileId
    name: ShortString
```

**Status:** Design validated, needs standardization

### Model Composition

**Pattern:** Embedding vs referencing
```python
# Embed full object
class Order(BaseModel):
    customer: Customer  # Full customer data

# Reference by ID
class Order(BaseModel):
    customer_id: CustomerId  # Just the ID
```

**Status:** In use, needs documentation

## Migration Path

**Step 1:** Document current usage in collider
**Step 2:** Identify breaking change risks
**Step 3:** Create `my-tiny-shared-libs` repo structure
**Step 4:** Copy with tests
**Step 5:** Update collider imports

## Next Steps

- [ ] Document all 20+ custom types with examples
- [ ] Standardize base model classes
- [ ] Write migration guide
- [ ] Create extraction checklist
