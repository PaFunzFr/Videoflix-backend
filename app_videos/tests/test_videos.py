from django.contrib.auth import get_user_model
from app_videos.models import Video
from django.urls import reverse
from django.http import FileResponse
from unittest.mock import Mock, patch

User = get_user_model()


def test_get_video_list_valid(auth_client, test_video):
    url = reverse('video-list') 
    response = auth_client.get(url, format="json")
    assert response.status_code == 200

    results = response.json()
    video_data = results[0]
    assert video_data['id'] == test_video.pk
    assert video_data['thumbnail_url'] is None


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


def test_video_post_save_signal_enqueues_tasks(db):
    with patch("app_videos.signals.django_rq.get_queue") as mock_get_queue:
        mock_queue = mock_get_queue.return_value
        mock_queue.enqueue = Mock()

        video = Video.objects.create(
            title="Test Video",
            video_file="dummy.mp4",
            category="Test"
        )
        #expecting 4 tasks (3 convertions, 1 masterfile)
        assert mock_queue.enqueue.call_count == 4
