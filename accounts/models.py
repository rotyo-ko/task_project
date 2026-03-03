from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    """拡張ユーザーモデル"""
    class Meta:
        verbose_name_plural = "CustomUser"
    @property
    def name(self):
        return f"{self.last_name} {self.first_name}"
       
class CustomUserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    bio = models.TextField("自己紹介", blank=True, max_length=5000)
    

class CustomUserCreateLog(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_create_log"
    )
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
