from django.test import TestCase
from psycopg2.errors import NumericValueOutOfRange

from marketplace_app.models import *

class UserDeatilTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="test", password="test")
    
    def test_no_mobile(self):
        User_Detail.objects.create(user=self.user)
        self.assertTrue(User_Detail.objects.filter(user=self.user).exists())
    
    # def test_too_long_mobile(self):
    #     user_detail = User_Detail.objects.create(user=self.user, mobile="04000000000")
    #     self.assertRaises(NumericValueOutOfRange, user_detail.clean)

    def test_invalid_mobile(self):
        user_detail = User_Detail.objects.create(user=self.user, mobile="1234567890")
        self.assertRaises(ValidationError, user_detail.clean)

    def test_creation(self):
        User_Detail.objects.create(user=self.user, mobile="0412345690")
        self.assertTrue(User_Detail.objects.filter(user=self.user).exists())

class FuelTypeTest(TestCase):
    def test_fuel_display(self):
        fuel_name = "Electricity"
        fuel = Fuel_Type.objects.create(name=fuel_name)
        self.assertEqual(fuel.name, str(Fuel_Type.objects.filter(name=fuel_name).first()))

class TestCarBrand(TestCase):
    def test_car_brand_display(self):
        brand_name = "Test Brand"
        brand = Car_Brand.objects.create(name=brand_name)
        self.assertEqual(brand.name, str(Car_Brand.objects.filter(name=brand_name).first()))

class TestCarModel(TestCase):

    def setUp(self) -> None:
        self.brand_detail = Car_Brand.objects.create(name="Test Brand")

    def test_car_model_display(self):
        model_name = "Test Model"
        model = Car_Model.objects.create(brand=self.brand_detail, name=model_name)

        self.assertEqual(model.name, str(Car_Model.objects.filter(name=model_name).first()))

class TestTransmissionType(TestCase):
    def test_transmission_type_display(self):
        transmission_name = "Test Transmission"
        transmission = Transmission_Type.objects.create(name=transmission_name)

        self.assertEqual(transmission.name, str(Transmission_Type.objects.filter(name=transmission_name).first()))

class TestCar(TestCase):
    def setUp(self) -> None:
        self.brand_detail = Car_Brand.objects.create(name="Test Brand")
        self.model_detail = Car_Model.objects.create(name="Test Model", brand=self.brand_detail)
        self.owner = User.objects.create(username="test", password="test")
        self.fuel_detail = Fuel_Type.objects.create(name="Test Fuel")
        self.transmission_detail = Transmission_Type.objects.create(name="Test Transmission")
        self.registration_number = "ABC123"
        self.odometer = 1000
        self.status = "AVAILABLE"
        self.price = 1000
        self.description = "Sample description"
        self.condition = "EXCELLENT"
        self.location = "Sydney"
    
    def test_future_year(self):
        year = 3000
        car = Car.objects.create(transmission=self.transmission_detail, year=year, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=self.description, condition=self.condition, owner=self.owner, location=self.location)

        self.assertRaises(ValidationError, car.clean_fields)
    
    def test_invalid_year(self):
        year = 123
        car = Car.objects.create(transmission=self.transmission_detail, year=year, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=self.description, condition=self.condition, owner=self.owner, location=self.location)

        self.assertRaises(ValidationError, car.clean_fields)

    def test_invalid_car_status(self):
        status = "Test"
        car = Car.objects.create(transmission=self.transmission_detail, year=2021, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=status, price=self.price, description=self.description, condition=self.condition, owner=self.owner, location=self.location)

        self.assertRaises(ValidationError, car.clean_fields)

    def test_invalid_car_condition(self):
        condition = "Test"
        car = Car.objects.create(transmission=self.transmission_detail, year=2021, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=self.description, condition=condition, owner=self.owner, location=self.location)

        self.assertRaises(ValidationError, car.clean_fields)

    def test_empty_description(self):
        description = ""
        car = Car.objects.create(transmission=self.transmission_detail, year=2021, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=description, condition=self.condition, owner=self.owner, location=self.location)

        self.assertTrue(Car.objects.filter(year=2021, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=description, condition=self.condition, owner=self.owner, location=self.location).exists())

