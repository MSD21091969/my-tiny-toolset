# ChatResponse

**Package:** `pydantic_models.operations`

Response to a chat message.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID | ✓ | ID of the originating request |
| `status` | RequestStatus | ✓ | Request processing status |
| `payload` | ChatResultPayload | ✓ | Response payload |
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
    "ChatMessagePayload": {
      "description": "Canonical chat message structure (data entity, not request payload).",
      "properties": {
        "content": {
          "description": "Message content",
          "examples": [
            "Hello, how can I help you?",
            "I found 5 messages matching your query."
          ],
          "title": "Content",
          "type": "string"
        },
        "message_type": {
          "$ref": "#/$defs/MessageType",
          "description": "Type of message",
          "examples": [
            "user",
            "assistant",
            "tool",
            "system"
          ]
        },
        "tool_calls": {
          "description": "Tool calls in this message",
          "examples": [
            [
              {
                "parameters": {
                  "title": "New Case"
                },
                "tool": "create_casefile_tool"
              }
            ]
          ],
          "items": {
            "additionalProperties": true,
            "type": "object"
          },
          "title": "Tool Calls",
          "type": "array"
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
          "description": "Client-provided session request ID",
          "examples": [
            "req_001"
          ],
          "title": "Session Request Id"
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
        }
      },
      "required": [
        "content",
        "message_type"
      ],
      "title": "ChatMessagePayload",
      "type": "object"
    },
    "ChatResultPayload": {
      "description": "Payload for chat message response (operation result).",
      "properties": {
        "message": {
          "$ref": "#/$defs/ChatMessagePayload",
          "description": "Assistant's response message"
        },
        "related_messages": {
          "description": "Related messages in conversation",
          "items": {
            "$ref": "#/$defs/ChatMessagePayload"
          },
          "title": "Related Messages",
          "type": "array"
        },
        "events": {
          "description": "Events generated during processing",
          "examples": [
            [
              {
                "event_type": "chat_message_processed",
                "timestamp": "2025-10-13T14:30:00Z"
              }
            ]
          ],
          "items": {
            "additionalProperties": true,
            "type": "object"
          },
          "title": "Events",
          "type": "array"
        }
      },
      "required": [
        "message"
      ],
      "title": "ChatResultPayload",
      "type": "object"
    },
    "MessageType": {
      "description": "Types of chat messages.",
      "enum": [
        "user",
        "assistant",
        "system",
        "tool",
        "error"
      ],
      "title": "MessageType",
      "type": "string"
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
  "description": "Response to a chat message.",
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
      "$ref": "#/$defs/ChatResultPayload",
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
  "title": "ChatResponse",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
