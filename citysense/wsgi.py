"""
WSGI config for citysense project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings if RENDER env var is set (Render deployment)
settings_module = 'citysense.settings.prod' if os.getenv('RENDER') else 'citysense.settings.dev'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()
