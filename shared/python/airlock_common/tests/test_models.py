"""
Tests for database models
These tests can run without a database connection
"""
import pytest
from datetime import datetime
from sqlalchemy import inspect

from airlock_common.db.models import (
    User,
    PackageSubmission,
    PackageRequest,
    Package,
    Workflow,
    CheckResult,
    AuditLog,
    APIKey,
    PackageUsage,
    LicenseAllowlist,
)
from airlock_common.db.models.package_submission import SubmissionStatus
from airlock_common.db.models.package_request import PackageRequestStatus
from airlock_common.db.models.package import PackageStatus
from airlock_common.db.models.workflow import WorkflowStatus, WorkflowStage
from airlock_common.db.models.check_result import CheckType, CheckStatus


def test_user_model_structure():
    """Test that User model has correct structure"""
    assert hasattr(User, "__tablename__")
    assert User.__tablename__ == "users"
    
    # Check columns
    mapper = inspect(User)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "username" in column_names
    assert "email" in column_names
    assert "roles" in column_names
    assert "created_at" in column_names
    assert "updated_at" in column_names


def test_package_submission_model_structure():
    """Test that PackageSubmission model has correct structure"""
    assert hasattr(PackageSubmission, "__tablename__")
    assert PackageSubmission.__tablename__ == "package_submissions"
    
    # Check columns
    mapper = inspect(PackageSubmission)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "user_id" in column_names
    assert "project_name" in column_names
    assert "project_version" in column_names
    assert "package_lock_json" in column_names
    assert "status" in column_names
    assert "created_at" in column_names
    assert "updated_at" in column_names


def test_package_request_model_structure():
    """Test that PackageRequest model has correct structure"""
    assert hasattr(PackageRequest, "__tablename__")
    assert PackageRequest.__tablename__ == "package_requests"
    
    # Check columns
    mapper = inspect(PackageRequest)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "submission_id" in column_names
    assert "package_name" in column_names
    assert "package_version" in column_names
    assert "status" in column_names
    assert "created_at" in column_names
    assert "updated_at" in column_names


def test_package_model_structure():
    """Test that Package model has correct structure"""
    assert hasattr(Package, "__tablename__")
    assert Package.__tablename__ == "packages"
    
    # Check columns
    mapper = inspect(Package)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "name" in column_names
    assert "version" in column_names
    assert "status" in column_names
    assert "metadata" in column_names
    assert "fetched_at" in column_names
    assert "created_at" in column_names
    assert "updated_at" in column_names


def test_workflow_model_structure():
    """Test that Workflow model has correct structure"""
    assert hasattr(Workflow, "__tablename__")
    assert Workflow.__tablename__ == "workflows"
    
    # Check columns
    mapper = inspect(Workflow)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "package_request_id" in column_names
    assert "status" in column_names
    assert "current_stage" in column_names
    assert "created_at" in column_names
    assert "updated_at" in column_names


def test_check_result_model_structure():
    """Test that CheckResult model has correct structure"""
    assert hasattr(CheckResult, "__tablename__")
    assert CheckResult.__tablename__ == "check_results"
    
    # Check columns
    mapper = inspect(CheckResult)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "workflow_id" in column_names
    assert "check_type" in column_names
    assert "status" in column_names
    assert "results" in column_names
    assert "created_at" in column_names


def test_audit_log_model_structure():
    """Test that AuditLog model has correct structure"""
    assert hasattr(AuditLog, "__tablename__")
    assert AuditLog.__tablename__ == "audit_logs"
    
    # Check columns
    mapper = inspect(AuditLog)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "user_id" in column_names
    assert "action" in column_names
    assert "resource_type" in column_names
    assert "resource_id" in column_names
    assert "details" in column_names
    assert "timestamp" in column_names


def test_api_key_model_structure():
    """Test that APIKey model has correct structure"""
    assert hasattr(APIKey, "__tablename__")
    assert APIKey.__tablename__ == "api_keys"
    
    # Check columns
    mapper = inspect(APIKey)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "key_hash" in column_names
    assert "scopes" in column_names
    assert "permissions" in column_names
    assert "created_at" in column_names
    assert "expires_at" in column_names


