import logging

from django.db.models import Q
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator 
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone

from .models import Task, TaskCreateLog
from .forms import TaskForm, TaskSearchForm


class TaskListView(ListView):
    model = Task
    template_name = "tasks/list.html"
    paginate_by = 10
        
    def get_queryset(self):
        qs = Task.objects.all()
        mode = self.kwargs.get("mode")
        if mode == "overdue":
            qs = qs.overdue()
        elif mode == "completed":
            qs = qs.completed()
        self.form = TaskSearchForm(self.request.GET)
        return self.form.filter_queryset(qs).order_by_deadline()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop("page", None)
        context["query_string"] = query.urlencode()
        context["form"] = self.form

        mode = self.kwargs.get("mode")
        page_title_dict = {
            None: "タスク一覧",
            "overdue": "期限切れタスク",
            "completed": "完了済みタスク",
        }
        page_title = page_title_dict.get(mode, "タスク一覧")
        context["page_title"] = page_title
        return context
        

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/detail.html"
    context_object_name = "task"

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/post_form.html"
    success_url = reverse_lazy("tasks:list")
    def form_valid(self, form):
        form.instance.creator = self.request.user 
        return super().form_valid(form)
    

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin,UpdateView):
    template_name = "tasks/post_form.html"
    form_class = TaskForm
    def test_func(self):
        task = self.get_object()
        return task.creator == self.request.user

    def get_success_url(self):
        self.object = self.get_object()
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_completed:
            raise Http404("完了済みタスクは編集できません")
        return super().dispatch(request, *args, **kwargs)
        

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = "tasks/delete_confirm.html"
    success_url = reverse_lazy("tasks:list")
    def test_func(self):
        task = self.get_object()
        return task.creator == self.request.user



@method_decorator(require_POST, name="dispatch")
class TaskCompleteView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = "tasks/complete_confirm.html"
    fields = []
    def test_func(self):
        task = self.get_object()
        return task.creator == self.request.user
    def get_queryset(self):
        return Task.objects.active()
    def form_valid(self, form):
        form.instance.mark_done()
        return super().form_valid(form)
    def get_success_url(self):
        return reverse("tasks:detail", kwargs={"pk": self.object.pk})

@method_decorator(require_POST, name="dispatch")    
class TaskReopenView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    template_name = "tasks/reopen_confirm.html"
    fields = []
    def test_func(self):
        task = self.get_object()
        return task.creator == self.request.user
    def get_queryset(self):
        return Task.objects.completed()
    def form_valid(self, form):
        form.instance.reopen()
        return super().form_valid(form)
    def get_success_url(self):
        return reverse("tasks:detail", kwargs={"pk": self.object.pk})
    

class TaskCreateLogListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    raise_exception = True # 管理者専用ページ
    model = TaskCreateLog
    template_name = "tasks/log.html"
    paginate_by = 20
    context_object_name = "logs"
    def test_func(self):
        return self.request.user.is_staff
    def get_queryset(self):
        return TaskCreateLog.objects.order_by("-created_at")
        


    



