"""
Tests for the core application.

Tests cover:
- Home page view
- Public access without authentication
- Template rendering
"""

from django.test import TestCase, Client
from django.urls import reverse


class HomeViewTests(TestCase):
    """Tests for the home page view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.home_url = reverse("core:home")

    def test_home_view_accessible(self):
        """Test that home page is accessible without authentication."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_home_view_uses_correct_template(self):
        """Test that home view uses the correct template."""
        response = self.client.get(self.home_url)
        self.assertTemplateUsed(response, "core/home.html")

    def test_home_view_context(self):
        """Test that home view has the expected context."""
        response = self.client.get(self.home_url)
        # Home page doesn't require special context data
        self.assertIsNotNone(response.context)

    def test_home_page_title(self):
        """Test that home page has correct title."""
        response = self.client.get(self.home_url)
        self.assertContains(response, "Welcome to CitySense")

