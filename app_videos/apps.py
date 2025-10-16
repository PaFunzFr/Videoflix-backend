from django.apps import AppConfig


class AppVideosConfig(AppConfig):
    """
    Configuration class for the 'app_videos' Django application.

    This class ensures that the app's signal handlers are imported and registered
    when the application is ready, enabling signal-based events such as video processing
    task triggers.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_videos'

    def ready(self):
        from . import signals