import re
import string

from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from email_validator import validate_email, EmailNotValidError

from .models import NewOfficerRegistration, OfficerLogin
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt


class officerRegistrationsForms(forms.Form):
    class Meta:
        model = NewOfficerRegistration
        fields = '__all__'
        widgets = {
            'officer_qualification': forms.Select(choices=NewOfficerRegistration.EDUCATION_QUALIFICATION_CHOICES),
            'officer_current_rank': forms.Select(choices=NewOfficerRegistration.OFFICER_RANK_CHOICES)
        }
    first_name = forms.CharField(label="Enter first Name", max_length=100,
                                 error_messages={'required': 'First Name is Required .',
                                                    'invalid': 'Name is Invalid.'})
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError(_("First name cannot be empty."))
        elif not re.match(r'^[a-zA-Z]*$', first_name):
            raise forms.ValidationError(_("Enter a valid first name."))
        return first_name
    
    middle_name = forms.CharField(required=False,max_length=250,)
    def clean_middle_name(self):
        middle_name = self.cleaned_data.get('middle_name')
        if middle_name and not re.match(r'^[a-zA-Z]*$', middle_name):
            raise forms.ValidationError(_("Enter a valid middle name."))
        return middle_name
    
    last_name = forms.CharField(label="Enter last Name", max_length=250,
                                error_messages={'required': 'Last Name is Required .',
                                                    'invalid': 'Name is Invalid.'})
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r'^[a-zA-Z]*$', last_name):
            raise forms.ValidationError(_("Enter a valid last name."))
        return last_name
    
    username = forms.CharField(label='Create a User Name', error_messages={'required': 'Please Create a user name'})
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and not re.match(r'^[a-zA-Z]*$', username):
            raise forms.ValidationError(_("Enter a valid last name."))
        if NewOfficerRegistration.objects.filter(username=username).exists():
            raise forms.ValidationError("User Name Not Available")
        return username
    
    officer_gender = forms.ChoiceField(label='Select Gender',
                                              choices=NewOfficerRegistration.OFFICER_GENDER_CHOICES)
    
    email = forms.EmailField(label='Enter Email', max_length=250,  error_messages={'required': 'Email is Required'})
    def clean_email(self):
        """
        Validate email address and ensure it ends with @gmail.com or @yahoo.com domain.
        """
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email address is required.")
        if NewOfficerRegistration.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        
            # Use email-validator library for more comprehensive validation
        try:
            validate_email(email)
        except EmailNotValidError:
            raise forms.ValidationError("Invalid email address.")
        return email


    phone_contact = forms.CharField(label='Enter Phone Number',max_length=10, error_messages={'required': 'Contact is Required .',
                                                                                                'invalid': 'Name is Invalid.'})
    def clean_phone_contact(self):
        phone_contact = self.cleaned_data.get('phone_contact')
        if not re.match(r'^\+?1?\d{9,15}$', phone_contact):
            raise forms.ValidationError(_("Enter a valid phone number."))
        if NewOfficerRegistration.objects.filter(phone_contact=phone_contact).exists():
            raise forms.ValidationError("Number already used")
        return phone_contact

    officer_address = forms.CharField(max_length=250,
                                      error_messages={'required': 'Address is Required .',
                                                        'invalid': 'Name is Invalid.'})
    def clean_officer_address(self):
        officer_address = self.cleaned_data.get('officer_address')
        if not officer_address:
            raise forms.ValidationError(_("Address cannot be empty."))
            # Additional validation logic if needed
        return officer_address


    officer_current_rank = forms.ChoiceField(label='Select Current Rank',
                                              choices=NewOfficerRegistration.OFFICER_RANK_CHOICES)
    
    officer_operations_region = forms.ChoiceField(label="Operational Region", choices=NewOfficerRegistration.OFFICER_OPERATIONS_REGION)
    officer_Operationsdistrict = forms.ChoiceField(label="Operational District", choices=NewOfficerRegistration.OFFICER_OPERATIONS_DISTRICT)
    officer_current_station = forms.CharField(max_length=250)
    officer_staff_ID = forms.CharField(label='Enter Staff ID', max_length=250)
    def clean_officer_staff_ID(self):
        officer_staff_ID = self.cleaned_data.get('officer_staff_ID')
        if not re.match(r'^[a-zA-Z0-9]*$', officer_staff_ID):
            raise forms.ValidationError(_("Enter a valid staff ID."))
        if NewOfficerRegistration.objects.filter(officer_staff_ID=officer_staff_ID).exists():
            raise forms.ValidationError('Staff ID alraedy exist')
        return officer_staff_ID
    

    officer_qualification = forms.ChoiceField(label='Select Level of Education',
                                              choices=NewOfficerRegistration.EDUCATION_QUALIFICATION_CHOICES)

    officer_date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    officer_operations_department = forms.ChoiceField(label='Department of Operations',
                                              choices=NewOfficerRegistration.OFFICER_DEPARTMENT_CHOICES)

    officer_profile_image = forms.ImageField()
    def clean_officer_image(self):
        officer_image = self.cleaned_data.get('officer_image')
        if not officer_image:
            raise forms.ValidationError('Image is required')
        return officer_image
    

    officer_stationRank = forms.ChoiceField(label='Select Current Station Rank',
                                        choices=NewOfficerRegistration.OFFICER_STATION_RANK_CHOICES)
    def clean_officer_stationRank(self):
        officer_stationRank = self.cleaned_data.get('officer_stationRank')
        if not officer_stationRank:
            raise forms.ValidationError('Station Rank is required')
        return officer_stationRank

    password = forms.CharField(label="Enter Password",max_length=128, widget=forms.PasswordInput)
    def clean_password(self):
        password = self.cleaned_data.get('password')
        criteria = {'special': set(string.punctuation), 'numeric': set(string.digits), 'uppercase': set(string.ascii_uppercase)}
        if len(password) < 8:
            raise forms.ValidationError(_("Password must be at least 8 characters long."))
        if  any(not any(char in char_set for char in password) for char_type, char_set in criteria.items()):
            raise forms.ValidationError('Password is weak, Try Again')
        return password

    confirm_password = forms.CharField(label="Confirm Password", max_length=128, widget=forms.PasswordInput)
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("The passwords do not match."))
        return confirm_password



class officer_loginForms(forms.Form):
    username = forms.CharField(label='Enter User Name')
    password = forms.CharField(label="Enter Password",max_length=128, widget=forms.PasswordInput)