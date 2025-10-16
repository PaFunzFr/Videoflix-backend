"""
test_registration.py
-------------------
Integration test for the user registration endpoint.

This test verifies that:
    • A new user can successfully register with valid credentials.
    • A confirmation email is queued for sending via RQ.
    • The newly registered user is initially inactive, requiring email confirmation.

Fixtures:
    auth_client: Authenticated DRF test client.
    mock_rq_enqueue: Mock for the RQ queue to capture enqueue calls.
    register_test_user: Provides sample user registration data.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_registration_sends_email(auth_client, mock_rq_enqueue, register_test_user):
    """
    Test that user registration triggers email confirmation workflow.

    Steps:
        1. Submit registration payload with email, password, and confirmed password.
        2. Assert that the HTTP response status is 201 CREATED.
        3. Assert that the email sending function was enqueued via RQ.
        4. Assert that the created user exists in the database and is inactive.

    This ensures that the registration endpoint correctly registers users 
    and triggers asynchronous email confirmation.
    """
    payload = {
        "email": register_test_user["email"],
        "password": register_test_user["password"],
        "confirmed_password": register_test_user["password"],
    }
    url = reverse("register")
    response = auth_client.post(url, payload, format="json")

    assert response.status_code == 201
    assert mock_rq_enqueue.get('called') is True

    user = User.objects.get(email=payload["email"])
    assert not user.is_active