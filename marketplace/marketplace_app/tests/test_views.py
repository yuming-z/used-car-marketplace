from django.test import TestCase
from django.urls import reverse
from django.core import mail

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode

from marketplace_app.models import *

APP_NAME = "marketplace_app/"

class ViewsTest(TestCase):
    # -- LOGIN -- 
    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'login.html')

    def test_login_view_post_valid(self):     
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )

        # check anon user logged in first
        response = self.client.get(reverse('login'))
        self.assertTrue(response.wsgi_request.user.is_anonymous)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertNotEqual(old_user, response.wsgi_request.user)

        response = self.client.post(reverse('login'), {
            'email': 'user@example.com',
            'password': 'your_password',
        })

        self.assertEqual(old_user, response.wsgi_request.user)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'user@example.com')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_login_view_post_invalid_user(self):
        response = self.client.post(reverse('login'), {
            'email': 'user@example.com',
            'password': 'your_password',
        })

        self.assertTrue(response.wsgi_request.user.is_anonymous)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        all_errors = response.context['login_form'].errors.get('__all__', [])
        self.assertIn('Login failed. Please check your email and password.', all_errors)

    def test_login_view_post_invalid_password(self):
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )

        response = self.client.post(reverse('login'), {
            'email': 'user@example.com',
            'password': 'wrong_password',
        })

        self.assertTrue(response.wsgi_request.user.is_anonymous)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        all_errors = response.context['login_form'].errors.get('__all__', [])
        self.assertIn('Login failed. Please check your email and password.', all_errors)

    # -- SIGNUP -- 
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
        self.assertRedirects(response, reverse('activate_email_sent'))
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertFalse(User.objects.get(username='user@example.com').is_active)
        self.assertEqual(User_Detail.objects.count(), user_count_before + 1)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual('Activate Your Carsales Account', mail.outbox[0].subject)

    def test_signup_view_post_invalid(self):
        user_count_before = User.objects.count()
        response = self.client.post(reverse('signup'), {}) 
        self.assertEqual(User.objects.count(), user_count_before)
        self.assertEqual(User_Detail.objects.count(), user_count_before)
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_view_post_invalid_number(self):
        user_count_before = User.objects.count()
        old_user = User.objects.create_user(
            email='user@example.com',
            username='user@example.com',
            first_name='User',
            last_name='Name',
            password='your_password'
        )
        old_user_number = User_Detail.objects.create(user=old_user, mobile='0411567980')
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertEqual(User_Detail.objects.count(), user_count_before + 1)

        response = self.client.post(reverse('signup'), {
            'email': 'diffemail@example.com',
            'first_name': 'User',
            'last_name': 'Name',
            'password1': 'your_password',
            'password2': 'your_password',
            'number': '0411567980',
        })
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertEqual(User_Detail.objects.count(), user_count_before + 1)
        self.assertEqual(len(mail.outbox), 0)
        
        all_errors = response.context['signup_form'].errors.get('__all__', [])
        self.assertIn('Signup failed. Phone Number already exists.', all_errors)

    def test_signup_view_post_invalid_email(self):
        user_count_before = User.objects.count()
        old_user = User.objects.create(
            email='user@example.com',
            username='user@example.com',
            first_name='User',
            last_name='Name',
            password='your_password'
        )
        old_user_number = User_Detail.objects.create(user=old_user, mobile='0411567980')
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertEqual(User_Detail.objects.count(), user_count_before + 1)

        response = self.client.post(reverse('signup'), {
            'email': 'user@example.com',
            'first_name': 'User',
            'last_name': 'Name',
            'password1': 'your_password',
            'password2': 'your_password',
            'number': '0411567989',
        })
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertEqual(User_Detail.objects.count(), user_count_before + 1)
        self.assertEqual(len(mail.outbox), 0)
        
        all_errors = response.context['signup_form'].errors.get('__all__', [])
        self.assertIn('Signup failed. Email already exists.', all_errors)

    # -- FORGOT PASSWORD -- 
    def test_forgotpassword_view_get(self):
        response = self.client.get(reverse('forgotpassword'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'forgotpassword.html')

    def test_forgotpassword_view_post_valid(self):
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )

        response = self.client.post(reverse('forgotpassword'), {
            'email': 'user@example.com',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reset_email_sent'))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual('Reset Your Carsales Account Password', mail.outbox[0].subject)

    def test_forgotpassword_view_post_invalid(self):
        response = self.client.post(reverse('forgotpassword'), {
            'email': 'wrong@example.com', 
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reset_email_sent'))

        self.assertEqual(len(mail.outbox), 0)

    def test_resetpassword_view_get(self):
        response = self.client.get(reverse('reset_password', args=['uidb64', 'token']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'reset_password.html')

    def test_resetpassword_view_post_valid(self):
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )
        uidb64 = urlsafe_base64_encode(bytes(str(old_user.pk), 'utf-8'))
        token = default_token_generator.make_token(old_user)

        response = self.client.post(reverse('reset_password', args=[uidb64, token]), {
            'password1': 'new_password123',
            'password2': 'new_password123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        updated_user = User.objects.get(pk=old_user.pk)
        self.assertTrue(updated_user.check_password('new_password123'))

    def test_resetpassword_view_post_invalid_match(self):
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )
        uidb64 = urlsafe_base64_encode(bytes(str(old_user.pk), 'utf-8'))
        token = default_token_generator.make_token(old_user)

        response = self.client.post(reverse('reset_password', args=[uidb64, token]), {
            'password1': 'new_password123',
            'password2': 'new_password3',
        })

        updated_user = User.objects.get(pk=old_user.pk)
        self.assertTrue(updated_user.check_password('your_password'))

        all_errors = response.context['reset_form'].errors.get('__all__', [])
        self.assertIn('Passwords do not match', all_errors)

    def test_resetpassword_view_post_invaid_existing(self):
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )
        uidb64 = urlsafe_base64_encode(bytes(str(old_user.pk), 'utf-8'))
        token = default_token_generator.make_token(old_user)

        response = self.client.post(reverse('reset_password', args=[uidb64, token]), {
            'password1': 'your_password',
            'password2': 'your_password',
        })

        updated_user = User.objects.get(pk=old_user.pk)
        self.assertTrue(updated_user.check_password('your_password'))

        all_errors = response.context['reset_form'].errors.get('__all__', [])
        self.assertIn('Password cannot be the same as your last password', all_errors)

    # def test_resetpassword_view_post_invaid_token(self):
    #     old_user = User.objects.create(
    #         username='user@example.com', 
    #         password='your_password', 
    #         first_name='User',
    #         last_name='Name',
    #         email='user@example.com'
    #     )
    #     uidb64 = urlsafe_base64_encode(bytes(str(old_user.pk), 'utf-8'))
    #     token = default_token_generator.make_token(old_user)

    #     response = self.client.post(reverse('reset_password', args=[uidb64, token]), {
    #         'password1': 'new_password123',
    #         'password2': 'new_password123',
    #     })

    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('invalid_reset'))
