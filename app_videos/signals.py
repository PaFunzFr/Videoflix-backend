"""
Video processing signals module

This module contains signal handlers that manage post-save and post-delete behaviors for the Video model.
These handlers integrate with Django RQ to enqueue asynchronous video processing tasks and handle media file cleanup.

Constants:
    VIDEO_FORMATS (list): Preset video quality specifications for transcoding.

Functions:
    video_post_save: Enqueues HLS video conversion and playlist creation tasks after a new Video instance is saved with a video file.
    auto_delete_file_on_delete: Cleans up video and thumbnail files from the filesystem when a Video instance is deleted.
"""

import shutil
from pathlib import Path
from django.conf import settings
import django_rq
from .tasks import convert_video_to_hls, create_master_playlist
from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db import transaction


VIDEO_FORMATS = [
    #("name", "scale", "video_bitrate", "audio_bitrate")
    ("480p", "854:480", "800k", "96k"),
    ("720p", "1280:720", "2800k", "128k"),
    ("1080p", "1920:1080", "5000k", "192k"),
]

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler triggered after saving a Video instance.

    If a new Video with an associated video_file is created, this function
    enqueues asynchronous RQ tasks to convert the video into multiple HLS resolutions
    (480p, 720p, 1080p) and to create the master playlist.
    """
    if created and instance.video_file:
        def enqueue_tasks():
            queue = django_rq.get_queue('default', autocommit=True)

            queue.enqueue(convert_video_to_hls, instance.id, *VIDEO_FORMATS[0])  # 480p
            queue.enqueue(convert_video_to_hls, instance.id, *VIDEO_FORMATS[1])  # 720p
            queue.enqueue(convert_video_to_hls, instance.id, *VIDEO_FORMATS[2])  # 1080p

            queue.enqueue(create_master_playlist, instance.id)
        transaction.on_commit(enqueue_tasks)


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Signal handler triggered after deleting a Video instance.

    This function removes the associated video directory and thumbnail image file from
    the filesystem to clean up storage when the Video object is deleted.
    """
    video_dir = Path(settings.MEDIA_ROOT) / f"video/{instance.pk}"
    if video_dir.exists() and video_dir.is_dir():
        # Remove entire directory tree containing video files (=> delete folder video/<video.pk>)
        shutil.rmtree(video_dir)

    if instance.thumbnail:
        path = Path(instance.thumbnail.path)
        if path.exists():
            path.unlink()
