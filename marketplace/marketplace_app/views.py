from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.utils.html import escape
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, authenticate, get_user_model
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import BaseModelForm
from django.views.generic import CreateView
from django.db.models import Avg
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages

# from .forms import UserDetailForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import UserUpdateForm, User_DetailUpdateForm

from .tokens import account_activation_token, reset_password_token
from .models import *
from .forms import *

APP_NAME = "marketplace_app/"

def index(request):
    return render(request, APP_NAME + 'index.html')

def activate_email_sent(request):
    return render(request,  APP_NAME + 'activate_email_sent.html')

def reset_email_sent(request):
    return render(request,  APP_NAME + 'reset_email_sent.html')

def invalid_activation_view(request):
    return render(request,  APP_NAME + 'invalid_activation.html')

def invalid_reset_view(request):
    return render(request,  APP_NAME + 'invalid_reset.html')

def confirm_rating_view(request):
    return render(request, APP_NAME + 'confirm_rating.html')

def error_page_view(request):
    return render(request, APP_NAME + 'error_page.html')

def logout_view(request):
    logout(request)
    return redirect('/')

# login page
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        # form valid.
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user_password = form.cleaned_data['password']

            user = authenticate(request, username=user_email, password=user_password)
            if user is not None:
                login(request, user)
                return redirect('index')
        
        # form invalid. user not found or invalid password.
        form.add_error(None, "Login failed. Please check your email and password.")
    else:
        form = LoginForm()

    return render(request,  APP_NAME + 'login.html', {'login_form': form})

# activating signup form from email sent to user
def activate(request, uidb64, token):
    # check if token is valid
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None             

    # complete signup registration and log user in
    if user is not None and account_activation_token.check_token(user, token):
        user_detail = User_Detail.objects.get(user=user)
        user_detail.email_confirmed = True
        user_detail.save()
        
        user.is_active = True
        user.save()

        login(request, user)
        print("User is logged in "+user.username)
        return redirect('index', permanent=True)
    else:
        return redirect('invalid_activation')

# signup page
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        # valid form.
        if form.is_valid():
            user, msg = form.save(commit=False)    
            if user is not None:
                user.is_active = False 
                user.save()

                User_Detail.objects.create(user=user, mobile=form.number_exists())

                # sending email to user to confirm
                current_site = get_current_site(request)
                subject = 'Activate Your Carsales Account'
                message = render_to_string(APP_NAME + 'activate_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email])
                return redirect('activate_email_sent')
            
            else: # if user signs up with number or email that already exists
                if msg == "mobile":
                    form.add_error(None, "Signup failed. Phone Number already exists.")
                elif msg == "email":
                    form.add_error(None, "Signup failed. Email already exists.")
            
    else:
        form = SignupForm()

    return render(request,  APP_NAME + 'signup.html', {'signup_form': form})

# user submits email to forget password
def forgotpassword_view(request):
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            user = form.get_user()

            # sends email to user to reset password
            if user is not None:
                current_site = get_current_site(request)
                subject = 'Reset Your Carsales Account Password'
                message = render_to_string(APP_NAME + 'reset_password_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': reset_password_token.make_token(user),
                })
                send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[user.email])

            else:
                print("Email does not exist")

            return redirect('reset_email_sent')

    else:
        form = ForgetPasswordForm()

    return render(request, APP_NAME + 'forgotpassword.html', {'forget_form': form})

# form for inputting new password
def resetpassword_view(request, uidb64, token):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # check if link is valid
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None    

            # update password based on user input
            # password cannot be the same as previous password
            if user is not None and reset_password_token.check_token(user, token):
                outcome, msg = form.checks_if_old_password(user)
                if outcome:
                    form.add_error(None, "Password cannot be the same as your last password")
                    
                else:
                    if msg == "success":
                        user.set_password(form.clean_password())
                        user.save()
                        print("User changed password")
                        return redirect('login')
                
                    elif msg == "matching":
                        form.add_error(None, "Passwords do not match")
            
            else:
                return redirect('invalid_reset')

    else:
        form = ResetPasswordForm()

    return render(request, APP_NAME + 'reset_password.html', {'reset_form': form})

# TODO: need to add car listing id, and check if user correctly bought this car
def rate_seller_view(request, seller_id):
    User = get_user_model()

    if request.method == 'POST':
        # user input
        rating = int(request.POST.get('rating', 0)) 
        comment = request.POST.get('comments', '')

        if rating != 0 or comment != '': # user has inputted something
            try:
                seller = get_object_or_404(User, id=seller_id)
                user = request.user

                print('Seller:', seller)
                print('User:', user)
                Seller_Rating.objects.create(seller=seller, buyer=user, rating=rating, comment=comment)

            except Http404: # seller is not found
                return redirect('error_page')
            except ValidationError: # buyer and seller are the same person
                return redirect('error_page')
        return redirect('confirm_rating')
    else:
        try:
            seller = get_object_or_404(User, id=seller_id)
            user = request.user
            if (seller == user):
                return redirect('error_page')

            seller_ratings = Seller_Rating.objects.filter(seller=seller)
            average_rating = seller_ratings.aggregate(Avg('rating'))['rating__avg']

            return render(request,  APP_NAME + 'rating_seller.html', {'seller': seller, 'average_rating': average_rating})
        except Http404:
            # seller is not found
            return redirect('error_page')
        
