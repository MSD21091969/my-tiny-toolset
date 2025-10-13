# Best Practices - Model Mapping & Code Versioning

Best practices for FastAPI model mapping and API versioning.

---

## Model Mapping Best Practices

### 1. Consistent Naming Convention

```python
# Pattern: {Entity}{Action}{Type}
class UserCreateRequest(BaseModel):   # Request for creating
    pass

class UserResponse(BaseModel):        # Response for user data
    pass

class UserUpdateRequest(BaseModel):   # Request for updating
    pass

# NOT: CreateUser, UserReq, UserDTO (inconsistent)
```

### 2. Explicit Request/Response Separation

```python
# ✅ Good - Clear separation
@app.post("/users", response_model=UserResponse)
def create_user(request: UserCreateRequest) -> UserResponse:
    pass

# ❌ Bad - Ambiguous
@app.post("/users")
def create_user(user: User) -> User:  # Same model for request/response
    pass
```

### 3. Version in Model Names (Breaking Changes)

```python
# When you have breaking changes
class UserCreateRequestV1(BaseModel):
    username: str
    email: str

class UserCreateRequestV2(BaseModel):  # Added required field
    username: str
    email: str
    phone: str  # Breaking change!

# Keep V1 for backwards compatibility
@app.post("/v1/users", response_model=UserResponseV1)
def create_user_v1(request: UserCreateRequestV1):
    pass

@app.post("/v2/users", response_model=UserResponseV2)
def create_user_v2(request: UserCreateRequestV2):
    pass
```

### 4. Model Inheritance for Shared Fields

```python
# Base model with common fields
class UserBase(BaseModel):
    username: str
    email: str

# Request adds creation-specific fields
class UserCreateRequest(UserBase):
    password: str

# Response adds system fields
class UserResponse(UserBase):
    id: int
    created_at: datetime
    
# Update only includes changeable fields
class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
```

### 5. Track Model Usage

```powershell
# Use version_tracker.py to see:
# - Which endpoints use each model
# - Model-to-endpoint mappings

python version_tracker.py . --version 1.0.0 --yaml

# Check "used_in_endpoints" in output
```

---

## Code Versioning Best Practices

### 1. Semantic Versioning (SemVer)

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1  (Bug fix, no API changes)
1.0.0 → 1.1.0  (New feature, backwards compatible)
1.0.0 → 2.0.0  (Breaking change)
```

### 2. Version Before Every Release

```powershell
# Before release
python version_tracker.py . --version 1.2.0 --json --yaml --output-dir releases/v1.2.0

# Commit version artifacts
git add releases/v1.2.0
git commit -m "Release v1.2.0"
git tag v1.2.0
```

### 3. Compare Before Deploying

```powershell
# Compare with production
python version_tracker.py . --compare production/version_analysis.json

# If breaking_changes array is not empty:
# → Increment MAJOR version
# → Update migration plan
# → Notify API consumers
```

### 4. Git Commit Strategy

```bash
# Commit BEFORE tracking for clean Git metadata
git add .
git commit -m "feat: add user phone field to UserCreateRequest"

# Then track
python version_tracker.py . --version 1.1.0 --json

# Git info will be accurate in output
```

### 5. Version History Archive

```powershell
# Keep historical versions
mkdir versions
python version_tracker.py . --version 1.0.0 --json --output-dir versions/v1.0.0
python version_tracker.py . --version 1.1.0 --json --output-dir versions/v1.1.0
python version_tracker.py . --version 2.0.0 --json --output-dir versions/v2.0.0

