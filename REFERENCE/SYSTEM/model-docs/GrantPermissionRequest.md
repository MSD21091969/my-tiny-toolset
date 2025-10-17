# GrantPermissionRequest

**Package:** `pydantic_models.operations`

Request to grant permission to a user.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID |  | Unique request identifier |
| `session_id` | Optional |  | Optional session identifier |
| `user_id` | str | ✓ | User making the request |
| `operation` | Literal |  | - |
| `payload` | GrantPermissionPayload | ✓ | Request payload |
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

**Default:** `grant_permission`

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
    "GrantPermissionPayload": {
      "description": "Payload for granting permission to a user.",
      "properties": {
        "casefile_id": {
          "description": "Casefile ID",
          "title": "Casefile Id",
          "type": "string"
        },
        "target_user_id": {
          "description": "User to grant permission to",
          "title": "Target User Id",
          "type": "string"
        },
        "permission": {
          "$ref": "#/$defs/PermissionLevel",
          "description": "Permission level to grant"
        },
        "expires_at": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Optional expiration timestamp",
          "title": "Expires At"
        },
        "notes": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Optional notes",
          "title": "Notes"
        }
      },
      "required": [
        "casefile_id",
        "target_user_id",
        "permission"
      ],
      "title": "GrantPermissionPayload",
      "type": "object"
    },
    "PermissionLevel": {
      "description": "Permission levels for casefile access.",
      "enum": [
        "owner",
        "admin",
        "editor",
        "viewer",
        "none"
      ],
      "title": "PermissionLevel",
      "type": "string"
    }
  },
  "description": "Request to grant permission to a user.",
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
      "const": "grant_permission",
      "default": "grant_permission",
      "title": "Operation",
      "type": "string"
    },
    "payload": {
      "$ref": "#/$defs/GrantPermissionPayload",
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
  "title": "GrantPermissionRequest",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
