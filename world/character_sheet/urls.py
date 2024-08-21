from django.urls import path
from . import views

app_name = 'charactersheet'

urlpatterns = [
    path('sheet/<int:object_id>/', views.character_sheet_view, name='character_sheet'),
    path('character/<int:object_id>/edit/', views.edit_character_sheet, name='edit_character_sheet'),
]