from django.urls import path

from . import views


urlpatterns = [
    path('get_place/<slug:city>/<slug:title>/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
    path('get_favorites/', views.FavoriteViewSet.as_view({'get': 'list'})),
    path('create_favorite/<slug:city>/<slug:title>/', views.FavoriteViewSet.as_view({'post': 'create'})),
    path('delete_favorite/<slug:city>/<slug:title>/', views.FavoriteViewSet.as_view({'post': 'destroy'})),
]