import os
import json
import random
import string
import logging
from io import BytesIO
import logging
import logging
from xhtml2pdf import pisa
logger = logging.getLogger(__name__)
from django.contrib.auth.decorators import login_required
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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
from .models import Case
from .pdf_generator import generate_pdf




# Redirection Message after succcesful registrations
def redirect_with_delay(request, url, delay_seconds=3):
    return render(request, 'redirect_with_delay.html', {'url': url, 'delay_seconds': delay_seconds})

def generate_case_id(station, region):
    # Generate a random string of 6 characters
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Generate Station Code
    station_code = ''.join(word[0].upper() for word in station.split())
    
    # Get Region Code (using the first two characters of the region choice)
    region_code = region[:2].upper()
    
    # Timestamp (to add an extra layer of uniqueness)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Combine all parts to create the Case ID
    case_id = f"{random_string}/{station_code}/{region_code}/{timestamp}"
    
    return case_id


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

    

def generate_case_pdf(case_data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle("Case Docket")

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Case Docket: {case_data.get('Initial_Case_Title', '')}")

    # Complainant Details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 720, "Complainant Details:")
    p.setFont("Helvetica", 12)
    p.drawString(120, 700, f"Name: {case_data.get('complainant_name', '')}")
    p.drawString(120, 680, f"Contact: {case_data.get('complainant_contact', '')}")
    p.drawString(120, 660, f"Address: {case_data.get('complainant_address', '')}")
    p.drawString(120, 640, f"ID Card: {case_data.get('complainant_identification_card', '')}")
    p.drawString(120, 620, f"Occupation: {case_data.get('complainant_occupation', '')}")
    p.drawString(120, 600, f"Date of Birth: {case_data.get('complainant_date_of_birth', '')}")
    p.drawString(120, 580, f"Gender: {case_data.get('complainant_gender', '')}")

    # Suspect Details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 550, "Suspect Details:")
    p.setFont("Helvetica", 12)
    p.drawString(120, 530, f"Name: {case_data.get('suspect_name', '')}")
    p.drawString(120, 510, f"Contact: {case_data.get('suspect_contact', '')}")
    p.drawString(120, 490, f"Address: {case_data.get('suspect_address', '')}")
    p.drawString(120, 470, f"ID Card: {case_data.get('suspect_identification_card', '')}")
    p.drawString(120, 450, f"Occupation: {case_data.get('suspect_occupation', '')}")
    p.drawString(120, 430, f"Date of Birth: {case_data.get('suspect_date_of_birth', '')}")
    p.drawString(120, 410, f"Gender: {case_data.get('suspect_gender', '')}")

    # Victim Details (if not the same as complainant)
    if not case_data.get('is_victim_same_as_complainant', True):
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 380, "Victim Details:")
        p.setFont("Helvetica", 12)
        p.drawString(120, 360, f"Name: {case_data.get('victim_name', '')}")
        p.drawString(120, 340, f"Contact: {case_data.get('victim_contact', '')}")
        p.drawString(120, 320, f"Address: {case_data.get('victim_address', '')}")
        p.drawString(120, 300, f"ID Card: {case_data.get('victim_identification_card', '')}")
        p.drawString(120, 280, f"Occupation: {case_data.get('victim_occupation', '')}")
        p.drawString(120, 260, f"Date of Birth: {case_data.get('victim_date_of_birth', '')}")
        p.drawString(120, 240, f"Gender: {case_data.get('victim_gender', '')}")

    # Incident Details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 210, "Incident Details:")
    p.setFont("Helvetica", 12)
    p.drawString(120, 190, f"Location: {case_data.get('location_of_incident', '')}")
    p.drawString(120, 170, f"Type: {case_data.get('type_of_incident', '')}")
    p.drawString(120, 150, f"Statement: {case_data.get('statement_of_incident', '')}")

    # Key Witness Details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 120, "Key Witness Details:")
    p.setFont("Helvetica", 12)
    p.drawString(120, 100, f"Name: {case_data.get('key_witness_name', '')}")
    p.drawString(120, 80, f"Contact: {case_data.get('key_witness_contact', '')}")
    p.drawString(120, 60, f"Address: {case_data.get('key_witness_address', '')}")
    p.drawString(120, 40, f"ID Card: {case_data.get('key_witness_identification_card', '')}")
    p.drawString(120, 20, f"Gender: {case_data.get('key_witness_gender', '')}")

    # Save the PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer




