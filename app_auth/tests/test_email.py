"""
test_user_registration_and_activation.py
----------------------------------------
Integration tests for user registration and account activation functionality.

These tests verify that:
    • A registration request triggers the asynchronous email confirmation workflow.
    • The user activation endpoint correctly validates and activates user accounts
      using a valid UID and token combination.

The tests ensure proper behavior of the registration process, background email
queueing via RQ, and account activation flow, in compliance with authentication
and security standards.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


def test_registration_link_in_email(auth_client, mock_rq_enqueue, register_test_user):
    """
    Verify that user registration successfully queues an email confirmation task.

    This test submits a valid registration payload and expects:
        • HTTP 201 Created response.
        • An asynchronous task enqueued via RQ to send the confirmation email.

    The test does not assert the actual email content, focusing instead on
    confirming that the background job has been triggered.
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


def test_user_activation(auth_client, created_registered_test_user):
    """
    Ensure that an inactive user can be successfully activated using a valid link.

    The test generates a valid activation UID and token for a newly registered
    user, performs a GET request to the activation endpoint, and expects:
        • HTTP 200 OK response.
        • The user’s `is_active` field to be updated to True.

    This validates the token-based activation logic used in the email
    confirmation process.
    """
    uid = urlsafe_base64_encode(force_bytes(created_registered_test_user.pk))
    token = default_token_generator.make_token(created_registered_test_user)
    url = reverse('activate', args=[uid, token])
    response = auth_client.get(url)
    assert response.status_code == 200

    created_registered_test_user.refresh_from_db()
    assert created_registered_test_user.is_active