import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from app_videos.models import Video
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

@pytest.fixture
def register_test_user():
    """
    Provides data for registering a test user.

    Returns:
        dict: A dictionary containing 'email' and 'password' keys with
              sample user registration credentials.
    """
    register_user = {
        "email":"register_user@email.com",
        "password":"Password123",
    }
    return register_user

@pytest.fixture
def created_registered_test_user(db):
    """
    Creates and returns a registered user in the test database.

    Args:
        db: pytest-django database access fixture.

    Returns:
        User: A Django User model instance representing the registered user.
    """
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
def test_video(db):
    """
    Creates and returns a Video instance without a thumbnail for testing purposes.

    Args:
        db: pytest-django database fixture for database access during tests.

    Returns:
        Video: An instance of the Video model with specified test data.
    """
    video = Video.objects.create(
        title="Ohne Thumbnail",
        description="Testbeschreibung",
        video_file="dummy.mp4",
        thumbnail=None,
        category="Comedy"
    )
    return video

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


@pytest.fixture
def mock_rq_enqueue():
    """
    Mocks django_rq's queue enqueue method to track if tasks are enqueued.

    This fixture replaces the 'enqueue' method with a simple callable that sets
    a flag when called, allowing tests to verify if asynchronous jobs are triggered.

    Yields:
        dict: A dictionary with a 'called' key set to True upon enqueue invocation.
    """
    called = {}

    def fake_enqueue(func, *args, **kwargs):
        called['called'] = True

    with patch("django_rq.get_queue") as mock_get_queue:
        mock_get_queue.return_value.enqueue = fake_enqueue
        yield called 