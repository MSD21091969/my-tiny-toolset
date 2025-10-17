# StoreGmailMessagesRequest

**Package:** `pydantic_models.operations`

Request to store Gmail messages in casefile.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID |  | Unique request identifier |
| `session_id` | Optional |  | Optional session identifier |
| `user_id` | str | ✓ | User making the request |
| `operation` | Literal |  | - |
| `payload` | StoreGmailMessagesPayload | ✓ | Request payload |
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

**Default:** `store_gmail_messages`

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
    "StoreGmailMessagesPayload": {
      "description": "Payload for storing Gmail messages in casefile.",
      "properties": {
        "casefile_id": {
          "description": "Casefile ID",
          "title": "Casefile Id",
          "type": "string"
        },
        "messages": {
          "description": "Gmail messages (GmailMessage dicts)",
          "items": {
            "additionalProperties": true,
            "type": "object"
          },
          "title": "Messages",
          "type": "array"
        },
        "sync_token": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Incremental sync token from Gmail API",
          "title": "Sync Token"
        },
        "overwrite": {
          "default": false,
          "description": "Replace existing cache instead of merging",
          "title": "Overwrite",
          "type": "boolean"
        },
        "threads": {
          "anyOf": [
            {
              "items": {
                "additionalProperties": true,
                "type": "object"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Gmail thread metadata",
          "title": "Threads"
        },
        "labels": {
          "anyOf": [
            {
              "items": {
                "additionalProperties": true,
                "type": "object"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Gmail label metadata",
          "title": "Labels"
        }
      },
      "required": [
        "casefile_id",
        "messages"
      ],
      "title": "StoreGmailMessagesPayload",
      "type": "object"
    }
  },
  "description": "Request to store Gmail messages in casefile.",
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
      "const": "store_gmail_messages",
      "default": "store_gmail_messages",
      "title": "Operation",
      "type": "string"
    },
    "payload": {
      "$ref": "#/$defs/StoreGmailMessagesPayload",
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
  "title": "StoreGmailMessagesRequest",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
