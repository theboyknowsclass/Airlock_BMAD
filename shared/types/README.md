# Airlock Shared TypeScript Types

Shared TypeScript types and interfaces for the Airlock project.

## Installation

This package is included in the frontend project. Types can be imported directly from the `shared/types` directory.

## Usage

### Import Types

```typescript
import type { User, PackageRequest, ApiError } from "@/shared";
import { HTTP_STATUS, ERROR_CODE, USER_ROLE, API_VERSION } from "@/shared";
```

### API Response Types

```typescript
import type { ApiResponse, ApiError } from "@/shared";

// Success response
const response: ApiResponse<User> = {
  data: {
    id: "123",
    username: "user",
    email: "user@example.com",
    roles: ["submitter"],
    created_at: "2025-11-12T10:00:00Z",
    updated_at: "2025-11-12T10:00:00Z",
  },
};

// Error response
const error: ApiError = {
  error: {
    code: "VALIDATION_ERROR",
    message: "Invalid input",
    details: { field: "email" },
  },
};
```

### Constants

```typescript
import { HTTP_STATUS, ERROR_CODE, USER_ROLE, API_VERSION, API_PREFIX } from "@/shared";

// Use HTTP status codes
if (response.status === HTTP_STATUS.OK) {
  // Process success
}

// Use error codes
if (error.code === ERROR_CODE.VALIDATION_ERROR) {
  // Handle validation error
}

// Use user roles
if (user.roles.includes(USER_ROLE.ADMIN)) {
  // Admin only
}

// Use API prefix
const healthUrl = `${API_PREFIX}/health`;
```

## Types

### API Types

- `ApiError` - API error response
- `ApiResponse<T>` - API success response
- `PaginationParams` - Pagination parameters
- `PaginationMeta` - Pagination metadata
- `HealthResponse` - Health check response

### Entity Types

- `User` - User entity
- `PackageSubmission` - Package submission entity
- `PackageRequest` - Package request entity
- `Package` - Package entity
- `Workflow` - Workflow entity
- `CheckResult` - Check result entity
- `AuditLog` - Audit log entity
- `ApiKey` - API key entity
- `PackageUsage` - Package usage entity
- `LicenseAllowlist` - License allowlist entity

### Constants

- `HTTP_STATUS` - HTTP status codes
- `ERROR_CODE` - Error codes
- `USER_ROLE` - User roles
- `API_VERSION` - API version
- `API_PREFIX` - API prefix

## Configuration

The frontend `vite.config.ts` and `tsconfig.json` are configured to include the shared types directory:

```typescript
// vite.config.ts
resolve: {
  alias: {
    "@/shared": path.resolve(__dirname, "../shared/types"),
  },
}

// tsconfig.json
paths: {
  "@/shared/*": ["../shared/types/*"]
}
include: ["src", "../shared/types"]
```

## Notes

- Types are shared between frontend and backend (via API contracts)
- Types are kept in sync with backend models
- Constants are shared for consistency
- All types are exported from `index.ts` for easy importing

