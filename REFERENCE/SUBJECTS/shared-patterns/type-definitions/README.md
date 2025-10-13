# Type Definition Patterns

**Last updated:** 2025-10-14

## Purpose

Custom type definitions for better type safety and IDE support.

## Patterns

### TypedDict for Configuration

```python
from typing import TypedDict

class DatabaseConfig(TypedDict):
    host: str
    port: int
    database: str
    username: str
    password: str
```

**Status:** Pattern identified, needs standardization

### Protocol for Duck Typing

```python
from typing import Protocol

class HasId(Protocol):
    @property
    def id(self) -> str: ...

def process_item(item: HasId) -> None:
    print(f"Processing {item.id}")
```

**Status:** Advanced pattern, document when needed

### Generic Types

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Repository(Generic[T]):
    def get(self, id: str) -> T | None: ...
    def save(self, entity: T) -> None: ...
```

**Status:** Pattern emerging, needs validation

### Type Aliases

```python
from typing import NewType

UserId = NewType('UserId', str)
CasefileId = NewType('CasefileId', str)

# Prevents mixing IDs
def get_user(user_id: UserId) -> User: ...
def get_casefile(casefile_id: CasefileId) -> Casefile: ...
```

**Status:** Alternative to Annotated types, document trade-offs

## Next Steps

- [ ] Document TypedDict vs Pydantic choice
- [ ] Protocol patterns for service interfaces
- [ ] Generic repository pattern
- [ ] NewType vs Annotated comparison
