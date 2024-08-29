from django import forms
from .models import WeaponModel

class WeaponForm(forms.ModelForm):
    class Meta:
        model = WeaponModel
        fields = ['name', 'description', 'weapon_type', 'damage', 'roll_keep',
                  'attack_skill', 'parry_skill', 'damage_bonus', 'cost', 'weight',
                  'requirements', 'flameblade_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_requirements(self):
        requirements = self.cleaned_data['requirements']
        # You might want to add custom validation for the JSON field here
        return requirements