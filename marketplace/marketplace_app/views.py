from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.utils.html import escape
from django.contrib.auth import login, authenticate

from .models import User_Detail
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

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()  
            User_Detail.objects.create(user=user, mobile=form.number_exists())
            user_password = form.cleaned_data['password1']
            user = authenticate(request, username=user.email, password=user_password) 
            if user is not None:
                login(request, user)  # Log the user in
                return redirect('index')  # Redirect to a home page
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
