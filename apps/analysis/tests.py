"""
Tests for the analysis application.

Tests cover:
- Models (Location, AnalysisResult)
- Views (analyze, report, heatmap, suggestions)
- Services (geocoding, city suggestions)
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Location, AnalysisResult
from .services import suggest_city_fuzzy
import json

User = get_user_model()


class LocationModelTests(TestCase):
    """Tests for Location model."""

    def test_create_location(self):
        """Test creating a location."""
        location = Location.objects.create(
            address="New York, USA",
            latitude=40.7128,
            longitude=-74.0060
        )
        self.assertEqual(location.address, "New York, USA")
        self.assertEqual(location.latitude, 40.7128)
        self.assertEqual(location.longitude, -74.0060)

    def test_location_str(self):
        """Test location string representation."""
        location = Location.objects.create(
            address="Paris, France",
            latitude=48.8566,
            longitude=2.3522
        )
        self.assertEqual(str(location), "Paris, France")


class AnalysisResultModelTests(TestCase):
    """Tests for AnalysisResult model."""

    def setUp(self):
        """Set up test user and location."""
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.location = Location.objects.create(
            address="London, UK",
            latitude=51.5074,
            longitude=-0.1278
        )

    def test_create_analysis_result(self):
        """Test creating an analysis result."""
        result = AnalysisResult.objects.create(
            user=self.user,
            location=self.location,
            safety_score=7.5,
            noise_level="Medium",
            rent_level="High",
            water_quality="Good",
            ai_summary="London is a vibrant city with good infrastructure.",
            ai_score=78,
            temperature=15.5,
            windspeed=10.2,
            weather_code="NORMAL"
        )
        
        self.assertEqual(result.user, self.user)
        self.assertEqual(result.location, self.location)
        self.assertEqual(result.ai_score, 78)

    def test_analysis_result_str(self):
        """Test analysis result string representation."""
        result = AnalysisResult.objects.create(
            user=self.user,
            location=self.location,
            safety_score=7.5,
            noise_level="Medium",
            rent_level="High",
            water_quality="Good",
            ai_summary="Test",
            ai_score=78
        )
        self.assertIn("78", str(result))


class AnalyzeViewTests(TestCase):
    """Tests for analyze view."""

    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.analyze_url = reverse("analysis:analyze")

    def test_analyze_view_requires_login(self):
        """Test that analyze view requires authentication."""
        response = self.client.get(self.analyze_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn("/users/login/", response.url)

    def test_analyze_view_displays_form(self):
        """Test that analyze view displays the form."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.analyze_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_analyze_form_invalid_address(self):
        """Test analyze view with non-existent address."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.post(self.analyze_url, {
            "address": "XYZ123NONEXISTENT"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.context)


class ReportViewTests(TestCase):
    """Tests for report view."""

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
        self.result = AnalysisResult.objects.create(
            user=self.user,
            location=self.location,
            safety_score=7.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Test summary",
            ai_score=75
        )

    def test_report_view_requires_login(self):
        """Test that report view requires authentication."""
        url = reverse("analysis:report", args=[self.result.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_report_view_shows_correct_data(self):
        """Test that report view displays correct data."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("analysis:report", args=[self.result.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["report"], self.result)

    def test_report_view_unauthorized_access(self):
        """Test that users can't view other users' reports."""
        other_user = User.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="testpass123"
        )
        self.client.login(email="other@example.com", password="testpass123")
        url = reverse("analysis:report", args=[self.result.id])
        response = self.client.get(url)
        # Should return 404 (no matching report for this user)
        self.assertEqual(response.status_code, 404)


class CityStuggestionsTests(TestCase):
    """Tests for city suggestions AJAX endpoint."""

    def test_suggestions_minimum_length(self):
        """Test that suggestions require minimum 2 characters."""
        url = reverse("analysis:city_suggestions")
        response = self.client.get(url, {"q": "a"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

    def test_suggestions_returns_json(self):
        """Test that suggestions endpoint returns JSON."""
        url = reverse("analysis:city_suggestions")
        response = self.client.get(url, {"q": "new"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_suggestions_valid_query(self):
        """Test suggestions with valid query."""
        url = reverse("analysis:city_suggestions")
        response = self.client.get(url, {"q": "york"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Should return a list (maybe empty if GeoNames isn't loaded)
        self.assertIsInstance(data, list)


class CityFuzzySuggestionsTests(TestCase):
    """Tests for fuzzy city matching service."""

    def test_fuzzy_match_exact(self):
        """Test exact city match."""
        # This tests the service directly - requires GeoNames data
        results = suggest_city_fuzzy("London", limit=5)
        self.assertIsInstance(results, list)

    def test_fuzzy_match_partial(self):
        """Test partial city match."""
        results = suggest_city_fuzzy("new", limit=10)
        self.assertIsInstance(results, list)

    def test_fuzzy_match_limit(self):
        """Test that limit parameter works."""
        results = suggest_city_fuzzy("city", limit=3)
        self.assertLessEqual(len(results), 3)


class HeatmapDataTests(TestCase):
    """Tests for heatmap data AJAX endpoint."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.location = Location.objects.create(
            address="Test City",
            latitude=40.7128,
            longitude=-74.0060
        )
        self.result = AnalysisResult.objects.create(
            user=self.user,
            location=self.location,
            safety_score=8.0,
            noise_level="Low",
            rent_level="Medium",
            water_quality="Good",
            ai_summary="Test",
            ai_score=80
        )

    def test_heatmap_returns_json(self):
        """Test that heatmap endpoint returns JSON."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("analysis:heatmap-data")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_heatmap_default_layer(self):
        """Test heatmap with default layer."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("analysis:heatmap-data")
        response = self.client.get(url)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("lat", data[0])
            self.assertIn("lng", data[0])
            self.assertIn("weight", data[0])

    def test_heatmap_safety_layer(self):
        """Test heatmap with safety layer."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("analysis:heatmap-data")
        response = self.client.get(url, {"layer": "safety"})
        data = json.loads(response.content)
        # For safety layer, weight should be the safety_score
        if data:
            self.assertEqual(data[0]["weight"], self.result.safety_score)

    def test_heatmap_noise_layer(self):
        """Test heatmap with noise layer."""
        self.client.login(email="test@example.com", password="testpass123")
        url = reverse("analysis:heatmap-data")
        response = self.client.get(url, {"layer": "noise"})
        data = json.loads(response.content)
        # For noise "Low", weight should be 15
        if data:
            self.assertEqual(data[0]["weight"], 15)
