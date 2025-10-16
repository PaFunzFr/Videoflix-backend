"""
test_token_refresh.py
---------------------
Unit tests for the token refresh endpoint in the authentication system.

These tests verify the correct behavior of the `CookieTokenRefreshView`, 
which is responsible for issuing a new access token using a valid refresh 
token stored in the client's cookies.

Scenarios covered:
    • Successful token refresh with valid refresh cookie.
    • Missing refresh cookie resulting in an HTTP 401 Unauthorized response.
    • Invalid refresh cookie resulting in an HTTP 401 Unauthorized response.

Each test ensures the correct response structure, status code, 
and cookie handling behavior according to authentication standards.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()
refresh_url = reverse("refresh-token")


def test_refresh_success(auth_client_with_refresh):
    """
    Verify that a valid refresh token allows the user to obtain a new access token.

    This test sends a POST request with a valid `refresh_token` cookie 
    and expects a 200 OK response containing the refreshed access token 
    in both the response body and as an updated `access_token` cookie.
    """
    response = auth_client_with_refresh.post(refresh_url)
    assert response.status_code == 200
    assert "Token refreshed" in str(response.data)
    assert "access" in response.data

    # cookie set?
    assert "access_token" in response.cookies
    assert response.cookies["access_token"].value != ""


def test_refresh_no_cookie(api_client):
    """
    Ensure that a missing refresh token cookie results in a 401 Unauthorized response.

    The endpoint should deny access and return an appropriate error message 
    indicating that the refresh token could not be found.
    """
    response = api_client.post(refresh_url)
    assert response.status_code == 401
    assert "Refresh Token not found." in str(response.data)


def test_refresh_invalid_cookie(api_client):
    """
    Ensure that an invalid refresh token cookie is rejected with a 401 Unauthorized response.

    This test simulates an invalid or tampered refresh token and verifies that 
    the API responds with an appropriate error message and does not issue a new access token.
    """
    api_client.cookies["refresh_token"] = "FAKETOKEN123"
    response = api_client.post(refresh_url)
    assert response.status_code == 401
    assert "Refresh Token invalid" in str(response.data)