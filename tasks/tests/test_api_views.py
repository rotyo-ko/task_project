from datetime import date, datetime
from unittest.mock import patch
from django.utils import timezone
from rest_framework.test import APITestCase

from ..models import Task


class TaskAPITest(APITestCase):
    def setUp(self):
        self.task = Task.objects.create(
            title="test",
            description="test_description",
            due_date=date(2026, 2, 24)
        )
    
    def test_get_tasks(self):
        res = self.client.get("/api/tasks/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], "test")
        self.assertEqual(res.data[0]["description"], "test_description")
        self.assertEqual(res.data[0]["status"], Task.STATUS_TODO)
        self.assertEqual(res.data[0]["due_date"], "2026-02-24")

    def test_get_id(self):
        res = self.client.get(f"/api/tasks/{self.task.pk}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "test")
        self.assertEqual(res.data["description"], "test_description")
        self.assertEqual(res.data["status"], Task.STATUS_TODO)
        self.assertEqual(res.data["due_date"], "2026-02-24")

    def test_put_id(self):
        res = self.client.put(
            f"/api/tasks/{self.task.pk}/",
            data={
                "title":"updated",
                }
            )
        self.assertEqual(res.data["title"], "updated")
        self.assertEqual(res.data["description"], "test_description")
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, "test_description")
        self.assertEqual(self.task.title, "updated")

    def test_put_invalid(self):
        res = self.client.put(
            f"/api/tasks/{self.task.pk}/",
            data={"description": "updated"},
        )
        self.assertEqual(res.status_code, 400)

    def test_patch_id(self):
        res = self.client.patch(
            f"/api/tasks/{self.task.pk}/",
            data={
                "description":"updated",
                }
            )
        self.assertEqual(res.data["title"], "test")
        self.assertEqual(res.data["description"], "updated")
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "test")
        self.assertEqual(self.task.description, "updated")

    def test_delete_id(self):
        res = self.client.delete(f"/api/tasks/{self.task.pk}/")
        self.assertEqual(res.status_code, 204)
        self.assertEqual(Task.objects.count(), 0)


class TaskCreateAPI(APITestCase):
    def test_post_task(self):
        res = self.client.post(
            "/api/tasks/",
            data={
                "title":"post_title",
                "description": "post_description",
                "due_date": date(2026, 2, 24)
            }
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["title"], "post_title")
        self.assertEqual(res.data["description"], "post_description")
        self.assertEqual(res.data["due_date"], "2026-02-24")

    def test_post_invalid(self):
        res = self.client.post("/api/tasks/", data={})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Task.objects.count(), 0)

class TestTaskMarkDone(APITestCase):
    
    @patch("tasks.models.timezone.now")
    def test_post_mark_done(self, mock_now):

        mock_now.return_value = timezone.make_aware(
            datetime(2026, 1, 1, 0, 0, 0)
        )
        self.task = Task.objects.create(
            title="test",
        )
        res = self.client.post(f"/api/tasks/{self.task.pk}/mark_done/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "test")
        self.assertEqual(res.data["status"], Task.STATUS_DONE)
        self.assertIn("2026-01-01T00:00:00", res.data["completed_at"])
               
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.STATUS_DONE)
        expected = timezone.make_aware(
            datetime(2026, 1, 1, 0, 0, 0)
        )
        self.assertEqual(self.task.completed_at, expected)
    
    def test_post_mark_done_404(self):
        res = self.client.post("/api/tasks/100/mark_done/")
        self.assertEqual(res.status_code, 404)

    def test_mark_done_with_done(self):
        self.task = Task.objects.create(
            title="test",
            status=Task.STATUS_DONE,
        )
        
        res = self.client.post(f"/api/tasks/{self.task.pk}/mark_done/")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data[0], "すでに終了しています。")
        


class TestTaskReopen(APITestCase):
    
    def test_reopen(self):
        self.task = Task.objects.create(
            title="test",
            status=Task.STATUS_DONE,
            completed_at=timezone.make_aware(
                datetime(2026, 1, 1, 0, 0, 0)
            ))
        res = self.client.post(f"/api/tasks/{self.task.pk}/reopen/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["title"], "test")
        self.assertEqual(res.data["status"], Task.STATUS_TODO)
        self.assertIsNone(res.data["completed_at"])
        
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.STATUS_TODO)
        self.assertIsNone(self.task.completed_at)

    def test_reopen_without_done(self):
        self.task = Task.objects.create(
            title="test",
            status=Task.STATUS_DOING
        )
        
        res = self.client.post(f"/api/tasks/{self.task.pk}/reopen/")
        self.assertEqual(res.data[0], '終了状態ではありません。')
        self.assertEqual(res.status_code, 400)

        
