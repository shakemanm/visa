from django.contrib.sessions.models import Session
from .models import ApplicantSession


class MultiSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.save()
        
        session_key = request.session.session_key
        session, created = ApplicantSession.objects.get_or_create(
            session_key=session_key,
            defaults={'active': True}
        )
        
        if not created and not session.active:
            session.active = True
            session.save()
        
        request.current_session = session
        
        response = self.get_response(request)
        return response