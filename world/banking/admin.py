from django.contrib import admin
from world.banking.models import Bank, BankAccount, HoldingAccount, GuildAccount
from evennia.scripts.models import ScriptDB

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'guilders_balance', 'doubloons_balance')
    search_fields = ['name']

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_holder', 'bank', 'account_number', 'guilders_balance', 'doubloons_balance')
    list_filter = ('bank',)
    search_fields = ['account_holder__db_key', 'account_number']
    raw_id_fields = ('account_holder',)

@admin.register(HoldingAccount)
class HoldingAccountAdmin(admin.ModelAdmin):
    list_display = ('holding', 'bank', 'account_number', 'guilders_balance', 'doubloons_balance')
    list_filter = ('bank',)
    search_fields = ['holding__name', 'account_number']
    raw_id_fields = ('holding',)

@admin.register(GuildAccount)
class GuildAccountAdmin(admin.ModelAdmin):
    list_display = ('guild', 'bank', 'account_number', 'guilders_balance', 'doubloons_balance')
    list_filter = ('bank',)
    search_fields = ['guild__db_name', 'account_number']
    raw_id_fields = ('guild',)

class HoldingIncomeScriptProxy(ScriptDB):
    class Meta:
        proxy = True
        verbose_name = "Holding Income Script"
        verbose_name_plural = "Holding Income Scripts"

@admin.register(HoldingIncomeScriptProxy)
class HoldingIncomeScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'db_key', 'db_interval', 'db_repeats', 'db_start_delay', 'db_is_active')
    list_filter = ('db_is_active',)
    search_fields = ['db_key']
    fieldsets = (
        (None, {
            'fields': ('db_key', 'db_desc', 'db_interval', 'db_repeats', 'db_start_delay', 'db_is_active')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(db_typeclass_path__endswith='HoldingIncomeScript')