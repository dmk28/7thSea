from django.urls import path
from . import views

app_name = 'character_sheet'

urlpatterns = [
    path('<int:object_id>/', views.character_sheet, name='character_sheet'),
    path('<int:object_id>/edit/', views.edit_character_sheet, name='edit_character_sheet'),
]