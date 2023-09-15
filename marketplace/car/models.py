from django.db import models
from django.contrib.auth.models import User

class CarBrand(models.Model):
    name = models.CharField(max_length=50)

class CarModel(models.Model):
    name = models.CharField(max_length=50)
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name="models")

class FuelType(models.Model):
    name = models.CharField(max_length=50)

class Car(models.Model):
    year = models.IntegerField()
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name="cars")
    registration_no = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    description = models.TextField()
    odometer = models.IntegerField()
    price = models.FloatField()
    condition = models.CharField(max_length=50)
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE, related_name="cars")
    transmission = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    prev_owner_count = models.IntegerField()
    location = models.CharField(max_length=50)

class CarFile(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="car/<int:car_id>/uploads/")