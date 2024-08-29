# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import WeaponModel, CraftingMaterial, CraftingRecipe
from .forms import WeaponForm



class WeaponListView(ListView):
    model = WeaponModel
    template_name = 'crafting/weapon_list.html'
    context_object_name = 'weapons'

class WeaponDetailView(DetailView):
    model = WeaponModel
    template_name = 'crafting/weapon_detail.html'
    context_object_name = 'weapon'

class MaterialListView(ListView):
    model = CraftingMaterial
    template_name = 'crafting/material_list.html'
    context_object_name = 'materials'

class MaterialDetailView(DetailView):
    model = CraftingMaterial
    template_name = 'crafting/material_detail.html'
    context_object_name = 'material'

class RecipeListView(ListView):
    model = CraftingRecipe
    template_name = 'crafting/recipe_list.html'
    context_object_name = 'recipes'

class RecipeDetailView(DetailView):
    model = CraftingRecipe
    template_name = 'crafting/recipe_detail.html'
    context_object_name = 'recipe'


@login_required
def weapon_list(request):
    weapons = WeaponModel.objects.all()
    return render(request, 'weapons/weapon_list.html', {'weapons': weapons})

@login_required
def weapon_detail(request, weapon_id):
    weapon = get_object_or_404(WeaponModel, id=weapon_id)
    return render(request, 'weapons/weapon_detail.html', {'weapon': weapon})

@login_required
def weapon_create(request):
    if request.method == 'POST':
        form = WeaponForm(request.POST)
        if form.is_valid():
            weapon = form.save()
            messages.success(request, f'Weapon "{weapon.name}" created successfully.')
            return redirect('weapon_detail', weapon_id=weapon.id)
    else:
        form = WeaponForm()
    return render(request, 'weapons/weapon_form.html', {'form': form, 'action': 'Create'})

@login_required
def weapon_edit(request, weapon_id):
    weapon = get_object_or_404(WeaponModel, id=weapon_id)
    if request.method == 'POST':
        form = WeaponForm(request.POST, instance=weapon)
        if form.is_valid():
            weapon = form.save()
            messages.success(request, f'Weapon "{weapon.name}" updated successfully.')
            return redirect('weapon_detail', weapon_id=weapon.id)
    else:
        form = WeaponForm(instance=weapon)
    return render(request, 'weapons/weapon_form.html', {'form': form, 'action': 'Edit'})

@login_required
def weapon_delete(request, weapon_id):
    weapon = get_object_or_404(WeaponModel, id=weapon_id)
    if request.method == 'POST':
        weapon_name = weapon.name
        weapon.delete()
        messages.success(request, f'Weapon "{weapon_name}" deleted successfully.')
        return redirect('weapon_list')
    return render(request, 'weapons/weapon_confirm_delete.html', {'weapon': weapon})