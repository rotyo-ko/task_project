from datetime import date, datetime
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from ..models import Task, TaskCreateLog
from ..forms import TaskForm


User = get_user_model()

class TestTaskList(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="password")
        self.member = User.objects.create_user(username="member", password="password")
        self.other = User.objects.create_user(username="other", password="password")
        self.task = Task.objects.create(
            creator=self.creator,
            title="test",
            description="test_description",
            due_date=date(2026, 2, 14),
        )
        
        self.task.members.set([self.member])
    def test_get_by_creator(self):
        """作成者がタスクを取得できるかテスト"""
        self.client.login(username="creator", password="password")
        res = self.client.get(reverse("tasks:list"))
        self.assertTemplateUsed(res, "tasks/list.html")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["task_list"][0].title, "test")
        self.assertEqual(res.context["task_list"][0].description, "test_description")
        self.assertEqual(res.context["task_list"][0].due_date, date(2026, 2, 14))
        self.assertEqual(res.context["task_list"][0].creator, self.creator)
        self.assertIn(self.member, res.context["task_list"][0].members.all())
        self.assertContains(res, "2026年02月14日")
    
    def test_get_by_member(self):
        """self.taskのmemberであるself.memberがタスクを取得できるかテスト"""
        self.client.login(username="member", password="password")
        res = self.client.get(reverse("tasks:list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["task_list"][0].title, "test")
        self.assertEqual(res.context["task_list"][0].description, "test_description")
        self.assertEqual(res.context["task_list"][0].due_date, date(2026, 2, 14))
        self.assertEqual(res.context["task_list"][0].creator, self.creator)
        self.assertIn(self.member, res.context["task_list"][0].members.all())
        self.assertContains(res, "2026年02月14日")

    def test_get_invalid(self):
        """creator, member でないユーザーがタスクを取得できないかチェック"""
        self.client.login(username="other", password="password")
        res = self.client.get(reverse("tasks:list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["task_list"].count(), 0)
    
    def test_get_invalid_without_login(self):
        res = self.client.get(reverse("tasks:list"))
        self.assertEqual(res.status_code, 302)


class TestListStatus(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="creator", password="password")
        self.client.login(username="creator", password="password")
        
        self.task1 = Task.objects.create(
            creator=self.user,
            title="test_todo",
            description="todo",
            due_date=date(2026, 2, 14),
            status = Task.STATUS_TODO

        )
        self.task2 = Task.objects.create(
            creator=self.user,
            title="test_doing",
            description="doing",
            due_date=date(2026, 2, 14),
            status = Task.STATUS_DOING

        )
        self.task3 = Task.objects.create(
            creator=self.user,
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
        self.user = User.objects.create_user(username="creator", password="password")
        self.client.login(username="creator", password="password")
        self.task1 = Task.objects.create(
            creator=self.user,
            title="title1",
            description="over_due",
            due_date=date(2026, 1, 1),
        )
        self.task2 =Task.objects.create(
            creator=self.user,
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

class TestTaskDetail(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="creator", password="password")
        self.member = User.objects.create_user(username="member", password="password")
        self.other = User.objects.create_user(username="other", password="password")
        self.task = Task.objects.create(
            creator=self.user,
            title="test",
            description="test_description",
            due_date=date(2026, 2, 14),
        )
        
        self.task.members.set([self.member])
    
    def test_get_by_creator(self):
        """作成者がタスクの詳細を取得できるか"""
        self.client.login(username="creator", password="password")
        res = self.client.get(reverse("tasks:detail", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "tasks/detail.html")
        self.assertEqual(res.context["task"].title, "test")
        self.assertEqual(res.context["task"].description, "test_description")
        self.assertEqual(res.context["task"].due_date, date(2026, 2, 14))
        self.assertIn(self.member, res.context["task"].members.all())

    def test_get_by_member(self):
        """"タスクのmemberがタスクの詳細を取得できるかチェック"""
        self.client.login(username="member", password="password")
        res = self.client.get(reverse("tasks:detail", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "tasks/detail.html")
        self.assertEqual(res.context["task"].title, "test")
        self.assertEqual(res.context["task"].description, "test_description")
        self.assertEqual(res.context["task"].due_date, date(2026, 2, 14))
        self.assertIn(self.member, res.context["task"].members.all())

    def test_get_by_other(self):
        """作成者でもmemberでもないotherは404 になるかチェック"""
        self.client.login(username="other", password="password")
        res = self.client.get(reverse("tasks:detail", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 404)

    def test_get_task_not_exists(self):
        self.client.login(username="creator", password="password")
        res = self.client.get(reverse("tasks:detail", kwargs={"pk": 100}) )
        self.assertEqual(res.status_code, 404)


class TestTaskUpdate(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="password")
        self.other = User.objects.create_user(username="other", password="password")
        self.task = Task.objects.create(
            creator=self.creator,
            title="title",
            description="description",
        )
    def test_get(self):
        self.client.login(username="creator", password="password")
        res = self.client.get(reverse("tasks:edit", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["form"].instance, self.task)

    def test_cannot_get_by_other(self):
        self.client.login(username="other", password="password")
        res = self.client.get(reverse("tasks:edit", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 404)

    def test_post(self):
        self.client.login(username="creator", password="password")
        res = self.client.post(
            reverse("tasks:edit", kwargs={"pk": self.task.pk}),
            data={
                "title": "update",
                "description": "update",
            })
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("tasks:detail", kwargs={"pk": self.task.pk}))
        self.assertEqual(Task.objects.first().title, "update")
        self.assertEqual(Task.objects.first().description, "update")
        self.assertEqual(Task.objects.count(), 1)
        self.assertFalse(Task.objects.fileter(pk=self.task.pk).exists())

    def test_post_by_not_creator(self):
        self.client.login(username="other", password="password")
        res = self.client.post(
            reverse("tasks:edit", kwargs={"pk": self.task.pk}),
            data={
                "title": "update",
                "description": "update",
            })
        self.assertEqual(res.status_code, 404)

    def test_post_without_login(self):
        res = self.client.post(
            reverse("tasks:edit", kwargs={"pk": self.task.pk}),
            data={
                "title": "update",
                "description": "update",
            })
        self.assertEqual(res.status_code, 302)

    def test_post_id_cannot_exist(self):
        self.client.login(username="creator", password="password")
        res = self.client.post(
            reverse("tasks:edit", kwargs={"pk": 100}),
            data={
                "title": "update",
                "description": "update",
            })
        self.assertEqual(res.status_code, 404)


class TestDelete(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="password")
        self.other = User.objects.create_user(username="other", password="password")
        self.task = Task.objects.create(
            creator=self.creator,
            title="title",
            description="description",
        )
    
    def test_get(self):
        self.client.login(username="creator", password="password")
        res = self.client.get(reverse("tasks:delete", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "tasks/delete_confirm.html")
        self.assertEqual(res.context["task"], self.task)

    def test_post(self):
        self.client.login(username="creator", password="password")
        res = self.client.post(reverse("tasks:delete", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("tasks:list"))
        self.assertEqual(Task.objects.count(), 0)

    def test_get_without_login(self):
        res = self.client.get(reverse("tasks:delete", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 302)
    
    def test_get_by_not_creator(self):
        self.client.login(username="other", password="password")
        res = self.client.get(reverse("tasks:delete", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 404)
        
    def test_post_without_login(self):
        res = self.client.post(reverse("tasks:delete", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 302)

    def test_post_by_not_creator(self):
        self.client.login(username="other", password="password")
        res = self.client.post(reverse("tasks:delete", kwargs={"pk": self.task.pk}))
        self.assertEqual(res.status_code, 404)

    def test_get_id_not_exist(self):
        self.client.login(username="creator", password="password")
        res = self.client.get(reverse("tasks:delete", kwargs={"pk": 100}))
        self.assertEqual(res.status_code, 404)
        
    def test_post_id_not_exist(self):
        self.client.login(username="creator", password="password")
        res = self.client.post(reverse("tasks:delete", kwargs={"pk": 100}))
        self.assertEqual(res.status_code, 404)

class TestTaskSignals(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="password")
        self.task = Task.objects.create(
            creator=self.user,
            title="test",
            description="description"
        )
    
    def test_signals(self):
        self.assertEqual(TaskCreateLog.objects.count(), 1)
        self.assertEqual(TaskCreateLog.objects.get().task, self.task)

    def test_task_update_does_not_create_log(self):
        """TaskオブジェクトをupdateしてもTaskCreateLogが増えていないことを確認"""
        self.task.title = "updated"
        self.task.save()

        self.assertEqual(TaskCreateLog.objects.count(), 1)
        
        
