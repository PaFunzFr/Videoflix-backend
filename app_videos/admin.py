from django import forms
from django.contrib import admin
from .models import Video, CATEGORY_CHOICES


class VideoAdminForm(forms.ModelForm):
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