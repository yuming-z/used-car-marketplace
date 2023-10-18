from django.forms import ModelForm

from .models import Car, Car_Brand, Car_Model, Car_File, Fuel_Type, Transmission_Type

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
            'odometer',
            'price',
            'condition',
            'fuel_type',
            'transmission',
            'owner',
            'prev_owner_count',
            'location',
            'description',
        )
        labels = {
            'fuel_type': 'Fuel type',
            'prev_owner_count': 'The number of previous owners'
        }
    
class ModelForm(ModelForm):
    '''
    The form to create a new model.
    '''
    class Meta:
        model = Car_Model
        fields = (
            'brand',
            'name',
        )

class BrandForm(ModelForm):
    '''
    The form to create a new car brand
    '''
    class Meta:
        model = Car_Brand
        fields = (
            'name',
        )

class TranmissionForm(ModelForm):
    '''
    The form to create a new transmission type
    '''
    class Meta:
        model = Transmission_Type
        fields = (
            'name',
        )

class FuelForm(ModelForm):
    class Meta:
        model = Fuel_Type
        fields = (
            'name',
        )

class CarFileForm(ModelForm):
    class Meta:
        model = Car_File
        fields = (
            'car',
            'file',
        )