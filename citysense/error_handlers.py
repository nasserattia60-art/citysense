"""
Error handlers and custom views for error pages.
"""

from django.shortcuts import render


def custom_404(request, exception=None):
    """Handle 404 Not Found errors."""
    return render(request, "error/404.html", status=404)


def custom_500(request):
    """Handle 500 Server errors."""
    return render(request, "error/500.html", status=500)
