from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Task, TaskCreateLog

@receiver(post_save, sender=Task)
def task_created(sender, instance, created, **kwargs):
    if created:
        try:
            TaskCreateLog.objects.create(task=instance)
        except Exception as e:
            print(f"Failed to create task log: {e}")