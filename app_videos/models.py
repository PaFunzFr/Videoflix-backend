import os
from django.db import models
from django.utils.text import slugify

CATEGORY_CHOICES = [
    ("action", "Action"),
    ("adventure", "Adventure"),
    ("animation", "Animation"),
    ("comedy", "Comedy"),
    ("crime", "Crime"),
    ("documentary", "Documentary"),
    ("drama", "Drama"),
    ("fantasy", "Fantasy"),
    ("historical", "Historical"),
    ("horror", "Horror"),
    ("musical", "Musical"),
    ("mystery", "Mystery"),
    ("romance", "Romance"),
    ("science_fiction", "Science Fiction"),
    ("thriller", "Thriller"),
    ("war", "War"),
    ("western", "Western"),
    ("biography", "Biography"),
    ("family", "Family"),
    ("sport", "Sport"),
]


def thumbnail_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    safe_title = slugify(instance.title)
    pk_part = instance.pk if instance.pk else "tmp"
    return f"thumbnails/{pk_part}_{safe_title}/{base}{ext}"


def video_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    safe_title = slugify(instance.title)
    pk_part = instance.pk if instance.pk else "tmp"
    return f"videos/{pk_part}_{safe_title}/{base}{ext}"

class Video(models.Model):
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    thumbnail = models.ImageField(upload_to=thumbnail_upload_path, blank=True, null=True)
    video_file = models.FileField(upload_to=video_upload_path, blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, blank=False, null = False, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} | {self.description or 'Video Description'} | {self.category} | Uploaded: {self.created_at:%Y-%m-%d %H:%M}"