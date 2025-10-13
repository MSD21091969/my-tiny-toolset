# Validator Patterns

**Last updated:** 2025-10-14

## Purpose

Reusable validator functions validated in `my-tiny-data-collider`.

## Validated Patterns

### Cross-Field Validators

**Source:** `my-tiny-data-collider/src/pydantic_models/base/validators.py`

**9 validators implemented:**
- `validate_timestamp_order` - Ensure timestamp ordering
- `validate_at_least_one` - At least one field required
- `validate_mutually_exclusive` - Only one field allowed
- `validate_conditional_required` - Conditional requirements
- `validate_list_not_empty` - Non-empty list validation
- `validate_list_unique` - Unique list items
- `validate_range` - Numeric range validation
- `validate_string_length` - String length constraints
- `validate_depends_on` - Field dependency validation

**Pattern:**
```python
def validate_timestamp_order(
    model: BaseModel,
    start_field: str,
    end_field: str,
    error_message: str | None = None
) -> BaseModel:
    start = getattr(model, start_field, None)
    end = getattr(model, end_field, None)
    
    if start and end and start > end:
        raise ValueError(error_message or f"{start_field} must be before {end_field}")
    
    return model
```

**Status:** Mature, 43+ tests passing

## Migration Path

**Ready for extraction:**
- All 9 validators tested
- Used across multiple models
- API stable

**Extraction checklist:**
- [ ] Copy validators with type hints
- [ ] Include comprehensive tests
- [ ] Document all parameters
- [ ] Add usage examples