class OrderTest(TestCase):

    def setUp(self) -> None:
        '''
        Set up the test cases.
        '''

        # create a user
        self.seller = User.objects.create(username="seller", password="seller")
        self.buyer = User.objects.create(username="buyer", password="buyer")

        # Create a sample brand for car
        self.brand = Car_Brand.objects.create(name="Test Brand")

        # Create a test model for car
        self.model = Car_Model.objects.create(name="Test Model", brand=self.brand)
        
        # Create a test fuel
        fuel = Fuel_Type.objects.create(name="Test Fuel")

        # Create a test transmission
        transmission = Transmission_Type.objects.create(name="Test Transmission")

        # Create a test car
        self.car = Car.objects.create(transmission=transmission, year=2021, model=self.model, registration_number="ABC123", odometer=1000, fuel_type=fuel, status="AVAILABLE", price=1000, description="", condition="EXCELLENT", owner=self.seller, location="Sydney")
        
    def test_order_same_seller_buyer(self):
        order = Order.objects.create(seller=self.seller, buyer=self.seller, car=self.car, status="PENDING")
        self.assertRaises(ValidationError, order.clean)

    def test_order_different_seller_buyer(self):
        Order.objects.create(seller=self.seller, buyer=self.buyer, car=self.car)
        self.assertTrue(Order.objects.filter(seller=self.seller, buyer=self.buyer, car=self.car).exists())      
    
    def test_order_invalid_status(self):
        status = "Test"
        order = Order.objects.create(seller=self.seller, buyer=self.buyer, car=self.car, status=status)
        self.assertRaises(ValidationError, order.clean_fields)
    
    def test_order_status(self):
        status_list = ["PENDING", "COMPLETED"]

        for status in status_list:
            with self.subTest(status=status):
                Order.objects.create(seller=self.seller, buyer=self.buyer, car=self.car, status=status)
                self.assertTrue(Order.objects.filter(seller=self.seller, buyer=self.buyer, car=self.car, status=status).exists())
    
class TestPreferredYearRange(TestCase):
    def test_invalid_max_year(self):
        year_min = 1990
        year_max = 1980
        preferred_year_range = Preferred_Year_Range.objects.create(year_min=year_min, year_max=year_max)
        self.assertRaises(ValidationError, preferred_year_range.clean)
    
    def test_invalid_min_year(self):
        year_min = 123
        year_max = 1990
        preferred_year_range = Preferred_Year_Range.objects.create(year_min=year_min, year_max=year_max)

        self.assertRaises(ValidationError, preferred_year_range.clean_fields)
    
    def test_min_future_year(self):
        year_min = 3000
        year_max = 3001
        preferred_year_range = Preferred_Year_Range.objects.create(year_min=year_min, year_max=year_max)
        self.assertRaises(ValidationError, preferred_year_range.clean_fields)
    
    def test_max_future_year(self):
        year_min = 1990
        year_max = 3001
        preferred_year_range = Preferred_Year_Range.objects.create(year_min=year_min, year_max=year_max)
        self.assertRaises(ValidationError, preferred_year_range.clean_fields)

    def test_invalid_max_year(self):
        year_min = 1990
        year_max = 12345
        preferred_year_range = Preferred_Year_Range.objects.create(year_min=year_min, year_max=year_max)
        self.assertRaises(ValidationError, preferred_year_range.clean_fields)
    
    def test_display(self):
        year_min = 1990
        year_max = 1991
        preferred_year_range = Preferred_Year_Range.objects.create(year_min=year_min, year_max=year_max)
        self.assertEqual(str(preferred_year_range), f"From {year_min} to {year_max}.")

class TestPreferredPriceRange(TestCase):
    def test_max_less_than_min(self):
        price_min = 1000.0
        price_max = 500.0
        preferred_price_range = Preferred_Price_Range.objects.create(price_min=price_min, price_max=price_max)
        
        self.assertRaises(ValidationError, preferred_price_range.clean)
    
    def test_preference_display(self):
        price_min = 1000.0
        price_max = 5000.0
        preferred_price_range = Preferred_Price_Range.objects.create(price_min=price_min, price_max=price_max)

        self.assertEqual(str(preferred_price_range), f"From {price_min} to {price_max}.")

