from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from app_videos.models import Video
from app_auth.api.views import CookieJWTAuthentication
from .serializers import VideoListSerializer
from pathlib import Path
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse


@extend_schema(
    tags=["Videos"],
    summary="Retrieve a list of available videos",
    description=(
        "Returns a list of all available videos for authenticated users. "
        "Each entry provides video metadata including title, description, category, and thumbnail URL."
    ),
    responses={
        200: OpenApiResponse(response=VideoListSerializer(many=True), description="Successfully retrieved list of videos."),
        401: OpenApiResponse(description="Unauthorized – authentication credentials were not provided or invalid."),
    },
)
class VideoListView(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all stored videos.

    This endpoint allows authenticated users to fetch all videos available in the system.  
    It requires a valid JWT access token to be present in the user's cookies.  
    Each video entry contains descriptive and relational metadata needed for playback or management.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer
    queryset = Video.objects.all()


@extend_schema(
    tags=["Videos"],
    summary="Serve an HLS playlist file (.m3u8)",
    description=(
        "Retrieves the HLS playlist file for a given video and resolution. "
        "The playlist defines how HLS-compatible clients (e.g., video players) stream segmented video data."
    ),
    responses={
        200: OpenApiResponse(description="M3U8 playlist file returned successfully."),
        401: OpenApiResponse(description="Unauthorized – missing or invalid authentication."),
        404: OpenApiResponse(description="HLS playlist not found at the specified path."),
    },
)
class ServeHLSPlaylistView(APIView):
    """
    Serves the primary HLS playlist file (.m3u8) for a specific video resolution.

    This endpoint streams the `.m3u8` playlist used by clients to initiate adaptive bitrate playback.  
    If the file does not exist in the expected directory path, a 404 HTTP error is returned.  

    **Expected File Path:**  
    `MEDIA_ROOT/video/<video_id>/<resolution>/index.m3u8`
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, resolution):
        file_path = Path(settings.MEDIA_ROOT) / f"video/{pk}/{resolution}/index.m3u8"
        if not file_path.exists():
            raise Http404("HLS playlist not found.")
        return FileResponse(open(file_path, 'rb'), content_type='application/vnd.apple.mpegurl')


@extend_schema(
    tags=["Videos"],
    summary="Serve an HLS video segment (.ts)",
    description=(
        "Provides access to a specific HLS video segment file, which is part of the adaptive streaming structure. "
        "Clients use these segment files to stream video data chunk by chunk."
    ),
    responses={
        200: OpenApiResponse(description="HLS video segment successfully returned."),
        401: OpenApiResponse(description="Unauthorized – authentication token invalid or missing."),
        404: OpenApiResponse(description="Requested video segment not found."),
    },
)
class ServeHLSSegmentView(APIView):
    """
    Serves an individual HLS video segment (.ts file) for playback.

    Segments are part of the HLS streaming protocol and are requested sequentially by video players.  
    Each segment represents a small piece (usually a few seconds) of the full video.

    **Expected File Path:**  
    `MEDIA_ROOT/video/<video_id>/<resolution>/<segment_name>.ts`
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, resolution, segment):
        file_path = Path(settings.MEDIA_ROOT) / f"video/{pk}/{resolution}/{segment}"
        if not file_path.exists():
            raise Http404("Segment not found.")
        return FileResponse(open(file_path, 'rb'), content_type='video/mp2t')