from django.http import FileResponse
from django.shortcuts import redirect

@login_required(login_url='officer_login')
def CaseStep1View(request):
    if 'case_id' not in request.session:
        officer = NewOfficerRegistration.objects.get(user=request.user)
        station = officer.officer_current_station
        region = officer.officer_operations_region
        
        case_id = generate_case_id(station, region)
        request.session['case_id'] = case_id
    else:
        case_id = request.session['case_id']

    form_step1 = CaseStep1Form(request.POST or None)

    if request.method == 'POST' and form_step1.is_valid():
        cleaned_data = form_step1.cleaned_data

        request.session.update({
            'Initial_Case_Title': cleaned_data['Initial_Case_Title'],
            'complainant_name': cleaned_data['complainant_name'],
            'complainant_contact': cleaned_data['complainant_contact'],
            'complainant_address': cleaned_data['complainant_address'],
            'complainant_identification_card': cleaned_data['complainant_identification_card'],
            'complainant_occupation': cleaned_data['complainant_occupation'],
            'complainant_date_of_birth': cleaned_data['complainant_date_of_birth'].isoformat(),
            'complainant_gender': cleaned_data['complainant_gender'],
            'suspect_name': cleaned_data['suspect_name'],
            'suspect_contact': cleaned_data['suspect_contact'],
            'suspect_address': cleaned_data['suspect_address'],
            'suspect_identification_card': cleaned_data['suspect_identification_card'],
            'suspect_occupation': cleaned_data['suspect_occupation'],
            'suspect_date_of_birth': cleaned_data['suspect_date_of_birth'].isoformat(),
            'suspect_gender': cleaned_data['suspect_gender'],
            'is_victim_same_as_complainant': cleaned_data['is_victim_same_as_complainant'],
            'location_of_incident': cleaned_data['location_of_incident'],
            'type_of_incident': cleaned_data['type_of_incident'],
            'statement_of_incident': cleaned_data['statement_of_incident'],
            'key_witness_name': cleaned_data['key_witness_name'],
            'key_witness_contact': cleaned_data['key_witness_contact'],
            'key_witness_address': cleaned_data['key_witness_address'],
            'key_witness_identification_card': cleaned_data['key_witness_identification_card'],
            'key_witness_gender': cleaned_data['key_witness_gender'],
        })

        if not cleaned_data['is_victim_same_as_complainant']:
            request.session.update({
                'victim_name': cleaned_data['victim_name'],
                'victim_contact': cleaned_data['victim_contact'],
                'victim_address': cleaned_data['victim_address'],
                'victim_identification_card': cleaned_data['victim_identification_card'],
                'victim_occupation': cleaned_data['victim_occupation'],
                'victim_date_of_birth': cleaned_data['victim_date_of_birth'].isoformat(),
                'victim_gender': cleaned_data['victim_gender'],
            })

        # Generate PDF
        pdf_buffer = generate_case_pdf(request.session)

        # Return PDF as a response
        return FileResponse(pdf_buffer, as_attachment=True, filename='case_docket.pdf')

    else:
        print("Form is not valid. Errors:", form_step1.errors)
        messages.error(request, "Please correct the errors below.")

    context = {
        'case_id': case_id,
        'form_step1': form_step1,
        'complainant_fields': [
            'complainant_name', 'complainant_contact', 'complainant_address',
            'complainant_identification_card', 'complainant_occupation',
            'complainant_date_of_birth', 'complainant_gender',
        ],
        'suspect_fields': [
            'suspect_name', 'suspect_contact', 'suspect_address',
            'suspect_identification_card', 'suspect_occupation',
            'suspect_date_of_birth', 'suspect_gender',
        ],
        'victim_fields': [
            'victim_name', 'victim_contact', 'victim_address',
            'victim_identification_card', 'victim_occupation',
            'victim_date_of_birth', 'victim_gender',
        ],
        'incident_fields': [
            'location_of_incident', 'type_of_incident', 'statement_of_incident',
        ],
        'witness_fields': [
            'key_witness_name', 'key_witness_contact', 'key_witness_address',
            'key_witness_identification_card', 'key_witness_gender',
        ]
    }

    return render(request, 'CaseStep1View.html', context)









