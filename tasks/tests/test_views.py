from datetime import date, datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tasks.models import Task
from tasks.forms import TaskForm


class TestTaskList(TestCase):
    def setUp(self):
        self.task1 = Task.objects.create(
            title="test",
            description="test_description",
            due_date=date(2026, 2, 14),
        )
        
    def test_get(self):
        res = self.client.get(reverse("tasks:list"))
        self.assertTemplateUsed(res, "tasks/list.html")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["task_list"][0].title, "test")
        self.assertEqual(res.context["task_list"][0].description, "test_description")
        self.assertEqual(res.context["task_list"][0].due_date, date(2026, 2, 14))
        self.assertContains(res, "2026年02月14日")

class TestListStatus(TestCase):
    def setUp(self):
        self.task1 = Task.objects.create(
            title="test_todo",
            description="todo",
            due_date=date(2026, 2, 14),
            status = Task.STATUS_TODO

        )
        self.task2 = Task.objects.create(
            title="test_doing",
            description="doing",
            due_date=date(2026, 2, 14),
            status = Task.STATUS_DOING

        )
        self.task3 = Task.objects.create(
            title="test_done",
            description="done",
            due_date=date(2026, 2, 14),
            status = Task.STATUS_DONE

        )
    def test_get(self):
        res = self.client.get(reverse("tasks:list"))
        self.assertTemplateUsed(res, "tasks/list.html")
        self.assertEqual(len(res.context["task_list"]), 3)
    
    def test_get_with_status(self):
        res = self.client.get(reverse("tasks:list"), data={"status": "todo"})
        self.assertTemplateUsed(res, "tasks/list.html")
        self.assertEqual(len(res.context["task_list"]), 1)
        self.assertEqual(res.context["task_list"][0].title, "test_todo")
        self.assertEqual(res.context["task_list"][0].description, "todo")
        self.assertEqual(res.context["task_list"][0].due_date, date(2026, 2, 14))

class TestOverdueList(TestCase):
    @patch("django.utils.timezone.now")
    def test_overdue(self, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(2026, 2, 1, 12, 0, 0)
        )
        self.task1 =Task.objects.create(
            title="title1",
            description="over_due",
            due_date=date(2026, 1, 1),
        )
        self.task2 =Task.objects.create(
            title="title2",
            description="under_due",
            due_date=date(2026, 3, 1),
        )
        res = self.client.get(reverse("tasks:overdue_list"))
        self.assertTemplateUsed(res, "tasks/list.html")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context["task_list"]), 1)
        self.assertEqual(res.context["task_list"][0].title, "title1")
        self.assertEqual(res.context["task_list"][0].description, "over_due")
        self.assertEqual(res.context["task_list"][0].due_date, date(2026, 1, 1))