class TestPreferredOdometerRange(TestCase):
    def test_max_less_than_min(self):
        odometer_min = 1000
        odometer_max = 500
        preferred_odometer_range = Preferred_Odometer_Range.objects.create(odometer_min=odometer_min, odometer_max=odometer_max)
        
        self.assertRaises(ValidationError, preferred_odometer_range.clean)
    
    def test_preference_display(self):
        odometer_min = 1000
        odometer_max = 5000
        preferred_odometer_range = Preferred_Odometer_Range.objects.create(odometer_min=odometer_min, odometer_max=odometer_max)

        self.assertEqual(str(preferred_odometer_range), f"From {odometer_min} to {odometer_max}.")

class TestPreference(TestCase):
    def setUp(self) -> None:
        # Create a user
        self.user = User.objects.create(username="test", password="test")

        # Define year range
        year_min = 2000
        year_max = 2022

        self.year_range = Preferred_Year_Range.objects.create(year_min=year_min, year_max=year_max)

        # Define price range
        price_min = 1000.0
        price_max = 5000.0

        self.price_range = Preferred_Price_Range.objects.create(price_min=price_min, price_max=price_max)

        # Define odometer range
        odometer_min = 1000
        odometer_max = 10000

        self.odometer_range = Preferred_Odometer_Range.objects.create(odometer_min=odometer_min, odometer_max=odometer_max)

        # Create fuel types
        self.diesel = Fuel_Type.objects.create(name="Diesel")
        self.electricity = Fuel_Type.objects.create(name="Electricity")

        # Create transmission types
        self.manual = Transmission_Type.objects.create(name="Manual")
        self.automatic = Transmission_Type.objects.create(name="Automatic")

        # Create car brands
        self.toyota = Car_Brand.objects.create(name="Toyota")
        self.honda = Car_Brand.objects.create(name="Honda")

        # Create car models
        self.camry = Car_Model.objects.create(name="Camry", brand=self.toyota)
        self.civic = Car_Model.objects.create(name="Civic", brand=self.honda)

    def test_blank_year_range(self):
        preference = Preference(
            user=self.user,
            price_range=self.price_range,
            odometer_range=self.odometer_range,
        )
        preference.save()

        # add many-to-many relationships
        preference.fuel.add(self.diesel, self.electricity)
        preference.transmission.add(self.manual, self.automatic)
        preference.model.add(self.camry, self.civic)
        preference.brand.add(self.toyota, self.honda)

        # Assertions
        self.assertTrue(Preference.objects.filter(user=self.user, price_range=self.price_range, odometer_range=self.odometer_range).exists())
        
    def test_blank_price_range(self):
        preference = Preference(
            user=self.user,
            year_range=self.year_range,
            odometer_range=self.odometer_range,
        )
        preference.save()

        # add many-to-many relationships
        preference.fuel.add(self.diesel, self.electricity)
        preference.transmission.add(self.manual, self.automatic)
        preference.model.add(self.camry, self.civic)
        preference.brand.add(self.toyota, self.honda)

        # Assertions
        self.assertTrue(Preference.objects.filter(user=self.user, year_range=self.year_range, odometer_range=self.odometer_range).exists())
    
    def test_blank_odometer_range(self):
        preference = Preference(
            user=self.user,
            year_range=self.year_range,
            price_range=self.price_range,
        )
        preference.save()

        # add many-to-many relationships
        preference.fuel.add(self.diesel, self.electricity)
        preference.transmission.add(self.manual, self.automatic)
        preference.model.add(self.camry, self.civic)
        preference.brand.add(self.toyota, self.honda)

        # Assertions
        self.assertTrue(Preference.objects.filter(user=self.user, year_range=self.year_range, price_range=self.price_range).exists())
    
    def test_blank_fuel(self):
        preference = Preference(
            user=self.user,
            year_range=self.year_range,
            price_range=self.price_range,
            odometer_range=self.odometer_range,
        )
        preference.save()

        # add many-to-many relationships
        preference.transmission.add(self.manual, self.automatic)
        preference.model.add(self.camry, self.civic)
        preference.brand.add(self.toyota, self.honda)

        # Assertions
        self.assertTrue(Preference.objects.filter(user=self.user, year_range=self.year_range, price_range=self.price_range, odometer_range=self.odometer_range).exists())
    
    def test_blank_transmission(self):
        preference = Preference(
            user=self.user,
            year_range=self.year_range,
            price_range=self.price_range,
            odometer_range=self.odometer_range,
        )
        preference.save()

        # add many-to-many relationships
        preference.fuel.add(self.diesel, self.electricity)
        preference.model.add(self.camry, self.civic)
        preference.brand.add(self.toyota, self.honda)

        # Assertions
        self.assertTrue(Preference.objects.filter(user=self.user, year_range=self.year_range, price_range=self.price_range, odometer_range=self.odometer_range).exists())
    
    def test_blank_model(self):
        preference = Preference(
            user=self.user,
            year_range=self.year_range,
            price_range=self.price_range,
            odometer_range=self.odometer_range,
        )
        preference.save()

        # add many-to-many relationships
        preference.fuel.add(self.diesel, self.electricity)
        preference.transmission.add(self.manual, self.automatic)
        preference.brand.add(self.toyota, self.honda)

        # Assertions
        self.assertTrue(Preference.objects.filter(user=self.user, year_range=self.year_range, price_range=self.price_range, odometer_range=self.odometer_range).exists())
    
    def test_blank_brand(self):
        preference = Preference(
            user=self.user,
            year_range=self.year_range,
            price_range=self.price_range,
            odometer_range=self.odometer_range,
        )
        preference.save()

        # add many-to-many relationships
        preference.fuel.add(self.diesel, self.electricity)
        preference.transmission.add(self.manual, self.automatic)
        preference.model.add(self.camry, self.civic)

        # Assertions
        self.assertTrue(Preference.objects.filter(user=self.user, year_range=self.year_range, price_range=self.price_range, odometer_range=self.odometer_range).exists())

