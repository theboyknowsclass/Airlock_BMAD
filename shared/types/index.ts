/**
 * Airlock Shared TypeScript Types
 * Main export file for shared types
 */

// API Contract Types
export * from "./api";

// Re-export commonly used types
export type {
  ApiError,
  ApiResponse,
  PaginationParams,
  PaginationMeta,
  HealthResponse,
  UserRole,
  User,
  PackageSubmission,
  PackageRequest,
  Package,
  Workflow,
  CheckResult,
  AuditLog,
  ApiKey,
  PackageUsage,
  LicenseAllowlist,
} from "./api";

// Re-export constants
export {
  HTTP_STATUS,
  ERROR_CODE,
  USER_ROLE,
  API_VERSION,
  API_PREFIX,
} from "./api";
