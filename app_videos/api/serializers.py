from rest_framework import serializers
from django.conf import settings
from app_videos.models import Video
from rest_framework.reverse import reverse

class VideoListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing video instances with relevant metadata.

    Methods:
        get_thumbnail_url(obj):
            Constructs the absolute URL for the video's thumbnail, considering the request context.
    """
    thumbnail_url = serializers.SerializerMethodField()
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']

    def get_thumbnail_url(self, obj):
        request = self.context.get("request")
        return reverse("video-thumbnail", args=[obj.pk], request=request)