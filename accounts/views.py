from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db import transaction

from .models import CustomUserCreateLog, CustomUserProfile
from .forms import CustomUserCreationForm, CustomUserEditForm, CustomUserProfileForm


User = get_user_model()

class CustomSignupView(CreateView):
    template_name = "accounts/signup.html"
    form_class = CustomUserCreationForm
    success_url=reverse_lazy("accounts:login")
    def form_valid(self, form):
        messages.success(self.request, "アカウントを作成しました ログインしてください")
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, "アカウントを作成できませんでした")
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    def form_valid(self, form):
        messages.success(self.request, "ログインしました")
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, "ログインできませんでした")
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("tasks:list")
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "ログアウトしました。")
        return super().dispatch(request, *args, **kwargs)


class CustomUserCreateLogListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    raise_exception = True 
    model = CustomUserCreateLog
    template_name = "accounts/log.html"
    paginate_by = 20
    context_object_name = "logs"
    def test_func(self):
        return self.request.user.is_staff
    def get_queryset(self):
        return CustomUserCreateLog.objects.order_by("created_at")

class UserDetailView(LoginRequiredMixin, DetailView):
    template_name = "accounts/user_detail.html"
    context_object_name = "user_obj"
    def get_object(self):
        return self.request.user


@login_required
def user_edit(request):
    profile, created = CustomUserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        user_form = CustomUserEditForm(instance=request.user, data=request.POST)
        profile_form = CustomUserProfileForm(instance=profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            return redirect("accounts:user_detail")

    else:
        user_form = CustomUserEditForm(instance=request.user)
        profile_form = CustomUserProfileForm(instance=profile)
    return render(request, "accounts/profile_edit.html",
                  {"user_form": user_form,
                   "profile_form": profile_form})