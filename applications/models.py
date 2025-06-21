from django.db import models
from django.core.exceptions import ValidationError
import datetime
from django.contrib.sessions.models import Session

from django.urls import reverse

from .constants import HIGH_SCHOOL_SUBJECTS, COUNTRIES, BUSINESS_TYPES, PERMIT_TYPE_CHOICES 
from datetime import date
from django.template.loader import render_to_string
from django.db import models
from django.contrib.postgres.fields import JSONField  # For PostgreSQL
from django.utils import timezone





class ApplicantSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Session {self.name or self.session_key[:8]}"


class JobProfile(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=100)
    duties = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    
    def clean(self):
        super().clean()
        if not isinstance(self.duties, list):
            raise ValidationError({'duties': 'Duties must be a list'})
        
        # Clean and validate each duty with proper capitalization
        cleaned_duties = []
        for duty in self.duties:
            if duty and isinstance(duty, str):
                cleaned_duty = duty.strip()
                if cleaned_duty:
                    # Capitalize first letter of each sentence in duty
                    sentences = [s.strip() for s in cleaned_duty.split('.') if s.strip()]
                    capitalized = '. '.join([s[0].upper() + s[1:] if s else '' for s in sentences])
                    cleaned_duty = capitalized + '.' if cleaned_duty.endswith('.') else capitalized
                    cleaned_duties.append(cleaned_duty)
        
        self.duties = cleaned_duties

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']

