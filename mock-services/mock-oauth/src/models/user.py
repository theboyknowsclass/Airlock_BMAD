"""
Test user models for mock OAuth service
"""
from typing import List, Optional
from dataclasses import dataclass

# Test users with different roles
TEST_USERS = {
    "submitter": {
        "user_id": "user-submitter-001",
        "username": "submitter",
        "email": "submitter@example.com",
        "roles": ["submitter"],
        "name": "Test Submitter",
        "given_name": "Test",
        "family_name": "Submitter",
    },
    "reviewer": {
        "user_id": "user-reviewer-001",
        "username": "reviewer",
        "email": "reviewer@example.com",
        "roles": ["reviewer"],
        "name": "Test Reviewer",
        "given_name": "Test",
        "family_name": "Reviewer",
    },
    "admin": {
        "user_id": "user-admin-001",
        "username": "admin",
        "email": "admin@example.com",
        "roles": ["admin"],
        "name": "Test Admin",
        "given_name": "Test",
        "family_name": "Admin",
    },
    # User with multiple roles
    "reviewer-admin": {
        "user_id": "user-reviewer-admin-001",
        "username": "reviewer-admin",
        "email": "reviewer-admin@example.com",
        "roles": ["reviewer", "admin"],
        "name": "Test Reviewer Admin",
        "given_name": "Test",
        "family_name": "Reviewer Admin",
    },
}


@dataclass
class TestUser:
    """Test user model"""
    user_id: str
    username: str
    email: str
    roles: List[str]
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "TestUser":
        """Create TestUser from dictionary"""
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            email=data["email"],
            roles=data["roles"],
            name=data.get("name"),
            given_name=data.get("given_name"),
            family_name=data.get("family_name"),
        )


def get_user_by_username(username: str) -> Optional[TestUser]:
    """Get user by username"""
    user_data = TEST_USERS.get(username)
    if user_data:
        return TestUser.from_dict(user_data)
    return None


def get_user_by_id(user_id: str) -> Optional[TestUser]:
    """Get user by user_id"""
    for user_data in TEST_USERS.values():
        if user_data["user_id"] == user_id:
            return TestUser.from_dict(user_data)
    return None


def get_all_users() -> List[TestUser]:
    """Get all test users"""
    return [TestUser.from_dict(user_data) for user_data in TEST_USERS.values()]

