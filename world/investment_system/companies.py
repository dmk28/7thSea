from evennia import DefaultScript
import random
from datetime import datetime, timedelta

# Commodities and their base prices in guilders
COMMODITIES = {
    "Spices": 500, "Silk": 400, "Tea": 300, "Coffee": 250,
    "Sugar": 200, "Tobacco": 180, "Cotton": 150, "Indigo": 120,
    "Wool": 100, "Timber": 80, "Wine": 70, "Grain": 50,
    "Fish": 40, "Salt": 30,
}

# Company name components for different nations
COMPANY_NAMES = {
    "Vendel": {
        "prefixes": ["Noord", "Zuid", "Oost", "West", "Groot", "Klein", "Nieuw"],
        "core": ["Handels", "Koop", "Zee", "Vaart", "Goederen", "Waren"],
        "suffixes": ["Maatschappij", "Compagnie", "Vereniging", "Gilde"],
    },
    "Avalon": {
        "prefixes": ["Royal", "Crown", "Imperial", "Grand", "Great", "New"],
        "core": ["Trade", "Merchant", "Sea", "Ocean", "Goods", "Wares"],
        "suffixes": ["Company", "Corporation", "Association", "Guild"],
    },
    "Eisen": {
        "prefixes": ["Nord", "Süd", "Ost", "West", "Groß", "Klein", "Neu"],
        "core": ["Handels", "Kauf", "See", "Waren", "Güter"],
        "suffixes": ["Gesellschaft", "Kompanie", "Verein", "Gilde"],
    },
    "Vodacce": {
        "prefixes": ["Nord", "Sud", "Est", "Ovest", "Grande", "Piccolo", "Nuovo"],
        "core": ["Commercio", "Mercante", "Mare", "Merci", "Beni"],
        "suffixes": ["Compagnia", "Corporazione", "Associazione", "Gilda"],
    },
    "Castille": {
        "prefixes": ["Norte", "Sur", "Este", "Oeste", "Gran", "Pequeño", "Nuevo"],
        "core": ["Comercio", "Mercader", "Mar", "Océano", "Mercancías", "Bienes"],
        "suffixes": ["Compañía", "Corporación", "Asociación", "Gremio"],
    },
    "Montaigne": {
        "prefixes": ["Nord", "Sud", "Est", "Ouest", "Grand", "Petit", "Nouveau"],
        "core": ["Commerce", "Marchand", "Mer", "Océan", "Marchandises", "Biens"],
        "suffixes": ["Compagnie", "Corporation", "Association", "Guilde"],
    },
}

class CommodityMarketScript(DefaultScript):
    """
    This script manages the commodity market for the game.
    """

    def at_script_creation(self):
        self.key = "commodity_market"
        self.desc = "Manages the commodity market"
        self.interval = 60 * 60 * 24  # 24 hours in seconds
        self.persistent = True
        self.db.companies = {}
        self.db.last_update = None

    def generate_company_name(self, nation):
        name_parts = COMPANY_NAMES[nation]
        return " ".join([
            random.choice(name_parts["prefixes"]),
            random.choice(name_parts["core"]),
            random.choice(name_parts["suffixes"])
        ])

    def update_market(self):
        current_time = datetime.now()
        if self.db.last_update is None or current_time - self.db.last_update > timedelta(days=1):
            self.db.companies = {}
            for commodity, base_price in COMMODITIES.items():
                nation = random.choice(list(COMPANY_NAMES.keys()))
                company_name = self.generate_company_name(nation)
                price_fluctuation = random.uniform(0.8, 1.2)
                current_price = int(base_price * price_fluctuation)
                self.db.companies[company_name] = {
                    "commodity": commodity,
                    "nation": nation,
                    "price": current_price
                }
            self.db.last_update = current_time

    def at_repeat(self):
        """
        This is called every self.interval seconds.
        """
        self.update_market()

    def get_market_status(self):
        self.update_market()
        return self.db.companies

    def invest(self, company_name, amount):
        self.update_market()
        if company_name in self.db.companies:
            company = self.db.companies[company_name]
            shares = amount // company["price"]
            return shares, company["commodity"], company["price"]
        return None

# To create and start the script:
# from evennia import create_script
# create_script("typeclasses.scripts.CommodityMarketScript")