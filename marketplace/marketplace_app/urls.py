from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('index', views.index, name="index"),

    # login/signup
    path('login', views.login_view, name="login"),
    path('signup', views.signup_view, name="signup"),
    path('forgotpassword', views.forgotpassword_view, name="forgotpassword"),

    # email activation for signup
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    path('activate_email_sent', views.activate_email_sent, name="activate_email_sent"),
    path('invalid_activation', views.invalid_activation_view, name="invalid_activation"),

    # car creations
    path('car', views.CarCreateView.as_view(), name="create-car"),
    path('model', views.CarModelCreateView.as_view(), name="create-model"),
    path('brand', views.CarBrandCreateView.as_view(), name="create-brand"),
    path('transmission', views.TransmissionCreateView.as_view(), name="create-transmission"),
    path("fuel", views.FuelCreateView.as_view(), name="create-fuel"),
]