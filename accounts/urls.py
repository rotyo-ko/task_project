from django.urls import path

from .views import (
    CustomSignupView,
    CustomLoginView,
    CustomLogoutView,
    CustomUserCreateLogListView,
    UserDetailView,
    user_edit,
)

app_name = "accounts"
urlpatterns = [
    path("signup/", CustomSignupView.as_view(),
        name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("logs/", CustomUserCreateLogListView.as_view(), name="log"),
    path("detail/", UserDetailView.as_view(), name="user_detail"),
    path("edit/", user_edit, name="user_edit")
]