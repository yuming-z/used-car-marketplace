from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  
from .models import User_Detail

from .models import Car, Car_Brand, Car_Model, Car_File, Fuel_Type, Transmission_Type, User_Detail

class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(label='Enter New Password', required=True, widget=forms.TextInput(attrs={ "placeholder": "password", "type":"password", "class": "form-control"}))  
    password2 = forms.CharField(label='Confirm New Password', required=True, widget=forms.TextInput(attrs={ "placeholder": "confirm password", "type":"password", "class": "form-control"}))  

    def clean_password(self):  
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
        if password1 and password2 and password1 != password2:  
            raise ValidationError("Password don't match")  
        return password2   
    
    def checks_if_old_password(self, user):
        try:
            password = self.clean_password()
            return user.check_password(password), "success"
        
        except ValidationError as e:
            return False, "matching"

class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, required=True, widget=forms.TextInput({"placeholder": "example@email.com", "class": "form-control"}))

    def email_exists(self):
        email = self.cleaned_data['email'].lower()  
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Email does not exist")
        return email 
    
    def get_user(self):
        try:
            user = User.objects.filter(email=self.email_exists()).first()
        except ValidationError as e:
            user = None
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, required=True, widget=forms.TextInput({"placeholder": "example@email.com", "class": "form-control"}))
    password = forms.CharField(label='Password', required=True, widget=forms.TextInput({ "placeholder": "password", "type": "password", "class": "form-control"}))

class SignupForm(UserCreationForm):
    email = forms.EmailField(label="Email", max_length=254, required=True, widget=forms.TextInput(attrs={ "placeholder": "example@email.com", "type":"email", "class": "form-control"}))
    number = forms.IntegerField(label="Mobile Number", required=True, widget=forms.TextInput(attrs={ "placeholder": "0444444444", "type":"tel", "pattern":"04[0-9]{2}[0-9]{3}[0-9]{3}", "class": "form-control"}))
    first_name = forms.CharField(label='First Name', required=True, min_length=1, max_length=150, widget=forms.TextInput(attrs={ "placeholder": "John", "class": "form-control"}))  
    last_name = forms.CharField(label='Last Name', required=True, min_length=1, max_length=150, widget=forms.TextInput(attrs={ "placeholder": "Citizen", "class": "form-control"}))  
    password1 = forms.CharField(label='Enter Password', required=True, widget=forms.TextInput(attrs={ "placeholder": "password", "type":"password", "class": "form-control"}))  
    password2 = forms.CharField(label='Confirm Password', required=True, widget=forms.TextInput(attrs={ "placeholder": "confirm password", "type":"password", "class": "form-control"}))  

    class Meta:
        model = User
        fields = ("email", "password1", "password2", "first_name", "last_name", "number")

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        try:
            user.email = self.email_exists()
            user.number = self.number_exists()
            user.username = self.first_name  # Set username to email
            user.first_name = self.first_name
            user.last_nameb = self.last_name
            if commit:
                user.save()
            return user, ""
        
        except ValidationError as e:
            print("Error saving. Mobile or Email already exists")
            print(e.message)
            if e.message == "Mobile number already exists":
                return None, "mobile"
            elif e.message == "Email already exists":
                return None, "email"
        
    # checks if email already exists in the database
    def email_exists(self):
        email = self.cleaned_data['email'].lower()  
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email  

    # checks if mobile number already exists in the database
    def number_exists(self):
        number = self.cleaned_data['number']
        if User_Detail.objects.filter(mobile=number).exists():
            raise ValidationError("Mobile number already exists") 
        return number 

    # checks if password and confirmation password match.
    # (never really used cause html handles it)
    def clean_password(self):  
        password1 = self.cleaned_data['password1']  
        password2 = self.cleaned_data['password2']  
        if password1 and password2 and password1 != password2:  
            raise ValidationError("Password don't match")  
        return password2   

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
    
class CarModelForm(forms.ModelForm):
    '''
    The form to create a new model.
    '''
    class Meta:
        model = Car_Model
        fields = (
            'brand',
            'name',
        )

class CarBrandForm(forms.ModelForm):
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

class UserUpdateForm(forms.ModelForm):
    # username = forms.CharField()
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class User_DetailUpdateForm(forms.ModelForm):
    # mobile = forms.IntegerField()
    city_address = forms.CharField()
    class Meta:
        model = User_Detail
        fields = ['city_address']

