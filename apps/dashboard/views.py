"""
Dashboard application views.

User dashboard with analytics and recent reports.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.analysis.models import AnalysisResult
import logging

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """
    User analytics dashboard.
    
    Displays:
    - Total reports created
    - Average AI quality score
    - 5 most recent reports
    """
    reports = AnalysisResult.objects.filter(user=request.user)

    context = {
        "reports_count": reports.count(),
        "avg_ai_score": round(
            sum(r.ai_score for r in reports) / reports.count(), 2
        ) if reports else 0,
        "latest_reports": reports.order_by("-created_at")[:5],
    }

    logger.debug(f"Dashboard viewed by user: {request.user.id}")
    return render(request, "dashboard/dashboard.html", context)

