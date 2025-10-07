from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
import os


class FrontendView(View):
    """
    Serves the compiled frontend single page application
    """
    def get(self, request, *args, **kwargs):
        try:
            # Try to serve from the built frontend
            frontend_path = os.path.join(settings.BASE_DIR, 'frontend_build', 'index.html')
            with open(frontend_path) as f:
                return HttpResponse(f.read(), content_type='text/html')
        except FileNotFoundError:
            return HttpResponse(
                """
                <html>
                <head><title>Frontend Not Built</title></head>
                <body>
                    <h1>Frontend Not Built</h1>
                    <p>The frontend has not been built yet. Please run:</p>
                    <pre>python build_frontend.py</pre>
                    <p>Or during development, run the frontend dev server:</p>
                    <pre>cd frontend && npm run dev</pre>
                </body>
                </html>
                """,
                content_type='text/html',
                status=503
            )
