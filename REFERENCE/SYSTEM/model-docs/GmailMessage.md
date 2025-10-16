# GmailMessage

**Package:** `pydantic_models.workspace`

Envelope + payload for a Gmail message.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | ✓ | Gmail message ID |
| `thread_id` | str | ✓ | Thread ID for the message |
| `subject` | str |  | Message subject |
| `sender` | str | ✓ | From email address |
| `to_recipients` | list |  | Primary recipient email addresses |
| `cc_recipients` | list |  | CC recipient email addresses |
| `bcc_recipients` | list |  | BCC recipient email addresses |
| `snippet` | str |  | Short snippet preview from Gmail |
| `internal_date` | str | ✓ | Gmail internal timestamp (ISO 8601) |
| `labels` | List |  | Gmail labels applied to the message |
| `has_attachments` | bool |  | Whether the message has attachments |
| `attachments` | List |  | Attachment metadata |
| `body_text` | Optional |  | Plaintext body, if available |
| `body_html` | Optional |  | HTML body, if available |
| `fetched_at` | str |  | Timestamp when data was fetched (ISO 8601) |

## Field Details

### `subject`

**Constraints:**
- max length: 1000

**Default:** ``

### `to_recipients`

**Default:** `PydanticUndefined`

### `cc_recipients`

**Default:** `PydanticUndefined`

### `bcc_recipients`

**Default:** `PydanticUndefined`

### `snippet`

**Constraints:**
- max length: 500

**Default:** ``

### `labels`

**Default:** `PydanticUndefined`

### `has_attachments`

**Default:** `False`

### `attachments`

**Default:** `PydanticUndefined`

### `fetched_at`

**Default:** `PydanticUndefined`

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
    }
  },
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
}
```

---

*Generated by model_docs_generator.py*
