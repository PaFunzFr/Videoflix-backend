import pytest
from django.core import mail
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


@pytest.mark.django_db
def test_registration_link_in_email(auth_client, monkeypatch, register_test_user):
    called = {}

    def fake_enqueue(func, *args, **kwargs):
        called['called'] = True

    monkeypatch.setattr('django_rq.get_queue', lambda *a, **k: type('Q', (), {'enqueue': fake_enqueue})())

    payload = {
        "email": register_test_user["email"],
        "password": register_test_user["password"],
        "confirmed_password": register_test_user["password"],
    }
    url = reverse("register")
    response = auth_client.post(url, payload, format="json")

    assert response.status_code == 201
    assert called.get('called') is True


@pytest.mark.django_db
def test_user_activation(auth_client, created_registered_test_user):
    uid = urlsafe_base64_encode(force_bytes(created_registered_test_user.pk))
    token = default_token_generator.make_token(created_registered_test_user)
    url = reverse('activate', args=[uid, token])
    response = auth_client.get(url)
    assert response.status_code == 200

    created_registered_test_user.refresh_from_db()
    assert created_registered_test_user.is_active