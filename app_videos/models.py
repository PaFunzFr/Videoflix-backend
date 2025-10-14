import os
from django.db import models

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

class Video(models.Model):
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    thumbnail = models.ImageField(upload_to="thumbnail/tmp/", blank=True, null=True)
    video_file = models.FileField(upload_to="videos/tmp/", blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, blank=False, null = False, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} | {self.description or 'Video Description'} | {self.category} | Uploaded: {self.created_at:%Y-%m-%d %H:%M}"