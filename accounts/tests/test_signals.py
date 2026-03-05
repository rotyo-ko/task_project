from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import CustomUserCreateLog, CustomUserProfile


User = get_user_model()

class TestSignals(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="password")
    
    def test_create_profile_and_log(self):
        self.assertEqual(CustomUserCreateLog.objects.count(), 1)
        self.assertEqual(CustomUserCreateLog.objects.get().user, self.user)

        self.assertEqual(CustomUserProfile.objects.count(), 1)
        self.assertEqual(CustomUserProfile.objects.get().user, self.user)

    def test_update_does_not_create_log(self):
        self.user.first_name = "first_name"
        self.user.save()

        self.assertEqual(CustomUserCreateLog.objects.count(), 1)
        self.assertEqual(CustomUserProfile.objects.count(), 1)


