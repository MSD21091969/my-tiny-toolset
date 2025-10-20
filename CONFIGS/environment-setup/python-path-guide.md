# Environment Variables & Python Path Guide

**Last Updated:** 2025-10-20  
**Purpose:** Document environment setup, import resolution, Python path management

---

## Part 1: Environment Variables

### Toolset Location

```powershell
# Windows PowerShell
$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"

# Usage in batch files
python %MY_TOOLSET%\analysis-tools\code_analyzer.py . --json

# Usage in Python scripts
import os
toolset_path = os.environ.get('MY_TOOLSET', '.')
```

**Why:** Toolset location varies by machine (dev, CI/CD, different users)

### Application Path

```powershell
# Application root (for workflow tools that need it)
$env:COLLIDER_PATH = "C:\Users\HP\my-tiny-data-collider"

# Workflow tools use this to find method registry
python %MY_TOOLSET%\workflow-tools\method_search.py "gmail"
```

### Python Path (Module Resolution)

```powershell
# Add src/ to Python path
$env:PYTHONPATH = "C:\Users\HP\my-tiny-data-collider\src"

# Now Python can find modules in src/
python -c "from casefileservice.service import CasefileService"
```

**Common patterns:**
```powershell
# Multiple paths (semicolon-separated on Windows)
$env:PYTHONPATH = "C:\project\src;C:\libs"

# Add to existing path
$env:PYTHONPATH = "$env:PYTHONPATH;C:\new\path"
```

### API Keys (Never Commit!)

```powershell
# OpenAI
$env:OPENAI_API_KEY = "sk-..."

# Google Workspace
$env:GOOGLE_CLIENT_ID = "..."
$env:GOOGLE_CLIENT_SECRET = "..."

# Firestore
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\service-account.json"
```

**Security:**
- Use `.env` files (gitignored)
- Use secret management (Azure Key Vault, AWS Secrets Manager)
- Never hardcode in source code

---

## Part 2: Import Resolution

### Why `from casefileservice...` not `from src.casefileservice...`

**Your directory structure:**
```
my-tiny-data-collider/
├── src/                    ← Added to sys.path
│   ├── casefileservice/    ← Import as: casefileservice
│   ├── tool_sessionservice/← Import as: tool_sessionservice
│   └── pydantic_models/    ← Import as: pydantic_models
├── tests/                  ← Added to sys.path (pytest)
└── scripts/                ← NOT in sys.path
```

**How Python finds modules:**

```python
import sys
print(sys.path)
# [
#   '',  # Current directory
#   'C:\\Users\\HP\\my-tiny-data-collider\\src',  # ← src/ added
#   'C:\\Python\\lib',
#   ...
# ]

# When you import:
from casefileservice.service import CasefileService

# Python searches sys.path for 'casefileservice' folder
# Finds it in: C:\Users\HP\my-tiny-data-collider\src\casefileservice
# Success!

# If you try:
from src.casefileservice.service import CasefileService

# Python searches sys.path for 'src' folder
# Not found (src/ is IN sys.path, not a subfolder OF something in sys.path)
# ModuleNotFoundError!
```

### How `src/` Gets Added to `sys.path`

**Option 1: pytest (automatic)**
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
pythonpath = "src"

# pytest adds src/ to sys.path before running tests
```

**Option 2: setuptools (package installation)**
```python
# pyproject.toml
[tool.setuptools]
packages = ["casefileservice", "tool_sessionservice", "pydantic_models"]
package-dir = {"": "src"}

# pip install -e . (editable mode)
# Adds src/ to sys.path permanently
```

**Option 3: Manual (in script)**
```python
# scripts/some_script.py
import sys
from pathlib import Path

# Add src/ to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Now can import
from casefileservice.service import CasefileService
```

**Option 4: PYTHONPATH environment variable**
```powershell
$env:PYTHONPATH = "C:\Users\HP\my-tiny-data-collider\src"
python scripts/some_script.py
```

---

## Part 3: CLI vs HTTP vs Direct Import

### Direct Import (SDK Pattern)

**When:** Consumer is Python, same environment

```python
# consumer.py
from casefileservice.service import CasefileService
from pydantic_models.operations.casefile_ops import CheckPermissionRequest

# Create request
request = CheckPermissionRequest(
    client_request_id="check_001",
    payload=CheckPermissionPayload(
        casefile_id="cf_abc123",
        user_id="usr_789",
        required_permission="read"
    )
)

