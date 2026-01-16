"""
Community application models.

User feedback and community engagement features.
"""

from django.db import models
from django.conf import settings
from apps.analysis.models import AnalysisResult


User = settings.AUTH_USER_MODEL


class ReportFeedback(models.Model):
    """
    User feedback on analysis reports.
    
    Allows users to rate report accuracy, usefulness, and clarity.
    Feedback is used to improve AI model over time.
    """
    report = models.ForeignKey(
        AnalysisResult,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedback_given"
    )

    accuracy = models.IntegerField(help_text="1-5 rating for accuracy")
    usefulness = models.IntegerField(help_text="1-5 rating for usefulness")
    clarity = models.IntegerField(help_text="1-5 rating for clarity")

    comment = models.TextField(blank=True, help_text="Optional additional comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def quality_score(self):
        """
        Calculate average quality score from the three rating dimensions.
        
        Returns:
            float: Average of accuracy, usefulness, clarity (rounded to 2 decimals)
        """
        return round(
            (self.accuracy + self.usefulness + self.clarity) / 3, 2
        )

    def __str__(self):
        return f"Feedback for Report {self.report.id}"

    class Meta:
        verbose_name_plural = "Report Feedback"
        unique_together = ("report", "user")  # One feedback per user per report
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['report', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]