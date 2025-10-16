"""
admin_video.py
---------------
Custom Django Admin configuration for the Video model.

Key Components:
    • VideoAdminForm – A custom ModelForm with an explicitly required
      category choice field, ensuring no uncategorized videos are created.
    • VideoAdmin – The associated admin interface configuration that applies
      the custom form and simplifies video management for administrators.

The configuration improves data consistency, user experience, and complies
with internal data validation standards used throughout the application.
"""

from django import forms
from django.contrib import admin
from .models import Video, CATEGORY_CHOICES


class VideoAdminForm(forms.ModelForm):
    """
    This form customizes the 'category' field to use a dropdown menu with 
    predefined choices, including a placeholder option prompting the user 
    to choose a category. The category field is mandatory, ensuring all videos 
    are categorized before saving.
    """
    category = forms.ChoiceField(
        choices=[("", "Choose Category")] + CATEGORY_CHOICES,
        required=True,
    )

    class Meta:
        model = Video
        fields = "__all__"

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    form = VideoAdminForm