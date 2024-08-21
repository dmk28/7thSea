from django.shortcuts import render, redirect, get_object_or_404
from evennia.utils.create import create_object
from .forms import ShipForm, ModificationForm, FlawForm
from .models import Ship
from django.forms import formset_factory

def create_ship(request):
    ModificationFormSet = formset_factory(ModificationForm, extra=1)
    FlawFormSet = formset_factory(FlawForm, extra=1)

    if request.method == 'POST':
        form = ShipForm(request.POST)
        modification_formset = ModificationFormSet(request.POST, prefix='modifications')
        flaw_formset = FlawFormSet(request.POST, prefix='flaws')

        if form.is_valid() and modification_formset.is_valid() and flaw_formset.is_valid():
            ship = form.save()
            
            for mod_form in modification_formset:
                if mod_form.cleaned_data:
                    Modification.objects.create(ship=ship, **mod_form.cleaned_data)

            for flaw_form in flaw_formset:
                if flaw_form.cleaned_data:
                    Flaw.objects.create(ship=ship, **flaw_form.cleaned_data)

            evennia_object = create_object("ships.typeclasses.Ship", key=ship.name)
            ship.evennia_object = evennia_object
            ship.save()

            return redirect('ship_detail', ship_id=ship.id)
    else:
        form = ShipForm()
        modification_formset = ModificationFormSet(prefix='modifications')
        flaw_formset = FlawFormSet(prefix='flaws')

    return render(request, 'ships/create_ship.html', {
        'form': form,
        'modification_formset': modification_formset,
        'flaw_formset': flaw_formset
    })

def ship_detail(request, ship_id):
    ship = get_object_or_404(Ship, id=ship_id)
    return render(request, 'ships/ship_detail.html', {'ship': ship})