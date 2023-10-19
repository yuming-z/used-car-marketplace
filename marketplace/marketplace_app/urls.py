from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('index', views.index, name="index"),
    path('login', views.login, name="login"),
    path('signup', views.signup, name="signup"),
    path('forgotpassword', views.forgotpassword, name="forgotpassword"),
    path('car', views.CarCreateView.as_view(), name="create-car"),
    path('model', views.CarModelCreateView.as_view(), name="create-model"),
]