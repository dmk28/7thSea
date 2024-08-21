from django.contrib import admin
from .models import CharacterSheet, Skill, Knack, SwordsmanSchool, Sorcery, KnackValue, Advantage, CharacterAdvantage

class KnackValueInline(admin.TabularInline):
    model = KnackValue
    extra = 1

class CharacterAdvantageInline(admin.TabularInline):
    model = CharacterAdvantage
    extra = 1

@admin.register(CharacterSheet)
class CharacterSheetAdmin(admin.ModelAdmin):
    list_display = ('db_object', 'full_name', 'nationality', 'hero_points', 'eye_color', 'hair_color', 'skin_hue')
    list_filter = ('nationality', 'is_sorcerer', 'approved')
    search_fields = ('full_name', 'db_object__db_key')
    filter_horizontal = ('skills', 'swordsman_schools', 'sorceries')
    fieldsets = (
        ('Basic Info', {
            'fields': ('db_object', 'full_name', 'gender', 'nationality', 'hero_points', 'eye_color', 'hair_color', 'skin_hue')
        }),
        ('Traits', {
            'fields': ('brawn', 'finesse', 'wits', 'resolve', 'panache')
        }),
        ('Combat', {
            'fields': ('flesh_wounds', 'dramatic_wounds', 'duelist_style')
        }),
        ('Sorcery', {
            'fields': ('is_sorcerer', 'sorceries')
        }),
        ('Skills and Schools', {
            'fields': ('skills', 'swordsman_schools')
        }),
        ('Description', {
            'fields': ('description', 'personality', 'biography')
        }),
        ('Other', {
            'fields': ('money_guilders', 'money_doubloons', 'sorte_magic_effects', 'approved', 'unconscious', 'eisen_bought', 'dracheneisen_slots', 'armor_soak_keep', 'move_dice', 'xp')
        }),
    )
    inlines = [KnackValueInline, CharacterAdvantageInline]

@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    search_fields = ('name', 'description')

    def cost_display(self, obj):
        if isinstance(obj.cost, list):
            return f"{min(obj.cost)}-{max(obj.cost)}"
        return str(obj.cost)
    cost_display.short_description = 'Cost'

@admin.register(CharacterAdvantage)
class CharacterAdvantageAdmin(admin.ModelAdmin):
    list_display = ('character_sheet', 'advantage', 'level')
    list_filter = ('advantage', 'level')
    search_fields = ('character_sheet__full_name', 'advantage__name')

admin.site.register(Skill)
admin.site.register(Knack)
admin.site.register(SwordsmanSchool)
admin.site.register(Sorcery)