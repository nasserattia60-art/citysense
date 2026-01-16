"""
User application models.

Custom user model and extended profile.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model with email-based authentication.
    
    Uses email as the primary identifier instead of username.
    """
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "Users"


class Profile(models.Model):
    """
    Extended user profile for optional information.
    
    One-to-one relationship with User model.
    Auto-created on first profile access.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, help_text="User bio or about section")
    city = models.CharField(max_length=100, blank=True, help_text="Current city of residence")
    avatar = models.ImageField(upload_to="avatars/", blank=True, help_text="Profile picture")

    def __str__(self):
        return f"{self.user.email} Profile"

    class Meta:
        verbose_name_plural = "Profiles"
