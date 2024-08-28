from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.contrib.sessions.models import Session

# Create your models here.
class OfficerLogin(models.Model):
    username = models.CharField(unique=True, max_length=250)
    password = models.CharField(max_length=256)  # Increase max_length for password


class NewOfficerRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    first_name = models.CharField(max_length=250)
    middle_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    
    username = models.CharField(max_length=250, unique=True, validators=[MinLengthValidator(1)])
    def save(self, *args, **kwargs):
        if not self.username.strip():
            raise ValueError("Username cannot be empty")
        super().save(*args, **kwargs)

    OFFICER_GENDER_CHOICES_MALE = 'M'
    OFFICER_GENDER_CHOICES_FEMALE = 'F'

    OFFICER_GENDER_CHOICES = [
        (OFFICER_GENDER_CHOICES_MALE, 'Male'),
        (OFFICER_GENDER_CHOICES_FEMALE, 'Female'),
        
        ]
    officer_gender = models.CharField(max_length=250, choices=OFFICER_GENDER_CHOICES, default='')
    email = models.EmailField(unique=True, max_length=250)
    phone_contact = models.IntegerField(unique=True)
    officer_address = models.CharField(max_length=250)
    
    # Constants for officer ranks
    RANK_Constable = 'Constable'
    RANK_Lance_Corporal = 'Lance Corporal'
    RANK_Corporal = 'Corporal'
    RANK_Sergeant = 'Sergeant'
    RANK_District_Sergeant_Major = 'District Sergeant Major'
    RANK_Inspector = 'Inspector'
    RANK_Regional_Sergeant_Major = 'Regional Sergeant Major'
    RANK_Chief_Inspector = 'Chief Inspector'
    RANK_Assistant_Superintendent_of_Police = 'Assistant Superintendent of Police'
    RANK_Deputy_Superintendent_of_Police = 'Deputy Superintendent of Police'
    RANK_Superintendent_of_Police = 'Superintendent of Police'
    RANK_Chief_Superintendent = 'Chief Superintendent'
    RANK_Assistant_Commissioner_of_Police = 'Assistant Commissioner of Police'
    RANK_Deputy_Commissioner_of_Police = 'Deputy Commissioner of Police'
    RANK_Commissioner_of_Police = 'Commissioner of Police'
    RANK_Inspector_General_of_Police = 'Inspector General of Police'

    # Choices for officer ranks
    OFFICER_RANK_CHOICES = [
        (RANK_Constable, 'Constable'),
        (RANK_Lance_Corporal, 'Lance Corporal'),
        (RANK_Corporal, 'Corporal'),
        (RANK_Sergeant, 'Sergeant'),
        (RANK_District_Sergeant_Major, 'District Sergeant Major'),
        (RANK_Inspector, 'Inspector'),
        (RANK_Regional_Sergeant_Major, 'Regional Sergeant Major'),
        (RANK_Chief_Inspector, 'Chief Inspector'),
        (RANK_Assistant_Superintendent_of_Police, 'Assistant Superintendent of Police'),
        (RANK_Deputy_Superintendent_of_Police, 'Deputy Superintendent of Police'),
        (RANK_Superintendent_of_Police, 'Superintendent of Police'),
        (RANK_Chief_Superintendent, 'Chief Superintendent'),
        (RANK_Assistant_Commissioner_of_Police, 'Assistant Commissioner of Police'),
        (RANK_Deputy_Commissioner_of_Police, 'Deputy Commissioner of Police'),
        (RANK_Commissioner_of_Police, 'Commissioner of Police'),
        (RANK_Inspector_General_of_Police, 'Inspector General of Police'),
    ]
    officer_current_rank = models.CharField(max_length=250, choices=OFFICER_RANK_CHOICES)

    officer_current_station = models.CharField(max_length=250)
    officer_staff_ID = models.CharField(unique=True, max_length=250)
    
    EDUCATION_WASSCE = 'WS'
    EDUCATION_DEGREE = 'DG'
    EDUCATION_MASTERS = 'MS'
    EDUCATION_PHD = 'PH'
    
    EDUCATION_QUALIFICATION_CHOICES = [
        (EDUCATION_WASSCE, 'WASSCE'),
        (EDUCATION_DEGREE, 'DEGREE'),
        (EDUCATION_MASTERS, 'MASTERS'),
        (EDUCATION_PHD, 'PHD'),
    ]
    officer_qualification = models.CharField(max_length=250, choices=EDUCATION_QUALIFICATION_CHOICES)
    officer_date_of_birth = models.DateField()

    OFFICER_OPERATIONS_REGION = [
    ('GA', 'Greater Accra'),
    ('AR', 'Ahafo Region'),
    ('ARR', 'Ashanti Region'),
    ('BR', 'Bono Region'),
    ('BER', 'Bono East Region'),
    ('CR', 'Central Region'),
    ('ER', 'Eastern Region'),
    ('NER', 'North East Region'),
    ('NR', 'Northern Region'),
    ('OR', 'Oti Region'),
    ('SR', 'Savannah Region'),
    ('UER', 'Upper East Region'),
    ('UWR', 'Upper West Region'),
    ('VR', 'Volta Region'),
    ('WR', 'Western Region'),
    ('WNR', 'Western North Region')
    ]
    officer_operations_region = models.CharField(max_length=250, choices=OFFICER_OPERATIONS_REGION)

        # Constants for officer departments
    DEPARTMENT_Criminal_InvestigationDepartment = 'CID'
    DEPARTMENT_Motor_Traffic_and_TransportDirectorate = 'MTTD'
    DEPARTMENT_Domestic_Violence_and_Victim_Support_Unit = 'DOVVSU'
    DEPARTMENT_The_Police_College = 'The Police College'
    DEPARTMENT_Other_Training_Institutions = 'Other Training Institutions'
    DEPARTMENT_Works_and_Housing_Department = 'W&H'
    DEPARTMENT_Public_Relations_Department = 'PRD'
    DEPARTMENT_Medical_Hospital = 'MH'
    DEPARTMENT_Marine_Ports_and_Railways = 'Marine Ports & Railways'
    DEPARTMENT_Community_Policing = 'Community Policing'

        # Choices for officer departments
    OFFICER_DEPARTMENT_CHOICES = [
            (DEPARTMENT_Criminal_InvestigationDepartment, 'Criminal Investigation Department [CID]'),
            (DEPARTMENT_Motor_Traffic_and_TransportDirectorate, 'Motor Traffic and Transport Directorate [MTTD]'),
            (DEPARTMENT_Domestic_Violence_and_Victim_Support_Unit, 'Domestic Violence and Victim Support Unit [DOVVSU]'),
            (DEPARTMENT_The_Police_College, 'The Police College'),
            (DEPARTMENT_Other_Training_Institutions, 'Other Training Institutions'),
            (DEPARTMENT_Works_and_Housing_Department, 'Works & Housing Department'),
            (DEPARTMENT_Public_Relations_Department, 'Public Relations Department'),
            (DEPARTMENT_Medical_Hospital, 'Medical – Hospital'),
            (DEPARTMENT_Marine_Ports_and_Railways, 'Marine Ports & Railways'),
            (DEPARTMENT_Community_Policing, 'Community Policing'),
        ]

    officer_operations_department = models.CharField(max_length=250, choices=OFFICER_DEPARTMENT_CHOICES)
    officer_profile_image = models.ImageField(upload_to='profileImages/', blank=True, null=True)

    OFFICER_STATION_RANK_CHOICES = [
            ('DC', 'District Commander'),
            ('DIVC', 'Divisional Commander'),
            ('SO', 'Station Officer'),
            ('DSO', 'Deputy Station Officer'),
            ('SSI', 'Station Sergeants and Inspector'),
            ('OO', 'Other Officer/Constables'),
        ]
    officer_stationRank = models.CharField(max_length=100, choices=OFFICER_STATION_RANK_CHOICES)


    OFFICER_OPERATIONS_DISTRICT = [
    ('GA', 'Greater Accra'),
    ('AR', 'Ahafo Region'),
    ('ARR', 'Ashanti Region'),
    ('BR', 'Bono Region'),
    ('BER', 'Bono East Region'),
    ('CR', 'Central Region'),
    ('ER', 'Eastern Region'),
    ('NER', 'North East Region'),
    ('NR', 'Northern Region'),
    ('OR', 'Oti Region'),
    ('SR', 'Savannah Region'),
    ('UER', 'Upper East Region'),
    ('UWR', 'Upper West Region'),
    ('VR', 'Volta Region'),
    ('WR', 'Western Region'),
    ('WNR', 'Western North Region')
    ]    
    officer_Operationsdistrict = models.CharField(max_length=250, choices=OFFICER_OPERATIONS_DISTRICT)
    password = models.CharField(max_length=128)



