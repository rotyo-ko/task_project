from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "creator",
            "members",
            "description", 
            "status", 
            "due_date",
            "completed_at"
        ]
        read_only_fields = [
            "creator",
            "created_at", 
            "completed_at", 
            "updated_at",
        ]