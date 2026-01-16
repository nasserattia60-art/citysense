"""
Community and feedback views.

Handles user feedback on analysis reports to help
improve AI accuracy and insights.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import FeedbackForm
from .models import ReportFeedback
from apps.analysis.models import AnalysisResult
import logging

logger = logging.getLogger(__name__)


@login_required
def feedback_view(request, report_id):
    """
    Feedback submission view for analysis reports.
    
    Users can provide feedback on report accuracy, usefulness, and clarity
    to help improve the AI system.
    
    Args:
        report_id (int): ID of the report being reviewed
    
    GET: Display feedback form
    POST: Save feedback and redirect to report
    """
    try:
        report = AnalysisResult.objects.get(id=report_id)
    except AnalysisResult.DoesNotExist:
        logger.warning(f"Feedback attempt for non-existent report: {report_id}")
        return render(request, "error/404.html", status=404)
    
    form = FeedbackForm(request.POST or None)

    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.user = request.user
        feedback.report = report
        feedback.save()
        
        # Update report's average feedback score
        feedbacks = ReportFeedback.objects.filter(report=report)
        if feedbacks.exists():
            avg_score = sum(f.quality_score() for f in feedbacks) / feedbacks.count()
            report.avg_feedback_score = avg_score
            report.save()
        
        logger.info(f"Feedback submitted: user={request.user.id}, report={report_id}")
        return redirect("analysis:report", report.id)

    return render(request, "community/feedback.html", {
        "form": form,
        "report": report
    })