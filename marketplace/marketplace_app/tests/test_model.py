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