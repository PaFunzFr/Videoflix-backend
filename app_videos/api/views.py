from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from app_videos.models import Video
from app_auth.api.views import CookieJWTAuthentication
from .serializers import VideoListSerializer
from pathlib import Path
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView


class VideoListView(generics.ListAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer
    queryset = Video.objects.all()


class ServeHLSPlaylistView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, resolution):
        file_path = Path(settings.MEDIA_ROOT) / f"video/{pk}/{resolution}/index.m3u8"
        if not file_path.exists():
            raise Http404("HLS playlist not found.")
        return FileResponse(open(file_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class ServeHLSSegmentView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, resolution, segment):
        file_path = Path(settings.MEDIA_ROOT) / f"video/{pk}/{resolution}/{segment}"
        if not file_path.exists():
            raise Http404("Segment not found.")
        return FileResponse(open(file_path, 'rb'), content_type='video/mp2t')