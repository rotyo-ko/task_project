from django.db import models
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings


class TaskQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            status__in=[Task.STATUS_TODO, Task.STATUS_DOING],
            completed_at__isnull=True)
        
    def completed(self):
        return self.filter(
            status=Task.STATUS_DONE,
            completed_at__isnull=False
        )
    
    def overdue(self):
        today = timezone.localdate() 
        # date なのでtimezone.now()ではなくtimezone.localdate()をつかう
        return self.filter(
            due_date__lt=today,
            status__in=[Task.STATUS_TODO, Task.STATUS_DOING]
        )
    
    def with_due_date(self):
        return self.filter(due_date__isnull=False)
    
    def can_complete(self):
        return self.filter(status__in=[Task.STATUS_TODO, Task.STATUS_DOING])

    def order_by_deadline(self):
        return self.order_by(F("due_date").asc(nulls_last=True))

class Task(models.Model):
    STATUS_TODO = "todo"
    STATUS_DOING = "doing"
    STATUS_DONE = "done"

    STATUS_CHOICES = [
        (STATUS_TODO, "未実行"),
        (STATUS_DOING, "実行中"),
        (STATUS_DONE, "完了"),
    ]

    title = models.CharField("タスク名 ")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_taskss"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tasks",
        blank=True
    )
    description = models.TextField("詳細", blank=True, null=True)
    status = models.CharField("ステータス", choices=STATUS_CHOICES, default=STATUS_TODO)
    due_date = models.DateField("期限", blank=True, null=True)
    completed_at = models.DateTimeField("完了日時", blank=True, null=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    objects = TaskQuerySet.as_manager()

    def mark_done(self):
        if self.status == self.STATUS_DONE:
            raise ValidationError("すでに終了しています。")
        self.status = self.STATUS_DONE
        
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    def reopen(self):
        if self.status != self.STATUS_DONE:
            raise ValidationError("終了状態ではありません。")
        self.status = self.STATUS_TODO
        self.completed_at = None
        self.save(update_fields=["status", "completed_at"])

    def can_complete(self):
        return self.status in (self.STATUS_TODO, self.STATUS_DOING)
    
    def can_reopen(self):
        return self.status == self.STATUS_DONE

    @property
    def is_completed(self):
        return self.status == self.STATUS_DONE
    
    @property
    def is_overdue(self):
        """ 期限を過ぎたかチェックする関数"""
        if not self.due_date:
            return False
        if self.is_completed:
            return False
 
        return self.due_date <= timezone.localdate()

    @property
    def can_complete(self):
        return self.status in (self.STATUS_DOING, self.STATUS_TODO)
    
    def clean(self):
        errors = {}
        if self.status == self.STATUS_DONE and self.completed_at is None:
            errors["completed_at"] = "完了日時がありません。"
        
        if self.completed_at is not None and self.status != self.STATUS_DONE:
            errors["status"] = "完了日時がある場合、ステータスは完了である必要があります。"


class TaskCreateLog(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="create_log")
    created_at = models.DateTimeField("作成日時", auto_now_add=True,)


        