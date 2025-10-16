# UpdateCasefileRequest

**Package:** `pydantic_models.operations`

Request to update a casefile.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID |  | Unique request identifier |
| `session_id` | Optional |  | Optional session identifier |
| `user_id` | str | ✓ | User making the request |
| `operation` | Literal |  | - |
| `payload` | UpdateCasefilePayload | ✓ | Request payload |
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

**Default:** `update_casefile`

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
    "UpdateCasefilePayload": {
      "description": "Payload for updating a casefile.\n\nSECURITY: Uses explicit fields instead of Dict[str, Any] to prevent injection.\nAll fields are optional - only provided fields will be updated.",
      "properties": {
        "casefile_id": {
          "description": "Casefile ID to update",
          "example": "cf_251013_abc123",
          "title": "Casefile Id",
          "type": "string"
        },
        "title": {
          "anyOf": [
            {
              "description": "Short string (1-200 characters)",
              "maxLength": 200,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "New title",
          "example": "Updated Investigation Case",
          "title": "Title"
        },
        "description": {
          "anyOf": [
            {
              "description": "Medium string (1-2000 characters)",
              "maxLength": 2000,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "New description",
          "example": "Updated description with new findings",
          "title": "Description"
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
          "description": "New tags (replaces existing)",
          "example": [
            "incident",
            "email",
            "resolved"
          ],
          "title": "Tags"
        },
        "notes": {
          "anyOf": [
            {
              "description": "Long string (1-5000 characters)",
              "maxLength": 5000,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "New notes",
          "example": "Additional investigation notes",
          "title": "Notes"
        }
      },
      "required": [
        "casefile_id"
      ],
      "title": "UpdateCasefilePayload",
      "type": "object"
    }
  },
  "description": "Request to update a casefile.",
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
      "const": "update_casefile",
      "default": "update_casefile",
      "title": "Operation",
      "type": "string"
    },
    "payload": {
      "$ref": "#/$defs/UpdateCasefilePayload",
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
  "title": "UpdateCasefileRequest",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
