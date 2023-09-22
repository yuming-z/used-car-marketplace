from django.test import TestCase
from unittest.mock import Mock

from ..models import *

class OrderTest(TestCase):

    def setUp(self) -> None:
        '''
        Set up the test cases.
        '''

        # create a user
        self.seller = Mock(spec=User)
        self.buyer = Mock(spec=User)

        # Create a mock for Car
        self.car = Mock(spec=Car)
        
    def test_order_same_seller_buyer(self):
        order = Order.objects.create(seller=self.seller, buyer=self.seller, car=self.car, status="PENDING")
        self.assertRaises(ValidationError, order.clean, "The buyer and seller cannot be the same person.")

    def test_order_different_seller_buyer(self):
        order = Order.objects.create(seller=self.seller, buyer=self.buyer, car=self.car, status="PENDING")
        self.assertIsNone(order.clean(), "The buyer and seller are different persons.")
    
    def test_order_invalid_status(self):
        status = "Test"
        order = Order.objects.create(seller=self.seller, buyer=self.buyer, car=self.car, status=status)
        self.assertRaises(ValidationError, order.clean(), "The status is invalid.")
    
    def test_order_pending(self):
        status = "PENDING"
        order = Order.objects.create(seller=self.seller, buyer=self.buyer, car=self.car, status=status)
        self.assertIsNone(order.clean(), "The status is valid.")

    def test_order_completed(self):
        status = "COMPLETED"
        order = Order.objects.create(seller=self.seller, buyer=self.buyer, car=self.car, status=status)
        self.assertIsNone(order.clean(), "The status is valid.")