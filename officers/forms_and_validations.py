import re
import string
import uuid
from datetime import datetime
from django.utils import timezone
from datetime import datetime
import pytz


from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from email_validator import validate_email, EmailNotValidError

from .models import NewOfficerRegistration, OfficerLogin, Case
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



#Start of 3-Stepper Forms Validation logics
class CaseStep1Form(forms.Form):

    Case_Title = forms.CharField(
        required=False,
        max_length=250,
        label="Case Title/Description",
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Enter case title'
        })
    )


    def clean_case_title(self):
        case_title = self.cleaned_data.get('case_title')
        if case_title and not re.match(r'^[a-zA-Z\s]*$', case_title):
            raise forms.ValidationError("Enter a valid case title.")
        return case_title

    date_time_of_incident = forms.DateTimeField(
        label="Date & Time Of Incident",
        error_messages={'required': 'Indicate Time and Date'},
        widget=forms.DateTimeInput(attrs={
            'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'YYYY-MM-DD HH:MM:SS',
            'type': 'datetime-local'
        }),
    )

    def clean_date_time_of_incident(self):
        date_time_of_incident = self.cleaned_data.get('date_time_of_incident')
        # Custom validation logic, e.g., ensuring the date is not in the future
        return date_time_of_incident

    date_time_of_report = forms.DateTimeField(
        label="Date & Time of Report",
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'YYYY-MM-DD HH:MM'
        }),
        error_messages={'required': 'Indicate Time and Date'}
    )

    def clean_date_time_of_report(self):
        date_time_of_report = self.cleaned_data.get('date_time_of_report')
    
        if not date_time_of_report:
            raise ValidationError("Date & Time of Report is required.")
        
        # Get the current time as timezone-aware
        now = timezone.now()
        
        # Make date_time_of_report timezone-aware if it's naive
        if timezone.is_naive(date_time_of_report):
            local_timezone = timezone.get_current_timezone()
            date_time_of_report = local_timezone.localize(date_time_of_report)
        
        # Compare report time with the current time
        if date_time_of_report > now:
            raise ValidationError("The report date cannot be in the future.")
        
        return date_time_of_report
    
    complainant_name = forms.CharField(
        label="Enter Complainant Name",
        max_length=100,
        error_messages={
            'required': 'Complainant name is required',
            'invalid': 'Name is invalid'
        },
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': "complainant's name"
        })
    )

    def clean_complainant_name(self):
        complainant_name = self.cleaned_data.get('complainant_name')
        if not complainant_name:
            raise forms.ValidationError("Complainant name cannot be empty.")
        elif not re.match(r'^[a-zA-Z\s]*$', complainant_name):
            raise forms.ValidationError("Enter a valid complainant name.")
        return complainant_name

    complainant_contact = forms.CharField(
        label="Complainant Contact",
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'e.g., +1234567890'
        }),
        error_messages={
            'required': 'Phone number is required.',
            'max_length': 'Phone number is too long.'
        }
    )

    def clean_complainant_contact(self):
        complainant_contact = self.cleaned_data.get('complainant_contact')
        phone_pattern = re.compile(r'^\+?\d{7,15}$')
        if not phone_pattern.match(complainant_contact):
            raise ValidationError("Enter a valid phone number with 7 to 15 digits.")
        return complainant_contact

    

    complainant_physical_address = forms.CharField(
    label="Complainant Physical Address",
    max_length=100,
    error_messages={
        'required': 'Complainant physical address is required.',
        'invalid': 'Address is invalid.'
    },
    widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
        'placeholder': 'Complainant\'s physical address'
    })
)

    def clean_complainant_physical_address(self):
        complainant_physical_address = self.cleaned_data.get('complainant_physical_address')
        if not complainant_physical_address:
            raise forms.ValidationError("Complainant physical address cannot be empty.")
        elif not re.match(r'^[\w\s.,-]*$', complainant_physical_address):  # Allows letters, numbers, spaces, and common address characters
            raise forms.ValidationError("Enter a valid address.")
        return complainant_physical_address


    complainant_digital_address = forms.CharField(
        label="Complainant Digital Address",
        max_length=100,
        error_messages={
            'required': 'Complainant digital address is required.',
            'invalid': 'Digital address is invalid.'
        },
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Complainant\'s digital address (e.g., email or social media handle)'
        })
    )

    def clean_complainant_digital_address(self):
        complainant_digital_address = self.cleaned_data.get('complainant_digital_address')
        if not complainant_digital_address:
            raise forms.ValidationError("Complainant digital address cannot be empty.")
        elif not re.match(r'^[\w@.-]+$', complainant_digital_address):  # Simplified for digital addresses
            raise forms.ValidationError("Enter a valid digital address (e.g., email or social media handle).")
        return complainant_digital_address


    complainant_occupation = forms.CharField(
        label="Complainant Occupation",
        max_length=100,
        error_messages={
            'required': 'Complainant occupation is required.',
            'invalid': 'Occupation is invalid.'
        },
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Complainant\'s occupation'
        })
    )

    def clean_complainant_occupation(self):
        complainant_occupation = self.cleaned_data.get('complainant_occupation')
        if not complainant_occupation:
            raise forms.ValidationError("Complainant occupation cannot be empty.")
        elif not re.match(r'^[\w\s-]*$', complainant_occupation):  # Allow letters, numbers, and common characters for occupations
            raise forms.ValidationError("Enter a valid occupation.")
        return complainant_occupation


    complainant_date_of_birth = forms.DateField(
        label="Complainant Date of Birth",
        required=True,
        error_messages={
            'required': 'Date of birth is required.'
        },
        widget=forms.DateInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date',  # Sets the input type to date
                'placeholder': 'YYYY-MM-DD'  # Placeholder for the input
            }
        )
    )

    def clean_complainant_date_of_birth(self):
        complainant_date_of_birth = self.cleaned_data.get('complainant_date_of_birth')
        if not complainant_date_of_birth:
            raise forms.ValidationError("Date of birth cannot be empty.")
        return complainant_date_of_birth


    suspect_name = forms.CharField(
        label="Suspect Name",
        max_length=100,
        error_messages={
            'required': 'Suspect name is required.',
            'invalid': 'Suspect name is invalid.'
        },
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Suspect\'s name'
            }
        )
    )

    def clean_suspect_name(self):
        suspect_name = self.cleaned_data.get('suspect_name')
        if not suspect_name:
            raise forms.ValidationError("Suspect name cannot be empty.")
        elif not re.match(r'^[a-zA-Z ]*$', suspect_name):  # Allow spaces in names
            raise forms.ValidationError("Enter a valid name (letters and spaces only).")
        return suspect_name


  
    suspect_contact = forms.CharField(
        label="Suspect Contact",
        max_length=15,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g., +1234567890'
            }
        ),
        error_messages={
            'required': 'Phone number is required.',
            'invalid': 'Phone number is invalid.'
        }
    )

    def clean_suspect_contact(self):
        suspect_contact = self.cleaned_data.get('suspect_contact')
        phone_pattern = re.compile(r'^\+?\d{7,15}$')
        if not phone_pattern.match(suspect_contact):
            raise forms.ValidationError("Enter a valid phone number with 7 to 15 digits.")
        return suspect_contact

    suspect_physical_address = forms.CharField(
        label="Suspect Physical Address",
        max_length=250,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'suspect\'s physical address'
            }
        ),
        error_messages={
            'required': 'Physical address is required.',
            'invalid': 'Physical address is invalid.'
        }
    )

    def clean_suspect_physical_address(self):
        suspect_physical_address = self.cleaned_data.get('suspect_physical_address')
        if not suspect_physical_address:
            raise forms.ValidationError("Physical address cannot be empty.")
        return suspect_physical_address

    suspect_digital_address = forms.CharField(
        label="Suspect Digital Address",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'suspect\'s digital address'
            }),
        error_messages={
            'required': 'Digital address is required.',
            'invalid': 'Digital address is invalid.'
        }
    )

    def clean_suspect_digital_address(self):
        suspect_digital_address = self.cleaned_data.get('suspect_digital_address')
        if not suspect_digital_address:
            raise forms.ValidationError("Digital address cannot be empty.")
        return suspect_digital_address

    suspect_occupation = forms.CharField(
        label="Suspect Occupation",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'suspect\'s occupation'
            }
        ),
        error_messages={
            'required': 'Occupation is required.',
            'invalid': 'Occupation is invalid.'
        }
    )

    def clean_suspect_occupation(self):
        suspect_occupation = self.cleaned_data.get('suspect_occupation')
        if not suspect_occupation:
            raise forms.ValidationError("Occupation cannot be empty.")
        elif not re.match(r'^[a-zA-Z ]*$', suspect_occupation):  # Allow spaces in occupations
            raise forms.ValidationError("Enter a valid occupation (letters and spaces only).")
        return suspect_occupation

    suspect_date_of_birth = forms.DateField(
        label="Suspect Date of Birth",
        required=True,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'YYYY-MM-DD'
            }
        ),
        error_messages={
            'required': 'Date of birth is required.'
        }
    )

    def clean_suspect_date_of_birth(self):
        suspect_date_of_birth = self.cleaned_data.get('suspect_date_of_birth')
        if not suspect_date_of_birth:
            raise forms.ValidationError("Date of birth cannot be empty.")
        return suspect_date_of_birth

    is_victim_same_as_complainant = forms.BooleanField(
        label="Is Victim Same as Complainant?",
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        is_victim_same_as_complainant = cleaned_data.get('is_victim_same_as_complainant')

        if is_victim_same_as_complainant:
            # Copy complainant data to victim fields
            cleaned_data['victim_name'] = cleaned_data.get('complainant_name')
            cleaned_data['victim_address'] = cleaned_data.get('complainant_address')
        return cleaned_data

    victim_name = forms.CharField(
        label="Victim Name",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'victim\'s name'
            }
        ),
        error_messages={
            'required': 'Victim name is required.'
        }
    )

    def clean_victim_name(self):
        victim_name = self.cleaned_data.get('victim_name')
        if not victim_name:
            raise forms.ValidationError("Victim name cannot be empty.")
        elif not re.match(r'^[a-zA-Z ]*$', victim_name):  # Allow spaces in names
            raise forms.ValidationError("Enter a valid name (letters and spaces only).")
        return victim_name

    victim_contact = forms.CharField(
        label="Victim Contact",
        max_length=15,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g., +1234567890'
            }
        ),
        error_messages={
            'required': 'Phone number is required.'
        }
    )

    def clean_victim_contact(self):
        victim_contact = self.cleaned_data.get('victim_contact')
        phone_pattern = re.compile(r'^\+?\d{7,15}$')
        if not phone_pattern.match(victim_contact):
            raise forms.ValidationError("Enter a valid phone number with 7 to 15 digits.")
        return victim_contact

    victim_physical_address = forms.CharField(
        label="Victim Physical Address",
        max_length=250,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter physical address'
            }
        ),
        error_messages={
            'required': 'Physical address is required.'
        }
    )

    def clean_victim_physical_address(self):
        victim_physical_address = self.cleaned_data.get('victim_physical_address')
        if not victim_physical_address:
            raise forms.ValidationError("Physical address cannot be empty.")
        return victim_physical_address

    victim_digital_address = forms.CharField(
        label="Victim Digital Address",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'digital address'
            }),
        error_messages={'required': 'Digital address is required.'}
    )

    def clean_victim_digital_address(self):
        victim_digital_address = self.cleaned_data.get('victim_digital_address')
        if not victim_digital_address:
            raise forms.ValidationError("Digital address cannot be empty.")
        return victim_digital_address


    
    victim_occupation = forms.CharField(
        label="Victim Occupation",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'victim occupation'
            }
        ),
        error_messages={
            'required': 'Occupation is required.'
        }
    )

    def clean_victim_occupation(self):
        victim_occupation = self.cleaned_data.get('victim_occupation')
        print(f"Validating victim occupation: '{victim_occupation}'")  # Debugging line
        if not victim_occupation:
            raise forms.ValidationError("Occupation cannot be empty.")
        elif not re.match(r'^[a-zA-Z ]*$', victim_occupation):  # Allow spaces in occupations
            raise forms.ValidationError("Enter a valid occupation (letters and spaces only).")
        return victim_occupation


    victim_date_of_birth = forms.DateField(
        label="Victim Date of Birth",
        required=True,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'YYYY-MM-DD'
            }
        ),
        error_messages={
            'required': 'Date of birth is required.'
        }
    )

    def clean_victim_date_of_birth(self):
        victim_date_of_birth = self.cleaned_data.get('victim_date_of_birth')
        if not victim_date_of_birth:
            raise forms.ValidationError("Date of birth cannot be empty.")
        return victim_date_of_birth

    location_of_incident = forms.CharField(
        label="Location of Incident",
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter the location of the incident'
            }
        ),
        error_messages={
            'required': 'Location of the incident is required.'
        }
    )

    def clean_location_of_incident(self):
        location_of_incident = self.cleaned_data.get('location_of_incident')
        if not location_of_incident:
            raise forms.ValidationError("Location of the incident cannot be empty.")
        return location_of_incident

    TYPE_OF_INCIDENT_CHOICES = [
        ('Theft', 'Theft'),
        ('Assault', 'Assault'),
        ('Traffic Accident', 'Traffic Accident'),
        ('Other', 'Other')
    ]

    type_of_incident = forms.ChoiceField(
        label="Type of Incident",
        choices=TYPE_OF_INCIDENT_CHOICES,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500'
            }
        ),
        error_messages={
            'required': 'Type of incident is required.'
        }
    )

    def clean_type_of_incident(self):
        type_of_incident = self.cleaned_data.get('type_of_incident')
        if not type_of_incident:
            raise forms.ValidationError("Type of incident cannot be empty.")
        if type_of_incident not in dict(self.TYPE_OF_INCIDENT_CHOICES).keys():
            raise forms.ValidationError("Invalid type of incident selected.")
        return type_of_incident

    statement_of_incident = forms.CharField(
        label="Statement of Incident",
        widget=forms.Textarea(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Describe the incident in detail',
                'rows': 5
            }
        ),
        required=True,
        error_messages={
            'required': 'Statement of the incident is required.'
        }
    )

    def clean_statement_of_incident(self):
        statement_of_incident = self.cleaned_data.get('statement_of_incident')
        if not statement_of_incident:
            raise forms.ValidationError("Statement of the incident cannot be empty.")
        return statement_of_incident

    key_witness_name = forms.CharField(
        label="Key Witness Name",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter key witness name'
            }
        ),
        error_messages={
            'invalid': 'Enter a valid witness name.'
        }
    )

    def clean_key_witness_name(self):
        key_witness_name = self.cleaned_data.get('key_witness_name')
        if key_witness_name and not re.match(r'^[a-zA-Z\s]*$', key_witness_name):
            raise forms.ValidationError("Key witness name should only contain letters and spaces.")
        return key_witness_name

    key_witness_contact = forms.CharField(
        label="Key Witness Contact",
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'e.g., +1234567890'
            }
        ),
        error_messages={
            'invalid': 'Enter a valid contact number.'
        })

    def clean_key_witness_contact(self):
        key_witness_contact = self.cleaned_data.get('key_witness_contact')
        if key_witness_contact:
            phone_pattern = re.compile(r'^\+?\d{7,15}$')
            if not phone_pattern.match(key_witness_contact):
                raise forms.ValidationError("Enter a valid phone number with 7 to 15 digits.")
        return key_witness_contact

    key_witness_physical_address = forms.CharField(
        label="Key Witness Physical Address",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter the physical address'
            }
        ),
        error_messages={
            'invalid': 'Enter a valid physical address.'
        })

    def clean_key_witness_physical_address(self):
        key_witness_physical_address = self.cleaned_data.get('key_witness_physical_address')
        if key_witness_physical_address and not re.match(r'^[a-zA-Z0-9\s,]*$', key_witness_physical_address):
            raise forms.ValidationError("Physical address should only contain letters, numbers, spaces, and commas.")
        return key_witness_physical_address

    key_witness_digital_address = forms.CharField(
        label="Key Witness Digital Address",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter the digital address'
            }),
        error_messages={
            'invalid': 'Enter a valid digital address.'
        })

    def clean_key_witness_digital_address(self):
        key_witness_digital_address = self.cleaned_data.get('key_witness_digital_address')
        if key_witness_digital_address and not re.match(r'^[a-zA-Z0-9\s,]*$', key_witness_digital_address):
            raise forms.ValidationError("Digital address should only contain letters, numbers, spaces, and commas.")
        return key_witness_digital_address
    



