from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import force_authenticate
from django.urls import reverse
from django.http import FileResponse


User = get_user_model()


def test_get_video_list_valid(auth_client):
    url = reverse('video-list') 
    response = auth_client.get(url, format="json")
    assert response.status_code == 200


def test_get_video_list_invalid(api_client):
    url = reverse('video-list')
    response = api_client.get(url, format="json")
    assert response.status_code == 401


def test_serve_hls_playlist_permission_denied(api_client):
    url = "/api/video/1/480p/index.m3u8"
    response = api_client.get(url, format="json")
    assert response.status_code == 401


def test_serve_hls_playlist_success(auth_client):
    url = "/api/video/1/480p/index.m3u8"
    response = auth_client.get(url)
    assert response.status_code == 200
    assert isinstance(response, FileResponse)
    assert response['Content-Type'] == 'application/vnd.apple.mpegurl'