def rate_buyer_view(request, buyer_id):
    User = get_user_model()

    if request.method == 'POST':
        # user input
        rating = int(request.POST.get('rating', 0)) 
        comment = request.POST.get('comments', '')

        if rating != 0 or comment != '': # user has inputted something
            try:
                buyer = get_object_or_404(User, id=buyer_id)
                user = request.user

                print('Buyer:', buyer)
                print('User:', user)
                Buyer_Rating.objects.create(seller=user, buyer=buyer, rating=rating, comment=comment)

            except Http404: # seller is not found
                return redirect('error_page')
            except ValidationError: # buyer and seller are the same person
                return redirect('error_page')
        return redirect('confirm_rating')
    else:
        try:
            buyer = get_object_or_404(User, id=buyer_id)
            user = request.user
            if (buyer == user):
                return redirect('error_page')

            buyer_ratings = Seller_Rating.objects.filter(buyer=buyer)
            average_rating = buyer_ratings.aggregate(Avg('rating'))['rating__avg']

            return render(request,  APP_NAME + 'rating_buyer.html', {'buyer': buyer, 'average_rating': average_rating})
        except Http404:
            # buyer is not found
            return redirect('error_page')

# single car listing view
def car_listing_view(request, car_id):
    try:
        current_car = get_object_or_404(Car, id=car_id)
        return render(request, APP_NAME + 'car_listing.html', {'car': current_car})
    except Http404:
        return render(request, APP_NAME + 'error_page.html')

# all car listings view
def car_listings_view(request):
    all_car_listings = Car.objects.all()
    # if request.user.is_authenticated: # dont show logged in users listings
    #     user = request.user
    #     all_car_listings = all_car_listings.exclude(owner=user)

    return render(request, APP_NAME + 'car_listings.html', {'all_car_listings': all_car_listings})

class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    success_url = 'index'
    form_class = CarForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class CarModelCreateView(LoginRequiredMixin, CreateView):
    model = Car_Model
    success_url = 'car'
    form_class = CarModelForm

class CarBrandCreateView(LoginRequiredMixin, CreateView):
    model = Car_Brand
    success_url = 'model'
    form_class = CarBrandForm

class TransmissionCreateView(LoginRequiredMixin, CreateView):
    model = Transmission_Type
    success_url = 'car'
    form_class = TranmissionForm

class FuelCreateView(LoginRequiredMixin, CreateView):
    model = Fuel_Type
    success_url = 'car'
    form_class = FuelForm

# def account_update(request):
#     user_change_form = UserChangeForm(isinstance = request.user)
#     return render(request, APP_NAME + 'account_update.html', {'form': form})

@login_required
def account_detail(request):
        if request.method == "POST":
            u_form = UserUpdateForm(request.POST, instance=request.user)
            ud_form = User_DetailUpdateForm(request.POST, instance=request.user.user_detail)
            # p_form = ProfileUpdateForm(request.POST,
                                        # request.FILES,
                                        # instance=request.user.profile)
            #  if u_form.is_valid() and p_form.is_valid():
            # if u_form.is_valid() and ud_form.is_valid():
            u_form.save()
            # print(ud_form.errors)
            ud_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('account_detail')

        else:
            u_form = UserUpdateForm(instance=request.user)
            ud_form = User_DetailUpdateForm(instance=request.user.user_detail)
            # p_form = ProfileUpdateForm(instance=request.user.profile)

        context = {
            'u_form': u_form,
            'ud_form': ud_form
            # 'p_form': p_form
        }

        return render(request, APP_NAME + 'account_detail.html', context)
@login_required
def account_delete(request):
    if request.method == "POST":
        request.user.delete()
        logout(request)
        return redirect('/')
    # If it's a GET request, render a confirmation page
    return render(request, APP_NAME + 'index.html')


# # Add by me
# def update_user_detail(request):
#     try:
#         user_detail = request.user.user_detail
#     except User_Detail.DoesNotExist:
#         user_detail = User_Detail(user=request.user)
    
#     user_change_form = UserChangeForm(instance = user_detail)

#     # if request.method == "POST":
#     #     form = UserDetailForm(request.POST, instance=user_detail)
#     #     if form.is_valid():
#     #         form.save()
#     #         return redirect('base.html') # Replace with appropriate redirect
#     # else:
#     #     form = UserDetailForm(instance=user_detail)

#     return render(request, APP_NAME + 'update_detail.html', {'user_change_form':user_change_form})
    # return render(request,  APP_NAME + 'login.html', {'login_form': form})
    

    # @login_required
    # def profile(request):
    #     u_form = UserUpdateForm()
    #     p_form = ProfileUpdateForm()

    #     context = {
    #         'u_form': u_form,
    #         'p_form': p_form
    #     }

    #     return render(request, APP_NAME + 'user_detail.html', context)
    
# def create_listing(request):
#     if request.method == 'POST':
#         form = CarForm(request.POST)
#         if form.is_valid():
#             listing = form.save(commit=False)
#             listing.owner = request.user
#             listing.save()
#             return redirect('listing_detail', listing_id=listing.id)
#     else:
#         form = CarForm()
#     return render(request, APP_NAME + 'car_form.html', {'form': form})

# def edit_listing(request, listing_id):
#     listing = get_object_or_404(Listing, id=listing_id)
#     if request.user != listing.owner:
#         return HttpResponse("Permission Denied")
    
#     if request.method == 'POST':
#         form = ListingForm(request.POST, instance=listing)
#         if form.is_valid():
#             form.save()
#             return redirect('listing_detail', listing_id=listing.id)
#     else:
#         form = ListingForm(instance=listing)
#     return render(request, 'edit_listing.html', {'form': form, 'listing': listing})

# def listing_detail(request, listing_id):
#     listing = get_object_or_404(Listing, id=listing_id)
#     return render(request, 'listing_detail.html', {'listing': listing})

# def delete_listing(request, listing_id):
#     listing = get_object_or_404(Listing, id=listing_id)
#     if request.user != listing.owner:
#         return HttpResponse("Permission Denied")
    
#     if request.method == 'POST':
#         listing.delete()
#         return redirect('listings')  