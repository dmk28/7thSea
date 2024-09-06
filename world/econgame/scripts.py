from evennia import DefaultScript
from django.utils import timezone
from datetime import timedelta
import random
from world.commodity_market.models import Commodity, Company, Investment, GuildInvestment, Market

class CommodityMarketScript(DefaultScript):
    def at_script_creation(self):
        self.key = "commodity_market"
        self.desc = "Manages the commodity market"
        self.interval = 60 * 60 * 24  # 24 hours in seconds
        self.persistent = True

    def at_repeat(self):
        self.update_market()

    def update_market(self):
        market = Market.get_or_create()
        if timezone.now() - market.last_update < timedelta(days=1):
            return  # Market was updated less than a day ago

        for company in Company.objects.all():
            base_price = company.commodity.base_price
            price_fluctuation = random.uniform(0.8, 1.2)
            company.current_price = int(base_price * price_fluctuation)
            company.save()

        market.save()  # This will update the last_update field

    def get_market_status(self):
        self.update_market()
        return {company.name: {
            "commodity": company.commodity.name,
            "nation": company.nation.name,
            "price": company.current_price
        } for company in Company.objects.all()}

    def invest(self, investor, company_name, amount):
        try:
            company = Company.objects.get(name=company_name)
            shares = amount // company.current_price
            if shares > 0:
                if isinstance(investor, AdventuringGuild):
                    investment, created = GuildInvestment.objects.get_or_create(
                        guild=investor,
                        company=company,
                        defaults={'shares': 0, 'buy_price': company.current_price}
                    )
                else:
                    investment, created = Investment.objects.get_or_create(
                        character=investor,
                        company=company,
                        defaults={'shares': 0, 'buy_price': company.current_price}
                    )
                investment.shares += shares
                investment.save()
                return shares, company.commodity.name, company.current_price
        except Company.DoesNotExist:
            pass
        return None

    # Add methods for selling investments, checking portfolio, etc.