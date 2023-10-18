from django.forms import ModelForm
from django.core.exceptions import ValidationError

import re

from .models import Car

class CarForm(ModelForm):
    '''
    The form to create a new car
    '''
    class Meta:
        model = Car
        fields = (
            'year',
            'model',
            'registration_number',
            'status',
            'description',
            'odometer',
            'price',
            'condition',
            'fuel_type',
            'transmission',
            'owner',
            'prev_owner_count',
            'location'
        )
        labels = {
            'fuel_type': 'Fuel type',
            'prev_owner_count': 'The number of previous owners'
        }
    
    def clean_year(self):
        year = self.cleaned_data['year']

        year = str(year) # ensure the data type is string

        if len(year) != 4:
            raise ValidationError("Year must have 4 digits")
        if not re.match("^[0-9]{4}$", year):
            raise ValidationError("Year must be all digits")
        
        return int(year)
        