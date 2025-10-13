# Utility Patterns

**Last updated:** 2025-10-14

## Purpose

Helper functions and utilities ready for sharing.

## Candidates

### ID Generation

**Source:** `my-tiny-data-collider/src/coreservice/id_service.py`

```python
import uuid

def generate_casefile_id() -> str:
    """Generate lowercase UUID for casefile."""
    return str(uuid.uuid4()).lower()

def generate_short_id(prefix: str = "") -> str:
    """Generate short ID with optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:8]}"
```

**Status:** In use, needs abstraction

### Date/Time Formatting

```python
from datetime import datetime

def to_iso_timestamp(dt: datetime) -> str:
    """Convert datetime to ISO 8601 string."""
    return dt.isoformat()

def parse_iso_timestamp(s: str) -> datetime:
    """Parse ISO 8601 string to datetime."""
    return datetime.fromisoformat(s)
```

**Status:** Pattern identified, needs implementation

### String Manipulation

```python
def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string with suffix."""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix
```

**Status:** Common pattern, needs extraction

## Next Steps

- [ ] Extract ID generation utilities
- [ ] Standardize datetime handling
- [ ] Collect string manipulation patterns
- [ ] Add type hints and tests
