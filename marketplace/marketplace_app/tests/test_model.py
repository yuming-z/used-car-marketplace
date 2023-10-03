from django.test import TestCase

from marketplace_app.models import *

class UserDeatilTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="test", password="test")
    
    def test_no_mobile(self):
        User_Detail.objects.create(user=self.user)
        self.assertTrue(User_Detail.objects.filter(user=self.user).exists())
    
    def test_too_long_mobile(self):
        user_detail = User_Detail.objects.create(user=self.user, mobile="04000000000")
        self.assertRaises(ValidationError, user_detail.clean)

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
        car = Car.objects.create(year=year, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=self.description, condition=self.condition, owner=self.owner, location=self.location)

        self.assertRaises(ValidationError, car.clean_fields)
    
    def test_invalid_year(self):
        year = 123
        car = Car.objects.create(year=year, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=self.description, condition=self.condition, owner=self.owner, location=self.location)

        self.assertRaises(ValidationError, car.clean_fields)

    def test_invalid_car_status(self):
        status = "Test"
        car = Car.objects.create(year=2021, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=status, price=self.price, description=self.description, condition=self.condition, owner=self.owner, location=self.location)

        self.assertRaises(ValidationError, car.clean_fields)

    def test_invalid_car_condition(self):
        condition = "Test"
        car = Car.objects.create(year=2021, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=self.description, condition=condition, owner=self.owner, location=self.location)

        self.assertRaises(ValidationError, car.clean_fields)

    def test_empty_description(self):
        description = ""
        car = Car.objects.create(year=2021, model=self.model_detail, registration_number=self.registration_number, odometer=self.odometer, fuel_type=self.fuel_detail, status=self.status, price=self.price, description=description, condition=self.condition, owner=self.owner, location=self.location)

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
        self.car = Car.objects.create(year=2021, model=self.model, registration_number="ABC123", odometer=1000, fuel_type=fuel, status="AVAILABLE", price=1000, description="", condition="EXCELLENT", owner=self.seller, location="Sydney")
        self.car.transmission.set([transmission])
        
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
        status = ["PENDING", "COMPLETED"]

        for s in range(0, len(status)):
            with self.subTest(status=status[s]):
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