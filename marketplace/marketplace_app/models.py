from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class User_Detail(models.Model):
    '''
    The model to store user details.
    It stores any extra fields about the user other the fields defined in the build-in user model.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_detail", primary_key=True)
    mobile = models.IntegerField(max_length=10, blank=True, null=True) # assume Asutralian mobile number without country code

class Fuel_Type(models.Model):
    '''
    The model to store fuel types.
    '''
    name = models.CharField(max_length=11)

    def __str__(self):
        return self.name
    
class Car_Brand(models.Model):
    '''
    The model to store car brand information.
    '''
    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.name

class Car_Model(models.Model):
    '''
    The model to store car model information.
    '''
    brand = models.ForeignKey(Car_Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

class Transmission_Type(models.Model):
    '''
    The model to store transmission types.
    '''
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name

class Car(models.Model):
    '''
    The model to store car information.
    '''
    CAR_STATUS = [
        ("AVAILABLE", "The car is available for sale."),
        ("PENDING", "The car is pending for sale."),
        ("SOLD", "The car is sold."),
        ("UNAVAILABLE", "The car is not available for sale."),
    ]

    CAR_CONDITION = [ # the standard from Kelly's Blue Book
        ("EXCELLENT", "The vehicle looks new and is in excellent mechanical condition."),
        ("GOOD", "The vehicle has minor cosmetic defects and is in good mechanical condition."),
        ("FAIR", "The vehicle has some repairable cosmetic defects and is free of major mechanical problems."),
        ("POOR", "The vehicle has significant cosmetic defects and is in need of mechanical repairs."),
    ]

    year = models.IntegerField(max_length=4)
    model = models.ForeignKey(Car_Model, on_delete=models.CASCADE, related_name="cars")
    registration_number = models.CharField(max_length=6)
    status = models.CharField(max_length=11, choices=CAR_STATUS)
    description = models.TextField()
    odometer = models.IntegerField()
    price = models.FloatField()
    condition = models.CharField(max_length=8, choices=CAR_CONDITION)
    fuel_type = models.ForeignKey(Fuel_Type, on_delete=models.CASCADE, related_name="cars")
    transmission = models.ManyToManyField(Transmission_Type, related_name="cars")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    prev_owner_count = models.IntegerField(default=1)
    location = models.CharField(max_length=100)

class Car_File(models.Model):
    '''
    The model to store car files.
    '''
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to='car/<int:car_id>/uploads')

class Wishlist(models.Model):
    '''
    The model to store the wishlist of a user.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist", primary_key=True)
    cars = models.ManyToManyField(Car, related_name="wishlists")

class Order(models.Model):
    '''
    The model to store the order information.
    '''
    ORDER_STATUS = [
        ("PENDING", "The order is pending."),
        ("COMPLETED", "The order is completed."),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=9, choices=ORDER_STATUS)

    def clean(self):
        '''
        The function to check if the buyer and seller are the same.
        '''
        if self.seller == self.buyer:
            raise ValidationError("The buyer and seller cannot be the same person.")

class Preferred_Year_Range(models.Model):
    '''
    The model to store the preferred year range for a user on the cars.
    '''
    year_min = models.IntegerField(max_length=4)
    year_max = models.IntegerField(max_length=4)

    def __str__(self) -> str:
        return "From " + str(self.year_min) + " to " + str(self.year_max) + "."
    
class Preferred_Price_Range(models.Model):
    '''
    The model to store the preferred price range for a user on the cars.
    '''
    price_min = models.FloatField()
    price_max = models.FloatField()

    def __str__(self) -> str:
        return "From " + str(self.price_min) + " to " + str(self.price_max) + "."
    
class Preferred_Odometer_Range(models.Model):
    '''
    The model to store the preferred odometer range for a user on the cars.
    '''
    odometer_min = models.IntegerField()
    odometer_max = models.IntegerField()

    def __str__(self) -> str:
        return "From " + str(self.odometer_min) + " to " + str(self.odometer_max) + "."

class Preference(models.Model):
    '''
    The model to store the preference of a user.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preference", primary_key=True)
    year_range = models.ForeignKey(Preferred_Year_Range, on_delete=models.CASCADE, related_name="preferences", blank=True, null=True)
    price_range = models.ForeignKey(Preferred_Price_Range, on_delete=models.CASCADE, related_name="preferences", blank=True, null=True)
    odometer_range = models.ForeignKey(Preferred_Odometer_Range, on_delete=models.CASCADE, related_name="preferences", blank=True, null=True)
    fuel = models.ManyToManyField(Fuel_Type, related_name="preferences", blank=True, null=True)
    transmission = models.ManyToManyField(Transmission_Type, related_name="preferences", blank=True, null=True)
    model = models.ManyToManyField(Car_Model, related_name="preferences", blank=True, null=True)
    brand = models.ManyToManyField(Car_Brand, related_name="preferences", blank=True, null=True)

    def clean(self):
        '''
        The function to check if the min value is less than the max value.
        '''
        if self.year_min > self.year_max:
            raise ValidationError("The minimum year cannot be greater than the maximum year.")
        if self.price_min > self.price_max:
            raise ValidationError("The minimum price cannot be greater than the maximum price.")
        if self.odometer_min > self.odometer_max:
            raise ValidationError("The minimum odometer cannot be greater than the maximum odometer.")

class Seller_Rating(models.Model):
    '''
    The model to store the seller rating information.
    '''
    RATING = [
        (1, "Very bad"),
        (2, "Bad"),
        (3, "Average"),
        (4, "Good"),
        (5, "Very good"),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_ratings")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_ratings")
    rating = models.IntegerField(choices=RATING)
    comment = models.TextField(blank=True)

    def clean(self) -> None:
        '''
        The function to check if the buyer and seller are the same.
        '''
        if self.seller == self.buyer:
            raise ValidationError("The buyer and seller cannot be the same person.")

class Buyer_Rating(models.Model):
    '''
    The model to store the buyer rating information.
    '''
    RATING = [
        (1, "Very bad"),
        (2, "Bad"),
        (3, "Average"),
        (4, "Good"),
        (5, "Very good"),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer_ratings")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer_ratings")
    rating = models.IntegerField(choices=RATING)
    comment = models.TextField(blank=True)

    def clean(self) -> None:
        '''
        The function to check if the buyer and seller are the same.
        '''
        if self.seller == self.buyer:
            raise ValidationError("The buyer and seller cannot be the same person.")