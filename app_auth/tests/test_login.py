"""
test_login_and_logout.py
------------------------
Integration tests for the authentication system, covering login and logout behavior.

These tests validate the end-to-end functionality of the authentication flow,
ensuring that JSON Web Tokens (JWT) are properly issued, stored in cookies,
and invalidated upon logout.

Test Coverage:
    • Login via email and password.
    • Secure cookie creation for access and refresh tokens.
    • Token cleanup and cookie deletion during logout.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


def test_login(auth_client, test_user):
    """
    Verify that a registered user can successfully log in and receive JWT cookies.

    This test submits valid user credentials to the login endpoint and expects:
        • HTTP 200 OK response.
        • A confirmation message in the response body.
        • Secure HTTP-only cookies (`access_token`, `refresh_token`) to be set.
        • Non-empty token values for both cookies.

    The test ensures that authentication and token handling are functioning as expected.
    """
    url = reverse('login') 
    payload = {
        "email": test_user.email,
        "password": "Password123" #set from test_user in conftest.py
    }
    response = auth_client.post(url, payload, format="json")

    # Login successful?
    assert response.status_code == 200
    assert "detail" in response.data
    assert "Login successfully!" in str(response.data)

    # Cookies created?
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # Token set?
    assert cookies["access_token"].value != ""
    assert cookies["refresh_token"].value != ""


def test_logout(auth_client):
    """
    Ensure that an authenticated user can log out and all authentication cookies are removed.

    This test performs a POST request to the logout endpoint and expects:
        • HTTP 200 OK response.
        • A success message confirming logout.
        • Both JWT cookies (`access_token`, `refresh_token`) to be deleted.
        • `max-age` set to 0 for both cookies, confirming removal.

    This guarantees proper session cleanup and secure token invalidation.
    """
    url = reverse('logout') 
    response = auth_client.post(url)
    
    assert response.status_code == 200
    assert "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid." in str(response.data)
    
    # check if cookies were deleted
    cookies = response.cookies

    assert cookies["access_token"].value == ""
    assert cookies["refresh_token"].value == ""
    assert cookies["access_token"]["max-age"] == 0
    assert cookies["refresh_token"]["max-age"] == 0