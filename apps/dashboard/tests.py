"""
Tests for the dashboard application.

Tests cover:
- Dashboard view with analytics
- Report statistics and aggregation
- Map view
- Authentication requirements
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.analysis.models import Location, AnalysisResult

User = get_user_model()


class DashboardViewTests(TestCase):
    """Tests for the dashboard view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.dashboard_url = reverse("dashboard:dashboard")

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn("/users/login/", response.url)

    def test_dashboard_view_for_authenticated_user(self):
        """Test that authenticated users can view dashboard."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_displays_report_count(self):
        """Test that dashboard shows correct report count."""
        # Create test reports
        location = Location.objects.create(
            address="Test City",
            latitude=0.0,
            longitude=0.0
        )
        AnalysisResult.objects.create(
            user=self.user,
            location=location,
            safety_score=7.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Test",
            ai_score=75
        )
        AnalysisResult.objects.create(
            user=self.user,
            location=location,
            safety_score=6.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Test",
            ai_score=70
        )

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.dashboard_url)
        
        self.assertContains(response, "2")  # Should show 2 reports

    def test_dashboard_calculates_average_score(self):
        """Test that dashboard calculates average AI score correctly."""
        location = Location.objects.create(
            address="Test City",
            latitude=0.0,
            longitude=0.0
        )
        AnalysisResult.objects.create(
            user=self.user,
            location=location,
            safety_score=7.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Test",
            ai_score=80
        )
        AnalysisResult.objects.create(
            user=self.user,
            location=location,
            safety_score=6.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Test",
            ai_score=60
        )

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.dashboard_url)
        
        # Average of 80 and 60 is 70
        self.assertContains(response, "70.0")

    def test_dashboard_shows_latest_reports(self):
        """Test that dashboard shows 5 most recent reports."""
        location = Location.objects.create(
            address="Test City",
            latitude=0.0,
            longitude=0.0
        )
        # Create 7 reports
        for i in range(7):
            AnalysisResult.objects.create(
                user=self.user,
                location=location,
                safety_score=7.0,
                noise_level="Low",
                rent_level="Medium",
                water_quality="Good",
                ai_summary="Test",
                ai_score=75 - i
            )

        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.dashboard_url)
        
        # Should show only 5 latest reports
        self.assertEqual(len(response.context["latest_reports"]), 5)


class MapViewTests(TestCase):
    """Tests for the map view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.map_url = reverse("dashboard:map")

    def test_map_view_requires_login(self):
        """Test that map view requires authentication."""
        response = self.client.get(self.map_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_map_view_for_authenticated_user(self):
        """Test that authenticated users can view map."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.map_url)
        self.assertEqual(response.status_code, 200)

