from django.contrib import admin
from .models import WeaponModel, CraftingMaterial, CraftingRecipe, RecipeRequirement

@admin.register(WeaponModel)
class WeaponModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'weapon_type', 'damage', 'roll_keep', 'cost', 'flameblade_active')
    list_filter = ('weapon_type', 'attack_skill', 'parry_skill', 'flameblade_active')
    search_fields = ('name', 'description')
    list_editable = ('damage', 'roll_keep', 'cost', 'flameblade_active')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'weapon_type')
        }),
        ('Damage', {
            'fields': ('damage', 'roll_keep', 'damage_bonus')
        }),
        ('Skills', {
            'fields': ('attack_skill', 'parry_skill')
        }),
        ('Additional Info', {
            'fields': ('cost', 'requirements', 'flameblade_active')
        }),
        ('Evennia Object', {
            'fields': ('evennia_object',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            obj.sync_from_typeclass()
        return form

    def save_model(self, request, obj, form, change):
        obj.sync_from_typeclass()
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('evennia_object',)
        return ()

# You don't need to use admin.site.register() when using the @admin.register decorator


# tomorrow: make ArmorModelAdmin WITHOUT AI for the first few steps. You can do it.

class RecipeRequirementInline(admin.TabularInline):
    model = RecipeRequirement
    extra = 1

class WeaponModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'weapon_type', 'damage', 'quality_level', 'crafted_by')
    list_filter = ('weapon_type', 'quality_level')
    search_fields = ('name', 'description')

@admin.register(CraftingMaterial)
class CraftingMaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name', 'description')

@admin.register(CraftingRecipe)
class CraftingRecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'result_type', 'difficulty')
    list_filter = ('result_type', 'difficulty')
    search_fields = ('name', 'description')
    inlines = [RecipeRequirementInline]

@admin.register(RecipeRequirement)
class RecipeRequirementAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'material', 'amount')
    list_filter = ('recipe', 'material')
