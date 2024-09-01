"""
This reroutes from an URL to a python view-function/class.
The main web/urls.py includes these routes for all urls (the root of the url)
so it can reroute to all website pages.
"""
from django.urls import path, include
from evennia.web.website.urls import urlpatterns as evennia_website_urlpatterns
from .views.views import CustomCharacterListView, public_character_profile, NationListView, NationDetailView, WorldMapView

# add patterns here
urlpatterns = [
    # path("url-pattern", imported_python_view),
    # path("url-pattern", imported_python_view),
    path('characters/', include([
        path('', CustomCharacterListView.as_view(), name='character_list'),
        path('detail/<str:character>/<int:object_id>/', public_character_profile, name='character'),
    ])),
    # add any extra urls here:
    # path("mypath/", include("path.to.my.urls.file")),
    path('ships/', include('world.ships.urls')),
    path('nations/', include([
        path('', NationListView.as_view(), name='nation_list'),  # This is the main nations list view
        path('detail/<str:nation>/<int:pk>/', NationDetailView.as_view(), name='nation_detail'),
        path('map/', WorldMapView.as_view(), name='world_map'),
    ])),
]
# read by Django
urlpatterns = urlpatterns + evennia_website_urlpatterns