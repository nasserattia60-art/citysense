"""
Community application forms.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import ReportFeedback


class FeedbackForm(forms.ModelForm):
    """
    Form for submitting report feedback.
    
    Users rate accuracy, usefulness, and clarity of reports
    on a 1-5 scale with optional comments.
    """
    class Meta:
        model = ReportFeedback
        fields = ["accuracy", "usefulness", "clarity", "comment"]
        widgets = {
            "accuracy": forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            "usefulness": forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            "clarity": forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={
                "rows": 4,
                "maxlength": 500,
                "placeholder": "What could we improve? (optional)"
            })
        }

    def clean_comment(self):
        """Validate comment length."""
        comment = self.cleaned_data.get("comment", "").strip()
        if len(comment) > 500:
            raise ValidationError("Comment must not exceed 500 characters.")
        return comment

    def clean(self):
        """Validate that at least one rating is provided."""
        cleaned_data = super().clean()
        accuracy = cleaned_data.get("accuracy")
        usefulness = cleaned_data.get("usefulness")
        clarity = cleaned_data.get("clarity")
        
        if not all([accuracy, usefulness, clarity]):
            raise ValidationError("Please provide ratings for all three categories.")
        
        return cleaned_data