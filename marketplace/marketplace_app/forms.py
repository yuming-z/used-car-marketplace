from django import forms

from .models import Car, Car_Brand, Car_Model, Car_File, Fuel_Type, Transmission_Type

class CarForm(forms.ModelForm):
    '''
    The form to create a new car
    '''
    class Meta:
        model = Car
        fields = (
            'year',
            'registration_number',
            'status',
            'odometer',
            'price',
            'condition',
            'owner',
            'prev_owner_count',
            'location',
            'description',
            'model',
            'fuel_type',
            'transmission',
        )
        labels = {
            'fuel_type': 'Fuel type',
            'prev_owner_count': 'The number of previous owners'
        }
    
class ModelForm(forms.ModelForm):
    '''
    The form to create a new model.
    '''
    class Meta:
        model = Car_Model
        fields = (
            'brand',
            'name',
        )

class BrandForm(forms.ModelForm):
    '''
    The form to create a new car brand
    '''
    class Meta:
        model = Car_Brand
        fields = (
            'name',
        )

class TranmissionForm(forms.ModelForm):
    '''
    The form to create a new transmission type
    '''
    class Meta:
        model = Transmission_Type
        fields = (
            'name',
        )

class FuelForm(forms.ModelForm):
    class Meta:
        model = Fuel_Type
        fields = (
            'name',
        )

class CarFileForm(forms.ModelForm):
    class Meta:
        model = Car_File
        fields = (
            'car',
            'file',
        )