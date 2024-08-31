
from django import forms
from .models import CharacterSheet, Skill, Knack  # SwordsmanKnack #SorceryKnack,

class CharacterSheetForm(forms.ModelForm):
    class Meta:
        model = CharacterSheet
        fields = [
            'full_name', 'gender', 'nationality', 'hero_points', 'brawn', 'finesse', 'wits', 'resolve', 'panache',
            'flesh_wounds', 'dramatic_wounds', 'is_sorcerer', 'duelist_style', 'advantages', 'sorte_magic_effects'
        ]

    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    # sorcery_knacks = forms.ModelMultipleChoiceField(queryset=SorceryKnack.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    # swordsman_knacks = forms.ModelMultipleChoiceField(queryset=SwordsmanKnack.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['skills'].initial = self.instance.skills.all()
            self.fields['sorcery_knacks'].initial = self.instance.sorcery_knacks.all()
            self.fields['swordsman_knacks'].initial = self.instance.swordsman_knacks.all()
            
            if self.instance.nationality == "Eisen":
                self.fields['dracheneisen_slots'] = forms.JSONField(required=False)
                self.fields['dracheneisen_slots'].initial = self.instance.dracheneisen_slots

    def clean(self):
        cleaned_data = super().clean()
        nationality = cleaned_data.get('nationality')
        dracheneisen_slots = cleaned_data.get('dracheneisen_slots')

        if nationality != "Eisen" and dracheneisen_slots:
            del cleaned_data['dracheneisen_slots']

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

# @login_required
def edit_character_sheet(request, object_id):
    if not has_builder_permissions(request.user):
        raise PermissionDenied("You don't have permission to edit character sheets.")
    character = get_object_or_404(ObjectDB, id=object_id)
    sheet, created = CharacterSheet.objects.get_or_create(db_object=character)
    if request.method == 'POST':
        form = CharacterSheetForm(request.POST, instance=sheet)
        if form.is_valid():
            form.save()
            
            # Update the in-game character object
            char = sheet.db_object
            for field in form.cleaned_data:
                if field not in ['skills', 'sorcery_knacks', 'swordsman_knacks', 'dracheneisen_slots']:
                    setattr(char.db, field, form.cleaned_data[field])
            
            # Update skills, sorcery knacks, and swordsman knacks
            char.db.skills = sheet.get_skills_by_category()
            char.db.sorcery_knacks = {sk.name: sk.value for sk in sheet.sorcery_knacks.all()}
            char.db.swordsman_knacks = {sk.name: sk.value for sk in sheet.swordsman_knacks.all()}
            
            # Update Sorte magic effects and Dracheneisen slots
            char.db.sorte_magic_effects = form.cleaned_data['sorte_magic_effects']
            if sheet.nationality == "Eisen":
                char.db.dracheneisen_slots = form.cleaned_data.get('dracheneisen_slots', {})
            else:
                char.db.dracheneisen_slots = {}
            
            char.save()
            return redirect('character_sheet:character_sheet', object_id=object_id)
    else:
        form = CharacterSheetForm(instance=sheet)

    context = {
        'character': character,
        'sheet': sheet,
        'form': form,
    }
    return render(request, 'character_sheet/edit_character_sheet.html', context)