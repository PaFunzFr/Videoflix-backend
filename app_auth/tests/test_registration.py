from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_registration(auth_client):
    pass