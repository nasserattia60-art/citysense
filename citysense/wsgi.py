"""
WSGI config for citysense project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Add project directory to Python path for PythonAnywhere
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Determine which settings module to use
if os.getenv('PYTHONANYWHERE'):
    settings_module = 'citysense.settings.pythonanywhere'
elif os.getenv('RENDER') or os.getenv('RAILWAY_ENVIRONMENT'):
    settings_module = 'citysense.settings.prod'
else:
    settings_module = 'citysense.settings.dev'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
