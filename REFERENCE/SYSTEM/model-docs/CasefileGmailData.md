# CasefileGmailData

**Package:** `pydantic_models.workspace`

Typed Gmail data stored on a casefile.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | List |  | Messages stored on the casefile |
| `threads` | List |  | Thread metadata |
| `labels` | List |  | Cached Gmail labels |
| `last_sync_token` | Optional |  | Token for incremental sync operations |
| `synced_at` | Optional |  | Timestamp of the most recent successful sync |
| `sync_status` | str |  | Current sync status (idle|syncing|error) |
| `error_message` | Optional |  | Last sync error message, if any |

## Field Details

### `messages`

**Default:** `PydanticUndefined`

### `threads`

**Default:** `PydanticUndefined`

### `labels`

**Default:** `PydanticUndefined`

### `sync_status`

**Default:** `idle`

---

## JSON Schema

```json
{
  "$defs": {
    "GmailAttachment": {
      "description": "Metadata describing a Gmail attachment.",
      "properties": {
        "filename": {
          "description": "Attachment filename",
          "example": "document.pdf",
          "minLength": 1,
          "title": "Filename",
          "type": "string"
        },
        "mime_type": {
          "description": "Attachment MIME type",
          "example": "application/pdf",
          "title": "Mime Type",
          "type": "string"
        },
        "size_bytes": {
          "description": "Attachment size in bytes",
          "example": 1024000,
          "minimum": 0,
          "title": "Size Bytes",
          "type": "integer"
        },
        "attachment_id": {
          "description": "Gmail attachment identifier",
          "example": "ANGjdJ8w...",
          "title": "Attachment Id",
          "type": "string"
        }
      },
      "required": [
        "filename",
        "mime_type",
        "size_bytes",
        "attachment_id"
      ],
      "title": "GmailAttachment",
      "type": "object"
    },
    "GmailLabel": {
      "description": "Representation of a Gmail label.",
      "properties": {
        "id": {
          "description": "Label identifier",
          "title": "Id",
          "type": "string"
        },
        "name": {
          "description": "Label name",
          "title": "Name",
          "type": "string"
        },
        "label_type": {
          "default": "user",
          "description": "Label type (system or user)",
          "title": "Label Type",
          "type": "string"
        },
        "message_visibility": {
          "default": "show",
          "description": "Whether messages with the label are shown in list views",
          "title": "Message Visibility",
          "type": "string"
        }
      },
      "required": [
        "id",
        "name"
      ],
      "title": "GmailLabel",
      "type": "object"
    },
    "GmailMessage": {
      "description": "Envelope + payload for a Gmail message.",
      "properties": {
        "id": {
          "description": "Gmail message ID",
          "example": "17a1b2c3d4e5f6",
          "title": "Id",
          "type": "string"
        },
        "thread_id": {
          "description": "Thread ID for the message",
          "example": "17a1b2c3d4e5f6",
          "title": "Thread Id",
          "type": "string"
        },
        "subject": {
          "default": "",
          "description": "Message subject",
          "example": "Important: Project Update",
          "maxLength": 1000,
          "title": "Subject",
          "type": "string"
        },
        "sender": {
          "description": "From email address",
          "example": "sender@example.com",
          "title": "Sender",
          "type": "string"
        },
        "to_recipients": {
          "description": "Primary recipient email addresses",
          "example": [
            "recipient1@example.com",
            "recipient2@example.com"
          ],
          "items": {
            "format": "email",
            "type": "string"
          },
          "title": "To Recipients",
          "type": "array"
        },
        "cc_recipients": {
          "description": "CC recipient email addresses",
          "items": {
            "format": "email",
            "type": "string"
          },
          "title": "Cc Recipients",
          "type": "array"
        },
        "bcc_recipients": {
          "description": "BCC recipient email addresses",
          "items": {
            "format": "email",
            "type": "string"
          },
          "title": "Bcc Recipients",
          "type": "array"
        },
        "snippet": {
          "default": "",
          "description": "Short snippet preview from Gmail",
          "example": "This is the beginning of the email message...",
          "maxLength": 500,
          "title": "Snippet",
          "type": "string"
        },
        "internal_date": {
          "description": "Gmail internal timestamp (ISO 8601)",
          "example": "2025-10-13T12:00:00",
          "title": "Internal Date",
          "type": "string"
        },
        "labels": {
          "description": "Gmail labels applied to the message",
          "example": [
            "INBOX",
            "IMPORTANT",
            "UNREAD"
          ],
          "items": {
            "type": "string"
          },
          "title": "Labels",
          "type": "array"
        },
        "has_attachments": {
          "default": false,
          "description": "Whether the message has attachments",
          "title": "Has Attachments",
          "type": "boolean"
        },
        "attachments": {
          "description": "Attachment metadata",
          "items": {
            "$ref": "#/$defs/GmailAttachment"
          },
          "title": "Attachments",
          "type": "array"
        },
        "body_text": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Plaintext body, if available",
          "title": "Body Text"
        },
        "body_html": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "HTML body, if available",
          "title": "Body Html"
        },
        "fetched_at": {
          "description": "Timestamp when data was fetched (ISO 8601)",
          "example": "2025-10-13T12:00:00",
          "title": "Fetched At",
          "type": "string"
        }
      },
      "required": [
        "id",
        "thread_id",
        "sender",
        "internal_date"
      ],
      "title": "GmailMessage",
      "type": "object"
    },
    "GmailThread": {
      "description": "Thread metadata for a set of Gmail messages.",
      "properties": {
        "id": {
          "description": "Gmail thread ID",
          "title": "Id",
          "type": "string"
        },
        "message_ids": {
          "description": "Ordered list of message IDs in this thread",
          "items": {
            "type": "string"
          },
          "title": "Message Ids",
          "type": "array"
        },
        "snippet": {
          "default": "",
          "description": "Thread snippet",
          "title": "Snippet",
          "type": "string"
        },
        "history_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Gmail history ID for incremental sync",
          "title": "History Id"
        },
        "updated_at": {
          "description": "Last time the thread was updated",
          "title": "Updated At",
          "type": "string"
        }
      },
      "required": [
        "id"
      ],
      "title": "GmailThread",
      "type": "object"
    }
  },
  "description": "Typed Gmail data stored on a casefile.",
  "properties": {
    "messages": {
      "description": "Messages stored on the casefile",
      "items": {
        "$ref": "#/$defs/GmailMessage"
      },
      "title": "Messages",
      "type": "array"
    },
    "threads": {
      "description": "Thread metadata",
      "items": {
        "$ref": "#/$defs/GmailThread"
      },
      "title": "Threads",
      "type": "array"
    },
    "labels": {
      "description": "Cached Gmail labels",
      "items": {
        "$ref": "#/$defs/GmailLabel"
      },
      "title": "Labels",
      "type": "array"
    },
    "last_sync_token": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Token for incremental sync operations",
      "title": "Last Sync Token"
    },
    "synced_at": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Timestamp of the most recent successful sync",
      "title": "Synced At"
    },
    "sync_status": {
      "default": "idle",
      "description": "Current sync status (idle|syncing|error)",
      "title": "Sync Status",
      "type": "string"
    },
    "error_message": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "Last sync error message, if any",
      "title": "Error Message"
    }
  },
  "title": "CasefileGmailData",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
