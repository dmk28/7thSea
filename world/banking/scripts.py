from evennia import DefaultScript
from evennia.utils.create import create_script
from world.adventuring_guilds.models import AdventuringGuild
from world.banking.models import Bank, GuildAccount, HoldingAccount

class HoldingIncomeScript(DefaultScript):
    """
    This script runs periodically to collect income from holdings
    and deposit it into the guild's bank account.
    """
    def at_script_creation(self):
        self.key = "holding_income_collector"
        self.desc = "Collects income from holdings and deposits into guild bank accounts"
        self.interval = 86400  # Run daily (24 hours * 60 minutes * 60 seconds)
        self.persistent = True

    def at_repeat(self):
        """
        This is called every self.interval seconds.
        """
        guilds = AdventuringGuild.objects.all()
        for guild in guilds:
            total_guilders, total_doubloons = guild.collect_all_income()

            # Find or create a bank account for the guild
            bank = Bank.objects.first()  # Assuming there's at least one bank
            if bank:
                guild_account, created = GuildAccount.objects.get_or_create(
                    guild=guild,
                    bank=bank,
                    defaults={'account_number': f"G-{guild.id}-{bank.id}"}
                )

                # Deposit the collected income into the guild's bank account
                guild_account.guilders_balance += total_guilders
                guild_account.doubloons_balance += total_doubloons
                guild_account.save()

                # Update or create HoldingAccounts
                for holding in guild.get_holdings():
                    holding_account, created = HoldingAccount.objects.get_or_create(
                        guild_account=guild_account,
                        holding=holding,
                        defaults={'account_number': f"H-{holding.id}-{guild_account.id}"}
                    )
                    # You might want to update holding_account balances here if needed

                # Notify the guild (you might want to implement a notification system)
                guild_members = guild.db_members.all()
                for member in guild_members:
                    if member.has_account:
                        member.msg(f"Your guild '{guild.db_name}' has collected {total_guilders} guilders and {total_doubloons} doubloons from its holdings.")
            else:
                print("No bank found. Unable to process guild income.")

        self.logger.info("Holding income collection completed.")

def start_holding_income_script():
    """
    Function to start the HoldingIncomeScript
    """
    try:
        script = create_script(HoldingIncomeScript)
        if script:
            print("HoldingIncomeScript started successfully.")
        else:
            print("Failed to start HoldingIncomeScript.")
    except Exception as e:
        print(f"Error starting HoldingIncomeScript: {str(e)}")