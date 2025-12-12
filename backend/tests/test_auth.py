"""
Unit tests untuk Authentication
Coverage: JWT, password hashing, user management
"""
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from src.infrastructure.auth.jwt_handler import JWTHandler
from src.infrastructure.auth.user_repository import User, UserRepository
from src.main import app


class TestJWTHandler:
    """Test JWT Handler"""

    def test_password_hashing(self):
        """Test: Hash password"""
        password = "testpassword123"
        hashed = JWTHandler.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        """Test: Verify correct password"""
        password = "testpassword123"
        hashed = JWTHandler.get_password_hash(password)

        assert JWTHandler.verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """Test: Verify wrong password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = JWTHandler.get_password_hash(password)

        assert JWTHandler.verify_password(wrong_password, hashed) is False

    def test_create_access_token(self):
        """Test: Create JWT token"""
        data = {"sub": "testuser"}
        token = JWTHandler.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_with_expiry(self):
        """Test: Create token with custom expiry"""
        data = {"sub": "testuser"}
        expires = timedelta(minutes=15)
        token = JWTHandler.create_access_token(data, expires_delta=expires)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test: Decode valid token"""
        username = "testuser"
        token = JWTHandler.create_access_token({"sub": username})

        decoded_username = JWTHandler.decode_access_token(token)

        assert decoded_username == username

    def test_decode_invalid_token(self):
        """Test: Decode invalid token"""
        invalid_token = "invalid.token.here"

        result = JWTHandler.decode_access_token(invalid_token)

        assert result is None

    def test_decode_expired_token(self):
        """Test: Decode expired token"""
        data = {"sub": "testuser"}
        # Create token that expires immediately
        expires = timedelta(seconds=-1)
        token = JWTHandler.create_access_token(data, expires_delta=expires)

        result = JWTHandler.decode_access_token(token)

        assert result is None


class TestUserRepository:
    """Test User Repository"""

    def test_initialize_default_users(self):
        """Test: Default users created on init"""
        repo = UserRepository()

        admin = repo.get_user("admin")
        user = repo.get_user("user")

        assert admin is not None
        assert user is not None
        assert admin.username == "admin"
        assert user.username == "user"

    def test_create_new_user(self, user_repository):
        """Test: Create new user"""
        user = user_repository.create_user(
            username="newuser", email="new@example.com", full_name="New User", password="newpass123"
        )

        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.full_name == "New User"
        assert user.hashed_password != "newpass123"  # Should be hashed
        assert user.is_active is True

    def test_create_duplicate_user(self, user_repository):
        """Test: Cannot create duplicate username"""
        user_repository.create_user(
            username="duplicate", email="dup1@example.com", full_name="First User", password="pass123"
        )

        with pytest.raises(ValueError, match="already exists"):
            user_repository.create_user(
                username="duplicate",  # Same username
                email="dup2@example.com",
                full_name="Second User",
                password="pass456",
            )

    def test_get_existing_user(self, user_repository):
        """Test: Get existing user"""
        user = user_repository.get_user("admin")

        assert user is not None
        assert user.username == "admin"
        assert user.email == "admin@hotel.com"

    def test_get_non_existing_user(self, user_repository):
        """Test: Get non-existent user"""
        user = user_repository.get_user("nonexistent")
        assert user is None

    def test_authenticate_valid_credentials(self, user_repository):
        """Test: Authenticate with valid credentials"""
        user = user_repository.authenticate_user("admin", "admin123")

        assert user is not None
        assert user.username == "admin"

    def test_authenticate_wrong_password(self, user_repository):
        """Test: Authenticate with wrong password"""
        user = user_repository.authenticate_user("admin", "wrongpassword")
        assert user is None

    def test_authenticate_non_existing_user(self, user_repository):
        """Test: Authenticate non-existent user"""
        user = user_repository.authenticate_user("nonexistent", "anypass")
        assert user is None

    def test_user_dataclass(self):
        """Test: User dataclass"""
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashedpass123",
            is_active=True,
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
