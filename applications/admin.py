from django.contrib import admin
from django.utils.html import format_html
from .models import Applicant, JobProfile
from .constants import HIGH_SCHOOL_SUBJECTS

class ApplicantAdmin(admin.ModelAdmin):
    list_display = (
        'get_full_name', 
        'passport_number', 
        'nationality',
        'get_subjects',
        'employment_status',
    )
    list_filter = (
        'nationality',
        'marital_status',
        'employed',
        'asylum_refugee_status',
    )
    search_fields = (
        'surname',
        'first_names',
        'passport_number',
        'email',
        'cell_phone_number'
    )
    list_select_related = ('job_profile',)
    ordering = ('-id',)  # Order by ID descending as fallback
    list_per_page = 25

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'title', 
                'surname', 
                'first_names',
                'date_of_birth',
                ('country_of_birth', 'city_of_birth'),
                ('nationality', 'present_nationality'),
                'marital_status',
                ('marriage_date', 'married_to_sa_citizen'),
            )
        }),
        ('Passport Information', {
            'fields': (
                'passport_number',
                ('passport_issue_date', 'passport_expiry_date'),
                'passport_issued_by',
                ('previous_permit', 'previous_permit_number'),
            )
        }),
        ('Contact Information', {
            'fields': (
                'house_number_and_street',
                ('suburb', 'town_or_city'),
                'postal_code',
                ('cell_phone_number', 'whatsapp_number'),
                ('work_phone_number', 'email'),
            )
        }),
        ('Employment Information', {
            'fields': (
                'employed',
                'employer_name',
                ('industry', 'business_type'),
                'job_profile',
                'custom_duties',
                'employer_street_address',
                ('employer_place', 'employer_town'),
                'employer_post_code',
                ('years_worked', 'commencement_date'),
                ('manager_name', 'reference'),
                'previous_employer',
            )
        }),
        ('Education Information', {
            'fields': (
                'school',
                'subjects',
            )
        }),
        ('Immigration Information', {
            'fields': (
                'asylum_refugee_status',
                ('refugee_reference_number', 'refugee_country'),
                ('date_of_entry_sa', 'place_of_entry_sa'),
            )
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.surname}, {obj.first_names}"
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'surname'

    def get_subjects(self, obj):
        if not obj.subjects:
            return "-"
        subject_dict = dict(HIGH_SCHOOL_SUBJECTS)
        subjects = [subject_dict.get(subj, subj) for subj in obj.subjects]
        return format_html("<br>".join(subjects[:3]) + ("..." if len(subjects) > 3 else ""))
    get_subjects.short_description = 'Subjects'

    def employment_status(self, obj):
        if obj.employed:
            return format_html(
                '<span style="color: green;">✓ Employed</span><br>{}',
                obj.employer_name
            )
        return format_html('<span style="color: red;">✗ Not Employed</span>')
    employment_status.short_description = 'Employment'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job_profile')

admin.site.register(Applicant, ApplicantAdmin)

class JobProfileAdmin(admin.ModelAdmin):
    list_display = ('title', 'industry', 'is_active', 'duty_count')
    list_filter = ('industry', 'is_active')
    search_fields = ('title', 'industry')
    list_editable = ('is_active',)

    def duty_count(self, obj):
        return len(obj.duties)
    duty_count.short_description = '# Duties'

admin.site.register(JobProfile, JobProfileAdmin)