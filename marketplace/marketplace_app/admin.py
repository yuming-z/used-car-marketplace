from django.contrib import admin
from django.contrib.auth.models import Group
from . import models

@admin.register(models.Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'model', 'transmission', 'registration_number', 'status']
    search_fields = ['id', 'year', 'model__name', 'transmission__name', 'status']
    list_filter = ['year', 'model', 'transmission']
    
admin.site.unregister(Group)