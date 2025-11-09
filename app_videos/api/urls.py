from django.urls import path
from .views import VideoListView, ServeHLSPlaylistView, ServeHLSSegmentView, ServeThumbnailView

urlpatterns = [
    path('video/', VideoListView.as_view(), name="video-list"),
    path("video/<int:pk>/thumbnail/", ServeThumbnailView.as_view(), name="video-thumbnail"),
    path('video/<int:pk>/<str:resolution>/index.m3u8', ServeHLSPlaylistView.as_view(), name='serve_hls_playlist'),
    path('video/<int:pk>/<str:resolution>/<str:segment>', ServeHLSSegmentView.as_view(), name='serve_hls_segment'),
]

