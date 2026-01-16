"""
Core application views.

Home page and base views for the CitySense application.
"""

from django.shortcuts import render


def home(request):
    """
    Home page view.
    
    Displays landing page with project information.
    No authentication required.
    """
    return render(request, 'core/home.html')