class TestSellerRating(TestCase):
    def setUp(self) -> None:
        self.seller = User.objects.create(username="seller", password="seller")
        self.buyer = User.objects.create(username="buyer", password="buyer")
        self.comment = "test comment"
    
    def test_invalid_rating(self):
        rating = 6
        seller_rating = Seller_Rating.objects.create(rating=rating, comment=self.comment, seller=self.seller, buyer=self.buyer)
        self.assertRaises(ValidationError, seller_rating.clean_fields)
    
    def test_invalid_user(self):
        seller_rating = Seller_Rating.objects.create(rating=1, comment=self.comment, seller=self.seller, buyer=self.seller)
        self.assertRaises(ValidationError, seller_rating.clean)
    
    def test_empty_comment(self):
        comment = ""
        Seller_Rating.objects.create(rating=1, comment=comment, seller=self.seller, buyer=self.buyer)
        self.assertTrue(Seller_Rating.objects.filter(rating=1, comment=comment, seller=self.seller, buyer=self.buyer).exists())

class TestBuyerRating(TestCase):
    def setUp(self) -> None:
        self.seller = User.objects.create(username="seller", password="seller")
        self.buyer = User.objects.create(username="buyer", password="buyer")
        self.comment = "test comment"
    
    def test_invalid_rating(self):
        rating = 6
        buyer_rating = Buyer_Rating.objects.create(rating=rating, comment=self.comment, buyer=self.buyer, seller=self.seller)
        self.assertRaises(ValidationError, buyer_rating.clean_fields)
    
    def test_invalid_user(self):
        buyer_rating = Buyer_Rating.objects.create(rating=1, comment=self.comment, buyer=self.seller, seller=self.seller)
        self.assertRaises(ValidationError, buyer_rating.clean)
    
    def test_empty_comment(self):
        comment = ""
        Buyer_Rating.objects.create(rating=1, comment=comment, buyer=self.buyer, seller=self.seller)
        self.assertTrue(Buyer_Rating.objects.filter(rating=1, comment=comment, buyer=self.buyer, seller=self.seller).exists())