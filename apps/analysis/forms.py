"""
Analysis application forms.
"""

from django import forms
from django.core.exceptions import ValidationError


class AnalysisForm(forms.Form):
    """
    Form for location search and analysis.
    
    Users enter an address or city name which is geocoded
    and sent to the AI analysis service.
    """
    address = forms.CharField(
        label="City or Address",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter a city or address to analyze",
            "autocomplete": "off",
        })
    )

    def clean_address(self):
        """Validate and clean address input."""
        address = self.cleaned_data.get("address", "").strip()
        
        if not address:
            raise ValidationError("Please enter a city or address.")
        
        if len(address) < 2:
            raise ValidationError("Address must be at least 2 characters long.")
        
        if len(address) > 255:
            raise ValidationError("Address is too long (max 255 characters).")
        
        # Check for injection attempts (very basic)
        dangerous_chars = ['<', '>', '{', '}', '|', '\\', '^', '`']
        if any(char in address for char in dangerous_chars):
            raise ValidationError("Address contains invalid characters.")
        
        return address
