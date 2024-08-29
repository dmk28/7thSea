# urls.py
from django.urls import path
from . import views

app_name = 'crafts'

urlpatterns = [
    path('weapons/', views.weapon_list, name='weapon_list'),
    path('weapons/<int:weapon_id>/', views.weapon_detail, name='weapon_detail'),
    path('weapons/create/', views.weapon_create, name='weapon_create'),
    path('weapons/<int:weapon_id>/edit/', views.weapon_edit, name='weapon_edit'),
    path('weapons/<int:weapon_id>/delete/', views.weapon_delete, name='weapon_delete'),
]