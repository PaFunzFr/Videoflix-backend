from django.urls import path
from .views import VideoListView, serve_hls_playlist, serve_hls_segment

urlpatterns = [
    path('video/', VideoListView.as_view(), name="video-list"),
    path('video/<int:pk>/<str:resolution>/index.m3u8', serve_hls_playlist, name='serve_hls_playlist'),
    path('video/<int:pk>/<str:resolution>/<str:segment>', serve_hls_segment, name='serve_hls_segment'),
]