class CaseStep2Form(forms.Form):
    complainant_statement = forms.CharField(
        label="Complainant Statement",
        widget=forms.Textarea(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Describe the incident in detail',
                'rows': 5
            }),
        required=True,
        error_messages={'required': 'Complainant statement is required.'})

    def clean_complainant_statement(self):
        complainant_statement = self.cleaned_data.get('complainant_statement')
        if not complainant_statement.strip():
            raise forms.ValidationError("Complainant statement cannot be empty.")
        return complainant_statement

    suspect_statement = forms.CharField(
        label="Suspect Statement",
        widget=forms.Textarea(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Describe the incident in detail',
                'rows': 5
            }),
        required=True,
        error_messages={'required': 'Suspect statement is required.'}
    )

    def clean_suspect_statement(self):
        suspect_statement = self.cleaned_data.get('suspect_statement')
        if not suspect_statement.strip():
            raise forms.ValidationError("Suspect statement cannot be empty.")
        return suspect_statement

    witness_statement = forms.CharField(
        label="Witness Statement",
        widget=forms.Textarea(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Describe the incident in detail',
                'rows': 5
            }
        ),
        required=True,
        error_messages={'required': 'Witness statement is required.'}
    )

    def clean_witness_statement(self):
        witness_statement = self.cleaned_data.get('witness_statement')
        if not witness_statement.strip():
            raise forms.ValidationError("Witness statement cannot be empty.")
        return witness_statement

    additional_witnesses = forms.CharField(
        label="Additional Witnesses",
        widget=forms.Textarea(
            attrs={
                'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Describe the incident in detail',
                'rows': 5
            }
        ),
        required=False
    )

    def clean_additional_witnesses(self):
        additional_witnesses = self.cleaned_data.get('additional_witnesses')
        # Example of additional validation: limit length of additional witnesses text
        if additional_witnesses and len(additional_witnesses) > 1000:
            raise forms.ValidationError("Additional witnesses information is too long.")
        return additional_witnesses



