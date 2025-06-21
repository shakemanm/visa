from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    CreateView, UpdateView, DetailView, ListView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Applicant, JobProfile
from .forms import ApplicantForm, JobProfileForm
from django.views.generic import (
    CreateView, UpdateView, DetailView, ListView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError

from django.urls import reverse_lazy
from .models import JobProfile
import logging
logger = logging.getLogger(__name__)
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Applicant, JobProfile
from .forms import ApplicantForm, JobProfileForm
import logging
from django.views.generic import View
from django.http import HttpResponse
from django.template.loader import render_to_string

import tempfile
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO
from django.utils import timezone
from django.contrib.sessions.models import Session
from .models import ApplicantSession
from django.views.generic import CreateView, UpdateView
from .models import Applicant, ApplicantSession
from .forms import ApplicantForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import ApplicantSession
from datetime import datetime  # Add this import at the top
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)

class JobProfileListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = JobProfile
    template_name = 'applications/jobprofile_list.html'
    context_object_name = 'job_profiles'
    ordering = ['title']
    
    def test_func(self):
        """Only staff users can view the job profiles list"""
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_delete'] = self.request.user.is_staff
        return context

class JobProfileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = JobProfile
    form_class = JobProfileForm
    template_name = 'applications/jobprofile_form.html'
    success_url = reverse_lazy('jobprofile_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        # Set created_at before saving
        job_profile = form.save(commit=False)
        job_profile.created_at = timezone.now()
        job_profile.save()
        
        messages.success(self.request, f"Job profile '{job_profile.title}' created successfully!")
        return super().form_valid(form)

class JobProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = JobProfile
    form_class = JobProfileForm
    template_name = 'applications/jobprofile_form.html'
    success_url = reverse_lazy('jobprofile_list')
    
    def test_func(self):
        """Only staff users can update job profiles"""
        return self.request.user.is_staff
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Job profile '{self.object.title}' updated successfully!")
        return response
        

class JobProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = JobProfile
    success_url = reverse_lazy('jobprofile_list')
    template_name = 'applications/jobprofile_confirm_delete.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Job profile deleted successfully')
        return super().delete(request, *args, **kwargs)

class ApplicantCreateView(CreateView):
    model = Applicant
    form_class = ApplicantForm
    template_name = 'applications/applicant_form.html'
    success_url = reverse_lazy('thank_you')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_edit'] = False
        kwargs['session_key'] = self.request.session.session_key
        kwargs['user'] = self.request.user if self.request.user.is_authenticated else None
        return kwargs

class ApplicantUpdateView(UpdateView):
    model = Applicant
    form_class = ApplicantForm
    template_name = 'applications/applicant_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_edit'] = True
        kwargs['session_key'] = self.request.session.session_key
        kwargs['user'] = self.request.user
        return kwargs

class ApplicantDetailView(DetailView):
    model = Applicant
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        applicant = context['object']
        
        # Process duties
        processed_duties = []
        if applicant.custom_duties:
            for duty in applicant.custom_duties:
                # Split duties by comma and clean up
                duties = str(duty).replace('[', '').replace(']', '').replace("'", "").split(',')
                processed_duties.extend([d.strip() for d in duties if d.strip()])
        
        context['processed_duties'] = processed_duties
        return context

class ApplicantDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Applicant
    template_name = 'applications/applicant_confirm_delete.html'
    success_url = reverse_lazy('applicant_list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Application deleted successfully')
        return super().delete(request, *args, **kwargs)

class ApplicantListView(LoginRequiredMixin, ListView):
    model = Applicant
    template_name = 'applications/applicant_list.html'
    context_object_name = 'applicants'
    paginate_by = 20
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_staff:
            # Get upcoming appointments (future dates only)
            today = timezone.now().date()
            context['upcoming_appointments'] = Applicant.objects.filter(
                appointment_date__isnull=False,
                appointment_date__gte=today
            ).order_by('appointment_date')[:10]  # Limit to 10 upcoming appointments
            
            # Get pending payments (deposited but not reflected)
            context['pending_payments'] = Applicant.objects.filter(
                deposited_at_standard_bank__isnull=False,
                payment_reflected__isnull=True
            ).order_by('deposited_at_standard_bank')[:10]  # Limit to 10 pending payments
            
        return context

def thank_you(request):
    return render(request, 'applications/thank_you.html')

def home(request):
    context = {
        'total_applicants': Applicant.objects.count(),
        'active_job_profiles': JobProfile.objects.filter(is_active=True).count(),
    }
    return render(request, 'applications/home.html', context)


# In views.py
class GenerateDocumentView(LoginRequiredMixin, View):
    def get(self, request, pk, doc_type):
        applicant = get_object_or_404(Applicant, pk=pk)

        # Base context with current time
        context = {
            'applicant': applicant,
            'now': timezone.now(),
        }

        if doc_type == 'cv':
            # Calculate work period if years_worked exists
            if applicant.years_worked:
                current_year = timezone.now().year
                start_year = current_year - applicant.years_worked + 1
                context['work_period'] = f"{start_year} to {current_year}"
            else:
                context['work_period'] = "[Years Worked Not Specified]"

            html_string = render_to_string('applications/cv_template.html', context)
            filename = f"CV_{applicant.surname}_{applicant.first_names}.pdf"

            if not applicant.cv_generated:
                applicant.cv_generated = True
                applicant.cv_generated_date = timezone.now()
                applicant.save()

        elif doc_type == 'motivation':
            html_string = applicant.generate_motivation_letter()
            filename = f"Motivation_Letter_{applicant.surname}_{applicant.first_names}.pdf"

            if not applicant.motivation_letter_generated:
                applicant.motivation_letter_generated = True
                applicant.motivation_letter_date = timezone.now()
                applicant.save()

        elif doc_type == 'contract':
            html_string = applicant.generate_contract()
            filename = f"Contract_{applicant.surname}_{applicant.first_names}.pdf"

            if not applicant.contract_generated:
                applicant.contract_generated = True
                applicant.contract_date = timezone.now()
                applicant.save()

        else:
            return HttpResponse("Invalid document type", status=400)

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        result = pisa.CreatePDF(html_string, dest=response)

        if result.err:
            logger.error(f"PDF generation error: {result.err}")
            return HttpResponse('PDF generation error', status=500)

        return response
    
def job_profile_duties(request, pk):
    """
    API endpoint to get duties for a specific job profile
    """
    profile = get_object_or_404(JobProfile, pk=pk)
    return JsonResponse({
        'duties': profile.duties,
        'title': profile.title
    })


@require_POST
@csrf_exempt
def cleanup_session(request):
    try:
        import json
        data = json.loads(request.body)
        session_key = data.get('session_key')
        if session_key:
            session = ApplicantSession.objects.get(session_key=session_key)
            session.active = False
            session.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)