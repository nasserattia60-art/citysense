"""
Tests for the community application.

Tests cover:
- Report feedback submission
- Feedback quality scoring
- Authorization
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.analysis.models import Location, AnalysisResult
from .models import ReportFeedback

User = get_user_model()


class ReportFeedbackModelTests(TestCase):
    """Tests for ReportFeedback model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.location = Location.objects.create(
            address="Test City",
            latitude=0.0,
            longitude=0.0
        )
        self.report = AnalysisResult.objects.create(
            user=self.user,
            location=self.location,
            safety_score=7.0,
            noise_level="Medium",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Test",
            ai_score=75
        )

    def test_create_feedback(self):
        """Test creating feedback."""
        feedback = ReportFeedback.objects.create(
            report=self.report,
            user=self.user,
            accuracy=5,
            usefulness=4,
            clarity=5,
            comment="Great analysis!"
        )
        self.assertEqual(feedback.report, self.report)
        self.assertEqual(feedback.user, self.user)

    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        feedback = ReportFeedback.objects.create(
            report=self.report,
            user=self.user,
            accuracy=5,
            usefulness=4,
            clarity=3
        )
        # (5 + 4 + 3) / 3 = 4.0
        self.assertEqual(feedback.quality_score(), 4.0)

    def test_feedback_str(self):
        """Test feedback string representation."""
        feedback = ReportFeedback.objects.create(
            report=self.report,
            user=self.user,
            accuracy=5,
            usefulness=5,
            clarity=5
        )
        self.assertIn(str(self.report.id), str(feedback))


class FeedbackViewTests(TestCase):
    """Tests for feedback submission view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.location = Location.objects.create(
            address="Test City",
            latitude=0.0,
            longitude=0.0
        )
        self.report = AnalysisResult.objects.create(
            user=self.user,
            location=self.location,
            safety_score=7.0,
            noise_level="Medium",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Test",
            ai_score=75
        )

    def test_feedback_view_requires_login(self):
        """Test that feedback view requires authentication."""
        url = reverse("community:feedback", args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_feedback_view_displays_form(self):
        """Test that feedback view displays form."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("community:feedback", args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_submit_feedback(self):
        """Test submitting feedback."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("community:feedback", args=[self.report.id])
        response = self.client.post(url, {
            "accuracy": 5,
            "usefulness": 4,
            "clarity": 5,
            "comment": "Very helpful!"
        })
        self.assertEqual(response.status_code, 302)  # Redirect to report
        self.assertTrue(
            ReportFeedback.objects.filter(
                report=self.report,
                user=self.user
            ).exists()
        )

    def test_feedback_updates_avg_score(self):
        """Test that feedback updates report's average feedback score."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("community:feedback", args=[self.report.id])
        self.client.post(url, {
            "accuracy": 4,
            "usefulness": 4,
            "clarity": 4,
            "comment": ""
        })
        self.report.refresh_from_db()
        # Should be 4.0 (average of 4, 4, 4)
        self.assertEqual(self.report.avg_feedback_score, 4.0)

    def test_feedback_nonexistent_report(self):
        """Test feedback for non-existent report."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("community:feedback", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
