from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from tasks.models import Task, TaskCreateLog
from .models import CustomUserCreateLog, CustomUserProfile

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


admin.site.register(CustomUserProfile)
admin.site.register(CustomUserCreateLog)
admin.site.register(Task)
admin.site.register(TaskCreateLog)
