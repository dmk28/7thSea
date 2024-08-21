from django.urls import path
from . import views

urlpatterns = [
    # ... other patterns ...
    path('create/', views.create_ship, name='create_ship'),
    path('<int:ship_id>/', views.ship_detail, name='ship_detail'),
]