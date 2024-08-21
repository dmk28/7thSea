from django.contrib import admin
from .models import AdventuringGuild, Holding

@admin.register(AdventuringGuild)
class AdventuringGuildAdmin(admin.ModelAdmin):
    list_display = ('name', 'founder', 'founding_date')
    search_fields = ('name', 'founder')

    def get_holdings(self, obj):
        return ", ".join([holding.name for holding in obj.holdings.all()])
    get_holdings.short_description = 'Holdings'


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ('name', 'custom_name', 'holding_type', 'level', 'income_type', 'owning_guild', 'current_income_rate')
    list_filter = ('holding_type', 'income_type', 'owning_guild')
    search_fields = ('name', 'custom_name', 'owning_guild__db_name')
    readonly_fields = ('name', 'description', 'base_income', 'upgrade_cost', 'upgrade_multiplier', 'current_income_rate', 'next_upgrade_cost')

    def current_income_rate(self, obj):
        return obj.calculate_income_rate()
    current_income_rate.short_description = 'Current Income Rate'

    def next_upgrade_cost(self, obj):
        return obj.get_upgrade_cost()
    next_upgrade_cost.short_description = 'Next Upgrade Cost'

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ('holding_type', 'custom_name', 'custom_description', 'level', 'income_type', 'owning_guild')
            }),
            ('Holding Information', {
                'fields': ('name', 'description', 'base_income', 'upgrade_cost', 'upgrade_multiplier')
            }),
            ('Current Status', {
                'fields': ('current_income_rate', 'next_upgrade_cost', 'specialization', 'staff', 'events')
            }),
        ]
        return fieldsets

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "holding_type":
            kwargs['choices'] = Holding.HOLDING_TYPE_CHOICES
        return super().formfield_for_choice_field(db_field, request, **kwargs)