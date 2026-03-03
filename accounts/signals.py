from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import CustomUser, CustomUserCreateLog, CustomUserProfile


User = get_user_model()

@receiver(post_save, sender=User)
def customuser_created(sender, instance, created, **kwargs):
    if created:
        try:
            CustomUserCreateLog.objects.create(user=instance)
            CustomUserProfile.objects.create(user=instance)
        except Exception as e:
            print(f"Failed to create user log: {e}")