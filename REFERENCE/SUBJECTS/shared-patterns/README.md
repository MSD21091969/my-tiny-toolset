# Shared Patterns

# Shared Code Patterns

**Last updated:** 2025-10-21

## Purpose

Reference implementations and validated patterns for reusable code across projects. These patterns are tested in `my-tiny-data-collider` and documented here for extraction into `my-tiny-shared-libs` when mature.

## Contents

### [VALIDATION_PATTERNS.md](VALIDATION_PATTERNS.md) ⭐
**Complete validation guide** (quick reference + pointer to full docs)
- 30 custom types catalog (IDs, strings, numbers, timestamps, URLs/emails)
- 12 reusable validators reference
- Migration instructions for other projects
- **Full detailed guide:** `my-tiny-data-collider/docs/VALIDATION_PATTERNS.md` (870 lines)

### [pydantic-models/](pydantic-models/)
Reusable Pydantic model patterns:
- Custom annotated types (CasefileId, ShortString, etc.)
- Base model classes with common fields
- Model composition patterns
- Serialization strategies

### [validators/](validators/)
Reusable validator functions (detailed breakdown):
- Field validators (@field_validator)
- Model validators (@model_validator)
- Cross-field validation patterns
- Conditional validation logic
- **See also:** VALIDATION_PATTERNS.md for complete catalog

### [utilities/](utilities/)
Helper functions and utilities:
- ID generation (UUID, short IDs)
- Date/time formatting
- String manipulation
- Type conversion helpers

### [type-definitions/](type-definitions/)
Custom type definitions:
- TypedDict patterns
- Protocol definitions
- Generic type patterns
- Type aliases

## Workflow

**1. Develop in collider:**
```python
# In my-tiny-data-collider/src/pydantic_models/base/
class CustomType:
    # Implement and test
```

**2. Document pattern here:**
```python
# In REFERENCE/SUBJECTS/shared-patterns/pydantic-models/
# Copy working implementation
# Add documentation and examples
# Note lessons learned
```

**3. Extract when stable:**
```bash
# Create my-tiny-shared-libs repo
# Move 5+ validated patterns
# Set up as installable package
# Update collider to import from package
```

## Maturity Criteria

Extract to `my-tiny-shared-libs` when:
- ✅ **5+ patterns validated** - Currently have 30 custom types + 12 validators (42 total)
- ✅ **Used in 3+ contexts** - Used across 16 model files in collider (95+ fields)
- ✅ **Comprehensive tests** - 236/236 tests passing
- ✅ **Documentation complete** - VALIDATION_PATTERNS.md (870 lines)
- ✅ **API stable** - No breaking changes expected

**Status:** ✅ Ready for extraction when shared-libs repo is created

## Related Documentation

**Source implementations:**
- `my-tiny-data-collider/src/pydantic_models/base/custom_types.py`
- `my-tiny-data-collider/src/pydantic_models/base/validators.py`

**Usage examples:**
- `my-tiny-data-collider/docs/VALIDATION_PATTERNS.md`

**Future package:**
- `my-tiny-shared-libs` (to be created)

## Maintenance

**Update when:**
- New pattern validated in collider
- Pattern proves useful across multiple services
- Breaking change identified and documented
- Pattern ready for extraction

**Date stamp:**
- Update when adding new pattern categories
- Document lessons learned from implementation
