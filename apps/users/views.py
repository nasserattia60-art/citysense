"""
User authentication and profile management views.

Handles user registration, profile viewing and editing,
and integrates with Django's auth system.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm, ProfileForm
from django.contrib.auth.decorators import login_required
from .models import Profile
import logging

logger = logging.getLogger(__name__)


def register_view(request):
    """
    User registration view.
    
    GET: Display registration form
    POST: Create new user account
    
    On success, logs user in and redirects to home.
    On error, re-displays form with error messages.
    """
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"New user registered: {user.email}")
            return redirect("core:home")
        else:
            logger.debug(f"Registration failed: {form.errors}")
            if "username" in form.errors or "email" in form.errors:
                return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


@login_required
def profile_view(request):
    """
    User profile view - display and edit profile information.
    
    GET: Display user's profile
    POST: Update user's profile (bio, city, avatar)
    
    Automatically creates Profile if it doesn't exist.
    Only authenticated users can view/edit their own profile.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)

    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile
    )
    if form.is_valid():
        form.save()
        logger.info(f"Profile updated: {request.user.email}")
        return redirect("users:profile")

    context = {
        "form": form,
        "user": request.user,
        "profile": profile,
        "context": {
            "form": form,
            "user": request.user,
            "profile": profile,
        }
    }
    return render(request, "users/profile.html", context)
