from django.urls import path

from . import views


urlpatterns = [
    path('place/get/<slug:city>/<slug:title>/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
    path('place/get/all/', views.PlaceViewSet.as_view({'get': 'list'})),
    path('place/create/', views.PlaceViewSet.as_view({'post': 'create'})),
    path('place/update/<slug:pk>/', views.PlaceViewSet.as_view({'post': 'update'})),
    path('place/delete/<slug:pk>/', views.PlaceViewSet.as_view({'post': 'destroy'})),
    path('place/upload_image/<slug:pk>/', views.PlaceViewSet.as_view({'post': 'upload_image'})),
    path('place/delete_image/<slug:pk>/', views.PlaceViewSet.as_view({'post': 'delete_image'})),
    path('favorite/get/', views.FavoriteViewSet.as_view({'get': 'retrieve'})),
    path('favorite/handle/<slug:pk>/', views.FavoriteViewSet.as_view({'post': 'handle'})),
    path('panel/get/all/', views.ControlPanelViewSet.as_view({'get': 'list'})),
    path('panel/get/<slug:pk>/', views.ControlPanelViewSet.as_view({'get': 'retrieve'})),
    path('photo/get/<str:pk>/', views.get_photo),
]