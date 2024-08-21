from django import forms
from .models import AdventuringGuild

class AdventuringGuildForm(forms.ModelForm):
    class Meta:
        model = AdventuringGuild
        fields = ['name', 'founder', 'founding_date', 'history', 'recent_history', 'members']
        widgets = {
            'members': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_members(self):
        members = self.cleaned_data['members']
        try:
            import json
            json.loads(members)
        except json.JSONDecodeError:
            raise forms.ValidationError("Members must be a valid JSON")
        return members