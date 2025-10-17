# CasefileDataPayload

**Package:** `pydantic_models.operations`

Response payload with full casefile data.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `casefile` | CasefileModel | ✓ | Complete casefile model |

---

## JSON Schema

```json
{
  "$defs": {
    "CasefileACL": {
      "description": "Access Control List for a casefile.",
      "properties": {
        "owner_id": {
          "description": "Casefile owner (has all permissions)",
          "example": "owner@example.com",
          "format": "email",
          "title": "Owner Id",
          "type": "string"
        },
        "permissions": {
          "description": "List of user permissions",
          "items": {
            "$ref": "#/$defs/PermissionEntry"
          },
          "title": "Permissions",
          "type": "array"
        },
        "public_access": {
          "$ref": "#/$defs/PermissionLevel",
          "default": "none",
          "description": "Default access level for all users",
          "example": "viewer"
        },
        "inherit_from_parent": {
          "default": false,
          "description": "Whether to inherit permissions from parent (future use)",
          "title": "Inherit From Parent",
          "type": "boolean"
        }
      },
      "required": [
        "owner_id"
      ],
      "title": "CasefileACL",
      "type": "object"
    },
    "CasefileDriveData": {
      "description": "Typed Drive artifacts stored on a casefile.",
      "properties": {
        "files": {
          "description": "Tracked Drive files",
          "items": {
            "$ref": "#/$defs/DriveFile"
          },
          "title": "Files",
          "type": "array"
        },
        "folders": {
          "description": "Tracked Drive folders",
          "items": {
            "$ref": "#/$defs/DriveFolder"
          },
          "title": "Folders",
          "type": "array"
        },
        "last_sync_token": {
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
          "description": "Token for incremental Drive sync",
          "title": "Last Sync Token"
        },
        "synced_at": {
          "anyOf": [
            {
              "description": "ISO 8601 timestamp (e.g., 2025-10-13T12:00:00)",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Timestamp of the most recent sync",
          "title": "Synced At"
        },
        "sync_status": {
          "default": "idle",
          "description": "Current sync status (idle|syncing|error)",
          "maxLength": 200,
          "minLength": 1,
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
          "description": "Last sync error message",
          "title": "Error Message"
        }
      },
      "title": "CasefileDriveData",
      "type": "object"
    },
    "CasefileGmailData": {
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
    },
    "CasefileMetadata": {
      "description": "Metadata for a casefile.",
      "properties": {
        "title": {
          "description": "Casefile title",
          "example": "Investigation Case 2025-001",
          "maxLength": 200,
          "minLength": 1,
          "title": "Title",
          "type": "string"
        },
        "description": {
          "default": "",
          "description": "Casefile description",
          "example": "Email investigation for incident #42",
          "maxLength": 2000,
          "minLength": 1,
          "title": "Description",
          "type": "string"
        },
        "tags": {
          "description": "Tags for categorization",
          "example": [
            "incident",
            "email",
            "security"
          ],
          "items": {
            "type": "string"
          },
          "title": "Tags",
          "type": "array"
        },
        "created_by": {
          "description": "User who created the casefile",
          "example": "user@example.com",
          "title": "Created By",
          "type": "string"
        },
        "created_at": {
          "description": "Creation timestamp (ISO 8601)",
          "example": "2025-10-13T12:00:00",
          "title": "Created At",
          "type": "string"
        },
        "updated_at": {
          "description": "Last update timestamp (ISO 8601)",
          "example": "2025-10-13T12:30:00",
          "title": "Updated At",
          "type": "string"
        }
      },
      "required": [
        "title",
        "created_by"
      ],
      "title": "CasefileMetadata",
      "type": "object"
    },
    "CasefileModel": {
      "description": "Complete casefile model with metadata and linked resources.",
      "properties": {
        "id": {
          "description": "Unique casefile ID in format cf_yymmdd_code",
          "title": "Id",
          "type": "string"
        },
        "metadata": {
          "$ref": "#/$defs/CasefileMetadata",
          "description": "Casefile metadata"
        },
        "acl": {
          "anyOf": [
            {
              "$ref": "#/$defs/CasefileACL"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Access Control List for permissions"
        },
        "resources": {
          "additionalProperties": {
            "items": {
              "$ref": "#/$defs/ResourceReference"
            },
            "type": "array"
          },
          "deprecated": true,
          "description": "Legacy resource references by type (deprecated)",
          "title": "Resources",
          "type": "object"
        },
        "session_ids": {
          "description": "Tool session IDs associated with this casefile",
          "items": {
            "type": "string"
          },
          "title": "Session Ids",
          "type": "array"
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
          "description": "Additional notes",
          "title": "Notes"
        },
        "gmail_data": {
          "anyOf": [
            {
              "$ref": "#/$defs/CasefileGmailData"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Typed Gmail data captured for this casefile"
        },
        "drive_data": {
          "anyOf": [
            {
              "$ref": "#/$defs/CasefileDriveData"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Typed Google Drive data captured for this casefile"
        },
        "sheets_data": {
          "anyOf": [
            {
              "$ref": "#/$defs/CasefileSheetsData"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Typed Google Sheets data captured for this casefile"
        }
      },
      "required": [
        "metadata"
      ],
      "title": "CasefileModel",
      "type": "object"
    },
    "CasefileSheetsData": {
      "description": "Typed Sheets data stored on a casefile.",
      "properties": {
        "spreadsheets": {
          "additionalProperties": {
            "$ref": "#/$defs/SheetData"
          },
          "description": "Spreadsheet data keyed by spreadsheet ID",
          "title": "Spreadsheets",
          "type": "object"
        },
        "last_sync_token": {
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
          "description": "Incremental sync token",
          "title": "Last Sync Token"
        },
        "synced_at": {
          "anyOf": [
            {
              "description": "ISO 8601 timestamp (e.g., 2025-10-13T12:00:00)",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Timestamp of the most recent sync",
          "title": "Synced At"
        },
        "sync_status": {
          "default": "idle",
          "description": "Current sync status (idle|syncing|error)",
          "maxLength": 200,
          "minLength": 1,
          "title": "Sync Status",
          "type": "string"
        },
        "error_message": {
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
          "description": "Last sync error",
          "title": "Error Message"
        }
      },
      "title": "CasefileSheetsData",
      "type": "object"
    },
    "DriveFile": {
      "description": "Representation of a Google Drive file.",
      "properties": {
        "id": {
          "description": "Drive file ID",
          "maxLength": 200,
          "minLength": 1,
          "title": "Id",
          "type": "string"
        },
        "name": {
          "description": "File name",
          "maxLength": 200,
          "minLength": 1,
          "title": "Name",
          "type": "string"
        },
        "mime_type": {
          "description": "MIME type",
          "maxLength": 200,
          "minLength": 1,
          "title": "Mime Type",
          "type": "string"
        },
        "size_bytes": {
          "anyOf": [
            {
              "description": "File size in bytes",
              "minimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "File size in bytes",
          "title": "Size Bytes"
        },
        "web_view_link": {
          "anyOf": [
            {
              "format": "uri",
              "maxLength": 2083,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Link for viewing the file",
          "title": "Web View Link"
        },
        "icon_link": {
          "anyOf": [
            {
              "format": "uri",
              "maxLength": 2083,
              "minLength": 1,
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Icon link for the file type",
          "title": "Icon Link"
        },
        "parents": {
          "description": "Parent folder IDs",
          "items": {
            "description": "Short string (1-200 characters)",
            "maxLength": 200,
            "minLength": 1,
            "type": "string"
          },
          "title": "Parents",
          "type": "array"
        },
        "owners": {
          "description": "File owners",
          "items": {
            "$ref": "#/$defs/DriveOwner"
          },
          "title": "Owners",
          "type": "array"
        },
        "created_time": {
          "description": "Creation timestamp",
          "title": "Created Time",
          "type": "string"
        },
        "modified_time": {
          "description": "Last modification timestamp",
          "title": "Modified Time",
          "type": "string"
        },
        "trashed": {
          "default": false,
          "description": "Whether the file is in trash",
          "title": "Trashed",
          "type": "boolean"
        }
      },
      "required": [
        "id",
        "name",
        "mime_type"
      ],
      "title": "DriveFile",
      "type": "object"
    },
    "DriveFolder": {
      "description": "Representation of a Google Drive folder.",
      "properties": {
        "id": {
          "description": "Drive folder ID",
          "maxLength": 200,
          "minLength": 1,
          "title": "Id",
          "type": "string"
        },
        "name": {
          "description": "Folder name",
          "maxLength": 200,
          "minLength": 1,
          "title": "Name",
          "type": "string"
        },
        "parents": {
          "description": "Parent folder IDs",
          "items": {
            "description": "Short string (1-200 characters)",
            "maxLength": 200,
            "minLength": 1,
            "type": "string"
          },
          "title": "Parents",
          "type": "array"
        },
        "created_time": {
          "description": "Creation timestamp",
          "title": "Created Time",
          "type": "string"
        },
        "modified_time": {
          "description": "Last modification timestamp",
          "title": "Modified Time",
          "type": "string"
        }
      },
      "required": [
        "id",
        "name"
      ],
      "title": "DriveFolder",
      "type": "object"
    },
    "DriveOwner": {
      "description": "Metadata describing a file owner.",
      "properties": {
        "email": {
          "description": "Owner email",
          "format": "email",
          "title": "Email",
          "type": "string"
        },
        "display_name": {
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
          "description": "Owner display name",
          "title": "Display Name"
        }
      },
      "required": [
        "email"
      ],
      "title": "DriveOwner",
      "type": "object"
    },
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
    },
    "PermissionEntry": {
      "description": "Single permission entry for a user on a casefile.",
      "properties": {
        "user_id": {
          "description": "User ID granted permission",
          "example": "user123@example.com",
          "format": "email",
          "title": "User Id",
          "type": "string"
        },
        "permission": {
          "$ref": "#/$defs/PermissionLevel",
          "description": "Level of access granted",
          "example": "editor"
        },
        "granted_by": {
          "description": "User who granted this permission",
          "example": "admin@example.com",
          "format": "email",
          "title": "Granted By",
          "type": "string"
        },
        "granted_at": {
          "description": "When permission was granted (ISO 8601)",
          "example": "2025-10-13T12:00:00",
          "title": "Granted At",
          "type": "string"
        },
        "expires_at": {
          "anyOf": [
            {
              "description": "ISO 8601 timestamp (e.g., 2025-10-13T12:00:00)",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Optional expiration timestamp (ISO 8601)",
          "example": "2025-12-31T23:59:59",
          "title": "Expires At"
        },
        "notes": {
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
          "description": "Optional notes about this permission",
          "example": "Temporary access for project collaboration",
          "title": "Notes"
        }
      },
      "required": [
        "user_id",
        "permission",
        "granted_by"
      ],
      "title": "PermissionEntry",
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
    },
    "ResourceReference": {
      "description": "Reference to an external resource linked to a casefile.",
      "properties": {
        "resource_id": {
          "description": "External resource ID",
          "example": "msg_123abc",
          "title": "Resource Id",
          "type": "string"
        },
        "resource_type": {
          "description": "Type of resource (gmail, drive, etc.)",
          "example": "gmail",
          "title": "Resource Type",
          "type": "string"
        },
        "added_at": {
          "description": "When this was added (ISO 8601)",
          "example": "2025-10-13T12:00:00",
          "title": "Added At",
          "type": "string"
        },
        "metadata": {
          "additionalProperties": true,
          "description": "Additional metadata",
          "example": {
            "subject": "Important Email"
          },
          "title": "Metadata",
          "type": "object"
        }
      },
      "required": [
        "resource_id",
        "resource_type"
      ],
      "title": "ResourceReference",
      "type": "object"
    },
    "SheetData": {
      "description": "Top-level spreadsheet data captured for a casefile.",
      "properties": {
        "spreadsheet_id": {
          "description": "Spreadsheet ID",
          "maxLength": 200,
          "minLength": 1,
          "title": "Spreadsheet Id",
          "type": "string"
        },
        "title": {
          "description": "Spreadsheet title",
          "maxLength": 200,
          "minLength": 1,
          "title": "Title",
          "type": "string"
        },
        "metadata": {
          "description": "Sheet metadata entries",
          "items": {
            "$ref": "#/$defs/SheetMetadata"
          },
          "title": "Metadata",
          "type": "array"
        },
        "ranges": {
          "description": "Captured ranges for the spreadsheet",
          "items": {
            "$ref": "#/$defs/SheetRange"
          },
          "title": "Ranges",
          "type": "array"
        },
        "updated_at": {
          "description": "Timestamp of last update",
          "title": "Updated At",
          "type": "string"
        }
      },
      "required": [
        "spreadsheet_id",
        "title"
      ],
      "title": "SheetData",
      "type": "object"
    },
    "SheetMetadata": {
      "description": "Metadata for a Google Sheet tab.",
      "properties": {
        "sheet_id": {
          "description": "Numeric sheet identifier",
          "exclusiveMinimum": 0,
          "title": "Sheet Id",
          "type": "integer"
        },
        "title": {
          "description": "Sheet title",
          "maxLength": 200,
          "minLength": 1,
          "title": "Title",
          "type": "string"
        },
        "index": {
          "anyOf": [
            {
              "description": "Positive integer (greater than 0)",
              "exclusiveMinimum": 0,
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Zero-based sheet index",
          "title": "Index"
        },
        "grid_properties": {
          "additionalProperties": true,
          "description": "Raw grid properties from API",
          "title": "Grid Properties",
          "type": "object"
        }
      },
      "required": [
        "sheet_id",
        "title"
      ],
      "title": "SheetMetadata",
      "type": "object"
    },
    "SheetRange": {
      "description": "Represents a rectangular range of spreadsheet values.",
      "properties": {
        "range": {
          "description": "A1-notation range (e.g. Sheet1!A1:C10)",
          "maxLength": 200,
          "minLength": 1,
          "title": "Range",
          "type": "string"
        },
        "values": {
          "description": "2D array of cell values",
          "items": {
            "items": {},
            "type": "array"
          },
          "title": "Values",
          "type": "array"
        },
        "major_dimension": {
          "default": "ROWS",
          "description": "Rows or COLUMNS orientation",
          "maxLength": 200,
          "minLength": 1,
          "title": "Major Dimension",
          "type": "string"
        }
      },
      "required": [
        "range"
      ],
      "title": "SheetRange",
      "type": "object"
    }
  },
  "description": "Response payload with full casefile data.",
  "properties": {
    "casefile": {
      "$ref": "#/$defs/CasefileModel",
      "description": "Complete casefile model"
    }
  },
  "required": [
    "casefile"
  ],
  "title": "CasefileDataPayload",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
