import os
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse
from django.urls import re_path

class ReactAppView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['STATIC_URL'] = settings.STATIC_URL
        return context

def serve_media_file(request, path):
    """
    Custom view to serve media files from the persistent disk
    """
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    # Check if file exists
    if os.path.exists(full_path):
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    else:
        return HttpResponse("File not found", status=404) 