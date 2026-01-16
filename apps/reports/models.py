"""
Reports application models.

Analytics and tracking for analysis reports.
"""

from django.db import models
from django.conf import settings
from apps.analysis.models import AnalysisResult

User = settings.AUTH_USER_MODEL


class ReportAnalytics(models.Model):
    """
    Analytics tracking for individual reports.
    
    Future feature: Track views, engagement, feedback trends.
    """
    report = models.OneToOneField(
        AnalysisResult,
        on_delete=models.CASCADE,
        related_name="analytics"
    )
    views = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this report has been viewed"
    )
    feedback_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Average user feedback score (0-100)"
    )

    def __str__(self):
        return f"Analytics for Report {self.report.id}"

    class Meta:
        verbose_name_plural = "Report Analytics"