@login_required(login_url='officer_login')
def CaseStep2View(request):
    # Check if the user accessed Step 2 without completing Step 1
    if not request.session.get('Initial_Case_Title'):
        # Redirect to Step 1 if required session data is missing
        return redirect('CaseStep1View')

    # Retrieve session data with default values
    session_data = {
        'Initial_Case_Title': request.session.get('Initial_Case_Title', ''),
        'complainant_name': request.session.get('complainant_name', ''),
        'complainant_contact': request.session.get('complainant_contact', ''),
        'complainant_date_of_birth': request.session.get('complainant_date_of_birth', ''),
        'complainant_physical_address': request.session.get('complainant_physical_address', ''),

        'suspect_name': request.session.get('suspect_name', ''),
        'suspect_contact': request.session.get('suspect_contact', ''),
        'suspect_date_of_birth': request.session.get('suspect_date_of_birth', ''),
        'suspect_physical_address': request.session.get('suspect_physical_address', ''),

        'key_witness_name': request.session.get('key_witness_name', ''),
        'key_witness_contact': request.session.get('key_witness_contact', ''),
        'key_witness_age': request.session.get('key_witness_age', ''),
        'key_witness_address': request.session.get('key_witness_address', ''),
    }

    if request.method == 'POST':
        form_step2 = CaseStep2Form(request.POST)
        if form_step2.is_valid():
            # Process form data and update session
            request.session.update({
                'complainant_statement': form_step2.cleaned_data.get('complainant_statement', ''),
                'suspect_statement': form_step2.cleaned_data.get('suspect_statement', ''),
                'key_witness_statement': form_step2.cleaned_data.get('key_witness_statement', ''),

                'case_title': form_step2.cleaned_data.get('case_title', ''),
                'is_victim_same_as_complainant': form_step2.cleaned_data.get('is_victim_same_as_complainant', ''),

                'suspect_name': form_step2.cleaned_data.get('suspect_name', session_data['suspect_name']),
                'suspect_contact': form_step2.cleaned_data.get('suspect_contact', session_data['suspect_contact']),
                'suspect_date_of_birth': form_step2.cleaned_data.get('suspect_date_of_birth', session_data['suspect_date_of_birth']),
                'suspect_physical_address': form_step2.cleaned_data.get('suspect_physical_address', session_data['suspect_physical_address']),

                'key_witness_name': form_step2.cleaned_data.get('key_witness_name', session_data['key_witness_name']),
                'key_witness_contact': form_step2.cleaned_data.get('key_witness_contact', session_data['key_witness_contact']),
                'key_witness_age': form_step2.cleaned_data.get('key_witness_age', session_data['key_witness_age']),
                'key_witness_address': form_step2.cleaned_data.get('key_witness_address', session_data['key_witness_address']),
            })

            # Redirect to the next step
            return redirect('CaseStep3View')
        else:
            # Log form errors
            logger.error(f"Form errors in CaseStep2View: {form_step2.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form_step2 = CaseStep2Form(initial=session_data)

    # Calculate ages
    complainant_age = calculate_age(session_data['complainant_date_of_birth']) if session_data['complainant_date_of_birth'] else ''
    suspect_age = calculate_age(session_data['suspect_date_of_birth']) if session_data['suspect_date_of_birth'] else ''

    context = {
        'form_step2': form_step2,
        'complainant_name': session_data['complainant_name'],
        'complainant_age': complainant_age,
        'complainant_contact': session_data['complainant_contact'],
        'complainant_physical_address': session_data['complainant_physical_address'],

        'suspect_name': session_data['suspect_name'],
        'suspect_age': suspect_age,
        'suspect_contact': session_data['suspect_contact'],
        'suspect_physical_address': session_data['suspect_physical_address'],

        'key_witness_name': session_data['key_witness_name'],
        'key_witness_age': session_data['key_witness_age'],
        'key_witness_contact': session_data['key_witness_contact'],
        'key_witness_address': session_data['key_witness_address'],
    }
    return render(request, 'CaseStep2View.html', context)







@login_required(login_url='officer_login')
def CaseStep3View(request):
    # Ensure that necessary session data exists
    required_keys = [
        'case_title', 'date_time_of_incident', 'date_time_of_report',
        'complainant_name', 'complainant_contact', 'complainant_physical_address',
        'complainant_digital_address', 'complainant_occupation', 'complainant_date_of_birth',
        'complainant_statement',  # Added necessary statement fields
        'suspect_name', 'suspect_contact', 'suspect_physical_address', 'suspect_digital_address',
        'suspect_occupation', 'suspect_date_of_birth', 'suspect_statement',
        'victim_name', 'victim_contact', 'victim_physical_address', 'victim_digital_address',
        'victim_occupation', 'victim_date_of_birth', 'location_of_incident', 'type_of_incident',
        'statement_of_incident',
        'key_witness_name', 'key_witness_contact', 'key_witness_physical_address',
        'key_witness_digital_address', 'key_witness_statement'
    ]

    # # Check if all required session data is present
    # if not all(request.session.get(key) for key in required_keys):
    #     return redirect('CaseStep2View')  # Redirect if any required data is missing

    if request.method == 'POST':
        form_step3 = CaseStep3Form(request.POST, request.FILES)
        if form_step3.is_valid():
            # Collect form data and session data
            case_data = {
                'Case_Title': request.session.get('case_title'),
                'date_time_of_incident': request.session.get('date_time_of_incident'),
                'date_time_of_report': request.session.get('date_time_of_report'),
                'complainant_name': request.session.get('complainant_name'),
                'complainant_contact': request.session.get('complainant_contact'),
                'complainant_physical_address': request.session.get('complainant_physical_address'),
                'complainant_digital_address': request.session.get('complainant_digital_address'),
                'complainant_occupation': request.session.get('complainant_occupation'),
                'complainant_date_of_birth': request.session.get('complainant_date_of_birth'),
                'complainant_statement': request.session.get('complainant_statement'),
                'suspect_name': request.session.get('suspect_name'),
                'suspect_contact': request.session.get('suspect_contact'),
                'suspect_physical_address': request.session.get('suspect_physical_address'),
                'suspect_digital_address': request.session.get('suspect_digital_address'),
                'suspect_occupation': request.session.get('suspect_occupation'),
                'suspect_date_of_birth': request.session.get('suspect_date_of_birth'),
                'suspect_statement': request.session.get('suspect_statement'),
                'victim_name': request.session.get('victim_name'),
                'victim_contact': request.session.get('victim_contact'),
                'victim_physical_address': request.session.get('victim_physical_address'),
                'victim_digital_address': request.session.get('victim_digital_address'),
                'victim_occupation': request.session.get('victim_occupation'),
                'victim_date_of_birth': request.session.get('victim_date_of_birth'),
                'location_of_incident': request.session.get('location_of_incident'),
                'type_of_incident': request.session.get('type_of_incident'),
                'statement_of_incident': request.session.get('statement_of_incident'),
                'key_witness_name': request.session.get('key_witness_name'),
                'key_witness_contact': request.session.get('key_witness_contact'),
                'key_witness_physical_address': request.session.get('key_witness_physical_address'),
                'key_witness_digital_address': request.session.get('key_witness_digital_address'),
                'key_witness_statement': request.session.get('key_witness_statement'),

                # Add final step form data
                'reporting_officer_name': form_step3.cleaned_data.get('reporting_officer_name'),
                'reporting_officer_badge_id': form_step3.cleaned_data.get('reporting_officer_badge_id'),
                'reporting_officer_rank': form_step3.cleaned_data.get('reporting_officer_rank'),
                'reporting_officer_station': form_step3.cleaned_data.get('reporting_officer_station'),
                'reporting_officer_division': form_step3.cleaned_data.get('reporting_officer_division'),
                'charges_filed': form_step3.cleaned_data.get('charges_filed'),
                'legal_actions_taken': form_step3.cleaned_data.get('legal_actions_taken'),
                'assigned_investigator': form_step3.cleaned_data.get('assigned_investigator'),
                'case_status': form_step3.cleaned_data.get('case_status'),
                'follow_up_required': form_step3.cleaned_data.get('follow_up_required'),
                'additional_notes': form_step3.cleaned_data.get('additional_notes'),
            }

            # Generate PDF
            pdf_buffer = generate_pdf(case_data)

            # Serve the PDF
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="case_report.pdf"'
            return response

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form_step3 = CaseStep3Form()

    return render(request, 'CaseStep3View.html', {'form': form_step3})



def success_page(request):
    return render(request, 'success_page.html')