from django.urls import path

from . import views


urlpatterns = [
    path('place/get/<slug:city>/<slug:title>/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
    path('place/get/all/', views.PlaceViewSet.as_view({'get': 'list'})),
    path('favorite/handle/<slug:place_id>/', views.FavoriteViewSet.as_view({'post': 'handle'})),
    path('favorite/get/all/', views.FavoriteViewSet.as_view({'get': 'list'})),
]