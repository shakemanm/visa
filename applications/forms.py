from django import forms
from .models import Applicant, JobProfile
from django.core.exceptions import ValidationError
from .constants import HIGH_SCHOOL_SUBJECTS, BUSINESS_TYPES
import json
from .models import ApplicantSession
class JobProfileForm(forms.ModelForm):
    duty_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a duty/responsibility',
            'class': 'form-control duty-input'
        }),
        label="Add Duty"
    )
    
    duties_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = JobProfile
        fields = ['title', 'description', 'industry', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.duties:
            self.initial['duties_json'] = json.dumps(self.instance.duties)

    def clean(self):
            cleaned_data = super().clean()
            duties_json = cleaned_data.get('duties_json')
            
            if duties_json:
                try:
                    duties = json.loads(duties_json)
                    if not isinstance(duties, list):
                        raise forms.ValidationError("Duties must be a list")
                    
                    # Capitalize each duty
                    cleaned_duties = []
                    for duty in duties:
                        if duty.strip():
                            # Capitalize first letter of each sentence
                            sentences = [s.strip() for s in duty.split('.') if s.strip()]
                            capitalized = '. '.join([s[0].upper() + s[1:] if s else '' for s in sentences])
                            cleaned_duty = capitalized + '.' if duty.endswith('.') else capitalized
                            cleaned_duties.append(cleaned_duty)
                    
                    cleaned_data['duties'] = cleaned_duties
                except json.JSONDecodeError:
                    raise forms.ValidationError("Invalid duties data format")
            else:
                cleaned_data['duties'] = []
                
            return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.duties = self.cleaned_data.get('duties', [])
        if commit:
            instance.save()
        return instance

class ApplicantForm(forms.ModelForm):
    subjects = forms.MultipleChoiceField(
        choices=HIGH_SCHOOL_SUBJECTS,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="High School Subjects"
    )
    session_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Name this session (optional)',
            'class': 'form-control'
        })
    )
    job_profile = forms.ModelChoiceField(
        queryset=JobProfile.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-action': 'change->applicant#updateDuties'
        }),
        label="Job Profile"
    )
    
    class Meta:
        model = Applicant
        fields = [
            # Personal Information

            'session_name',
            'applying_for',  # Add this line
            'previous_permit', 'previous_permit_number', 'title', 'surname', 
            'first_names', 'date_of_birth', 'country_of_birth', 'city_of_birth',
            'nationality', 'present_nationality', 'passport_number', 
            'passport_issue_date', 'passport_expiry_date', 'passport_issued_by',
            'marital_status', 'marriage_date', 'married_to_sa_citizen',
            
            # Contact Information
            'house_number_and_street', 'suburb', 'town_or_city', 'postal_code',
            'cell_phone_number', 'work_phone_number', 'whatsapp_number', 'email',
            
            # Employment Information
            'employed', 'employer_name', 'industry', 'job_profile', 
            'employer_street_address', 'employer_place', 'employer_town',
            'employer_post_code', 'years_worked', 'business_type', 
            'commencement_date', 'manager_name', 'reference', 'previous_employer',
            
            # Education Information
            'school', 'subjects',
            
            # Immigration Information
            'asylum_refugee_status', 'refugee_reference_number', 'refugee_country',
            'date_of_entry_sa', 'place_of_entry_sa',
            
            # Application Stage Information
            'deposit_slip_sent', 'deposited_at_standard_bank', 'payment_reflected',
            'appointment_booked', 'appointment_date','documents_sent', 'agent_fee_paid',
            'agent_fee_paid_date', 'submitted', 'visa_status'
        ]
        widgets = {

            'applying_for': forms.Select(attrs={
                'class': 'form-control',
                'data-action': 'change->applicant#updatePermitType'}),

            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'passport_issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'passport_expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'marriage_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'commencement_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_entry_sa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'deposit_slip_sent': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'deposited_at_standard_bank': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_reflected': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_booked': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                        'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'documents_sent': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'agent_fee_paid_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'submitted': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'agent_fee_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'visa_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.session_key = kwargs.pop('session_key', None)
        self.user = kwargs.pop('user', None)
      
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        if not self.is_edit:
            # Make all employment-related fields not required
            employment_fields = [
                'employed', 'employer_name', 'industry', 'job_profile',
                'business_type', 'employer_street_address', 'employer_town',
                'employer_post_code', 'years_worked', 'commencement_date',
                'manager_name', 'reference', 'previous_employer'
            ]
            for field in employment_fields:
                if field in self.fields:
                    self.fields[field].required = False
            
            # Make education fields not required
            education_fields = ['school', 'subjects']
            for field in education_fields:
                if field in self.fields:
                    self.fields[field].required = False

        if not self.is_edit:
            self.fields['employed'].required = False
            self.fields['school'].required = False
            self.fields['subjects'].required = False

        


        if self.instance and self.instance.pk:
            if self.instance.previous_permit == 'No':
                self.initial['applying_for'] = 'none'
        
        if self.instance and self.instance.pk and self.instance.session:
            self.initial['session_name'] = self.instance.session.name


        # Make applying_for required if previous_permit is Yes
        if 'previous_permit' in self.data and self.data.get('previous_permit') == 'Yes':
            self.fields['applying_for'].required = True
        elif self.instance and self.instance.previous_permit == 'Yes':
            self.fields['applying_for'].required = True
        else:
            self.fields['applying_for'].required = False
            self.initial['applying_for'] = 'none'

    
       
       
       
       
       
       
        self.fields['job_profile'].queryset = JobProfile.objects.filter(is_active=True)
        
        
        
        if self.instance and self.instance.pk:
            if self.instance.subjects:
                self.fields['subjects'].initial = self.instance.subjects
        
        # Initialize refugee fields based on current status
        if self.instance and self.instance.pk and self.instance.asylum_refugee_status == 'No':
            self.initial['refugee_reference_number'] = ''
            self.initial['refugee_country'] = ''
        
        # Set field classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif not isinstance(field.widget, (forms.SelectMultiple, forms.CheckboxSelectMultiple)):
                field.widget.attrs['class'] = 'form-control'

        # Only show application stage fields in update mode for staff users
        if not (self.instance and self.instance.pk and user and user.is_staff):
            for field in ['deposit_slip_sent', 'deposited_at_standard_bank', 'payment_reflected',
                        'appointment_booked', 'documents_sent', 'agent_fee_paid',
                        'agent_fee_paid_date', 'submitted', 'visa_status']:
                if field in self.fields:
                    self.fields.pop(field)

    def clean(self):
        cleaned_data = super().clean()
        asylum_status = cleaned_data.get('asylum_refugee_status')
        previous_permit = cleaned_data.get('previous_permit')
        applying_for = cleaned_data.get('applying_for')

         # Ensure passport number is uppercase
        # Address fields processing
        employment_address_fields = [
            'employer_street_address',
            'employer_place',
            'employer_town',
            'previous_employer',
            'reference'
        ]

        # Validate applying_for field
        if previous_permit == 'Yes' and not applying_for:
            self.add_error('applying_for', 'This field is required if you have a previous permit')
        elif previous_permit == 'No' and applying_for != 'none':
            self.add_error('applying_for', 'This field should be "Not Applicable" if no previous permit')

        for field in employment_address_fields:
            if field in cleaned_data and cleaned_data[field]:
                value = cleaned_data[field]
                if field == 'employer_street_address':
                    parts = value.split()
                    formatted_parts = []
                    for part in parts:
                        if part.isdigit():
                            formatted_parts.append(part)
                        else:
                            formatted_parts.append(part.title())
                    cleaned_data[field] = ' '.join(formatted_parts)
                else:
                    cleaned_data[field] = value.title()


        # Other field processing
        if 'passport_number' in cleaned_data:
            cleaned_data['passport_number'] = cleaned_data['passport_number'].upper()
            
        capitalize_fields = [
            'surname', 'first_names', 'city_of_birth', 'employer_name',
            'manager_name', 'previous_employer', 'school'
        ]
        
        for field in capitalize_fields:
            if field in cleaned_data and cleaned_data[field]:
                cleaned_data[field] = cleaned_data[field].title()
                
        if 'email' in cleaned_data and cleaned_data['email']:
            cleaned_data['email'] = cleaned_data['email'].lower()
            
        if 'subjects' in cleaned_data and cleaned_data['subjects']:
            cleaned_data['subjects'] = [
                subject.title() for subject in cleaned_data['subjects'] 
                if isinstance(subject, str)
            ]
        
        # Refugee field validation
        if asylum_status == 'Yes':
            if not cleaned_data.get('refugee_reference_number'):
                self.add_error('refugee_reference_number', 'This field is required for refugees')
            if not cleaned_data.get('refugee_country'):
                self.add_error('refugee_country', 'This field is required for refugees')
        else:
            # Only validate if fields exist in submitted data and have values
            if 'refugee_reference_number' in self.data and self.data.get('refugee_reference_number'):
                self.add_error('refugee_reference_number', 'This field should be empty if not a refugee')
            if 'refugee_country' in self.data and self.data.get('refugee_country'):
                self.add_error('refugee_country', 'This field should be empty if not a refugee')
        
        # Validate marital status
        marital_status = cleaned_data.get('marital_status')
        marriage_date = cleaned_data.get('marriage_date')
        married_to_sa_citizen = cleaned_data.get('married_to_sa_citizen')
        
        if marital_status == 'Single':
            if marriage_date:
                self.add_error('marriage_date', 'Marriage date should be empty for Single applicants')
            if married_to_sa_citizen is not None:
                self.add_error('married_to_sa_citizen', 'This field should be empty for Single applicants')
        
        # Validate previous permit
        previous_permit = cleaned_data.get('previous_permit')
        previous_permit_number = cleaned_data.get('previous_permit_number')
        
        if previous_permit == 'No' and previous_permit_number:
            self.add_error('previous_permit_number', 'This field must be empty if "Previous permit" is "No"')
        if previous_permit == 'Yes' and not previous_permit_number:
            self.add_error('previous_permit_number', 'This field is required if "Previous permit" is "Yes"')

        # Validate employment information
        employed = cleaned_data.get('employed')
        if employed:
            required_fields = [
                'employer_name', 'industry', 'job_profile',
                'employer_street_address', 'employer_town', 'employer_post_code'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for employed applicants')
        
        return cleaned_data

    def save(self, commit=True):
        applicant = super().save(commit=False)
        applicant.subjects = self.cleaned_data.get('subjects', [])

        if self.session_key:
            session, _ = ApplicantSession.objects.get_or_create(
                session_key=self.session_key,
                defaults={'active': True}
            )
            if self.cleaned_data.get('session_name'):
                session.name = self.cleaned_data['session_name']
                session.save()
            applicant.session = session
        
        # Clear refugee fields if not applicable
        if applicant.asylum_refugee_status == 'No':
            applicant.refugee_reference_number = None
            applicant.refugee_country = None
        
        if commit:
            applicant.save()
            self.save_m2m()
        
        return applicant