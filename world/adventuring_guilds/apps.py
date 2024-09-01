from django.apps import AppConfig


class AdventuringGuildsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'world.adventuring_guilds'

    def ready(self):
        import world.adventuring_guilds.signals
