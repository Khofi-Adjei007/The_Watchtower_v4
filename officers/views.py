import os
import json
import logging
from io import BytesIO
from datetime import datetime
from django.middleware.csrf import get_token

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_protect


from .models import NewOfficerRegistration, OfficerLogin,Case
from .forms_and_validations import officerRegistrationsForms, officer_loginForms,CaseStep1Form, CaseStep2Form, CaseStep3Form
from .templatetags.custom_filters import calculate_age



# Redirection Message after succcesful registrations
def redirect_with_delay(request, url, delay_seconds=3):
    return render(request, 'redirect_with_delay.html', {'url': url, 'delay_seconds': delay_seconds})


# New Officers Registration Views
@csrf_protect
def officer_registrations(request):
    if request.method == "POST":
        form = officerRegistrationsForms(request.POST, request.FILES)
        if form.is_valid():
            form_data = form.cleaned_data
            user, created = User.objects.get_or_create(username=form_data['username'], defaults={'email': form_data['email']})

            if created:
                user.set_password(form_data['password'])
                user.save()
            else:
                messages.error(request, 'A user with this username already exists.')
                return render(request, 'officer_registrations.html', {"form": form})

            NewOfficerRegistration.objects.create(
                user=user,
                first_name=form_data['first_name'],
                middle_name=form_data['middle_name'],
                last_name=form_data['last_name'],
                username=form_data['username'],
                officer_gender=form_data['officer_gender'],
                email=form_data['email'],
                phone_contact=form_data['phone_contact'],
                officer_address=form_data['officer_address'],
                officer_staff_ID=form_data['officer_staff_ID'],
                officer_qualification=form_data['officer_qualification'],
                officer_date_of_birth=form_data['officer_date_of_birth'],
                officer_operations_region=form_data['officer_operations_region'],
                officer_current_rank=form_data['officer_current_rank'],
                officer_current_station=form_data['officer_current_station'],
                officer_operations_department=form_data['officer_operations_department'],
                officer_profile_image=form_data['officer_profile_image'],
                officer_stationRank=form_data['officer_stationRank'],
            )

            messages.success(request, 'Registration successful!')
            return redirect(reverse('officer_login'))
    else:
        form = officerRegistrationsForms()

    return render(request, 'officer_registrations.html', {"form": form})



