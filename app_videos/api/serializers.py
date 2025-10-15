from rest_framework import serializers
from django.conf import settings
from app_videos.models import Video

class VideoListSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return f"{settings.MEDIA_URL}{obj.thumbnail.name}"
        return None