# CasefileDriveData

**Package:** `pydantic_models.workspace`

Typed Drive artifacts stored on a casefile.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | List |  | Tracked Drive files |
| `folders` | List |  | Tracked Drive folders |
| `last_sync_token` | Optional |  | Token for incremental Drive sync |
| `synced_at` | Optional |  | Timestamp of the most recent sync |
| `sync_status` | str |  | Current sync status (idle|syncing|error) |
| `error_message` | Optional |  | Last sync error message |

## Field Details

### `files`

**Default:** `PydanticUndefined`

### `folders`

**Default:** `PydanticUndefined`

### `sync_status`

**Constraints:**
- min length: 1
- max length: 200

**Default:** `idle`

---

## JSON Schema

```json
{
  "$defs": {
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
    }
  },
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
}
```

---

*Generated by model_docs_generator.py*
