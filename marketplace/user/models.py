from django.db import models
from django.contrib.auth.models import User

class Wishlist(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    car_id = models.ManyToManyField('car.Car')

class Preference(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preference")
    fuel_type = models.ManyToManyField('car.FuelType', blank=True, null=True)
    transmission = models.CharField(max_length=50, blank=True)
    model = models.ManyToManyField('car.CarModel', blank=True, null=True)
    brand = models.ManyToManyField('car.CarBrand', blank=True, null=True)
    year_min = models.IntegerField(blank=True, null=True)
    year_max = models.IntegerField(blank=True, null=True)
    odometer_min = models.IntegerField(blank=True, null=True)
    odometer_max = models.IntegerField(blank=True, null=True)
    price_min = models.IntegerField(blank=True, null=True)
    price_max = models.IntegerField(blank=True, null=True)