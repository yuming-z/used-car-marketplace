from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  

from .models import User_Detail

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
            user.username = user.email  # Set username to email
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