class Case(models.Model):

    # Gender Choices
    GENDER_CHOICES_MALE = 'M'
    GENDER_CHOICES_FEMALE = 'F'

    GENDER_CHOICES = [
        (GENDER_CHOICES_MALE, 'Male'),
        (GENDER_CHOICES_FEMALE, 'Female'),
    ]

    # Case Information
    case_ID = models.CharField(max_length=255)
    Case_Title = models.CharField(max_length=255)
    date_time_of_incident = models.DateTimeField()
    date_time_of_report = models.DateTimeField()

    # Complainant Information
    complainant_name = models.CharField(max_length=255)
    complainant_contact = models.CharField(max_length=20)
    complainant_address = models.CharField(max_length=255)
    complainant_identification_card = models.CharField(max_length=255, blank=True, null=True)
    complainant_occupation = models.CharField(max_length=100, blank=True, null=True)
    complainant_date_of_birth = models.DateField(blank=True, null=True)
    complainant_gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)


    # Suspect Information
    suspect_name = models.CharField(max_length=255, blank=True, null=True)
    suspect_contact = models.CharField(max_length=20, blank=True, null=True)
    suspect_address = models.CharField(max_length=255, blank=True, null=True)
    suspect_identification_card = models.CharField(max_length=255, blank=True, null=True)
    suspect_occupation = models.CharField(max_length=100, blank=True, null=True)
    suspect_date_of_birth = models.DateField(blank=True, null=True)
    suspect_gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)


    # Victim Information
    is_victim_same_as_complainant = models.BooleanField(default=True)
    victim_name = models.CharField(max_length=255, blank=True, null=True)
    victim_contact = models.CharField(max_length=20, blank=True, null=True)
    victim_address = models.CharField(max_length=255, blank=True, null=True)
    victim_identification_card = models.CharField(max_length=255, blank=True, null=True)
    victim_occupation = models.CharField(max_length=100, blank=True, null=True)
    victim_date_of_birth = models.DateField(blank=True, null=True)
    victim_gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    # Incident Details
    location_of_incident = models.CharField(max_length=255)
    type_of_incident = models.CharField(max_length=100, choices=[
        ('Theft', 'Theft'),
        ('Assault', 'Assault'),
        ('Traffic Accident', 'Traffic Accident'),
        ('Other', 'Other')
    ])
    statement_of_incident = models.TextField()

    # Key Witness Information
    key_witness_name = models.CharField(max_length=255, blank=True, null=True)
    key_witness_contact = models.CharField(max_length=20, blank=True, null=True)
    key_witness_address = models.CharField(max_length=255, blank=True, null=True)
    key_witness_identification_card = models.CharField(max_length=255, blank=True, null=True)
    key_witness_occupation = models.CharField(max_length=100, blank=True, null=True)
    key_witness_gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
 
    

    # Step 2 Fields: Statements and Additional Witnesses
    complainant_statement = models.TextField(blank=False, null=False)
    suspect_statement = models.TextField(blank=False, null=False)
    key_witness_statement = models.TextField(blank=False, null=False)
    

    # Step 3 Fields: Reporting Officer and Case Progression
    reporting_officer_name = models.CharField(max_length=255, blank=True, null=True)
    reporting_officer_badge_id = models.CharField(max_length=50, blank=True, null=True)
    reporting_officer_rank = models.CharField(max_length=50, blank=True, null=True)
    reporting_officer_station = models.CharField(max_length=255, blank=True, null=True)
    reporting_officer_division = models.CharField(max_length=255, blank=True, null=True)
    charges_filed = models.TextField(blank=True, null=True)
    legal_actions_taken = models.TextField(blank=True, null=True)
    assigned_investigator = models.CharField(max_length=255, blank=True, null=True)
    case_status = models.CharField(max_length=50, choices=[
        ('Open', 'Open'),
        ('Under Investigation', 'Under Investigation'),
        ('Closed', 'Closed')
    ], blank=True, null=True)
    follow_up_required = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    # Attachments
    mugshot = models.FileField(upload_to='mugshots/', blank=True, null=True)
    fingerprint = models.FileField(upload_to='fingerprints/', blank=True, null=True)

    def __str__(self):
        return self.Case_Title

