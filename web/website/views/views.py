# from django.views.generic import ListView
# from evennia.objects.models import ObjectDB
# from  .utils import render_to_response
# import logging

# logger = logging.getLogger(__name__)

# class CustomCharacterListView(ListView):
#     template_name = 'website/character_list.html'
#     context_object_name = 'characters'

#     def get_queryset(self):
#         logger.info("CustomCharacterListView.get_queryset() called")
        
#         characters = ObjectDB.objects.filter(db_typeclass_path__contains='characters.Character')
#         logger.info(f"Found {characters.count()} characters")
        
#         character_data = []
#         for char in characters:
#             logger.info(f"Processing character: id={char.id}, name={char.name}")
#             try:
#                 character_data.append({
#                     'name': char.name,
#                     'url': char.web_get_detail_url(),
#                     'full_name': char.db.full_name or 'N/A',
#                     'nationality': char.db.nationality or 'N/A',
#                     'gender': char.db.gender or 'N/A',
#                 })
#                 logger.info(f"Successfully added character: {char.name}")
#             except AttributeError as e:
#                 logger.error(f"Error processing character {char.id}: {str(e)}")
#             except Exception as e:
#                 logger.error(f"Unexpected error processing character {char.id}: {str(e)}")

#         logger.info(f"Returning {len(character_data)} characters")
#         return character_data

#     def render_to_response(self, context, **response_kwargs):
#         return render_to_response(self.request, self.template_name, context)