from evennia import default_cmds
from world.economy import CommodityMarket
import random

class CmdInvest(default_cmds.MuxCommand):
    """
    Handle all investment-related actions.

    Usage:
      invest/market
      invest/buy <company name> <amount>
      invest/sell <company name> <shares>
      invest/portfolio

    Switches:
      market - View the current commodity market status
      buy - Invest in a company
      sell - Sell shares of a company
      portfolio - View your current investments

    Examples:
      invest/market
      invest/buy "Noord Handels Maatschappij" 1000
      invest/sell "Royal Trade Company" 5
      invest/portfolio
    """

    key = "invest"
    aliases = ["investment"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        if not self.switches:
            self.caller.msg("You must use a switch with the invest command. See 'help invest' for options.")
            return

        # Ensure the market exists
        if not self.caller.ndb.market:
            self.caller.ndb.market = CommodityMarket()

        # Ensure the investments attribute exists
        if not self.caller.db.investments:
            self.caller.db.investments = {}

        switch = self.switches[0]

        if switch == "market":
            self.view_market()
        elif switch == "buy":
            self.buy_investment()
        elif switch == "sell":
            self.sell_investment()
        elif switch == "portfolio":
            self.view_portfolio()
        else:
            self.caller.msg(f"Invalid switch '{switch}'. See 'help invest' for options.")

    def view_market(self):
        market_status = self.caller.ndb.market.get_market_status()
        table = self.styled_table("Company", "Nation", "Commodity", "Price")
        for company, details in market_status.items():
            table.add_row(company, details['nation'], details['commodity'], f"{details['price']} guilders")
        self.caller.msg(table)

    def buy_investment(self):
        if not self.args or len(self.args.split()) < 2:
            self.caller.msg("Usage: invest/buy <company name> <amount>")
            return

        company_name = " ".join(self.args.split()[:-1])
        try:
            amount = int(self.args.split()[-1])
        except ValueError:
            self.caller.msg("The amount must be a number.")
            return

        if amount <= 0:
            self.caller.msg("You must invest a positive amount.")
            return

        if self.caller.db.money < amount:
            self.caller.msg("You don't have enough money for this investment.")
            return

        success_chance = self.calculate_success_chance()
        roll = random.randint(1, 100)

        if roll <= success_chance:
            result = self.caller.ndb.market.invest(company_name, amount)
            if result:
                shares, commodity, price = result
                self.caller.db.money -= shares * price
                
                if company_name in self.caller.db.investments:
                    self.caller.db.investments[company_name]["shares"] += shares
                else:
                    self.caller.db.investments[company_name] = {
                        "shares": shares,
                        "commodity": commodity,
                        "buy_price": price
                    }
                
                self.caller.msg(f"Investment successful! You bought {shares} shares of {commodity} at {price} guilders each.")
            else:
                self.caller.msg("Invalid company name or insufficient funds.")
        else:
            self.caller.msg("Your investment attempt failed. The market conditions were not favorable.")

    def sell_investment(self):
        if not self.args or len(self.args.split()) < 2:
            self.caller.msg("Usage: invest/sell <company name> <shares>")
            return

        company_name = " ".join(self.args.split()[:-1])
        try:
            shares_to_sell = int(self.args.split()[-1])
        except ValueError:
            self.caller.msg("The number of shares must be a number.")
            return

        if shares_to_sell <= 0:
            self.caller.msg("You must sell a positive number of shares.")
            return

        if company_name not in self.caller.db.investments:
            self.caller.msg(f"You don't have any investments in {company_name}.")
            return

        investment = self.caller.db.investments[company_name]
        if investment["shares"] < shares_to_sell:
            self.caller.msg(f"You only have {investment['shares']} shares in {company_name}.")
            return

        market_status = self.caller.ndb.market.get_market_status()
        if company_name not in market_status:
            self.caller.msg(f"Cannot find {company_name} in the current market. Please try again later.")
            return

        current_price = market_status[company_name]["price"]
        sell_value = shares_to_sell * current_price

        self.caller.db.money += sell_value
        investment["shares"] -= shares_to_sell

        if investment["shares"] == 0:
            del self.caller.db.investments[company_name]
        
        self.caller.msg(f"You sold {shares_to_sell} shares of {company_name} for {sell_value} guilders.")

    def view_portfolio(self):
        if not self.caller.db.investments:
            self.caller.msg("You don't have any investments.")
            return

        market_status = self.caller.ndb.market.get_market_status()
        table = self.styled_table("Company", "Shares", "Buy Price", "Current Price", "Profit/Loss")

        for company, investment in self.caller.db.investments.items():
            shares = investment["shares"]
            buy_price = investment["buy_price"]
            current_price = market_status[company]["price"] if company in market_status else "N/A"
            
            if current_price != "N/A":
                profit_loss = (current_price - buy_price) * shares
                profit_loss_str = f"{profit_loss:+d} guilders"
            else:
                profit_loss_str = "N/A"

            table.add_row(company, shares, f"{buy_price} guilders", 
                          f"{current_price} guilders" if current_price != "N/A" else current_price, 
                          profit_loss_str)

        self.caller.msg(table)

    def calculate_success_chance(self):
        base_chance = 50  # Start with a 50% base chance

        # Add bonuses from skills
        skills = self.caller.db.skills
        steward_bonus = skills.get('Professional', {}).get('Steward', {}).get('Basic', 0) * 5
        commerce_bonus = skills.get('Professional', {}).get('Commerce', {}).get('Basic', 0) * 5
        accounting_bonus = skills.get('Professional', {}).get('Accounting', {}).get('Basic', 0) * 5

        skill_bonus = min(steward_bonus + commerce_bonus + accounting_bonus, 35)  # Cap at 35%

        # Check for Indomitable Will
        if 'Indomitable Will' in self.caller.db.advantages:
            base_chance += 5

        # Check for Foul Weather Jack
        if 'Foul Weather Jack' in self.caller.db.advantages:
            if random.choice([True, False]):  # 50% chance
                base_chance += 10
            else:
                base_chance -= 10

        final_chance = base_chance + skill_bonus
        final_chance = max(0, min(final_chance, 100))  # Ensure the chance is between 0 and 100

        return final_chance