# Directory structure:
# versions/
#   v1.0.0/version_analysis.json
#   v1.1.0/version_analysis.json
#   v2.0.0/version_analysis.json
```

### 6. Automated Version Tracking in CI/CD

```yaml
# GitHub Actions - track on every push
on: [push]
jobs:
  version:
    steps:
      - name: Track version
        run: |
          VERSION=${{ github.ref_name }}
          python ~/my-tiny-toolset/version_tracker.py . --version $VERSION --json --yaml
      
      - name: Compare with main
        if: github.ref != 'refs/heads/main'
        run: |
          # Download main branch version
          wget https://raw.githubusercontent.com/user/repo/main/version_analysis.json -O main_version.json
          
          # Compare
          python ~/my-tiny-toolset/version_tracker.py . --compare main_version.json
          
          # Fail if breaking changes on non-major version bump
          breaking=$(jq '.breaking_changes | length' version_analysis/changes.json)
          if [ "$breaking" -gt 0 ]; then
            echo "⚠️ Breaking changes detected!"
            exit 1
          fi
```

### 7. Model Hash for Change Detection

```python
# version_tracker.py automatically calculates hash based on:
# - Model name
# - Base classes
# - Field names and types

# Use hash to detect if model structure changed
# Same hash = identical structure
# Different hash = something changed

# Check hash in api_versions.yaml:
# - name: UserCreateRequest
#   hash: a1b2c3d4  # Changes if structure changes
```

### 8. Breaking Change Rules

**Track these as MAJOR version bumps:**
- ❌ Model removed
- ❌ Required field added to request model
- ❌ Field removed from response model
- ❌ Field type changed
- ❌ Endpoint removed

**Safe changes (MINOR/PATCH):**
- ✅ Optional field added to request
- ✅ Field added to response
- ✅ New model added
- ✅ New endpoint added

### 9. Document Model Changes

```python
class UserCreateRequest(BaseModel):
    """
    Request model for creating users.
    
    Version History:
    - v1.0.0: Initial version (username, email)
    - v1.1.0: Added optional phone field
    - v2.0.0: Made phone required (breaking change)
    """
    username: str
    email: str
    phone: str  # Added in v1.1.0, required in v2.0.0
```

### 10. Per-Environment Versioning

```powershell
# Development (unstable)
python version_tracker.py . --version dev-20251012 --output-dir versions/dev

# Staging (release candidates)
python version_tracker.py . --version 1.2.0-rc1 --output-dir versions/staging

# Production (stable)
python version_tracker.py . --version 1.2.0 --output-dir versions/production
```

---

## Complete Workflow Example

```powershell
# 1. Start with clean Git state
git status

# 2. Make model changes
# Edit api/models/user.py

# 3. Commit changes
git add api/models/user.py
git commit -m "feat: add phone field to UserCreateRequest"

# 4. Track current version
python version_tracker.py . --version 1.0.0 --json --output-dir versions/current

# 5. Compare with previous
python version_tracker.py . --compare versions/v1.0.0/version_analysis.json

# 6. Review breaking changes
cat version_analysis/changes.json

# 7. Decide version bump
# - Breaking changes? → 2.0.0
# - New features? → 1.1.0
# - Bug fixes? → 1.0.1

# 8. Track new version
python version_tracker.py . --version 1.1.0 --json --yaml --output-dir versions/v1.1.0

# 9. Tag release
git tag v1.1.0
git push --tags
```

---

## Model Organization

```
api/
  models/
    __init__.py
    base.py          # Base classes
    user.py          # User models (all versions)
    product.py       # Product models
  routes/
    users.py         # Uses models from api.models.user
    products.py
```

**Key Points:**
- ✅ Group related models by entity (user, product)
- ✅ Keep all versions in same file for visibility
- ✅ Import from central location
- ✅ Use version tracker to see model usage across routes

---

## Quick Reference

| Action | Version Bump | Example |
|--------|-------------|---------|
| Bug fix | PATCH | 1.0.0 → 1.0.1 |
| New optional field | MINOR | 1.0.0 → 1.1.0 |
| New endpoint | MINOR | 1.0.0 → 1.1.0 |
| Required field added | MAJOR | 1.0.0 → 2.0.0 |
| Field removed | MAJOR | 1.0.0 → 2.0.0 |
| Field type changed | MAJOR | 1.0.0 → 2.0.0 |
| Model removed | MAJOR | 1.0.0 → 2.0.0 |

---

**Use `version_tracker.py --compare` to detect breaking changes automatically!**
