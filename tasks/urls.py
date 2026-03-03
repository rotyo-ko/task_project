from django.urls import path

from .views import (
    TaskListView,
    TaskDetailView,
    TaskCreateView,
    TaskDeleteView,
    TaskUpdateView,
    TaskCompleteView,
    TaskReopenView,
    TaskCreateLogListView,
)

app_name = "tasks"

urlpatterns = [
    path("", TaskListView.as_view(), name="list"),
    path("list/overdue/", TaskListView.as_view(), kwargs={"mode": "overdue"},
         name="overdue_list"),
    path("list/completed/", TaskListView.as_view(), kwargs={"mode": "completed"},
         name="completed_list"),
    path("<int:pk>/", TaskDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", TaskUpdateView.as_view(), name="edit"),
    path("create/", TaskCreateView.as_view(), name="create"),
    path("<int:pk>/delete/", TaskDeleteView.as_view(),
         name="delete"),
    path("<int:pk>/complete/", TaskCompleteView.as_view(),
         name="complete"),
    path("<int:pk>/reopen", TaskReopenView.as_view(),
        name="reopen"),
    path("list/log/", TaskCreateLogListView.as_view(), name="log"),

]