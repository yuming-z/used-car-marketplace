from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from django.utils.html import escape
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail

from .tokens import account_activation_token
from .models import User_Detail, User
from .forms import SignupForm, LoginForm    

# Create your views here.
def index(request):
    return render(request, 'index.html')

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

    return render(request, 'login.html', {'login_form': form})

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
        return redirect('index')
    else:
        return redirect('invalid_activation')

def activate_email_sent(request):
    return render(request, 'activate_email_sent.html')

def invalid_activation_view(request):
    return render(request, 'invalid_activation.html')

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
                message = render_to_string('activate_email.html', {
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

    return render(request, 'signup.html', {'signup_form': form})

def forgotpassword_view(request):
    return render(request, 'forgotpassword.html')

# made for testing purposes
# def search(request):
#     try:
#         # cars = Car.objects.all() # for now, just get all cars, not based on search
#         fuels = Fuel_Type.objects.all() # TESTING
#         return render(request, 'search.html', {'fuels': fuels})
#     except Car.DoesNotExist:
#         raise Http404("Could not find cars with that search criteria.")
