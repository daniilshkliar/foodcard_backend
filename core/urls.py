from django.urls import path

from . import views


urlpatterns = [
    path('get_place/<slug:city>/<slug:title>/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
    path('get_places/', views.PlaceViewSet.as_view({'get': 'list'})),
    path('get_favorites/', views.FavoriteViewSet.as_view({'get': 'list'})),
    path('handle_favorite/<slug:place_id>/', views.FavoriteViewSet.as_view({'post': 'handle'})),
]