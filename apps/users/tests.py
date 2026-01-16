"""
Tests for the users application.

Tests cover:
- Custom User model
- Registration
- Profile management
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class UserModelTests(TestCase):
    """Tests for custom User model."""

    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)

    def test_user_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(
            email="test@example.com",
            username="user1",
            password="pass123"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="test@example.com",
                username="user2",
                password="pass123"
            )

    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.assertEqual(str(user), "test@example.com")


class ProfileModelTests(TestCase):
    """Tests for Profile model."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )

    def test_create_profile(self):
        """Test creating a profile."""
        profile = Profile.objects.create(
            user=self.user,
            bio="I love traveling",
            city="London"
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, "I love traveling")
        self.assertEqual(profile.city, "London")

    def test_profile_str(self):
        """Test profile string representation."""
        profile = Profile.objects.create(user=self.user)
        self.assertIn("Profile", str(profile))


class RegisterViewTests(TestCase):
    """Tests for registration view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.register_url = reverse("users:register")

    def test_register_view_displays_form(self):
        """Test that registration page displays form."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_register_valid_user(self):
        """Test registering a valid user."""
        response = self.client.post(self.register_url, {
            "email": "newuser@example.com",
            "username": "newuser",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!"
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_duplicate_email(self):
        """Test registering with duplicate email."""
        User.objects.create_user(
            email="existing@example.com",
            username="existing",
            password="testpass123"
        )
        response = self.client.post(self.register_url, {
            "email": "existing@example.com",
            "username": "newuser",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!"
        })
        # Should have error
        self.assertEqual(response.status_code, 200)
        self.assertIn("error", response.context or {})

    def test_register_password_mismatch(self):
        """Test registering with mismatched passwords."""
        response = self.client.post(self.register_url, {
            "email": "test@example.com",
            "username": "testuser",
            "password1": "SecurePass123!",
            "password2": "DifferentPass123!"
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="test@example.com").exists())


class ProfileViewTests(TestCase):
    """Tests for profile view."""

    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123"
        )
        self.profile_url = reverse("users:profile")

    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_profile_view_displays_form(self):
        """Test that profile view displays form."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_profile_update(self):
        """Test updating profile information."""
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.post(self.profile_url, {
            "bio": "I'm a traveler",
            "city": "Paris"
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.bio, "I'm a traveler")
        self.assertEqual(profile.city, "Paris")

    def test_profile_auto_created(self):
        """Test that profile is auto-created on first access."""
        self.client.login(email="test@example.com", password="testpass123")
        self.client.get(self.profile_url)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
