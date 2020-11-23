from django.urls import path

from . import views


urlpatterns = [
    path('get_place/<title>/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
]