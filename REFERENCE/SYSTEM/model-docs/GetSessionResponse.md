# GetSessionResponse

**Package:** `pydantic_models.operations`

Response with session details.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID | ✓ | ID of the originating request |
| `status` | RequestStatus | ✓ | Request processing status |
| `payload` | SessionDataPayload | ✓ | Response payload |
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
    },
    "SessionDataPayload": {
      "description": "Response payload with full session data.",
      "properties": {
        "session_id": {
          "description": "Session ID",
          "examples": [
            "ts_251013_tool001"
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
          "description": "Associated casefile ID",
          "examples": [
            "cf_251013_abc123"
          ],
          "title": "Casefile Id",
          "type": "string"
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
          "description": "Session title",
          "examples": [
            "Data Analysis Session"
          ],
          "title": "Title"
        },
        "request_count": {
          "default": 0,
          "description": "Number of tool requests in session",
          "examples": [
            0,
            5,
            12
          ],
          "minimum": 0,
          "title": "Request Count",
          "type": "integer"
        },
        "event_count": {
          "default": 0,
          "description": "Total events across all requests",
          "examples": [
            0,
            15,
            48
          ],
          "minimum": 0,
          "title": "Event Count",
          "type": "integer"
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
        "casefile_id",
        "created_at",
        "updated_at",
        "active"
      ],
      "title": "SessionDataPayload",
      "type": "object"
    }
  },
  "description": "Response with session details.",
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
      "$ref": "#/$defs/SessionDataPayload",
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
  "title": "GetSessionResponse",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
