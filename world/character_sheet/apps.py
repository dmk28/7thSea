from django.apps import AppConfig

class CharacterSheetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "world.character_sheet"

    def ready(self):
        from . import signals