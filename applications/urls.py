from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views  # Added this import for the API view
from .views import (
    
    cleanup_session,
    ApplicantCreateView, 
    ApplicantUpdateView,
    ApplicantDetailView,
    ApplicantListView,
    JobProfileCreateView, 
    JobProfileUpdateView,
    ApplicantDeleteView,
    GenerateDocumentView,
    thank_you,
    home
)

urlpatterns = [
    # Main application URLs
    path('', home, name='home'),
    
    # Applicant URLs
    path('apply/', ApplicantCreateView.as_view(), name='applicant_create'),
    path('applications/', ApplicantListView.as_view(), name='applicant_list'),
    path('applications/<int:pk>/', ApplicantDetailView.as_view(), name='applicant_detail'),
    path('applications/<int:pk>/edit/', ApplicantUpdateView.as_view(), name='applicant_update'),
    path('applicant/<int:pk>/delete/', ApplicantDeleteView.as_view(), name='applicant_delete'),
    path('applicant/<int:pk>/generate/<str:doc_type>/', GenerateDocumentView.as_view(), name='generate_document'),
    path('thank-you/', thank_you, name='thank_you'),
    
    # Authentication URL
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Job Profile URLs
    path('jobprofile/new/', JobProfileCreateView.as_view(), name='jobprofile_create'),
    path('jobprofile/<int:pk>/edit/', JobProfileUpdateView.as_view(), name='jobprofile_update'),
  
    # API Endpoint
    path('api/jobprofile/<int:pk>/duties/', views.job_profile_duties, name='jobprofile_duties'),
    
    # Job Profile List View (new addition)
    path('jobprofiles/', views.JobProfileListView.as_view(), name='jobprofile_list'),
   
    path('jobprofile/<int:pk>/delete/', views.JobProfileDeleteView.as_view(), name='jobprofile_delete'),
    path('jobprofile/new/', views.JobProfileCreateView.as_view(), name='jobprofile_create'),
    path('jobprofile/<int:pk>/edit/', views.JobProfileUpdateView.as_view(), name='jobprofile_update'),

   path('cleanup-session/', cleanup_session, name='cleanup_session'),
    
  
    
    
    
    
    
]