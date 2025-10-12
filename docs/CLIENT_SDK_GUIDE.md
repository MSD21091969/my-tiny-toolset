# Client SDK - What It Is and Why You Need It

## What is a Client SDK?

A **Client SDK (Software Development Kit)** is a library/package that makes it **easy for developers to use your API** in their programming language.

Instead of manually making HTTP requests, clients import your SDK and call simple methods with full type safety and autocomplete.

---

## The Problem: Manual HTTP Calls

### Your FastAPI Backend
```python
# Your API endpoint
@app.post("/api/users", response_model=UserResponse)
def create_user(request: UserCreateRequest) -> UserResponse:
    # Create user logic
    return UserResponse(id=1, username=request.username, email=request.email)
```

### Client Without SDK (Pain 😫)

**Python Client:**
```python
import requests

# Manual HTTP call - error prone!
response = requests.post(
    "https://api.example.com/api/users",
    json={
        "username": "john",
        "email": "john@example.com"
    },
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    user_id = data["id"]  # Hope this field exists!
else:
    # Manual error handling
    print(f"Error: {response.status_code}")
```

**JavaScript Client:**
```javascript
// Manual fetch - tedious!
const response = await fetch('https://api.example.com/api/users', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'john',
    email: 'john@example.com'
  })
});

if (!response.ok) {
  throw new Error(`HTTP error! status: ${response.status}`);
}

const data = await response.json();
console.log(data.id);  // No autocomplete, no type checking
```

### Problems Without SDK
- ❌ Must know exact URL structure
- ❌ Must manually build JSON
- ❌ No type checking or autocomplete
- ❌ Manual error handling
- ❌ Easy to make mistakes
- ❌ Hard to maintain when API changes
- ❌ Repeat code for every request

---

## The Solution: Client SDK

### Client With SDK (Easy 🎉)

**Python SDK:**
```python
from your_api_sdk import APIClient

client = APIClient(base_url="https://api.example.com")

# Simple, clean, type-safe!
user = client.users.create(
    username="john",
    email="john@example.com"
)

print(user.id)  # IDE autocomplete works!
print(user.username)  # Type checking works!
```

**TypeScript SDK:**
```typescript
import { APIClient } from 'your-api-sdk';

const client = new APIClient('https://api.example.com');

// Full TypeScript types and autocomplete!
const user = await client.users.create({
  username: "john",
  email: "john@example.com"
});

console.log(user.id);  // TypeScript knows this is a number
```

**C# SDK:**
```csharp
using YourApiSdk;

var client = new APIClient("https://api.example.com");

var user = await client.Users.CreateAsync(new UserCreateRequest
{
    Username = "john",
    Email = "john@example.com"
});

Console.WriteLine(user.Id);  // IntelliSense works!
```

### Benefits of SDK
- ✅ Simple, clean code
- ✅ Type checking and IDE autocomplete
- ✅ Automatic error handling
- ✅ Built-in authentication
- ✅ Retry logic included
- ✅ Matches your API models exactly
- ✅ Updates automatically when API changes

---

## SDK Examples for Different Languages

### Python SDK Structure
```python
# Auto-generated from your version_analysis.json

from dataclasses import dataclass
from typing import Optional
import requests

@dataclass
class UserCreateRequest:
    username: str
    email: str

@dataclass
class UserResponse:
    id: int
    username: str
    email: str
    created_at: str

class UsersAPI:
    def __init__(self, client):
        self._client = client
    
    def create(self, username: str, email: str) -> UserResponse:
        """Create a new user"""
        response = self._client._request(
            "POST",
            "/api/users",
            json={"username": username, "email": email}
        )
        return UserResponse(**response)
    
    def get(self, user_id: int) -> UserResponse:
        """Get user by ID"""
        response = self._client._request("GET", f"/api/users/{user_id}")
        return UserResponse(**response)
    
    def update(self, user_id: int, email: Optional[str] = None) -> UserResponse:
        """Update user"""
        data = {}
        if email:
            data["email"] = email
        response = self._client._request("PUT", f"/api/users/{user_id}", json=data)
        return UserResponse(**response)

class APIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.users = UsersAPI(self)
    
    def _request(self, method: str, path: str, **kwargs):
        headers = kwargs.pop("headers", {})
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

# Usage:
# client = APIClient("https://api.example.com", api_key="secret")
# user = client.users.create(username="john", email="john@example.com")
```

