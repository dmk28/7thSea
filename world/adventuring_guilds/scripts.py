from evennia import DefaultScript
from evennia.utils import logger
from .models import AdventuringGuild

class IncomeCollectionScript(DefaultScript):
    """A script to periodically collect income from all guild holdings."""
    
    def at_script_creation(self):
        self.key = "income_collection_script"
        self.desc = "Collects income from guild holdings"
        self.interval = 3600 * 24 * 7  # Run every week (adjust as needed)
        self.persistent = True

    def at_repeat(self):
        logger.log_info("Starting income collection for all guilds.")
        for guild in AdventuringGuild.objects.all():
            try:
                guilders, doubloons = guild.collect_all_income()
                logger.log_info(f"Collected {guilders} guilders and {doubloons} doubloons for {guild.db_name}")
            except Exception as e:
                logger.log_err(f"Error collecting income for guild {guild.db_name}: {str(e)}")
        logger.log_info("Finished income collection for all guilds.")
