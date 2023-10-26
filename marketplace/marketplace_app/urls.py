from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('index', views.index, name="index"),
    path('error_page', views.error_page_view, name="error_page"),

    # login/signup
    path('login', views.login_view, name="login"),
    path('signup', views.signup_view, name="signup"),

    # forgot/reset password
    path('forgotpassword', views.forgotpassword_view, name="forgotpassword"),
    path('reset_password/<uidb64>/<token>/', views.resetpassword_view, name="reset_password"),
    path('reset_email_sent', views.reset_email_sent, name="reset_email_sent"),
    path('invalid_reset', views.invalid_reset_view, name="invalid_reset"),

    # email activation for signup
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    path('activate_email_sent', views.activate_email_sent, name="activate_email_sent"),
    path('invalid_activation', views.invalid_activation_view, name="invalid_activation"),

    # ratings
    path('rating_seller/<int:seller_id>/', views.rate_seller_view, name='rating_seller'),
    path('rating_buyer/<int:buyer_id>/', views.rate_buyer_view, name="rating_buyer"),
    path('confirm_rating', views.confirm_rating_view, name="confirm_rating"),
    
    # car creations
    path('car', views.CarCreateView.as_view(), name="create-car"),
    path('model', views.CarModelCreateView.as_view(), name="create-model"),
    path('brand', views.CarBrandCreateView.as_view(), name="create-brand"),
    path('transmission', views.TransmissionCreateView.as_view(), name="create-transmission"),
    path("fuel", views.FuelCreateView.as_view(), name="create-fuel"),
]