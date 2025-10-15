import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
def test_registration_sends_email(auth_client, monkeypatch, register_test_user):
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

    user = User.objects.get(email=payload["email"])
    assert not user.is_active