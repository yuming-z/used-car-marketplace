from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('index', views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('forgotpassword', views.forgotpassword_view, name="forgotpassword"),
    path('signup', views.signup_view, name="signup"),
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    path('activate_email_sent', views.activate_email_sent, name='activate_email_sent'),
    path('invalid_activation', views.invalid_activation_view, name='invalid_activation'),
]