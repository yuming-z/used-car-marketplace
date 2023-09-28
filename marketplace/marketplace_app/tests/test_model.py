from django.test import TestCase

from marketplace_app.models import *

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