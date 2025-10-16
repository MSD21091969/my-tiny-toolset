# Validator Patterns

**Last updated:** 2025-10-16  
**Status:** ✅ Production Ready - 12 validators, 236 tests passing

## Purpose

Reusable validator functions validated in `my-tiny-data-collider`. **Zero duplication pattern** - all validation logic centralized.

## Complete Reference

**📖 Full Documentation:** [`my-tiny-data-collider/docs/VALIDATION_PATTERNS.md`](../../../../my-tiny-data-collider/docs/VALIDATION_PATTERNS.md)

**Source Code:** `my-tiny-data-collider/src/pydantic_models/base/validators.py`

## Validated Patterns (12 validators)

### Timestamp Validators (3)
- `validate_timestamp_order` - Ensure timestamp ordering (created_at <= updated_at)
- `validate_timestamp_in_range` - Validate timestamp within min/max range
- Custom types: `FutureTimestamp`, `PastTimestamp`, `DateString`, `TimeString`

### Domain Validators (2)
- `validate_email_domain` - Whitelist/blacklist email domains
- `validate_url_domain` - Whitelist/blacklist URL domains

### Field Relationship Validators (4)
- `validate_at_least_one` - At least one field required
- `validate_mutually_exclusive` - Only one field allowed
- `validate_conditional_required` - Conditional requirements
- `validate_depends_on` - Field dependency validation

### Collection Validators (2)
- `validate_list_not_empty` - Non-empty list validation
- `validate_list_unique` - Unique list items

### Range Validators (2)
- `validate_range` - Numeric range validation
- `validate_string_length` - String length constraints

## Quick Example

```python
from src.pydantic_models.base.validators import validate_timestamp_order

@model_validator(mode='after')
def validate_timestamps(self) -> 'MyModel':
    # Pass actual values, not model instance
    validate_timestamp_order(
        self.created_at, 
        self.updated_at, 
        'created_at', 
        'updated_at'
    )
    return self
```

**Key Pattern:** Validators receive **field values** (not model), plus field names for error messages.

## Custom Types (30 types)

**Source:** `my-tiny-data-collider/src/pydantic_models/base/custom_types.py`

### ID Types (10)
CasefileId, ToolSessionId, ChatSessionId, SessionId, UserId, GmailMessageId, GmailThreadId, GmailAttachmentId, ResourceId, EventId

### String Types (7)
NonEmptyString, ShortString, MediumString, LongString, EmailAddress, UrlString

### Numeric Types (5)
PositiveInt, NonNegativeInt, PositiveFloat, NonNegativeFloat, Percentage, FileSizeBytes

### Timestamp Types (5)
IsoTimestamp, FutureTimestamp, PastTimestamp, DateString, TimeString

### URL/Email Types (3)
SecureUrl, GoogleWorkspaceEmail, EmailList, TagList

## Status

**Production Status:** ✅ Mature, fully tested
- 236/236 Pydantic tests passing
- 16 model files using custom types (95+ fields)
- Zero validation duplication achieved
- API stable since 2025-10-16

## Migration Path

**Already extracted and production-ready:**
- ✅ All 12 validators tested
- ✅ Used across multiple models
- ✅ API stable and documented
- ✅ Zero duplication pattern validated

**For reuse in other projects:**
1. Copy `custom_types.py` and `validators.py` to your project
2. Import validators: `from .base.validators import validate_timestamp_order`
3. Use custom types: `from .base.custom_types import CasefileId, ShortString`
4. See full guide in `VALIDATION_PATTERNS.md` for examples