# Call service directly
service = CasefileService()
response = await service.check_permission(request)
print(response.payload.has_required_permission)
```

**Requirements:**
- Python installed
- Package installed (`pip install my-tiny-data-collider`)
- OR: `$env:PYTHONPATH` includes src/

**Pros:**
- Fast (no network, no subprocess)
- Type-safe (IDE autocomplete, type checking)
- Debugging (step through code)

**Cons:**
- Python-only
- Version lock (must match package version)
- Same process (crashes affect consumer)

---

### CLI Pattern (Subprocess)

**When:** Consumer is non-Python, scripting, CI/CD

```powershell
# Hypothetical CLI (not implemented yet)
python -m my_tiny_data_collider casefile check-permission \
  --casefile-id cf_abc123 \
  --user-id usr_789 \
  --required-permission read \
  --output json

# Output:
# {
#   "request_id": "check_001",
#   "status": "success",
#   "payload": {
#     "has_required_permission": true,
#     "can_read": true,
#     "can_write": false
#   }
# }
```

**Implementation (cli.py - not in codebase yet):**
```python
# src/my_tiny_data_collider/cli.py
import click
import asyncio
import json
from casefileservice.service import CasefileService
from pydantic_models.operations.casefile_ops import CheckPermissionRequest

@click.group()
def cli():
    """My Tiny Data Collider CLI"""
    pass

@cli.group()
def casefile():
    """Casefile operations"""
    pass

@casefile.command()
@click.option('--casefile-id', required=True)
@click.option('--user-id', required=True)
@click.option('--required-permission', required=True)
@click.option('--output', type=click.Choice(['json', 'yaml']), default='json')
def check_permission(casefile_id, user_id, required_permission, output):
    """Check if user has permission"""
    request = CheckPermissionRequest(
        client_request_id=f"cli_{casefile_id}_{user_id}",
        payload=CheckPermissionPayload(
            casefile_id=casefile_id,
            user_id=user_id,
            required_permission=required_permission
        )
    )
    
    service = CasefileService()
    response = asyncio.run(service.check_permission(request))
    
    if output == 'json':
        click.echo(response.model_dump_json(indent=2))
    elif output == 'yaml':
        click.echo(yaml.dump(response.model_dump(), indent=2))

if __name__ == '__main__':
    cli()
```

**Usage from other languages:**
```bash
# Bash script
#!/bin/bash
result=$(python -m my_tiny_data_collider casefile check-permission \
  --casefile-id cf_abc123 \
  --user-id usr_789 \
  --required-permission read \
  --output json)

has_permission=$(echo "$result" | jq '.payload.has_required_permission')
if [ "$has_permission" = "true" ]; then
  echo "Access granted"
fi
```

```javascript
// Node.js
const { exec } = require('child_process');

exec('python -m my_tiny_data_collider casefile check-permission --casefile-id cf_abc123 --user-id usr_789 --required-permission read --output json', 
  (error, stdout, stderr) => {
    if (error) throw error;
    const response = JSON.parse(stdout);
    console.log('Has permission:', response.payload.has_required_permission);
  }
);
```

**Pros:**
- Language-agnostic (any language can call subprocess)
- Isolated (separate process, crashes don't affect consumer)
- Scriptable (shell scripts, CI/CD pipelines)

**Cons:**
- Slower (process startup ~100ms)
- Serialization overhead (JSON parsing)
- No type safety (consumer doesn't know schema)

---

### HTTP API Pattern (RESTful)

**When:** Distributed systems, multiple consumers, scalability

```python
# api/main.py (not in codebase yet)
from fastapi import FastAPI, Depends, HTTPException
from pydantic_models.operations.casefile_ops import (
    CheckPermissionRequest,
    CheckPermissionResponse
)
from casefileservice.service import CasefileService

app = FastAPI()

