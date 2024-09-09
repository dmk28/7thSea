from django.contrib import admin
from .models import AdventuringGuild, Holding, GuildRank, GuildMembership

class GuildRankInline(admin.TabularInline):
    model = GuildRank
    extra = 1

class GuildMembershipInline(admin.TabularInline):
    model = GuildMembership
    extra = 1
    raw_id_fields = ('character',)

@admin.register(AdventuringGuild)
class AdventuringGuildAdmin(admin.ModelAdmin):
    list_display = ('db_name', 'founder', 'founding_date', 'member_count', 'get_holdings')
    search_fields = ('db_name', 'db_founder__db_key')
    inlines = [GuildRankInline, GuildMembershipInline]

    def founder(self, obj):
        return obj.db_founder.db_key if obj.db_founder else 'N/A'

    def founding_date(self, obj):
        return obj.db_founding_date

    def member_count(self, obj):
        return obj.db_members.count()

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

@admin.register(GuildRank)
class GuildRankAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'guild')
    list_filter = ('guild',)
    search_fields = ('name', 'guild__db_name')

@admin.register(GuildMembership)
class GuildMembershipAdmin(admin.ModelAdmin):
    list_display = ('character', 'guild', 'rank', 'join_date')
    list_filter = ('guild', 'rank')
    search_fields = ('character__db_key', 'guild__db_name', 'rank__name')
    raw_id_fields = ('character',)