### TypeScript SDK Structure
```typescript
// Auto-generated from your version_analysis.json

export interface UserCreateRequest {
  username: string;
  email: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export class UsersAPI {
  constructor(private client: APIClient) {}

  async create(request: UserCreateRequest): Promise<UserResponse> {
    return this.client.request<UserResponse>('POST', '/api/users', request);
  }

  async get(userId: number): Promise<UserResponse> {
    return this.client.request<UserResponse>('GET', `/api/users/${userId}`);
  }

  async update(userId: number, email?: string): Promise<UserResponse> {
    return this.client.request<UserResponse>('PUT', `/api/users/${userId}`, { email });
  }
}

export class APIClient {
  users: UsersAPI;

  constructor(
    private baseUrl: string,
    private apiKey?: string
  ) {
    this.users = new UsersAPI(this);
  }

  async request<T>(method: string, path: string, body?: any): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}

// Usage:
// const client = new APIClient('https://api.example.com', 'secret');
// const user = await client.users.create({ username: 'john', email: 'john@example.com' });
```

### Go SDK Structure
```go
// Auto-generated from your version_analysis.json

package sdk

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type UserCreateRequest struct {
    Username string `json:"username"`
    Email    string `json:"email"`
}

type UserResponse struct {
    ID        int    `json:"id"`
    Username  string `json:"username"`
    Email     string `json:"email"`
    CreatedAt string `json:"created_at"`
}

type UsersAPI struct {
    client *APIClient
}

func (u *UsersAPI) Create(req *UserCreateRequest) (*UserResponse, error) {
    var resp UserResponse
    err := u.client.request("POST", "/api/users", req, &resp)
    return &resp, err
}

func (u *UsersAPI) Get(userID int) (*UserResponse, error) {
    var resp UserResponse
    err := u.client.request("GET", fmt.Sprintf("/api/users/%d", userID), nil, &resp)
    return &resp, err
}

type APIClient struct {
    BaseURL string
    APIKey  string
    Users   *UsersAPI
}

func NewClient(baseURL, apiKey string) *APIClient {
    client := &APIClient{
        BaseURL: baseURL,
        APIKey:  apiKey,
    }
    client.Users = &UsersAPI{client: client}
    return client
}

func (c *APIClient) request(method, path string, body, result interface{}) error {
    var reqBody *bytes.Buffer
    if body != nil {
        jsonData, _ := json.Marshal(body)
        reqBody = bytes.NewBuffer(jsonData)
    }

    req, _ := http.NewRequest(method, c.BaseURL+path, reqBody)
    req.Header.Set("Content-Type", "application/json")
    if c.APIKey != "" {
        req.Header.Set("Authorization", "Bearer "+c.APIKey)
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    return json.NewDecoder(resp.Body).Decode(result)
}

// Usage:
// client := sdk.NewClient("https://api.example.com", "secret")
// user, err := client.Users.Create(&sdk.UserCreateRequest{
//     Username: "john",
//     Email:    "john@example.com",
// })
```

---

## How SDKs Are Generated

### Step 1: Analyze Your API
```powershell
# Generate version_analysis.json
python tools\version_tracker.py . --version 1.0.0 --json --yaml
```

### Step 2: SDK Generator Reads version_analysis.json
```json
{
  "models": [
    {
      "name": "UserCreateRequest",
      "fields": [
        {"name": "username", "type": "str", "required": true},
        {"name": "email", "type": "str", "required": true}
      ]
    }
  ],
  "endpoints": [
    {
      "path": "/api/users",
      "method": "POST",
      "request_model": "UserCreateRequest",
      "response_model": "UserResponse"
    }
  ]
}
```

### Step 3: Generate SDK Code

**For Python:**
```python
# Generator creates:
class UserCreateRequest:
    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

class UsersAPI:
    def create(self, username: str, email: str) -> UserResponse:
        # HTTP POST logic
```

**For TypeScript:**
```typescript
// Generator creates:
interface UserCreateRequest {
  username: string;
  email: string;
}

class UsersAPI {
  async create(request: UserCreateRequest): Promise<UserResponse> {
    // HTTP POST logic
  }
}
```

---

## SDK vs Manual HTTP Calls Comparison

| Aspect | Manual HTTP | With SDK |
|--------|-------------|----------|
| **Code complexity** | High | Low |
| **Type safety** | None | Full |
| **IDE autocomplete** | No | Yes |
| **Error handling** | Manual | Built-in |
| **Authentication** | Manual | Built-in |
| **Retries** | Manual | Built-in |
| **Timeout handling** | Manual | Built-in |
| **Request validation** | Manual | Automatic |
| **Response parsing** | Manual | Automatic |
| **Maintenance** | Manual updates | Auto-generated |
| **Documentation** | Separate | Built-in (docstrings) |
| **Testing** | Manual mocks | Mock support |

---

## Real-World SDK Examples

### Stripe SDK
```python
# Without SDK
requests.post(
    "https://api.stripe.com/v1/charges",
    auth=("sk_test_...", ""),
    data={"amount": 1000, "currency": "usd"}
)

# With Stripe SDK
import stripe
stripe.Charge.create(amount=1000, currency="usd")
```

