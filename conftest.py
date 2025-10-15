import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def register_test_user():
    register_user = {
        "email":"register_user@email.com",
        "password":"Password123",
    }
    return register_user

@pytest.fixture
def created_registered_test_user(db):
    register_test_user = User.objects.create_user(
        username="register-testuser",
        email="register_user@email.com",
        password="Password123"
    )
    return register_test_user

@pytest.fixture
def test_user(db):
    """
    Fixture to create a test user.

    Returns:
        User: A newly created user instance with predefined username, email, and password.
    """
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="Password123"
    )
    return user


@pytest.fixture
def api_client():
    """
    Fixture to provide an unauthenticated DRF APIClient instance.

    Returns:
        APIClient: DRF test client without authentication credentials.
    """
    return APIClient()


@pytest.fixture
def token_pair(test_user):
    """
    Fixture to generate JWT access and refresh tokens for a given user.

    Args:
        test_user (User): The user for whom tokens are generated.

    Returns:
        dict: Dictionary containing 'access' and 'refresh' tokens as strings.
    """
    refresh = RefreshToken.for_user(test_user)
    access = str(refresh.access_token)
    refresh = str(refresh)
    return {"access": access, "refresh": refresh}


@pytest.fixture
def auth_client(api_client, token_pair):
    """
    Fixture to provide an authenticated APIClient using JWT cookies.

    Args:
        api_client (APIClient): The DRF test client.
        token_pair (dict): Dictionary containing 'access' and 'refresh' JWT tokens.

    Returns:
        APIClient: APIClient with JWT cookies set for authentication.
    """
    api_client.cookies["access_token"] = token_pair["access"]
    api_client.cookies["refresh_token"] = token_pair["refresh"]
    return api_client


@pytest.fixture
def auth_client_with_refresh(api_client, token_pair):
    """
    Provides an APIClient with a valid refresh token cookie set.
    """
    api_client.cookies["refresh_token"] = token_pair["refresh"]
    return api_client