# officer login views
@csrf_protect
def officer_login(request):
    error_message = ''
    if request.method == 'POST':
        form = officer_loginForms(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Optionally store user-related data in session
                if hasattr(user, 'newofficerregistration'):
                    request.session['officer_staff_ID'] = user.newofficerregistration.officer_staff_ID
                    request.session['officer_current_rank'] = user.newofficerregistration.officer_current_rank
                return redirect('selectPurpose')
            else:
                error_message = 'Invalid username or password'
        else:
            error_message = 'Invalid form data'
    else:
        form = officer_loginForms()
    return render(request, 'officer_login.html', {'form': form, 'error_message': error_message})

# Home Selector
@login_required(login_url='officer_login')
@csrf_exempt
def selectPurpose(request):
    return render(request, 'selectPurpose.html')

# Route to Search Database
@login_required(login_url='officer_login')
def searchdatabase(request):
    return render(request, 'searchdatabase.html')


# Route to get cases and thier progress
@login_required(login_url='officer_login')
def casesProgress(request):
    return render(request, 'casesProgress.html')

# Route to command messaging
@login_required(login_url='officer_login')
def commandmessaging(request):
    return render(request, 'commandmessaging.html')



# officer logout views
def officer_logout(request):
    logout(request)
    request.session.flush()
    return redirect(reverse('officer_login'))


@login_required(login_url='officer_login')
def officer_profile(request):
    user = request.user  # Get the currently logged-in user
    officer_profile = user.newofficerregistration
    return render(request, 'officer_profile.html', {'officer_profile': officer_profile})



@login_required(login_url='officer_login')
@csrf_protect
def docketforms(request):
    # Determine the current step
    current_step = request.session.get('current_step', 1)
    
    if request.method == 'POST':
        if current_step == 1:
            form = CaseStep1Form(request.POST)
            if form.is_valid():
                request.session['form_step1_data'] = form.cleaned_data
                request.session['current_step'] = 2
                return redirect('docketforms')
        elif current_step == 2:
            form = CaseStep2Form(request.POST)
            if form.is_valid():
                request.session['form_step2_data'] = form.cleaned_data
                request.session['current_step'] = 3
                return redirect('docketforms')
        elif current_step == 3:
            form = CaseStep3Form(request.POST)
            if form.is_valid():
                request.session['form_step3_data'] = form.cleaned_data
                # Process all data here
                form_data = {
                    **request.session.get('form_step1_data', {}),
                    **request.session.get('form_step2_data', {}),
                    **request.session.get('form_step3_data', {}),
                }
                # Clear session data after processing
                request.session.flush()
                # Redirect to a success page or render a success template
                return render(request, 'success.html', {'form_data': form_data})
    else:
        # Initialize the appropriate form based on current step
        if current_step == 1:
            form = CaseStep1Form()
        elif current_step == 2:
            form = CaseStep2Form()
        elif current_step == 3:
            form = CaseStep3Form()
        else:
            # Reset to step 1 if current_step is invalid
            request.session['current_step'] = 1
            form = CaseStep1Form()

    context = {
        'form': form,
        'current_step': current_step,
    }
    return render(request, 'docketforms.html', context)


@login_required(login_url='officer_login')
@csrf_exempt
@require_POST
def verify_badge(request):
    if request.user.is_authenticated:
        badge_number = request.POST.get('officer_staff_ID')
        # Compare the badge number with the logged-in user's badge number
        if request.user.newofficerregistration.officer_staff_ID == badge_number:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid badge number'})
    else:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'})

    


@login_required(login_url='officer_login')
def CaseStep1View(request):
    if request.method == 'POST':
        form_step1 = CaseStep1Form(request.POST)
        if form_step1.is_valid():
            # Extract cleaned data
            cleaned_data = form_step1.cleaned_data

            # Store form data in session, ensuring JSON serialization
            # request.session['case_ID'] = cleaned_data.get('case_ID')
            request.session['Case_Title'] = cleaned_data.get('case_title')
            
            # Convert datetime to string before storing in session
            date_time_of_incident = cleaned_data.get('date_time_of_incident')
            if date_time_of_incident:
                request.session['date_time_of_incident'] = date_time_of_incident.isoformat()

            date_time_of_report = cleaned_data.get('date_time_of_report')
            if date_time_of_report:
                request.session['date_time_of_report'] = date_time_of_report.isoformat()

            # Complainant Information
            request.session['complainant_name'] = cleaned_data.get('complainant_name')
            request.session['complainant_contact'] = cleaned_data.get('complainant_contact')
            request.session['complainant_physical_address'] = cleaned_data.get('complainant_physical_address')
            request.session['complainant_digital_address'] = cleaned_data.get('complainant_digital_address')
            request.session['complainant_occupation'] = cleaned_data.get('complainant_occupation')
            
            complainant_date_of_birth = cleaned_data.get('complainant_date_of_birth')
            if complainant_date_of_birth:
                request.session['complainant_date_of_birth'] = complainant_date_of_birth.isoformat()

            # Suspect Information
            request.session['suspect_name'] = cleaned_data.get('suspect_name')
            request.session['suspect_contact'] = cleaned_data.get('suspect_contact')
            request.session['suspect_physical_address'] = cleaned_data.get('suspect_physical_address')
            request.session['suspect_digital_address'] = cleaned_data.get('suspect_digital_address')
            request.session['suspect_occupation'] = cleaned_data.get('suspect_occupation')

            suspect_date_of_birth = cleaned_data.get('suspect_date_of_birth')
            if suspect_date_of_birth:
                request.session['suspect_date_of_birth'] = suspect_date_of_birth.isoformat()

            # Victim Information
            is_victim_same_as_complainant = cleaned_data.get('is_victim_same_as_complainant')
            if is_victim_same_as_complainant:
                # Copy complainant data to victim
                request.session['victim_name'] = cleaned_data.get('complainant_name')
                request.session['victim_contact'] = cleaned_data.get('complainant_contact')
                request.session['victim_physical_address'] = cleaned_data.get('complainant_physical_address')
                request.session['victim_digital_address'] = cleaned_data.get('complainant_digital_address')
                request.session['victim_occupation'] = cleaned_data.get('complainant_occupation')
                
                complainant_date_of_birth = cleaned_data.get('complainant_date_of_birth')
                if complainant_date_of_birth:
                    request.session['victim_date_of_birth'] = complainant_date_of_birth.isoformat()
            else:
                # Store victim information
                request.session['victim_name'] = cleaned_data.get('victim_name')
                request.session['victim_contact'] = cleaned_data.get('victim_contact')
                request.session['victim_physical_address'] = cleaned_data.get('victim_physical_address')
                request.session['victim_digital_address'] = cleaned_data.get('victim_digital_address')
                request.session['victim_occupation'] = cleaned_data.get('victim_occupation')
                
                victim_date_of_birth = cleaned_data.get('victim_date_of_birth')
                if victim_date_of_birth:
                    request.session['victim_date_of_birth'] = victim_date_of_birth.isoformat()

            # Incident Details
            request.session['location_of_incident'] = cleaned_data.get('location_of_incident')
            request.session['type_of_incident'] = cleaned_data.get('type_of_incident')
            request.session['statement_of_incident'] = cleaned_data.get('statement_of_incident')

            # Key Witness Information
            request.session['key_witness_name'] = cleaned_data.get('key_witness_name')
            request.session['key_witness_contact'] = cleaned_data.get('key_witness_contact')
            request.session['key_witness_physical_address'] = cleaned_data.get('key_witness_physical_address')
            request.session['key_witness_digital_address'] = cleaned_data.get('key_witness_digital_address')
            print("Form Step 1 Data Stored in Session:", cleaned_data)

            # Proceed to the next step
            return redirect('CaseStep2View')
        else:
            # Print the form errors for debugging
            print("Form is not valid. Errors:", form_step1.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form_step1 = CaseStep1Form()

    # Define field groups
    complainant_fields = ['complainant_name', 'complainant_contact', 'complainant_physical_address', 'complainant_digital_address', 'complainant_occupation', 'complainant_date_of_birth']
    suspect_fields = ['suspect_name', 'suspect_contact', 'suspect_physical_address', 'suspect_digital_address', 'suspect_occupation', 'suspect_date_of_birth']
    victim_fields = ['victim_name', 'victim_contact', 'victim_physical_address', 'victim_digital_address', 'victim_occupation', 'victim_date_of_birth']
    incident_details_fields = ['location_of_incident', 'type_of_incident', 'statement_of_incident']
    key_witness_fields = ['key_witness_name', 'key_witness_contact', 'key_witness_physical_address', 'key_witness_digital_address']

    context = {
        'form_step1': form_step1,
        'complainant_fields': complainant_fields,
        'suspect_fields': suspect_fields,
        'victim_fields': victim_fields,
        'incident_details_fields': incident_details_fields,
        'key_witness_fields': key_witness_fields,
    }
    return render(request, 'docketforms.html', context)




# @login_required(login_url='officer_login')
def CaseStep2View(request):
    # Retrieve session data for form initialization
    complainant_statement = request.session.get('complainant_statement', '')
    suspect_statement = request.session.get('suspect_statement', '')
    witness_statement = request.session.get('witness_statement', '')
    additional_witnesses = request.session.get('additional_witnesses', '')

    if request.method == 'POST':
        # Create form instance with POST data
        form_step2 = CaseStep2Form(request.POST)
        
        if form_step2.is_valid():
            # Process the valid form data
            cleaned_data = form_step2.cleaned_data

            # Store data in session or process it as needed
            request.session['complainant_statement'] = cleaned_data.get('complainant_statement')
            request.session['suspect_statement'] = cleaned_data.get('suspect_statement')
            request.session['witness_statement'] = cleaned_data.get('witness_statement')
            request.session['additional_witnesses'] = cleaned_data.get('additional_witnesses')

            # For demonstration, you might want to print or log the cleaned data
            print("Form Step 2 Data Stored in Session:", cleaned_data)

            # Proceed to the next step
            return redirect('CaseStep3View')  # Adjust this to your next step URL or view
        else:
            # Print the form errors for debugging
            print("Form errors:", form_step2.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        # Initialize form with prepopulated data from the session
        form_step2 = CaseStep2Form(initial={
            'complainant_statement': complainant_statement,
            'suspect_statement': suspect_statement,
            'witness_statement': witness_statement,
            'additional_witnesses': additional_witnesses,
        })

    # Prepare context for rendering the template
    context = {
        'form_step2': form_step2,
    }
    print("Context for Step 2:", context)
    return render(request, 'docketforms.html', context)






# @login_required(login_url='officer_login')
def CaseStep3View(request):
    if request.method == 'POST':
        form = CaseStep3Form(request.POST, request.FILES or None) 
        if form.is_valid():
            # Retrieve data from the session
            case_data = {
                'Case_Title': request.session.get('case_title'),
                'date_time_of_incident': request.session.get('date_time_of_incident'),
                'date_time_of_report': request.session.get('date_time_of_report'),

                # Complainant Information
                'complainant_name': request.session.get('complainant_name'),
                'complainant_contact': request.session.get('complainant_contact'),
                'complainant_physical_address': request.session.get('complainant_physical_address'),
                'complainant_digital_address': request.session.get('complainant_digital_address'),
                'complainant_occupation': request.session.get('complainant_occupation'),
                'complainant_date_of_birth': request.session.get('complainant_date_of_birth'),

                # Suspect Information
                'suspect_name': request.session.get('suspect_name'),
                'suspect_contact': request.session.get('suspect_contact'),
                'suspect_physical_address': request.session.get('suspect_physical_address'),
                'suspect_digital_address': request.session.get('suspect_digital_address'),
                'suspect_occupation': request.session.get('suspect_occupation'),
                'suspect_date_of_birth': request.session.get('suspect_date_of_birth'),

                # Victim Information
                'is_victim_same_as_complainant': request.session.get('is_victim_same_as_complainant'),
                'victim_name': request.session.get('victim_name'),
                'victim_contact': request.session.get('victim_contact'),
                'victim_physical_address': request.session.get('victim_physical_address'),
                'victim_digital_address': request.session.get('victim_digital_address'),
                'victim_occupation': request.session.get('victim_occupation'),
                'victim_date_of_birth': request.session.get('victim_date_of_birth'),

                # Incident Details
                'location_of_incident': request.session.get('location_of_incident'),
                'type_of_incident': request.session.get('type_of_incident'),
                'statement_of_incident': request.session.get('statement_of_incident'),

                # Key Witness Information
                'key_witness_name': request.session.get('key_witness_name'),
                'key_witness_contact': request.session.get('key_witness_contact'),
                'key_witness_physical_address': request.session.get('key_witness_physical_address'),
                'key_witness_digital_address': request.session.get('key_witness_digital_address'),

                # Final step data from the current form submission
                'reporting_officer_name': form.cleaned_data.get('reporting_officer_name'),
                'reporting_officer_badge_id': form.cleaned_data.get('reporting_officer_badge_id'),
                'reporting_officer_rank': form.cleaned_data.get('reporting_officer_rank'),
                'reporting_officer_station': form.cleaned_data.get('reporting_officer_station'),
                'reporting_officer_division': form.cleaned_data.get('reporting_officer_division'),
                'charges_filed': form.cleaned_data.get('charges_filed'),
                'legal_actions_taken': form.cleaned_data.get('legal_actions_taken'),
                'assigned_investigator': form.cleaned_data.get('assigned_investigator'),
                'case_status': form.cleaned_data.get('case_status'),
                'follow_up_required': form.cleaned_data.get('follow_up_required'),
                'additional_notes': form.cleaned_data.get('additional_notes'),
            }

            # Handle file uploads separately and add to case_data
            mugshot = form.cleaned_data.get('mugshot')
            fingerprint = form.cleaned_data.get('fingerprint')

            # Create the Docket instance with all the collected data
            docket = docketforms.objects.create(**case_data)

            # Save the files if they exist
            if mugshot:
                docket.mugshot = mugshot
            if fingerprint:
                docket.fingerprint = fingerprint
            docket.save()

            # Clear the session after saving
            request.session.flush()

            messages.success(request, "Docket successfully registered.")
            return redirect('success_page')  # Replace with the name of your success URL
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CaseStep3Form()  # Instantiate an empty form for GET requests
    return render(request, 'docketforms.html', {'form': form})