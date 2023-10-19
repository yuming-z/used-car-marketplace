"""
URL configuration for marketplace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('marketplace_app.urls')),
    path('index', include('marketplace_app.urls')),
    path('login', include('marketplace_app.urls')),
    path('signup', include('marketplace_app.urls')),
    path('forgotpassword', include('marketplace_app.urls')),
    path('activate/<uidb64>/<token>/', include('marketplace_app.urls')),
    path('activate_email_sent', include('marketplace_app.urls')),
    path('invalid_activation', include('marketplace_app.urls')),
    path('admin/', admin.site.urls),
]
