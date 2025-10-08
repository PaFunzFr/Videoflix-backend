from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video saved') # always executed
    if created:
        print('New video created')



# post_save after saving
# pre_save before saving

# post_delete
# pre_delete

# post_save.connect(video_post_save, sender=Video)