from django.forms.models import BaseModelForm
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils.html import escape
from django.views.generic import CreateView

from .models import *
from .forms import *

APP_NAME = "marketplace_app/"

# Create your views here.
def index(request):
    return render(request, APP_NAME + 'index.html')

def login(request):
    return render(request, APP_NAME + 'login.html')

def signup(request):
    return render(request, APP_NAME + 'signup.html')

def forgotpassword(request):
    return render(request, APP_NAME + 'forgotpassword.html')

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