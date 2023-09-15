from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from car.models import Car

class Order(models.Model):

    ORDER_STATUS = [
        ("PENDING", "PENDING"),
        ("FINALISED", "FINALISED"),
    ]

    seller = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="orders")
    buyer = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="orders")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default="PENDING")

    def clean(self) -> None:
        if self.seller == self.buyer:
            raise ValidationError({"buyer": "You cannot buy your own car!"})