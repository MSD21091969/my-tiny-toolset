# ChatRequest

**Package:** `pydantic_models.operations`

Request to send a chat message.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID |  | Unique request identifier |
| `session_id` | Optional |  | Optional session identifier |
| `user_id` | str | ✓ | User making the request |
| `operation` | Literal |  | - |
| `payload` | ChatRequestPayload | ✓ | Request payload |
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

**Default:** `chat`

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
    "ChatRequestPayload": {
      "description": "Payload for chat message request (operation parameters).",
      "properties": {
        "message": {
          "description": "User message content",
          "examples": [
            "Find all emails from last week",
            "Create a casefile for the Smith investigation"
          ],
          "title": "Message",
          "type": "string"
        },
        "session_id": {
          "description": "Chat session ID",
          "examples": [
            "cs_251013_chat001",
            "cs_250920_conv456"
          ],
          "title": "Session Id",
          "type": "string"
        },
        "casefile_id": {
          "anyOf": [
            {
              "description": "Casefile ID in format cf_YYMMDD_code",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Optional casefile context",
          "examples": [
            "cf_251013_abc123"
          ],
          "title": "Casefile Id"
        },
        "session_request_id": {
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
          "description": "Client-provided session request ID for tracking",
          "examples": [
            "req_001"
          ],
          "title": "Session Request Id"
        }
      },
      "required": [
        "message",
        "session_id"
      ],
      "title": "ChatRequestPayload",
      "type": "object"
    }
  },
  "description": "Request to send a chat message.",
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
      "const": "chat",
      "default": "chat",
      "title": "Operation",
      "type": "string"
    },
    "payload": {
      "$ref": "#/$defs/ChatRequestPayload",
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
  "title": "ChatRequest",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
