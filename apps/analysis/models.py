"""
Analysis application models.

Core models for location analysis and reporting.
"""

from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Location(models.Model):
    """
    A geographic location that has been analyzed.
    
    Stores normalized location data to avoid duplicates
    when users analyze the same place.
    """
    address = models.CharField(max_length=255, unique=False)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.address

    class Meta:
        verbose_name_plural = "Locations"
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]


class AnalysisResult(models.Model):
    """
    Complete analysis result for a location.
    
    Contains AI-generated insights, weather data, feedback scores.
    One result per user per location per analysis.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analyses")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="analyses")

    # AI Metrics (from Groq)
    safety_score = models.FloatField(help_text="0-10 safety rating")
    noise_level = models.CharField(max_length=50, choices=[
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ])
    rent_level = models.CharField(max_length=50, choices=[
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ])
    water_quality = models.CharField(max_length=50, choices=[
        ("Poor", "Poor"),
        ("Average", "Average"),
        ("Good", "Good"),
    ])

    ai_summary = models.TextField(help_text="AI-generated summary")
    ai_score = models.IntegerField(help_text="0-100 overall livability score")
    
    # User Feedback Metrics
    avg_feedback_score = models.FloatField(
        default=0,
        help_text="Average score from user feedback (0-5)"
    )
    
    # Weather Data (from Open-Meteo)
    temperature = models.FloatField(null=True, blank=True, help_text="Apparent temperature in Celsius")
    windspeed = models.FloatField(null=True, blank=True, help_text="Wind speed in km/h")
    weather_code = models.CharField(max_length=50, null=True, blank=True, help_text="Weather risk level")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location} - Score: {self.ai_score}"

    class Meta:
        verbose_name_plural = "Analysis Results"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['location', '-created_at']),
        ]