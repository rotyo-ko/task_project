from django.urls import path
from .api_views import (
    TaskListCreateAPIView,
    TaskDetailAPIView,
    TaskMarkDoneAPIView,
    TaskReopenAPIView,
)


urlpatterns = [
    path('tasks/', TaskListCreateAPIView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailAPIView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/mark_done/", TaskMarkDoneAPIView.as_view(), name="task-mark_done"),
    path("tasks/<int:pk>/reopen/", TaskReopenAPIView.as_view(), name="task-reopen")
]