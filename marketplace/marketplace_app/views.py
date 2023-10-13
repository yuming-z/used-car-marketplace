from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils.html import escape

from .models import Car, Fuel_Type

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def forgotpassword(request):
    return render(request, 'forgotpassword.html')

# made for testing purposes
# def search(request):
#     try:
#         # cars = Car.objects.all() # for now, just get all cars, not based on search
#         fuels = Fuel_Type.objects.all() # TESTING
#         return render(request, 'search.html', {'fuels': fuels})
#     except Car.DoesNotExist:
#         raise Http404("Could not find cars with that search criteria.")
