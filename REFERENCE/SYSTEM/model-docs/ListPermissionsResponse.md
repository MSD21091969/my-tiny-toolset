# ListPermissionsResponse

**Package:** `pydantic_models.operations`

Response with list of permissions.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | UUID | ✓ | ID of the originating request |
| `status` | RequestStatus | ✓ | Request processing status |
| `payload` | PermissionListPayload | ✓ | Response payload |
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
    "PermissionListPayload": {
      "description": "Response payload with list of all permissions.",
      "properties": {
        "casefile_id": {
          "description": "Casefile ID in format cf_YYMMDD_code",
          "title": "Casefile Id",
          "type": "string"
        },
        "owner_id": {
          "description": "User identifier (typically email address)",
          "title": "Owner Id",
          "type": "string"
        },
        "public_access": {
          "$ref": "#/$defs/PermissionLevel"
        },
        "permissions": {
          "items": {
            "$ref": "#/$defs/PermissionEntry"
          },
          "title": "Permissions",
          "type": "array"
        },
        "total_users": {
          "title": "Total Users",
          "type": "integer"
        }
      },
      "required": [
        "casefile_id",
        "owner_id",
        "public_access",
        "permissions",
        "total_users"
      ],
      "title": "PermissionListPayload",
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
  "description": "Response with list of permissions.",
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
      "$ref": "#/$defs/PermissionListPayload",
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
  "title": "ListPermissionsResponse",
  "type": "object"
}
```

---

*Generated by model_docs_generator.py*
