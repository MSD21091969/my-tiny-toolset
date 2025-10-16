# ToolEvent

**Package:** `pydantic_models.canonical`

Record of a tool execution within a session.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | str |  | - |
| `event_type` | str | ✓ | Type of event: tool_request_received, tool_execution_started, tool_execution_completed, tool_execution_failed, tool_response_sent |
| `tool_name` | str | ✓ | Name of the tool executed |
| `timestamp` | str |  | Event timestamp (ISO 8601) |
| `parameters` | Dict |  | Tool execution parameters |
| `result_summary` | Optional |  | Summary of execution result |
| `duration_ms` | Optional |  | Execution duration in milliseconds |
| `status` | Optional |  | Event status: success, error, pending |
| `error_message` | Optional |  | Error message if status is error |
| `initiator` | str |  | Who/what initiated this tool execution |
| `chain_position` | Optional |  | Position in execution chain |
| `chain_id` | Optional |  | Unique identifier for a chain of tool executions |
| `reasoning` | Optional |  | Agent reasoning for this execution |
| `source_message_id` | Optional |  | Source message ID if applicable |
| `related_events` | List |  | Related event IDs |

## Field Details

### `event_id`

**Default:** `PydanticUndefined`

### `timestamp`

**Default:** `PydanticUndefined`

### `parameters`

**Default:** `PydanticUndefined`

### `initiator`

**Default:** `user`

### `chain_id`

**Default:** `PydanticUndefined`

### `related_events`

**Default:** `PydanticUndefined`

---

## JSON Schema

```json
{
  "description": "Record of a tool execution within a session.",
  "properties": {
    "event_id": {
      "example": "evt_abc123",
      "title": "Event Id",
      "type": "string"
    },
    "event_type": {
      "description": "Type of event: tool_request_received, tool_execution_started, tool_execution_completed, tool_execution_failed, tool_response_sent",
      "example": "tool_execution_completed",
      "title": "Event Type",
      "type": "string"
    },
    "tool_name": {
      "description": "Name of the tool executed",
      "example": "create_casefile_tool",
      "title": "Tool Name",
      "type": "string"
    },
    "timestamp": {
      "description": "Event timestamp (ISO 8601)",
      "example": "2025-10-13T12:00:00",
      "title": "Timestamp",
      "type": "string"
    },
    "parameters": {
      "additionalProperties": true,
      "description": "Tool execution parameters",
      "example": {
        "title": "Test Casefile"
      },
      "title": "Parameters",
      "type": "object"
    },
    "result_summary": {
      "anyOf": [
        {
          "additionalProperties": true,
          "type": "object"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Summary of execution result",
      "example": {
        "casefile_id": "cf_251013_abc123"
      },
      "title": "Result Summary"
    },
    "duration_ms": {
      "anyOf": [
        {
          "description": "Non-negative integer (greater than or equal to 0)",
          "minimum": 0,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Execution duration in milliseconds",
      "example": 250,
      "title": "Duration Ms"
    },
    "status": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Event status: success, error, pending",
      "example": "success",
      "title": "Status"
    },
    "error_message": {
      "anyOf": [
        {
          "maxLength": 2000,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Error message if status is error",
      "title": "Error Message"
    },
    "initiator": {
      "default": "user",
      "description": "Who/what initiated this tool execution",
      "example": "user",
      "title": "Initiator",
      "type": "string"
    },
    "chain_position": {
      "anyOf": [
        {
          "description": "Non-negative integer (greater than or equal to 0)",
          "minimum": 0,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Position in execution chain",
      "example": 1,
      "title": "Chain Position"
    },
    "chain_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "description": "Unique identifier for a chain of tool executions",
      "example": "chain_abc123",
      "title": "Chain Id"
    },
    "reasoning": {
      "anyOf": [
        {
          "maxLength": 2000,
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Agent reasoning for this execution",
      "title": "Reasoning"
    },
    "source_message_id": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Source message ID if applicable",
      "title": "Source Message Id"
    },
    "related_events": {
      "description": "Related event IDs",
      "items": {
        "type": "string"
      },
      "title": "Related Events",
      "type": "array"
    }
  },
  "required": [
    "event_type",
    "tool_name"
  ],
  "title": "ToolEvent",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
