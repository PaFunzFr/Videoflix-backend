import shutil
from pathlib import Path
from django.conf import settings
import django_rq
from .tasks import convert_video_to_hls, create_master_playlist
from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


VIDEO_FORMATS = [
    #("name", "scale", "video_bitrate", "audio_bitrate")
    ("480p", "854:480", "800k", "96k"),
    ("720p", "1280:720", "2800k", "128k"),
    ("1080p", "1920:1080", "5000k", "192k"),
]

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        queue = django_rq.get_queue('default', autocommit=True)

        queue.enqueue(convert_video_to_hls, instance.id, *VIDEO_FORMATS[0])  # 480p
        queue.enqueue(convert_video_to_hls, instance.id, *VIDEO_FORMATS[1])  # 720p
        queue.enqueue(convert_video_to_hls, instance.id, *VIDEO_FORMATS[2])  # 1080p

        queue.enqueue(create_master_playlist, instance.id)


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):

    video_dir = Path(settings.MEDIA_ROOT) / f"video/{instance.pk}"
    if video_dir.exists() and video_dir.is_dir():
        # shutil / shell utilities -> remove tree (=> delete folder video/<video.pk>)
        shutil.rmtree(video_dir)

    if instance.thumbnail:
        path = Path(instance.thumbnail.path)
        if path.exists():
            path.unlink()
