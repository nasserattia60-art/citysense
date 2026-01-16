"""
Reports application views.

User report history and management.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.analysis.models import AnalysisResult
import logging

logger = logging.getLogger(__name__)


@login_required
def reports_list_view(request):
    """
    User's analysis reports history view.
    
    Shows all reports created by the authenticated user,
    ordered by most recent first.
    """
    reports = AnalysisResult.objects.filter(user=request.user).order_by("-created_at")
    logger.debug(f"Reports list viewed by user: {request.user.id}, count: {reports.count()}")
    return render(request, "reports/list.html", {"reports": reports})