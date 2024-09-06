from django.contrib import admin
from world.commodity_market.models import Commodity, Company, Investment, GuildInvestment, Market

@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price')
    search_fields = ('name',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'nation', 'commodity', 'current_price', 'last_updated')
    list_filter = ('nation', 'commodity')
    search_fields = ('name', 'nation__name', 'commodity__name')

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('character', 'company', 'shares', 'buy_price', 'date_invested')
    list_filter = ('company', 'date_invested')
    search_fields = ('character__db_key', 'company__name')

@admin.register(GuildInvestment)
class GuildInvestmentAdmin(admin.ModelAdmin):
    list_display = ('guild', 'company', 'shares', 'buy_price', 'date_invested')
    list_filter = ('company', 'date_invested')
    search_fields = ('guild__db_name', 'company__name')

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('last_update',)

    def has_add_permission(self, request):
        # Prevent creating multiple Market instances
        return not Market.objects.exists()

# If you want to customize the admin site header and title
admin.site.site_header = "Commodity Market Administration"
admin.site.site_title = "Commodity Market Admin Portal"
admin.site.index_title = "Welcome to Commodity Market Admin Portal"