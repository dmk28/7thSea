from django.contrib import admin
from .models import Nation, Stronghold

class StrongholdInline(admin.TabularInline):
    model = Stronghold
    extra = 1

@admin.register(Nation)
class NationAdmin(admin.ModelAdmin):
    list_display = ('name', 'population', 'capital', 'ruler')
    search_fields = ['name', 'capital', 'ruler']
    list_filter = ['government_type']
    inlines = [StrongholdInline]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return readonly_fields + ('get_characters_display',)

    def get_characters_display(self, obj):
        characters = obj.get_characters()
        return ", ".join(characters) if characters else "No characters"
    get_characters_display.short_description = "Characters from this nation"

@admin.register(Stronghold)
class StrongholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'nation', 'location', 'ruler')
    search_fields = ['name', 'location', 'ruler']
    list_filter = ['nation']