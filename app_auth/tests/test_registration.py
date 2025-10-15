import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
def test_registration_sends_email(auth_client, mock_rq_enqueue, register_test_user):

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