### Twilio SDK
```python
# Without SDK
requests.post(
    "https://api.twilio.com/2010-04-01/Accounts/.../Messages.json",
    auth=("AC...", "token"),
    data={"To": "+1234567890", "From": "+0987654321", "Body": "Hello"}
)

# With Twilio SDK
from twilio.rest import Client
client = Client("account_sid", "auth_token")
client.messages.create(to="+1234567890", from_="+0987654321", body="Hello")
```

### AWS SDK
```python
# Without SDK - complex authentication, signing, etc.
# (100+ lines of code)

# With AWS SDK
import boto3
s3 = boto3.client('s3')
s3.upload_file('file.txt', 'my-bucket', 'file.txt')
```

---

## Tools for Generating SDKs

### 1. OpenAPI Generator
```bash
# Convert version_analysis.json to OpenAPI spec
# Then generate SDKs:

openapi-generator-cli generate \
  -i openapi.json \
  -g python \
  -o python-sdk/

openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-fetch \
  -o typescript-sdk/
```

Supports: Python, TypeScript, Go, Java, C#, Ruby, PHP, Rust, Kotlin, Swift, and 50+ more!

### 2. Swagger Codegen
```bash
swagger-codegen generate \
  -i openapi.json \
  -l python \
  -o python-sdk/
```

### 3. Custom Generator (Example)
```python
import json

def generate_python_sdk(version_analysis_file):
    with open(version_analysis_file) as f:
        data = json.load(f)
    
    # Generate model classes
    for model in data['models']:
        class_code = f"class {model['name']}:\n"
        class_code += f"    def __init__(self"
        for field in model['fields']:
            class_code += f", {field['name']}: {map_type(field['type'])}"
        class_code += "):\n"
        for field in model['fields']:
            class_code += f"        self.{field['name']} = {field['name']}\n"
        
        print(class_code)
    
    # Generate API client
    # ... similar logic for endpoints

def map_type(python_type):
    """Map Python type to target language type"""
    type_map = {
        "str": "str",
        "int": "int",
        "Optional[int]": "Optional[int]"
    }
    return type_map.get(python_type, "Any")
```

---

## Why Use version_analysis.json for SDK Generation?

### Benefits

1. **Always in Sync**
   - SDK matches API exactly
   - No manual updates needed

2. **Multi-Language Support**
   - Generate Python, TypeScript, Go, C# from same source
   - Consistent API across languages

3. **Type Safety**
   - Models have correct types in each language
   - Catch errors at compile time

4. **Versioning**
   - SDK v1.0.0 matches API v1.0.0
   - Easy to maintain multiple versions

5. **Automatic Updates**
   - Change API → Regenerate SDK
   - CI/CD can automate this

### Workflow

```
1. Update FastAPI code
2. Run version_tracker.py → version_analysis.json
3. Run SDK generator → python-sdk/, typescript-sdk/, etc.
4. Publish SDKs to package managers (PyPI, npm, etc.)
5. Clients install updated SDK
```

---

## Complete Example: From API to SDK

### Your FastAPI
```python
class UserCreateRequest(BaseModel):
    username: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

@app.post("/api/users", response_model=UserResponse)
def create_user(request: UserCreateRequest):
    # ... logic
    return UserResponse(...)
```

### Generate Analysis
```powershell
python tools\version_tracker.py . --version 1.0.0 --json
# Creates: version_analysis/version_analysis.json
```

### Generate Python SDK
```python
# Auto-generated
class UserCreateRequest:
    def __init__(self, username: str, email: str, age: Optional[int] = None):
        self.username = username
        self.email = email
        self.age = age

client = APIClient("https://api.com")
user = client.users.create(username="john", email="john@example.com")
```

### Client Uses SDK
```python
# Client code - simple!
from your_api_sdk import APIClient

client = APIClient("https://api.example.com", api_key="secret")
user = client.users.create(username="john", email="john@example.com", age=30)
print(f"Created user {user.id}")
```

---

## Summary

**Client SDK** = Library that wraps your API for easy use in any language

**Key Points:**
- ✅ Makes API easy to use
- ✅ Type-safe and autocomplete-friendly
- ✅ Handles errors, auth, retries automatically
- ✅ Generated from `version_analysis.json`
- ✅ Multi-language support
- ✅ Always in sync with API

**Popular SDKs:**
- Stripe (payment processing)
- Twilio (SMS/voice)
- AWS (cloud services)
- GitHub (Octokit)
- Slack
- SendGrid

**Bottom line:** SDKs make your API developer-friendly and increase adoption! 🚀
