# GetChatSessionResponse

**Package:** `pydantic_models.operations`

Response with chat session details.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID | ✓ | ID of the originating request |
| `status` | RequestStatus | ✓ | Request processing status |
| `payload` | ChatSessionDataPayload | ✓ | Response payload |
| `timestamp` | str |  | Response timestamp |
| `error` | Optional |  | Error message if status is FAILED |
| `metadata` | Dict |  | Additional metadata for the response |

## Field Details

### `request_id`

**Constraints:**
- format: uuid

### `timestamp`

**Default:** `PydanticUndefined`

### `metadata`

**Default:** `PydanticUndefined`

---

## JSON Schema

```json
{
  "$defs": {
    "ChatSessionDataPayload": {
      "description": "Response payload with full chat session data.",
      "properties": {
        "session_id": {
          "description": "Session ID",
          "examples": [
            "cs_251013_chat001"
          ],
          "title": "Session Id",
          "type": "string"
        },
        "user_id": {
          "description": "User who owns the session",
          "examples": [
            "user@example.com",
            "admin@company.org"
          ],
          "title": "User Id",
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
          "description": "Associated casefile ID",
          "examples": [
            "cf_251013_abc123"
          ],
          "title": "Casefile Id"
        },
        "created_at": {
          "description": "Creation timestamp",
          "examples": [
            "2025-10-13T14:30:00Z"
          ],
          "title": "Created At",
          "type": "string"
        },
        "updated_at": {
          "description": "Last update timestamp",
          "examples": [
            "2025-10-13T15:45:00Z"
          ],
          "title": "Updated At",
          "type": "string"
        },
        "active": {
          "description": "Whether session is active",
          "examples": [
            true,
            false
          ],
          "title": "Active",
          "type": "boolean"
        },
        "message_count": {
          "default": 0,
          "description": "Number of messages in session",
          "examples": [
            0,
            15,
            42
          ],
          "minimum": 0,
          "title": "Message Count",
          "type": "integer"
        },
        "event_count": {
          "default": 0,
          "description": "Total events in session",
          "examples": [
            0,
            8,
            23
          ],
          "minimum": 0,
          "title": "Event Count",
          "type": "integer"
        },
        "messages": {
          "description": "Message history if requested",
          "items": {
            "additionalProperties": true,
            "type": "object"
          },
          "title": "Messages",
          "type": "array"
        },
        "metadata": {
          "additionalProperties": true,
          "description": "Additional session metadata",
          "title": "Metadata",
          "type": "object"
        }
      },
      "required": [
        "session_id",
        "user_id",
        "created_at",
        "updated_at",
        "active"
      ],
      "title": "ChatSessionDataPayload",
      "type": "object"
    },
    "RequestStatus": {
      "description": "Status of a request.",
      "enum": [
        "pending",
        "processing",
        "completed",
        "failed"
      ],
      "title": "RequestStatus",
      "type": "string"
    }
  },
  "description": "Response with chat session details.",
  "properties": {
    "request_id": {
      "description": "ID of the originating request",
      "format": "uuid",
      "title": "Request Id",
      "type": "string"
    },
    "status": {
      "$ref": "#/$defs/RequestStatus",
      "description": "Request processing status"
    },
    "payload": {
      "$ref": "#/$defs/ChatSessionDataPayload",
      "description": "Response payload"
    },
    "timestamp": {
      "description": "Response timestamp",
      "title": "Timestamp",
      "type": "string"
    },
    "error": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Error message if status is FAILED",
      "title": "Error"
    },
    "metadata": {
      "additionalProperties": true,
      "description": "Additional metadata for the response",
      "title": "Metadata",
      "type": "object"
    }
  },
  "required": [
    "request_id",
    "status",
    "payload"
  ],
  "title": "GetChatSessionResponse",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
