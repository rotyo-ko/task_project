from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import CustomUserProfile


User = get_user_model()


class CustomUserCreationForm(UserCreationForm): 
    username = forms.CharField(
        label="ユーザー名",
        min_length=6,
        help_text="(半角英数6文字以上)"
    )
    password1 = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput,
        min_length=6,
        help_text="(半角英数6文字以上)"
    )
    password2 = forms.CharField(
        label="パスワード（確認用)",
        widget=forms.PasswordInput,
        min_length=6
    )
    class Meta:                                 
        model = User                           
        fields = ("username", "password1", "password2")


class CustomUserEditForm(forms.ModelForm):
    """CustomUserの編集フォーム"""
    last_name = forms.CharField(
        label="姓",
        help_text="(苗字を入力してください)"
    )
    first_name = forms.CharField(
        label="名",
        help_text="(名前を入力してください)"
    )
    email = forms.EmailField(
        label="メールアドレス",
        help_text="(メールアドレスを入力してください)",
    )
    class Meta:
        model = User
        fields = ("last_name", "first_name", "email")


class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUserProfile
        fields = ["bio"]