@app.post("/api/v1/casefile/check-permission", response_model=CheckPermissionResponse)
async def check_permission_endpoint(
    request: CheckPermissionRequest,
    service: CasefileService = Depends()
) -> CheckPermissionResponse:
    try:
        return await service.check_permission(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Consumer (any language with HTTP client):**
```python
# Python consumer
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/casefile/check-permission",
    json={
        "client_request_id": "check_001",
        "payload": {
            "casefile_id": "cf_abc123",
            "user_id": "usr_789",
            "required_permission": "read"
        }
    }
)

result = response.json()
print(result['payload']['has_required_permission'])
```

```javascript
// JavaScript consumer
const response = await fetch('http://localhost:8000/api/v1/casefile/check-permission', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    client_request_id: 'check_001',
    payload: {
      casefile_id: 'cf_abc123',
      user_id: 'usr_789',
      required_permission: 'read'
    }
  })
});

const result = await response.json();
console.log(result.payload.has_required_permission);
```

```bash
# Curl
curl -X POST http://localhost:8000/api/v1/casefile/check-permission \
  -H "Content-Type: application/json" \
  -d '{
    "client_request_id": "check_001",
    "payload": {
      "casefile_id": "cf_abc123",
      "user_id": "usr_789",
      "required_permission": "read"
    }
  }'
```

**Pros:**
- Language-agnostic (any HTTP client)
- Scalable (horizontal scaling, load balancing)
- Versioned (API v1, v2)
- Cacheable (HTTP caching)

**Cons:**
- Network latency (~10-50ms)
- Server required (deployment, monitoring)
- More complex (authentication, rate limiting)

---

## Part 4: Comparison Table

| Feature | Direct Import (SDK) | CLI (Subprocess) | HTTP API |
|---------|-------------------|------------------|----------|
| **Speed** | ⚡ Fastest (microseconds) | 🐢 Slow (100ms startup) | 🌐 Medium (10-50ms network) |
| **Type Safety** | ✅ Full (Python types, IDE) | ❌ None (strings only) | ⚠️ Partial (OpenAPI schema) |
| **Language** | Python only | Any (subprocess) | Any (HTTP) |
| **Isolation** | Same process | Separate process | Separate machine |
| **Debugging** | ✅ Step through | ❌ Opaque | ⚠️ Logs/traces |
| **Deployment** | `pip install` | Include Python | Server deployment |
| **Versioning** | Package version | CLI version | API version |
| **Use Case** | Python apps, notebooks | Scripts, CI/CD | Web/mobile, distributed |

---

## Part 5: Setup Checklists

### For SDK Usage (Direct Import)

```powershell
# 1. Install package (or add to PYTHONPATH)
pip install -e C:\Users\HP\my-tiny-data-collider
# OR
$env:PYTHONPATH = "C:\Users\HP\my-tiny-data-collider\src"

# 2. Verify imports work
python -c "from casefileservice.service import CasefileService; print('OK')"

# 3. Set API keys (if needed)
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\creds.json"

# 4. Use in code
python your_script.py
```

### For CLI Usage (Subprocess)

```powershell
# 1. Ensure Python on PATH
python --version  # Should print Python 3.11+

# 2. Install CLI (hypothetical)
pip install my-tiny-data-collider[cli]

# 3. Verify CLI works
python -m my_tiny_data_collider --help

# 4. Use in scripts
python -m my_tiny_data_collider casefile check-permission --help
```

### For HTTP API

```powershell
# 1. Install with API dependencies
pip install my-tiny-data-collider[api]

# 2. Configure environment
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\creds.json"
$env:API_HOST = "0.0.0.0"
$env:API_PORT = "8000"

# 3. Run server
uvicorn api.main:app --reload

# 4. Test endpoint
curl http://localhost:8000/api/docs  # Swagger UI
```

---

## Part 6: Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

**Problem:** Trying to import `from src.casefileservice...`

**Solution:** Remove `src.` prefix
```python
# Wrong:
from src.casefileservice.service import CasefileService

# Right:
from casefileservice.service import CasefileService
```

### "ModuleNotFoundError: No module named 'casefileservice'"

**Problem:** `src/` not in Python path

**Solution:** Add to PYTHONPATH or install package
```powershell
# Option A:
$env:PYTHONPATH = "C:\Users\HP\my-tiny-data-collider\src"

# Option B:
pip install -e C:\Users\HP\my-tiny-data-collider
```

### "ImportError: cannot import name 'CasefileService'"

**Problem:** Module found, but class not in module

**Solution:** Check spelling, check if class is exported in `__init__.py`

### "%MY_TOOLSET% not recognized"

**Problem:** Environment variable not set

**Solution:** Set in PowerShell profile or before running script
```powershell
$env:MY_TOOLSET = "C:\Users\HP\my-tiny-toolset\TOOLSET"
```

---

## Summary

**Key concepts:**
1. **Environment variables:** Configure paths, API keys (never commit!)
2. **Import resolution:** `src/` in path → import `casefileservice`, not `src.casefileservice`
3. **SDK:** Fast, type-safe, Python-only
4. **CLI:** Slow, language-agnostic, scriptable
5. **HTTP:** Scalable, distributed, requires server

**Choose based on:**
- **Speed needs:** SDK > HTTP > CLI
- **Language:** Python → SDK | Other → CLI/HTTP
- **Isolation:** Same process → SDK | Separate → CLI/HTTP
- **Scale:** Single user → SDK/CLI | Multiple → HTTP
