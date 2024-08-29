# custom_fields.py
from django import forms
from evennia.objects.models import ObjectDB
from django.utils.safestring import mark_safe
from .utils import get_weapon_objects

class WeaponObjectWidget(forms.Select):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs)
        output = [f'<select name="{name}"']
        output.extend(f' {k}="{v}"' for k, v in final_attrs.items())
        output.append('>')
        options = self.render_options([value])
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe('\n'.join(output))

    def render_options(self, selected_choices):
        weapon_ids = get_weapon_objects()
        weapons = ObjectDB.objects.filter(id__in=weapon_ids)
        output = []
        for weapon in weapons:
            option_value = str(weapon.id)
            option_label = f"{weapon.name} ({weapon.db_typeclass_path.split('.')[-1]})"
            if option_value in selected_choices:
                output.append(f'<option value="{option_value}" selected>{option_label}</option>')
            else:
                output.append(f'<option value="{option_value}">{option_label}</option>')
        return '\n'.join(output)

class WeaponObjectFormField(forms.ModelChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = ObjectDB.objects.filter(id__in=get_weapon_objects())
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.db_typeclass_path.split('.')[-1]})"