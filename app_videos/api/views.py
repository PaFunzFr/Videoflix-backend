from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics
from app_videos.models import Video
from app_auth.api.views import CookieJWTAuthentication
from .serializers import VideoListSerializer
from pathlib import Path
from django.http import FileResponse, Http404
from django.conf import settings


def auth_permission_check(request):
    # Authentication
    user_auth = CookieJWTAuthentication().authenticate(request)
    if user_auth is None:
        raise PermissionDenied("Authentication credentials were not provided")

    # Permission Check
    if not IsAuthenticated().has_permission(request, None):
        raise PermissionDenied("User not allowed")


class VideoListView(generics.ListAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer
    queryset = Video.objects.all()


def serve_hls_playlist(request, pk, resolution):
    auth_permission_check(request)
    file_path = Path(settings.MEDIA_ROOT) / f"video/{pk}/{resolution}/index.m3u8"
    if not file_path.exists():
        raise Http404("HLS playlist not found.")
    return FileResponse(open(file_path, 'rb'), content_type='application/vnd.apple.mpegurl')


def serve_hls_segment(request, pk, resolution, segment):
    auth_permission_check(request)
    file_path = Path(settings.MEDIA_ROOT) / f"video/{pk}/{resolution}/{segment}"
    if not file_path.exists():
        raise Http404("Segment not found.")
    return FileResponse(open(file_path, 'rb'), content_type='video/mp2t')