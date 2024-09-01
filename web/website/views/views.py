from django.views.generic import ListView
from evennia.objects.models import ObjectDB
from django.urls import reverse
from .utils import render_to_response, mush_to_html
from django.shortcuts import get_object_or_404, render
import logging
from world.character_sheet.models import CharacterSheet

logger = logging.getLogger(__name__)

class CustomCharacterListView(ListView):
    template_name = 'website/character_list.html'
    context_object_name = 'object_list'  # This matches the template's for loop

    def get_queryset(self):
        logger.info("CustomCharacterListView.get_queryset() called")
        characters = ObjectDB.objects.filter(db_typeclass_path__endswith='characters.Character')
        logger.info(f"Found {characters.count()} characters")
        character_data = []
        for char in characters:
            logger.info(f"Processing character: id={char.id}, name={char.name}")
            try:
                sheet, created = CharacterSheet.objects.get_or_create(db_object=char)
                character_data.append({
                    'name': char.name,
                    'web_get_detail_url': reverse('character', kwargs={'character': char.name, 'object_id': char.id}),
                    'full_name': sheet.full_name or char.db.full_name or char.name,
                    'nation': sheet.nationality or char.db.nationality or 'N/A',
                    'eye_color': sheet.eye_color or char.db.eye_color or 'N/A',
                    'hair_color': sheet.hair_color or char.db.hair_color or 'N/A',
                })
                logger.info(f"Successfully added character: {char.name}")
            except AttributeError as e:
                logger.error(f"Error processing character {char.id}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error processing character {char.id}: {str(e)}")
        logger.info(f"Returning {len(character_data)} characters")
        return character_data

    def render_to_response(self, context, **response_kwargs):
        return render_to_response(self.request, self.template_name, context)

def public_character_profile(request, character, object_id):
    character = get_object_or_404(ObjectDB, id=object_id)
    sheet, _ = CharacterSheet.objects.get_or_create(db_object=character)
    context = {
        'character': character,
        'sheet': sheet,
        'public_traits': {
            'Full Name': sheet.full_name or character.db.full_name or character.name,
            'Nation': sheet.nationality or character.db.nationality or 'N/A',
            'Eye Color': sheet.eye_color or character.db.eye_color or 'N/A',
            'Hair Color': sheet.hair_color or character.db.hair_color or 'N/A',
            'Description': mush_to_html(sheet.description) or mush_to_html(character.db.description) or 'N/A'
        },
        'biography': mush_to_html(sheet.biography) or mush_to_html(character.db.biography) or 'N/A',
        'personality': mush_to_html(sheet.personality) or mush_to_html(character.db.personality) or 'N/A',
    }
    return render_to_response(request, f'character/profile.html', context)