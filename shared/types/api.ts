/**
 * API Contract Types for Airlock
 * Shared TypeScript types for API requests and responses
 */

/**
 * API Error Response
 */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * API Success Response
 */
export interface ApiResponse<T = unknown> {
  data: T;
  meta?: {
    timestamp: string;
    pagination?: {
      page: number;
      page_size: number;
      total: number;
      total_pages: number;
    };
  };
}

/**
 * Pagination Parameters
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

/**
 * Pagination Metadata
 */
export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

/**
 * Health Check Response
 */
export interface HealthResponse {
  status: string;
  service: string;
  timestamp: string;
}

/**
 * User Role
 */
export type UserRole = "submitter" | "reviewer" | "admin";

/**
 * User
 */
export interface User {
  id: string;
  username: string;
  email: string;
  roles: UserRole[];
  name?: string;
  given_name?: string;
  family_name?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Package Submission
 */
export interface PackageSubmission {
  id: string;
  user_id: string;
  project_name: string;
  package_lock_json: string;
  status: string;
  created_at: string;
  updated_at: string;
}

/**
 * Package Request
 */
export interface PackageRequest {
  id: string;
  submission_id: string;
  package_name: string;
  package_version: string;
  status: string;
  created_at: string;
  updated_at: string;
}

/**
 * Package
 */
export interface Package {
  id: string;
  name: string;
  version: string;
  status: string;
  metadata?: string;
  fetched_at?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Workflow
 */
export interface Workflow {
  id: string;
  package_request_id: string;
  status: string;
  current_stage: string;
  created_at: string;
  updated_at: string;
}

/**
 * Check Result
 */
export interface CheckResult {
  id: string;
  workflow_id: string;
  check_type: string;
  status: string;
  results: string;
  created_at: string;
}

/**
 * Audit Log
 */
export interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: string;
  timestamp: string;
}

/**
 * API Key
 */
export interface ApiKey {
  id: string;
  key_hash: string;
  scopes: string[];
  permissions: string[];
  created_at: string;
  expires_at?: string;
}

/**
 * Package Usage
 */
export interface PackageUsage {
  id: string;
  package_request_id: string;
  project_name: string;
  created_at: string;
}

/**
 * License Allowlist
 */
export interface LicenseAllowlist {
  id: string;
  license_identifier: string;
  license_name: string;
  description?: string;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

/**
 * HTTP Status Codes
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

/**
 * Error Codes
 */
export const ERROR_CODE = {
  VALIDATION_ERROR: "VALIDATION_ERROR",
  NOT_FOUND: "NOT_FOUND",
  UNAUTHORIZED: "UNAUTHORIZED",
  FORBIDDEN: "FORBIDDEN",
  CONFLICT: "CONFLICT",
  INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
  SERVICE_UNAVAILABLE: "SERVICE_UNAVAILABLE",
} as const;

/**
 * User Roles
 */
export const USER_ROLE = {
  SUBMITTER: "submitter",
  REVIEWER: "reviewer",
  ADMIN: "admin",
} as const;

/**
 * API Version
 */
export const API_VERSION = "v1";

/**
 * API Prefix
 */
export const API_PREFIX = `/api/${API_VERSION}`;

