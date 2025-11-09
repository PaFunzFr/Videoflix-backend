"""
test_videos_api_and_signals.py
------------------------------
Integration and unit tests for video API endpoints and signal-based background processing.


These tests verify that:
    • Authenticated users can successfully retrieve video lists and HLS playlist files.
    • Unauthorized requests to video endpoints are properly rejected (HTTP 401).
    • The video post_save signal automatically enqueues background tasks for video
      conversion (480p, 720p, 1080p) and master playlist creation via RQ.


The tests ensure correct behavior of the video-serving API, secure authentication via
Cookie-based JWT, and reliable asynchronous task scheduling through Django signals.
"""

from django.contrib.auth import get_user_model
from app_videos.models import Video
from django.urls import reverse
from django.http import FileResponse
from unittest.mock import Mock, patch
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


def test_get_video_list_valid(auth_client, test_video):
    """
    Tests the video list API endpoint with a valid, authenticated client.

    Ensures that a successfully authenticated GET request to the video list endpoint
    returns HTTP 200 and includes the test video's metadata. Specifically, this
    test asserts that the returned `thumbnail_url` property is `None` for videos
    without a thumbnail file.
    """
    url = reverse('video-list') 
    response = auth_client.get(url, format="json")
    assert response.status_code == 200

    results = response.json()
    video_data = results[0]
    assert video_data['id'] == test_video.pk
    assert video_data['thumbnail_url'] is None


def test_get_video_list_invalid(api_client):
    """
    Tests that unauthenticated requests to the video list endpoint are denied.

    Sends a GET request to the video list endpoint using an unauthenticated API client
    and verifies that the response status code is 401 Unauthorized.
    """
    url = reverse('video-list')
    response = api_client.get(url, format="json")
    assert response.status_code == 401


def test_serve_hls_playlist_permission_denied(api_client):
    """
    Validates that unauthenticated requests for HLS playlists are rejected.

    Attempts to fetch an HLS playlist file (.m3u8) without authentication and
    expects a 401 Unauthorized response.
    """
    url = "/api/video/1/480p/index.m3u8"
    response = api_client.get(url, format="json")
    assert response.status_code == 401


def test_serve_hls_playlist_success(auth_client):
    """
    Tests that authenticated users can retrieve an HLS playlist file.

    Sends a GET request for a specific .m3u8 playlist as an authenticated user and
    checks that:
      - the request is successful (HTTP 200),
      - the response is a Django FileResponse,
      - the content type is correct for an HLS playlist.
    """
    video = Video.objects.create(
        id=1,
        title="Test Video",
        video_file="dummy.mp4",
        category="Test"
    )
    url = "/api/video/1/480p/index.m3u8"
    response = auth_client.get(url)
    assert response.status_code == 200
    assert isinstance(response, FileResponse)
    assert response['Content-Type'] == 'application/vnd.apple.mpegurl'


def run_on_commit_immediately(func):
    """
    Executes the given function immediately instead of deferring it with `transaction.on_commit`.

    This helper is typically used in tests to run Django signal handlers or RQ tasks 
    that are normally registered via `transaction.on_commit` directly and synchronously, 
    without waiting for the database transaction to complete.

    Args:
        func (Callable): The function to execute immediately.
    """
    func()


def test_video_post_save_signal_enqueues_tasks(db):
    """
    Ensures the Video post_save signal enqueues conversion/master tasks.

    This test mocks the RQ queue and creates a new Video instance with a video_file,
    then verifies that the signal handler enqueues 4 tasks:
        - 3 for HLS conversion (480p, 720p, 1080p)
        - 1 for thumbnail creation
        - 1 for master playlist creation
    """
    with patch("django_rq.get_queue") as mock_get_queue:
        mock_queue = mock_get_queue.return_value
        mock_queue.enqueue = Mock()

        # Patch transaction.on_commit
        with patch("django.db.transaction.on_commit", side_effect=run_on_commit_immediately):

            video = Video.objects.create(
                title="Test Video",
                video_file=SimpleUploadedFile("dummy.mp4", b"dummy content"), # Dummy File
                category="Test"
            )
        
        assert mock_queue.enqueue.call_count == 5
