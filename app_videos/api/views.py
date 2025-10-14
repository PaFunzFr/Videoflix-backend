from rest_framework.permissions import IsAuthenticated 
from rest_framework import generics
from app_videos.models import Video
from app_auth.api.views import CookieJWTAuthentication
from .serializers import VideoListSerializer

class VideoListView(generics.ListAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VideoListSerializer
    queryset = Video.objects.all()