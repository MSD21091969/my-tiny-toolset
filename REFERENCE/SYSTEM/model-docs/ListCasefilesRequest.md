# ListCasefilesRequest

**Package:** `pydantic_models.operations`

Request to list casefiles.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID |  | Unique request identifier |
| `session_id` | Optional |  | Optional session identifier |
| `user_id` | str | ✓ | User making the request |
| `operation` | Literal |  | - |
| `payload` | ListCasefilesPayload | ✓ | Request payload |
| `timestamp` | str |  | Request timestamp |
| `metadata` | Dict |  | Additional metadata for the request |
| `context_requirements` | List |  | Optional context requirements for RequestHub (e.g., ['mds_context', 'casefile']). |
| `hooks` | List |  | Optional list of hook identifiers RequestHub should execute for this request. |
| `policy_hints` | Dict |  | Optional policy hints that pattern loaders can use to customize orchestration. |
| `route_directives` | Dict |  | Optional route-level directives (e.g., {'emit_metrics': True}). |

## Field Details

### `request_id`

**Constraints:**
- format: uuid

**Default:** `PydanticUndefined`

### `operation`

**Default:** `list_casefiles`

### `timestamp`

**Default:** `PydanticUndefined`

### `metadata`

**Default:** `PydanticUndefined`

### `context_requirements`

**Default:** `PydanticUndefined`

### `hooks`

**Default:** `PydanticUndefined`

### `policy_hints`

**Default:** `PydanticUndefined`

### `route_directives`

**Default:** `PydanticUndefined`

---

## JSON Schema

```json
{
  "$defs": {
    "ListCasefilesPayload": {
      "description": "Payload for listing casefiles with filters.",
      "properties": {
        "user_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Filter by user ID (owner)",
          "example": "user@example.com",
          "title": "User Id"
        },
        "tags": {
          "anyOf": [
            {
              "description": "List of tags for categorization",
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Filter by tags (any match)",
          "example": [
            "incident",
            "email"
          ],
          "title": "Tags"
        },
        "search_query": {
          "anyOf": [
            {
              "maxLength": 500,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Search in title/description",
          "example": "investigation",
          "title": "Search Query"
        },
        "limit": {
          "default": 50,
          "description": "Maximum results to return",
          "example": 50,
          "exclusiveMinimum": 0,
          "maximum": 100,
          "title": "Limit",
          "type": "integer"
        },
        "offset": {
          "default": 0,
          "description": "Offset for pagination",
          "example": 0,
          "minimum": 0,
          "title": "Offset",
          "type": "integer"
        }
      },
      "title": "ListCasefilesPayload",
      "type": "object"
    }
  },
  "description": "Request to list casefiles.",
  "properties": {
    "request_id": {
      "description": "Unique request identifier",
      "format": "uuid",
      "title": "Request Id",
      "type": "string"
    },
    "session_id": {
      "anyOf": [
        {
          "description": "Session ID (tool or chat) in format ts_XXX or cs_XXX",
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Optional session identifier",
      "title": "Session Id"
    },
    "user_id": {
      "description": "User making the request",
      "title": "User Id",
      "type": "string"
    },
    "operation": {
      "const": "list_casefiles",
      "default": "list_casefiles",
      "title": "Operation",
      "type": "string"
    },
    "payload": {
      "$ref": "#/$defs/ListCasefilesPayload",
      "description": "Request payload"
    },
    "timestamp": {
      "description": "Request timestamp",
      "title": "Timestamp",
      "type": "string"
    },
    "metadata": {
      "additionalProperties": true,
      "description": "Additional metadata for the request",
      "title": "Metadata",
      "type": "object"
    },
    "context_requirements": {
      "description": "Optional context requirements for RequestHub (e.g., ['mds_context', 'casefile']).",
      "items": {
        "type": "string"
      },
      "title": "Context Requirements",
      "type": "array"
    },
    "hooks": {
      "description": "Optional list of hook identifiers RequestHub should execute for this request.",
      "items": {
        "type": "string"
      },
      "title": "Hooks",
      "type": "array"
    },
    "policy_hints": {
      "additionalProperties": true,
      "description": "Optional policy hints that pattern loaders can use to customize orchestration.",
      "title": "Policy Hints",
      "type": "object"
    },
    "route_directives": {
      "additionalProperties": true,
      "description": "Optional route-level directives (e.g., {'emit_metrics': True}).",
      "title": "Route Directives",
      "type": "object"
    }
  },
  "required": [
    "user_id",
    "payload"
  ],
  "title": "ListCasefilesRequest",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
