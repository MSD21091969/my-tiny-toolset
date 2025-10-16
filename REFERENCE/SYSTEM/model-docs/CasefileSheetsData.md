# CasefileSheetsData

**Package:** `pydantic_models.workspace`

Typed Sheets data stored on a casefile.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `spreadsheets` | Dict |  | Spreadsheet data keyed by spreadsheet ID |
| `last_sync_token` | Optional |  | Incremental sync token |
| `synced_at` | Optional |  | Timestamp of the most recent sync |
| `sync_status` | str |  | Current sync status (idle|syncing|error) |
| `error_message` | Optional |  | Last sync error |

## Field Details

### `spreadsheets`

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
}
```

---

*Generated by model_docs_generator.py*
