from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import datetime

def validate_year(year):
    """
    Validate whether the year is in the correct format.
    Year should be in the format of 4 digits (yyyy).
    """
    if len(str(year)) != 4:
        raise ValidationError(_("Year must be 4 digits."))
    
    if year > datetime.now().year:
        raise ValidationError(_("Year cannot be in the future."))

class User_Detail(models.Model):
    '''
    The model to store user details.
    It stores any extra fields about the user other the fields defined in the build-in user model.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_detail", primary_key=True)
    mobile = models.IntegerField(blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    city_address = models.CharField(max_length=255,blank=True, null=True)

    def clean(self) -> None:
        '''
        The function to check if the mobile number is valid.
        Assume Australian mobile number without country code.
        '''
        if (self.mobile is not None) and (self.mobile != ""):

            mobile_string = str(self.mobile)

            if len(mobile_string) != 10:
                raise ValidationError(_("The mobile number should have 10 numbers."))
            
            if not mobile_string.startswith("04"):
                # ref: https://www.australia.gov.au/telephone-country-and-area-codes
                raise ValidationError(_("The mobile number is invalid."))
            
# define a natural key for car brand 
# to be better referenced as a foreign key
class FuelTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Fuel_Type(models.Model):
    '''
    The model to store fuel types.
    '''
    name = models.CharField(max_length=11)
    
    objects = FuelTypeManager()

    def __str__(self):
        return self.name
    
# define a natural key for car brand 
# to be better referenced as a foreign key
class CarBrandManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
class Car_Brand(models.Model):
    '''
    The model to store car brand information.
    '''
    name = models.CharField(max_length=30)
    
    objects = CarBrandManager()

    def __str__(self) -> str:
        return self.name

# define a natural key method for car model 
# to be better referenced as a foreign key
class CarModelManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
class Car_Model(models.Model):
    '''
    The model to store car model information.
    '''
    brand = models.ForeignKey(Car_Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    
    objects = CarModelManager()

    def __str__(self) -> str:
        return self.name

class TransmissionManager(models.Manager):
        def get_by_natural_key(self, name):
            return self.get(name=name)
    
class Transmission_Type(models.Model):
    '''
    The model to store transmission types.
    '''
    name = models.CharField(max_length=20)
    
    objects = TransmissionManager()

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

    year = models.IntegerField(validators=[validate_year])
    model = models.ForeignKey(Car_Model, on_delete=models.CASCADE, related_name="cars")
    registration_number = models.CharField(max_length=6)
    status = models.CharField(max_length=11, choices=CAR_STATUS)
    description = models.TextField(blank=True, null=True)
    odometer = models.IntegerField()
    price = models.FloatField()
    condition = models.CharField(max_length=9, choices=CAR_CONDITION)
    fuel_type = models.ForeignKey(Fuel_Type, on_delete=models.CASCADE, related_name="cars")
    transmission = models.ForeignKey(Transmission_Type, on_delete=models.CASCADE, related_name="cars")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cars")
    prev_owner_count = models.IntegerField(default=1)
    location = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return "[Car ID: {}] {} {} {}, {}".format(self.id,  self.year, self.model, self.transmission, self.registration_number)


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

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "sales_orders")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchase_orders")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=9, choices=ORDER_STATUS, default="PENDING")
    order_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        '''
        The function to check if the buyer and seller are the same.
        '''
        if self.seller == self.buyer:
            raise ValidationError(_("The buyer and seller cannot be the same person."))

class Preferred_Year_Range(models.Model):
    '''
    The model to store the preferred year range for a user on the cars.
    '''
    year_min = models.IntegerField(validators=[validate_year])
    year_max = models.IntegerField(validators=[validate_year])

    def __str__(self) -> str:
        return "From " + str(self.year_min) + " to " + str(self.year_max) + "."
    
    def clean(self) -> None:
        '''
        Field validation
        '''
        # check if min year is less than max year
        if (self.year_min > self.year_max):
            raise ValidationError(_("The minimum year cannot be greater than the maximum year."))
        
    
class Preferred_Price_Range(models.Model):
    '''
    The model to store the preferred price range for a user on the cars.
    '''
    price_min = models.FloatField()
    price_max = models.FloatField()

    def __str__(self) -> str:
        return "From " + str(self.price_min) + " to " + str(self.price_max) + "."

    def clean(self) -> None:
        if self.price_min > self.price_max:
            raise ValidationError(_("The minimum price cannot be greater than the maximum price."))
    
class Preferred_Odometer_Range(models.Model):
    '''
    The model to store the preferred odometer range for a user on the cars.
    '''
    odometer_min = models.IntegerField()
    odometer_max = models.IntegerField()

    def __str__(self) -> str:
        return "From " + str(self.odometer_min) + " to " + str(self.odometer_max) + "."

    def clean(self) -> None:
        if self.odometer_min > self.odometer_max:
            raise ValidationError(_("The minimum odometer cannot be greater than the maximum odometer."))

class Preference(models.Model):
    '''
    The model to store the preference of a user.
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preference", primary_key=True)
    year_range = models.ForeignKey(Preferred_Year_Range, on_delete=models.CASCADE, related_name="preferences", blank=True, null=True)
    price_range = models.ForeignKey(Preferred_Price_Range, on_delete=models.CASCADE, related_name="preferences", blank=True, null=True)
    odometer_range = models.ForeignKey(Preferred_Odometer_Range, on_delete=models.CASCADE, related_name="preferences", blank=True, null=True)
    fuel = models.ManyToManyField(Fuel_Type, related_name="preferences", blank=True)
    transmission = models.ManyToManyField(Transmission_Type, related_name="preferences", blank=True)
    model = models.ManyToManyField(Car_Model, related_name="preferences", blank=True)
    brand = models.ManyToManyField(Car_Brand, related_name="preferences", blank=True)

class Rating(models.Model):
    '''
    The model to store the rating information.
    '''
    RATING = [
        (1, "Very bad"),
        (2, "Bad"),
        (3, "Average"),
        (4, "Good"),
        (5, "Very good"),
    ]
    
    rating = models.IntegerField(choices=RATING)
    comment = models.TextField(blank=True)
        
    class Meta:
        abstract = True
        
class Seller_Rating(Rating):
    '''
    The model to store the seller rating information.
    '''

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_ratings")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self) -> None:
        '''
        The function to check if the buyer and seller are the same.
        '''
        if self.seller == self.buyer:
            raise ValidationError(_("The buyer and seller cannot be the same person."))

class Buyer_Rating(Rating):
    '''
    The model to store the buyer rating information.
    '''

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer_ratings")
    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self) -> None:
        '''
        The function to check if the buyer and seller are the same.
        '''
        if self.seller == self.buyer:
            raise ValidationError(_("The buyer and seller cannot be the same person."))
        
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  
      
class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=100, choices=[("ACTIVE", "Active"), ("INACTIVE", "Inactive")])
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
