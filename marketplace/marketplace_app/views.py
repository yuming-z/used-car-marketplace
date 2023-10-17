from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils.html import escape

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
