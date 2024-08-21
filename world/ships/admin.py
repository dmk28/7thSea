from django.contrib import admin
from .models import Ship, Modification, Flaw
from evennia.objects.models import ObjectDB

class ModificationInline(admin.TabularInline):
    model = Modification
    extra = 1

class FlawInline(admin.TabularInline):
    model = Flaw
    extra = 1

@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ('name', 'brawn', 'finesse', 'resolve', 'wits', 'panache', 'cargo', 'draft', 'captain')
    search_fields = ('name', 'captain__db_key')
    inlines = [ModificationInline, FlawInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "captain":
            kwargs["queryset"] = ObjectDB.objects.filter(db_typeclass_path__contains='Character')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)