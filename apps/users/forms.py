"""
User application forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, Profile


class RegisterForm(UserCreationForm):
    """
    User registration form.
    
    Creates a new User account with email and password.
    Validates password strength via Django's default validators.
    """
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get("email", "").lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email

    def clean_username(self):
        """Validate username."""
        username = self.cleaned_data.get("username", "").strip()
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if not username.replace("_", "").isalnum():
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        return username


class ProfileForm(forms.ModelForm):
    """
    User profile editing form.
    
    Allows users to update bio, city, and avatar.
    """
    class Meta:
        model = Profile
        fields = ["bio", "city", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "maxlength": 500,
                "placeholder": "Tell us about yourself (max 500 chars)"
            }),
            "city": forms.TextInput(attrs={
                "placeholder": "Your city",
                "maxlength": 100
            }),
        }

    def clean_bio(self):
        """Validate bio length."""
        bio = self.cleaned_data.get("bio", "").strip()
        if len(bio) > 500:
            raise ValidationError("Bio must not exceed 500 characters.")
        return bio

    def clean_city(self):
        """Validate city name."""
        city = self.cleaned_data.get("city", "").strip()
        if city and len(city) > 100:
            raise ValidationError("City name is too long.")
        return city

    def clean_avatar(self):
        """Validate avatar file."""
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            # Max 5MB
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError("Avatar file is too large (max 5MB).")
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if avatar.content_type not in allowed_types:
                raise ValidationError("Avatar must be a JPEG, PNG, or GIF image.")
        return avatar
