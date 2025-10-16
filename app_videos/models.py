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
    """
    Database model representing a video entity.

    Attributes:
        title (CharField): The title of the video, max length 80 characters.
        description (CharField): A brief description or summary of the video, max length 500 characters.
        thumbnail (ImageField): Optional image representing a thumbnail for the video,
                                stored under 'thumbnail/tmp/', can be null or blank.
        video_file (FileField): Optional uploaded video media file,
                                stored under 'video/tmp/', can be null or blank.
        category (CharField): Required categorical classification of the video,
                              restricted to predefined CATEGORY_CHOICES.
        created_at (DateTimeField): Timestamp showing when the video record was created,
                                   automatically set on record insertion.

    Methods:
        __str__: Returns a concise string representation including primary key, title,
                  description fallback, category, and upload datetime formatted as 'YYYY-MM-DD HH:mm'.
    """
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    thumbnail = models.ImageField(upload_to="thumbnail/tmp/", blank=True, null=True)
    video_file = models.FileField(upload_to="video/tmp/", blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, blank=False, null = False, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk} | {self.title} | {self.description or 'Video Description'} | {self.category} | Uploaded: {self.created_at:%Y-%m-%d %H:%M}"