def test_package_usage_model_structure():
    """Test that PackageUsage model has correct structure"""
    assert hasattr(PackageUsage, "__tablename__")
    assert PackageUsage.__tablename__ == "package_usage"
    
    # Check columns
    mapper = inspect(PackageUsage)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "package_request_id" in column_names
    assert "project_name" in column_names
    assert "created_at" in column_names


def test_license_allowlist_model_structure():
    """Test that LicenseAllowlist model has correct structure"""
    assert hasattr(LicenseAllowlist, "__tablename__")
    assert LicenseAllowlist.__tablename__ == "license_allowlist"
    
    # Check columns
    mapper = inspect(LicenseAllowlist)
    column_names = [col.key for col in mapper.columns]
    
    assert "id" in column_names
    assert "license_identifier" in column_names
    assert "license_name" in column_names
    assert "description" in column_names
    assert "is_active" in column_names
    assert "created_by" in column_names
    assert "created_at" in column_names
    assert "updated_at" in column_names


def test_enum_values():
    """Test that enum values are correct"""
    # SubmissionStatus
    assert SubmissionStatus.PENDING.value == "pending"
    assert SubmissionStatus.PROCESSING.value == "processing"
    assert SubmissionStatus.COMPLETED.value == "completed"
    assert SubmissionStatus.FAILED.value == "failed"
    
    # PackageRequestStatus
    assert PackageRequestStatus.PENDING.value == "pending"
    assert PackageRequestStatus.IN_WORKFLOW.value == "in_workflow"
    assert PackageRequestStatus.APPROVED.value == "approved"
    assert PackageRequestStatus.REJECTED.value == "rejected"
    
    # PackageStatus
    assert PackageStatus.PENDING.value == "pending"
    assert PackageStatus.FETCHED.value == "fetched"
    assert PackageStatus.APPROVED.value == "approved"
    assert PackageStatus.REJECTED.value == "rejected"
    
    # WorkflowStatus
    assert WorkflowStatus.REQUESTED.value == "requested"
    assert WorkflowStatus.FETCHING.value == "fetching"
    assert WorkflowStatus.VALIDATING.value == "validating"
    assert WorkflowStatus.CHECKING.value == "checking"
    assert WorkflowStatus.REVIEWING.value == "reviewing"
    assert WorkflowStatus.APPROVED.value == "approved"
    assert WorkflowStatus.REJECTED.value == "rejected"
    
    # CheckType
    assert CheckType.TRIVY.value == "trivy"
    assert CheckType.LICENSE.value == "license"
    
    # CheckStatus
    assert CheckStatus.PENDING.value == "pending"
    assert CheckStatus.RUNNING.value == "running"
    assert CheckStatus.COMPLETED.value == "completed"
    assert CheckStatus.FAILED.value == "failed"


def test_model_relationships():
    """Test that model relationships are defined"""
    # User relationships
    assert hasattr(User, "package_submissions")
    assert hasattr(User, "audit_logs")
    assert hasattr(User, "license_allowlist_entries")
    
    # PackageSubmission relationships
    assert hasattr(PackageSubmission, "user")
    assert hasattr(PackageSubmission, "package_requests")
    
    # PackageRequest relationships
    assert hasattr(PackageRequest, "submission")
    assert hasattr(PackageRequest, "workflow")
    assert hasattr(PackageRequest, "package_usage")
    
    # Workflow relationships
    assert hasattr(Workflow, "package_request")
    assert hasattr(Workflow, "check_results")
    
    # CheckResult relationships
    assert hasattr(CheckResult, "workflow")
    
    # AuditLog relationships
    assert hasattr(AuditLog, "user")
    
    # PackageUsage relationships
    assert hasattr(PackageUsage, "package_request")
    
    # LicenseAllowlist relationships
    assert hasattr(LicenseAllowlist, "created_by_user")

