from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.utils.html import escape
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.forms.models import BaseModelForm
from django.views.generic import CreateView

from .tokens import account_activation_token, reset_password_token
from .models import *
from .forms import *

APP_NAME = "marketplace_app/"

# Create your views here.
def index(request):
    return render(request, APP_NAME + 'index.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user_password = form.cleaned_data['password']

            user = authenticate(request, username=user_email, password=user_password)
            if user is not None:
                login(request, user)
                return redirect('index')
        
        form.add_error(None, "Login failed. Please check your email and password.")
    else:
        form = LoginForm()

    return render(request,  APP_NAME + 'login.html', {'login_form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None             

    if user is not None and account_activation_token.check_token(user, token):
        user_detail = User_Detail.objects.get(user=user)
        user_detail.email_confirmed = True
        user_detail.save()
        
        user.is_active = True
        user.save()

        login(request, user) # Log the user in
        print("User is logged in "+user.username)
        return redirect('index', permanent=True)
    else:
        return redirect('invalid_activation')

def activate_email_sent(request):
    return render(request,  APP_NAME + 'activate_email_sent.html')

def reset_email_sent(request):
    return render(request,  APP_NAME + 'reset_email_sent.html')

def invalid_activation_view(request):
    return render(request,  APP_NAME + 'invalid_activation.html')

def invalid_reset_view(request):
    return render(request,  APP_NAME + 'invalid_reset.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            
            user, msg = form.save(commit=False)    
            if user is not None:
                print("Signup works")
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
                send_mail(subject=subject, message=message, from_email='elec05471@gmail.com', recipient_list=[user.email])
                return redirect('activate_email_sent')
            
            else:
                if msg == "mobile":
                    form.add_error(None, "Signup failed. Phone Number already exists.")
                elif msg == "email":
                    form.add_error(None, "Signup failed. Email already exists.")
            
    else:
        form = SignupForm()

    return render(request,  APP_NAME + 'signup.html', {'signup_form': form})

def forgotpassword_view(request):
    if request.method == 'POST':
        form = ForgetPasswordForm(request.POST)
        if form.is_valid():
            user = form.get_user()

            if user is not None:
                current_site = get_current_site(request)
                subject = 'Reset Your Carsales Account Password'
                message = render_to_string(APP_NAME + 'reset_password_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': reset_password_token.make_token(user),
                })
                send_mail(subject=subject, message=message, from_email='elec05471@gmail.com', recipient_list=[user.email])

            else:
                print("Email does not exist")

            return redirect('reset_email_sent')

    else:
        form = ForgetPasswordForm()

    return render(request, APP_NAME + 'forgotpassword.html', {'forget_form': form})

def resetpassword_view(request, uidb64, token):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None    

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

def car_listings_view(request):
    all_car_listings = Car.objects.all()
    return render(request, APP_NAME + 'car_listings.html', {'all_car_listings': all_car_listings})

class CarCreateView(CreateView):
    model = Car
    # TODO The URL redirected after the a new car is created successfully
    form_class = CarForm

class CarModelCreateView(CreateView):
    model = Car_Model
    success_url = 'car'
    form_class = CarModelForm

class CarBrandCreateView(CreateView):
    model = Car_Brand
    success_url = 'model'
    form_class = CarBrandForm

class TransmissionCreateView(CreateView):
    model = Transmission_Type
    success_url = 'car'
    form_class = TranmissionForm

class FuelCreateView(CreateView):
    model = Fuel_Type
    success_url = 'car'
    form_class = FuelForm
    
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm()
    return render(request, 'create_listing.html', {'form': form})

def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.user != listing.owner:
        return HttpResponse("Permission Denied")
    
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'edit_listing.html', {'form': form, 'listing': listing})

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    return render(request, 'listing_detail.html', {'listing': listing})


def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    if request.user != listing.owner:
        return HttpResponse("Permission Denied")
    
    if request.method == 'POST':
        listing.delete()
        return redirect('listings')  

