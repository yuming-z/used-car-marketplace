from django.test import TestCase
from unittest.mock import Mock

from ..models import *

class OrderTest(TestCase):

    def setUp(self) -> None:
        '''
        Set up the test cases.
        '''

        # create a user
        self.user = Mock(spec=User)

        # Create a mock for Car
        self.car = Mock(spec=Car)
        
    def test_order_creation(self):
        order = Order.objects.create(seller=self.user, buyer=self.user, car=self.car, status="PENDING")
        self.assertRaises(ValidationError, order.clean)