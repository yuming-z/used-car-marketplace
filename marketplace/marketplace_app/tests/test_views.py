from django.test import TestCase
from django.urls import reverse

from marketplace_app.models import *

APP_NAME = "marketplace_app/"

class SignUpViewTest(TestCase):
    def test_signup_view_get(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'signup.html')

    def test_signup_view_post_valid(self):
        user_count_before = User.objects.count()
        response = self.client.post(reverse('signup'), {
            'email': 'user@example.com',
            'first_name': 'User',
            'last_name': 'Name',
            'password1': 'your_password',
            'password2': 'your_password',
            'number': '0411567980',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertFalse(User.objects.get(username='user@example.com').is_active)
        self.assertEqual(User_Detail.objects.count(), user_count_before + 1)

    def test_signup_view_post_invalid(self):
        user_count_before = User.objects.count()
        response = self.client.post(reverse('signup'), {}) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), user_count_before)
        self.assertEqual(User_Detail.objects.count(), user_count_before)