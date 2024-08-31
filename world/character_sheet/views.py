from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from evennia.objects.models import ObjectDB
from evennia.accounts.models import AccountDB
from .models import CharacterSheet
from .forms import CharacterSheetForm

def has_builder_permissions(user):
    account = AccountDB.objects.get(id=user.id)
    return account.check_permstring("Builders") or account.check_permstring("Admin")

def character_sheet(request, object_id):
    character = get_object_or_404(ObjectDB, id=object_id)
    if not character.access(request.user, 'read'):
        raise PermissionDenied("You don't have permission to view this character sheet.")
    
    sheet, created = CharacterSheet.objects.get_or_create(db_object=character)
    if created or request.GET.get('refresh'):
        sheet.update_from_typeclass()
    
    form = CharacterSheetForm(instance=sheet)
    context = {
        'character': character,
        'sheet': sheet,
        'form': form,
        'skills': sheet.get_skills_by_category(),
        'can_edit': has_builder_permissions(request.user),
    }
    return render(request, 'character_sheet/character_sheet.html', context)

@login_required
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
                if field not in ['skills', 'sorcery_knacks', 'swordsman_knacks']:
                    setattr(char.db, field, form.cleaned_data[field])
            # Update skills, sorcery knacks, and swordsman knacks
            char.db.skills = sheet.get_skills_by_category()
            char.db.sorcery_knacks = {sk.name: sk.value for sk in sheet.sorcery_knacks.all()}
            char.db.swordsman_knacks = {sk.name: sk.value for sk in sheet.swordsman_knacks.all()}
            char.save()
            return redirect('character_sheet:character_sheet', object_id=object_id)
    else:
        form = CharacterSheetForm(instance=sheet)
    
    context = {
        'character': character,
        'sheet': sheet,
        'form': form,
        'skills': sheet.get_skills_by_category(),
    }
    return render(request, 'character_sheet/edit_character_sheet.html', context)

