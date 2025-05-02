import os
import re
from django.conf import settings
from django.http import HttpResponse, FileResponse
from django.views.static import serve

class MediaFilesMiddleware:
    """
    Middleware to intercept requests for media files and serve them from the persistent disk.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile a regular expression to match media URLs
        self.media_url_pattern = re.compile(f'^{settings.MEDIA_URL.lstrip("/")}(.*)')

    def __call__(self, request):
        # Check if this is a media file request
        media_match = self.media_url_pattern.match(request.path.lstrip('/'))
        
        if media_match:
            # Extract the path within the media root
            media_path = media_match.group(1)
            full_path = os.path.join(settings.MEDIA_ROOT, media_path)
            
            # Log for debugging
            print(f"Media request: {request.path} -> {full_path}")
            
            # Check if file exists and serve it
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return serve(request, media_path, document_root=settings.MEDIA_ROOT)
        
        # For all other requests, continue with normal processing
        return self.get_response(request) 