class Applicant(models.Model):
    YES_NO_CHOICES = [('Yes', 'Yes'), ('No', 'No')]
    STATUS_CHOICES = [('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Separated', 'Separated')]
    TITLE_CHOICES = [('Mr', 'Mr'), ('Ms', 'Ms'), ('Miss', 'Miss'), ('Mrs', 'Mrs'), ('Prof', 'Prof'), ('Dr', 'Dr'), ('Other', 'Other')]
    VISA_STATUS_CHOICES = [(None, 'Pending'), (True, 'Granted'), (False, 'Denied')]
    session = models.ForeignKey(ApplicantSession, on_delete=models.SET_NULL, null=True, blank=True)
    # Personal Information
    previous_permit = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    previous_permit_number = models.CharField(max_length=50, null=True, blank=True)
    applying_for = models.CharField(
        max_length=10, 
        choices=PERMIT_TYPE_CHOICES, 
        default='none',
        verbose_name="Applying for"
    )
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='Mr')
    surname = models.CharField(max_length=100)
    first_names = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    country_of_birth = models.CharField(max_length=100, choices=COUNTRIES)
    city_of_birth = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100, choices=COUNTRIES)
    present_nationality = models.CharField(max_length=100, choices=COUNTRIES)
    passport_number = models.CharField(max_length=20)
    passport_issue_date = models.DateField()
    passport_expiry_date = models.DateField()
    passport_issued_by = models.CharField(max_length=100, choices=COUNTRIES)
    marital_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Single')
    marriage_date = models.DateField(null=True, blank=True)
    married_to_sa_citizen = models.BooleanField(null=True, blank=True)

    # Contact Information
    house_number_and_street = models.CharField(max_length=200, verbose_name="House Number and Street", default="")
    suburb = models.CharField(max_length=100, verbose_name="Suburb", default="")
    town_or_city = models.CharField(max_length=100, verbose_name="Town/City", default="")
    postal_code = models.CharField(max_length=10)
    cell_phone_number = models.CharField(max_length=15)
    work_phone_number = models.CharField(max_length=15, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    # Employment Information
    employed = models.BooleanField(default=False)
    employer_name = models.CharField(max_length=200, blank=True, default='')
    industry = models.CharField(max_length=100, blank=True, default='')
    job_profile = models.ForeignKey(
        JobProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applicants'
    )
    custom_duties = models.JSONField(default=list, blank=True)
    employer_street_address = models.CharField(max_length=100, blank=True, null=True)
    employer_place = models.CharField(max_length=100, blank=True, null=True)
    employer_town = models.CharField(max_length=100, blank=True, null=True)
    employer_post_code = models.CharField(max_length=10, blank=True, null=True)
    years_worked = models.IntegerField(blank=True, null=True)
    business_type = models.CharField(
        max_length=5,
        choices=BUSINESS_TYPES,
        default='OTH')
    commencement_date = models.DateField(blank=True, null=True, verbose_name="Commencement Date")
    manager_name = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    previous_employer = models.CharField(max_length=100, blank=True, null=True)

    # Education Information
    school = models.CharField(max_length=100, blank=True, null=True)
    subjects = models.JSONField(default=list, blank=True)

    # Immigration Information
    asylum_refugee_status = models.CharField(
        max_length=3, 
        choices=YES_NO_CHOICES, 
        default='No'
    )
    refugee_reference_number = models.CharField(max_length=100, null=True, blank=True)
    refugee_country = models.CharField(max_length=100, choices=COUNTRIES, null=True, blank=True)
    date_of_entry_sa = models.DateField()
    place_of_entry_sa = models.CharField(max_length=100)

    # Application Stage Information
    deposit_slip_sent = models.DateField(null=True, blank=True)
    deposited_at_standard_bank = models.DateField(null=True, blank=True)
    payment_reflected = models.DateField(null=True, blank=True)
    appointment_booked = models.DateField(null=True, blank=True)
    appointment_date = models.DateField(null=True, blank=True, verbose_name="Appointment Date")
    documents_sent = models.DateField(null=True, blank=True)
    agent_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    agent_fee_paid_date = models.DateField(null=True, blank=True)
    submitted = models.DateField(null=True, blank=True)
    visa_status = models.BooleanField(choices=VISA_STATUS_CHOICES, null=True, blank=True)

    # Document generation fields
    cv_generated = models.BooleanField(default=False)
    motivation_letter_generated = models.BooleanField(default=False)
    contract_generated = models.BooleanField(default=False)
    cv_generated_date = models.DateField(null=True, blank=True)
    motivation_letter_date = models.DateField(null=True, blank=True)
    contract_date = models.DateField(null=True, blank=True)
    cv_template = models.TextField(blank=True)
    motivation_letter_template = models.TextField(blank=True)
    contract_template = models.TextField(blank=True)
    def save(self, *args, **kwargs):
        # Automatically set agent_fee_paid_date when agent_fee_paid is set
        if self.agent_fee_paid and not self.agent_fee_paid_date:
            self.agent_fee_paid_date = timezone.now().date()
        elif not self.agent_fee_paid:
            self.agent_fee_paid_date = None

    def get_absolute_url(self):
        return reverse('applicant_detail', kwargs={'pk': self.pk})

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        
        # List of all address-related fields
        # Employment address fields to be capitalized
        employment_address_fields = [
            'employer_street_address',
            'employer_place',
            'employer_town',
            'previous_employer',
            'reference'
        ]

        for field in employment_address_fields:
            value = getattr(self, field)
            if value:
                # Special handling for street addresses (preserve numbers)
                if field == 'employer_street_address':
                    parts = value.split()
                    formatted_parts = []
                    for part in parts:
                        if part.isdigit():
                            formatted_parts.append(part)
                        else:
                            formatted_parts.append(part.title())
                    setattr(self, field, ' '.join(formatted_parts))
                else:
                    # Standard title case for other fields
                    setattr(self, field, value.title())

        # Capitalize other fields
        capitalize_fields = [
            'surname', 'first_names', 'city_of_birth', 'employer_name',
            'manager_name', 'previous_employer', 'school'
        ]
        
        for field in capitalize_fields:
            if getattr(self, field):
                setattr(self, field, getattr(self, field).title())
                
        # Uppercase passport number
        if self.passport_number:
            self.passport_number = self.passport_number.upper()
            
        # Lowercase email
        if self.email:
            self.email = self.email.lower()
            
        # Capitalize subjects if they exist
        if self.subjects and isinstance(self.subjects, list):
            self.subjects = [subject.title() for subject in self.subjects 
                           if isinstance(subject, str)]
    
    def save(self, *args, **kwargs):
        self.clean_fields()
        super().save(*args, **kwargs)

    def clean(self):
        # Validate marital status
        if self.marital_status == 'Single':
            if self.marriage_date:
                raise ValidationError({'marriage_date': 'Marriage date should be empty for Single applicants'})
            if self.married_to_sa_citizen is not None:
                raise ValidationError({'married_to_sa_citizen': 'This field should be empty for Single applicants'})

        # Validate previous permit
        if self.previous_permit == 'No' and self.previous_permit_number:
            raise ValidationError({
                'previous_permit_number': 'This field must be empty if "Previous permit" is "No"'
            })
        if self.previous_permit == 'Yes' and not self.previous_permit_number:
            raise ValidationError({
                'previous_permit_number': 'This field is required if "Previous permit" is "Yes"'
            })

        # Validate employment information
        if self.employed:
            if not self.employer_name:
                raise ValidationError({'employer_name': 'Employer name is required when employed'})
            if not self.industry:
                raise ValidationError({'industry': 'Industry is required when employed'})
            if not self.job_profile:
                raise ValidationError({'job_profile': 'Job profile is required when employed'})

        # Validate refugee status
        if self.asylum_refugee_status == 'Yes':
            if not self.refugee_reference_number:
                raise ValidationError({
                    'refugee_reference_number': 'This field is required for refugees'
                })
            if not self.refugee_country:
                raise ValidationError({
                    'refugee_country': 'This field is required for refugees'
                })
        else:
            if self.refugee_reference_number:
                raise ValidationError({
                    'refugee_reference_number': 'This field should be empty if not a refugee'
                })
            if self.refugee_country:
                raise ValidationError({
                    'refugee_country': 'This field should be empty if not a refugee'
                })

    def save(self, *args, **kwargs):
        # Clear fields when not applicable
        if self.previous_permit == 'No':
            self.previous_permit_number = None
        if self.marital_status == 'Single':
            self.marriage_date = None
            self.married_to_sa_citizen = None
        if self.asylum_refugee_status == 'No':
            self.refugee_reference_number = None
            self.refugee_country = None

        # Only set defaults when not employed AND fields are empty
        if not self.employed:
            if not self.employer_name:
                self.employer_name = ''
            if not self.industry:
                self.industry = ''
            if not self.job_profile:
                self.job_profile = None

        super().save(*args, **kwargs)

    def get_all_duties(self):
        """Return job profile duties as clean bullet points"""
        if self.job_profile and self.job_profile.duties:
            duties = []
            for duty in self.job_profile.duties:
                clean_duty = str(duty).replace('•', '').replace('-', '').strip()
                clean_duty = clean_duty.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
                if clean_duty:
                    duties.append(clean_duty)
            return duties
        return []

    def get_all_subjects(self):
        """Returns list of subjects"""
        return self.subjects if self.subjects else []

    def generate_cv(self):
        """Generate CV HTML content"""
        today = date.today()
        age = today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
        
        context = {
            'applicant': self,
            'date': today.strftime('%d %B %Y'),
            'age': age,
            'duties': self.get_all_duties(),
            'subjects': self.subjects if self.subjects else [],
        }
        
        return render_to_string('applications/cv_template.html', context)

    def generate_motivation_letter(self):
        """Generate Motivation Letter HTML content"""
        today = date.today()
        business_type_display = dict(BUSINESS_TYPES).get(self.business_type, 'business')
        
        context = {
            'applicant': self,
            'date': today.strftime('%d %B %Y'),
            'business_type_display': business_type_display,
            'years_worked': self.years_worked or 0,
            'job_title': self.job_profile.title if self.job_profile else 'employee',
        }
        
        return render_to_string('applications/motivation_letter_template.html', context)

    def generate_contract(self):
        """Generate Contract HTML content"""
        today = date.today()
        
        context = {
            'applicant': self,
            'date': today.strftime('%d %B %Y'),
            'job_title': self.job_profile.title if self.job_profile else '[Job Title]',
        }
        
        return render_to_string('applications/contract_template.html', context)

    def generate_documents(self):
        """Generate all documents at once"""
        today = date.today()
        
        # Generate CV
        if not self.cv_generated:
            self.cv_template = self.generate_cv()
            self.cv_generated = True
            self.cv_generated_date = today
        
        # Generate Motivation Letter
        if not self.motivation_letter_generated:
            self.motivation_letter_template = self.generate_motivation_letter()
            self.motivation_letter_generated = True
            self.motivation_letter_date = today
        
        # Generate Contract
        if not self.contract_generated:
            self.contract_template = self.generate_contract()
            self.contract_generated = True
            self.contract_date = today
        
        self.save()

    def __str__(self):
        return f"{self.surname}, {self.first_names}"