# Step 3 Form: Reporting Officer and Case Progression
class CaseStep3Form(forms.Form):
    reporting_officer_name = forms.CharField(
        label="Reporting Officer Name", max_length=250, required=True,
        error_messages={'required': 'Reporting officer name is required.'}
    )
    def clean_reporting_officer_name(self):
        reporting_officer_name = self.cleaned_data.get('reporting_officer_name')
        if not reporting_officer_name:
            raise forms.ValidationError("Reporting officer name cannot be empty.")
        return reporting_officer_name

    reporting_officer_badge_id = forms.CharField(
        label="Badge ID", max_length=50, required=True,
        error_messages={'required': 'Badge ID is required.'}
    )
    def clean_reporting_officer_badge_id(self):
        reporting_officer_badge_id = self.cleaned_data.get('reporting_officer_badge_id')
        if not reporting_officer_badge_id:
            raise forms.ValidationError("Badge ID cannot be empty.")
        return reporting_officer_badge_id

    reporting_officer_rank = forms.CharField(
        label="Rank", max_length=100, required=True,
        error_messages={'required': 'Rank is required.'}
    )
    def clean_reporting_officer_rank(self):
        reporting_officer_rank = self.cleaned_data.get('reporting_officer_rank')
        if not reporting_officer_rank:
            raise forms.ValidationError("Rank cannot be empty.")
        return reporting_officer_rank

    reporting_officer_station = forms.CharField(
        label="Station", max_length=250, required=True,
        error_messages={'required': 'Station is required.'}
    )
    def clean_reporting_officer_station(self):
        reporting_officer_station = self.cleaned_data.get('reporting_officer_station')
        if not reporting_officer_station:
            raise forms.ValidationError("Station cannot be empty.")
        return reporting_officer_station

    reporting_officer_division = forms.CharField(
        label="Division", max_length=250, required=True,
        error_messages={'required': 'Division is required.'}
    )
    def clean_reporting_officer_division(self):
        reporting_officer_division = self.cleaned_data.get('reporting_officer_division')
        if not reporting_officer_division:
            raise forms.ValidationError("Division cannot be empty.")
        return reporting_officer_division

    charges_filed = forms.CharField(
        label="Charges Filed",
        widget=forms.Textarea(),  # Add parentheses to create an instance of the widget
        required=True,
        error_messages={'required': 'Charges filed are required.'}
    )
    def clean_charges_filed(self):
        charges_filed = self.cleaned_data.get('charges_filed')
        if not charges_filed:
            raise forms.ValidationError("Charges filed cannot be empty.")
        return charges_filed

    legal_actions_taken = forms.CharField(
        label="Legal Actions Taken",
        widget=forms.Textarea(),  # Add parentheses here as well
        required=True,
        error_messages={'required': 'Legal actions taken are required.'}
    )
    def clean_legal_actions_taken(self):
        legal_actions_taken = self.cleaned_data.get('legal_actions_taken')
        if not legal_actions_taken:
            raise forms.ValidationError("Legal actions taken cannot be empty.")
        return legal_actions_taken

    assigned_investigator = forms.CharField(
        label="Assigned Investigator", max_length=250, required=True,
        error_messages={'required': 'Assigned investigator is required.'}
    )
    def clean_assigned_investigator(self):
        assigned_investigator = self.cleaned_data.get('assigned_investigator')
        if not assigned_investigator:
            raise forms.ValidationError("Assigned investigator cannot be empty.")
        return assigned_investigator

    case_status = forms.CharField(
        label="Case Status", max_length=100, required=True,
        error_messages={'required': 'Case status is required.'}
    )
    def clean_case_status(self):
        case_status = self.cleaned_data.get('case_status')
        if not case_status:
            raise forms.ValidationError("Case status cannot be empty.")
        return case_status

    follow_up_required = forms.BooleanField(
        label="Follow-Up Required", required=False
    )

    additional_notes = forms.CharField(
        label="Additional Notes",
        widget=forms.Textarea(),  # Add parentheses here as well
        required=False
    )

    mugshot = forms.ImageField(
        label="Mugshot", required=True,
        error_messages={'required': 'Mugshot is required.'}
    )
    def clean_mugshot(self):
        mugshot = self.cleaned_data.get('mugshot')
        if mugshot and not mugshot.content_type.startswith('image/'):
            raise forms.ValidationError("Mugshot must be an image file.")
        return mugshot

    fingerprint = forms.FileField(
        label="Fingerprint", required=True,
        error_messages={'required': 'Fingerprint is required.'}
    )
    def clean_fingerprint(self):
        fingerprint = self.cleaned_data.get('fingerprint')
        if fingerprint and fingerprint.content_type not in ['image/png', 'image/jpeg']:
            raise forms.ValidationError("Fingerprint must be a PNG or JPEG file.")
        return fingerprint
