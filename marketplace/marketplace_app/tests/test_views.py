from django.test import TestCase
from django.urls import reverse
from django.core import mail

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode

from marketplace_app.models import *
from marketplace_app.tokens import *

APP_NAME = "marketplace_app/"

class ViewsTest(TestCase):
    # -- LOGOUT -- 
    def test_logout_view_get(self):
        '''
        Test correct logout
        '''
        user = User.objects.create_user(
            username='buyer@example.com', 
            password='your_password', 
            first_name='Buyer',
            last_name='Name',
            email='buyer@example.com'
        )
        self.client.login(username='buyer@example.com', password='your_password')
        
        response = self.client.get(reverse('logout'))
        self.assertTrue(response.wsgi_request.user.is_anonymous)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertNotEqual(user, response.wsgi_request.user)

    # -- LOGIN -- 
    def test_login_view_get(self):
        '''
        Test correct login get view
        '''
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'login.html')

    def test_login_view_post_valid(self): 
        '''
        Test correct login post with valid arguments and existing user. 
        Also test anonymous user is logged in first.
        '''    
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

        # check user is logged in
        self.assertEqual(old_user, response.wsgi_request.user)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'user@example.com')

        # check response is redirected
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_login_view_post_invalid_user(self):
        '''
        Test correct login post for invalid user, where the user does not exist at all.
        '''
        response = self.client.post(reverse('login'), {
            'email': 'user@example.com',
            'password': 'your_password',
        })

        # shows that anonymous user is still logged in
        self.assertTrue(response.wsgi_request.user.is_anonymous)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # check form shows correct error
        all_errors = response.context['login_form'].errors.get('__all__', [])
        self.assertIn('Login failed. Please check your email and password.', all_errors)

    def test_login_view_post_invalid_password(self):
        '''
        Test correct login post for invalid passowrd, where password is correctly written in.
        '''
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

        # check that anonymous user is still logged in
        self.assertTrue(response.wsgi_request.user.is_anonymous)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # check form shows correct error
        all_errors = response.context['login_form'].errors.get('__all__', [])
        self.assertIn('Login failed. Please check your email and password.', all_errors)

    # -- ACTIVATE --
    def test_activate_view_valid_token(self):
        '''
        Test activation token for signup and ensures user object is activated and logged in.
        '''
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )
        old_user_number = User_Detail.objects.create(user=old_user, mobile='0411567980')
        uidb64 = urlsafe_base64_encode(bytes(str(old_user.pk), 'utf-8'))
        token = account_activation_token.make_token(old_user)

        response = self.client.get(reverse('activate', args=[uidb64, token]))

        # check valid activation token moves to index page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

        # check user is active now
        updated_user = User.objects.get(pk=old_user.pk)
        self.assertTrue(updated_user.is_active)
        
        # check user email is confirmed now
        updated_user_detail = User_Detail.objects.get(user=updated_user)
        self.assertTrue(updated_user_detail.email_confirmed)

    def test_activate_view_invalid_token(self):
        '''
        Test invalid activation token for signup for wrong token.
        '''
        response = self.client.get(reverse('activate', args=['wrong', 'wrong']))

        # check redirections to error page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('invalid_activation'))

    # -- SIGNUP -- 
    def test_signup_view_get(self):
        '''
        Test correct signup get view
        '''
        response = self.client.get(reverse('signup'))

        # check correct view of signup page
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

    def test_resetpassword_view_post_invaid_token(self):
        old_user = User.objects.create(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )
        uidb64 = urlsafe_base64_encode(bytes(str('cause error'), 'utf-8'))
        token = default_token_generator.make_token(old_user)

        response = self.client.post(reverse('reset_password', args=[uidb64, token]), {
            'password1': 'new_password123',
            'password2': 'new_password123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('invalid_reset'))

    # -- GET VIEWS --
    def test_car_listing_view_get_valid(self):
        car_brand = Car_Brand.objects.create(name='Test Brand')
        car_model = Car_Model.objects.create(brand=car_brand, name='Test Model')
        fuel_type = Fuel_Type.objects.create(name='Petrol')
        transmission_type = Transmission_Type.objects.create(name='Automatic')
        old_user = User.objects.create(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )

        test_car = Car.objects.create(
            year=2023,
            model=car_model,
            registration_number='ABC123',
            status='AVAILABLE',
            description='This is a test car',
            odometer=50000,
            price=15000.00,
            condition='GOOD',
            fuel_type=fuel_type,
            transmission=transmission_type,
            owner=old_user,
            prev_owner_count=1,
            location='Test Location',
        )

        response = self.client.get(reverse('car_listing', args=[test_car.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'car_listing.html')
        self.assertEqual(response.context['car'], test_car)

    def test_car_listing_view_get_invalid(self):
        response = self.client.get(reverse('car_listing', args=[999]))
        self.assertTemplateUsed(response, APP_NAME + 'error_page.html')

    def test_car_listings_view_get_valid(self):
        response = self.client.get(reverse('car_listings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'car_listings.html')

    # -- SELLER RATINGS --
    def test_rate_seller_view_get_valid(self):
        seller_user = User.objects.create(
            username='seller@example.com', 
            password='your_password', 
            first_name='Seller',
            last_name='Name',
            email='seller@example.com'
        )

        response = self.client.get(reverse('rating_seller', args=[seller_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'rating_seller.html')

    def test_rate_seller_view_post_valid(self):
        seller_user = User.objects.create_user(
            username='seller@example.com', 
            password='your_password', 
            first_name='Seller',
            last_name='Name',
            email='seller@example.com'
        )
        buyer_user = User.objects.create_user(
            username='buyer@example.com', 
            password='your_password', 
            first_name='Buyer',
            last_name='Name',
            email='buyer@example.com'
        )

        self.client.login(username='buyer@example.com', password='your_password')

        response = self.client.post(reverse('rating_seller', args=[seller_user.id]), {
            'rating': 5,
            'comments': 'Test comment',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('confirm_rating'))

        seller_rating = Seller_Rating.objects.get(seller=seller_user, buyer=buyer_user)
        self.assertEqual(seller_rating.rating, 5)
        self.assertEqual(seller_rating.comment, 'Test comment')

    # def test_rate_seller_view_post_invalid_same(self):
    #     seller_user = User.objects.create_user(
    #         username='seller@example.com', 
    #         password='your_password', 
    #         first_name='Seller',
    #         last_name='Name',
    #         email='seller@example.com'
    #     )
    #     self.client.login(username='seller@example.com', password='your_password')

    #     response = self.client.post(reverse('rating_seller', args=[seller_user.id]), {
    #         'rating': 5,
    #         'comments': 'Test comment',
    #     })

    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('error_page'))
        
    def test_rate_seller_view_post_invalid_seller(self):
        buyer_user = User.objects.create_user(
            username='buyer@example.com', 
            password='your_password', 
            first_name='Buyer',
            last_name='Name',
            email='buyer@example.com'
        )
        self.client.login(username='buyer@example.com', password='your_password')

        response = self.client.post(reverse('rating_seller', args=[999]), {
            'rating': 5,
            'comments': 'Test comment',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('error_page'))

    def test_rate_seller_view_get_invalid_same(self):
        buyer_user = User.objects.create_user(
            username='buyer@example.com', 
            password='your_password', 
            first_name='Buyer',
            last_name='Name',
            email='buyer@example.com'
        )
        self.client.login(username='buyer@example.com', password='your_password')
        response = self.client.get(reverse('rating_seller', args=[buyer_user.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('error_page'))
    
    def test_rate_seller_view_get_invalid_seller(self):
        response = self.client.get(reverse('rating_seller', args=[999]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('error_page'))

    # -- BUYER RATINGS --
    def test_rate_buyer_view_get_valid(self):
        seller_user = User.objects.create(
            username='seller@example.com', 
            password='your_password', 
            first_name='Seller',
            last_name='Name',
            email='seller@example.com'
        )

        response = self.client.get(reverse('rating_buyer', args=[seller_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'rating_buyer.html')

    def test_rate_buyer_view_post_valid(self):
        seller_user = User.objects.create_user(
            username='seller@example.com', 
            password='your_password', 
            first_name='Seller',
            last_name='Name',
            email='seller@example.com'
        )
        buyer_user = User.objects.create_user(
            username='buyer@example.com', 
            password='your_password', 
            first_name='Buyer',
            last_name='Name',
            email='buyer@example.com'
        )

        self.client.login(username='seller@example.com', password='your_password')

        response = self.client.post(reverse('rating_buyer', args=[buyer_user.id]), {
            'rating': 5,
            'comments': 'Test comment',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('confirm_rating'))

        buyer_rating = Buyer_Rating.objects.get(seller=seller_user, buyer=buyer_user)
        self.assertEqual(buyer_rating.rating, 5)
        self.assertEqual(buyer_rating.comment, 'Test comment')

    # def test_rate_buyer_view_post_invalid_same(self):
    #     seller_user = User.objects.create_user(
    #         username='seller@example.com', 
    #         password='your_password', 
    #         first_name='Seller',
    #         last_name='Name',
    #         email='seller@example.com'
    #     )
    #     self.client.login(username='seller@example.com', password='your_password')

    #     response = self.client.post(reverse('rating_seller', args=[seller_user.id]), {
    #         'rating': 5,
    #         'comments': 'Test comment',
    #     })

    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('error_page'))
        
    def test_rate_buyer_view_post_invalid_seller(self):
        seller_user = User.objects.create_user(
            username='seller@example.com', 
            password='your_password', 
            first_name='Seller',
            last_name='Name',
            email='seller@example.com'
        )
        self.client.login(username='seller@example.com', password='your_password')

        response = self.client.post(reverse('rating_buyer', args=[999]), {
            'rating': 5,
            'comments': 'Test comment',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('error_page'))

    def test_rate_buyer_view_get_invalid_same(self):
        user = User.objects.create_user(
            username='buyer@example.com', 
            password='your_password', 
            first_name='Buyer',
            last_name='Name',
            email='buyer@example.com'
        )
        self.client.login(username='buyer@example.com', password='your_password')
        response = self.client.get(reverse('rating_buyer', args=[user.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('error_page'))
    
    def test_rate_buyer_view_get_invalid_seller(self):
        response = self.client.get(reverse('rating_buyer', args=[999]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('error_page'))

    # -- UPDATE ACCOUNT --
    def test_account_detail_view_get_valid(self):
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )
        old_user_number = User_Detail.objects.create(user=old_user, mobile='0411567980')
        self.client.login(username='user@example.com', password='your_password')

        response = self.client.get(reverse('account_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'account_detail.html')

    def test_account_detail_view_post_valid(self):
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )
        old_user_number = User_Detail.objects.create(user=old_user, mobile='0411567980')
        self.client.login(username='user@example.com', password='your_password')

        response = self.client.post(reverse('account_detail'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'user@example.com',
            'city_address': 'Sydney',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account_detail'))

        old_user_update = User.objects.get(username='user@example.com')
        self.assertEqual(old_user_update.first_name, 'Updated')
        self.assertEqual(old_user_update.last_name, 'Name')
        self.assertEqual(old_user_update.email, 'user@example.com')

    # -- DELETE ACCOUNT --
    def test_account_delete_view_get(self):
        old_user = User.objects.create_user(
            username='user@example.com', 
            password='your_password', 
            first_name='User',
            last_name='Name',
            email='user@example.com'
        )
        self.client.login(username='user@example.com', password='your_password')

        response = self.client.get(reverse('account_delete'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, APP_NAME + 'index.html')
