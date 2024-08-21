from django.urls import path
from .views import CustomCharacterListView  # Import your new view

urlpatterns = [
    # ... other URL patterns ...
    # path('characters/', CustomCharacterListView.as_view(), name='character_list'),
    
    # ... other URL patterns ...
]