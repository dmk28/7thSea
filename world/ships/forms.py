from django import forms
from .models import Ship, Modification, Flaw
from evennia.objects.models import ObjectDB

class ShipForm(forms.ModelForm):
    captain = forms.ModelChoiceField(queryset=ObjectDB.objects.filter(db_typeclass_path__contains='Character'), required=False)

    class Meta:
        model = Ship
        fields = ['name', 'brawn', 'finesse', 'resolve', 'wits', 'panache', 'cargo', 'draft', 'captain']

    def clean(self):
        cleaned_data = super().clean()
        total_attributes = sum(cleaned_data.get(attr, 0) for attr in ['brawn', 'finesse', 'resolve', 'wits', 'panache'])
        if total_attributes > 15:
            raise forms.ValidationError("The sum of all attributes cannot exceed 15.")
        return cleaned_data

class ModificationForm(forms.ModelForm):
    class Meta:
        model = Modification
        fields = ['name']

class FlawForm(forms.ModelForm):
    class Meta:
        model = Flaw
        fields = ['name']