from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdventuringGuildListView.as_view(), name='guild_list'),
    path('<int:pk>/', views.AdventuringGuildDetailView.as_view(), name='guild_detail'),
    path('create/', views.AdventuringGuildCreateView.as_view(), name='guild_create'),
    path('<int:pk>/update/', views.AdventuringGuildUpdateView.as_view(), name='guild_update'),
    path('<int:pk>/delete/', views.AdventuringGuildDeleteView.as_view(), name='guild_delete'),
]