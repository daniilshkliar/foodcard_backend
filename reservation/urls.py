from django.urls import path

from . import views


urlpatterns = [
    path('create/<slug:pk>/', views.ReservationViewSet.as_view({'post': 'create'})),
    path('get/<slug:pk>/', views.ReservationViewSet.as_view({'get': 'list'})),
    # path('create/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
    # path('create/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
]