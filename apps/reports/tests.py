"""
Tests for the reports application.

Tests cover:
- Reports list view
- Filtering by user
- Pagination
- Authentication requirements
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.analysis.models import Location, AnalysisResult

User = get_user_model()


class ReportsListViewTests(TestCase):
    """Tests for the reports list view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="testpass123"
        )
        self.reports_url = reverse("reports:reports")

    def test_reports_view_requires_login(self):
        """Test that reports view requires authentication."""
        response = self.client.get(self.reports_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn("/users/login/", response.url)

    def test_reports_view_for_authenticated_user(self):
        """Test that authenticated users can view their reports."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.reports_url)
        self.assertEqual(response.status_code, 200)

    def test_reports_shows_user_reports_only(self):
        """Test that users only see their own reports."""
        # Create reports for both users
        location = Location.objects.create(
            address="Test City",
            latitude=0.0,
            longitude=0.0
        )
        user_report = AnalysisResult.objects.create(
            user=self.user,
            location=location,
            safety_score=7.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="User report",
            ai_score=75
        )
        other_report = AnalysisResult.objects.create(
            user=self.other_user,
            location=location,
            safety_score=6.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Other report",
            ai_score=70
        )

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.reports_url)
        
        # Should contain user's report
        self.assertContains(response, "User report")
        # Should not contain other user's report
        self.assertNotContains(response, "Other report")

    def test_reports_ordered_by_date(self):
        """Test that reports are ordered by most recent first."""
        location = Location.objects.create(
            address="Test City",
            latitude=0.0,
            longitude=0.0
        )
        # Create reports (oldest first)
        report1 = AnalysisResult.objects.create(
            user=self.user,
            location=location,
            safety_score=7.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="First report",
            ai_score=75
        )
        report2 = AnalysisResult.objects.create(
            user=self.user,
            location=location,
            safety_score=8.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Second report",
            ai_score=85
        )

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.reports_url)
        
        reports = response.context["reports"]
        # Most recent should be first
        self.assertEqual(reports[0].id, report2.id)
        self.assertEqual(reports[1].id, report1.id)

    def test_reports_list_template(self):
        """Test that correct template is used."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.reports_url)
        self.assertTemplateUsed(response, "reports/list.html")

    def test_empty_reports_list(self):
        """Test that empty reports list is handled gracefully."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.reports_url)
        
        reports = response.context["reports"]
        self.assertEqual(len(reports), 0)

