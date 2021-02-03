from django.urls import path

from . import views


urlpatterns = [
    path('get_by_user/', views.ReservationViewSet.as_view({'get': 'list_by_user'})),
    path('get_by_place/<slug:pk>/', views.ReservationViewSet.as_view({'post': 'list_by_place'})),
    path('create/<slug:pk>/', views.ReservationViewSet.as_view({'post': 'create'})),
    path('update/<slug:pk>/', views.ReservationViewSet.as_view({'post': 'update'})),
    path('delete/<slug:pk>/', views.ReservationViewSet.as_view({'post': 'destroy'})),
]