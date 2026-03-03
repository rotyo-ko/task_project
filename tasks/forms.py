from django import forms
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Task


User = get_user_model()

class TaskForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple,
    )
    
    class Meta:
        model = Task
        fields = ["title", "members", "description", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs=
                {"type": "date"}),
        }

class TaskSearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=200, help_text="検索")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "-----")]+Task.STATUS_CHOICES
    )
    def filter_queryset(self, queryset):
        if not self.is_valid():
            return queryset
        
        keyword = self.cleaned_data.get("keyword")
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | (Q(description__icontains=keyword)))
        status = self.cleaned_data.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset