from django.urls import path

from . import views


urlpatterns = [
    path('get_place/<slug:city>/<slug:title>/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
]