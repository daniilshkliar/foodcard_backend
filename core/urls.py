from django.urls import path

from . import views


urlpatterns = [
    path('place/get/<slug:city>/<slug:title>/', views.PlaceViewSet.as_view({'get': 'retrieve'})),
    path('place/get/all/', views.PlaceViewSet.as_view({'get': 'list'})),
    path('place/create/', views.PlaceViewSet.as_view({'post': 'create'})),
    path('place/update/<slug:pk>/', views.PlaceViewSet.as_view({'post': 'update'})),
    path('place/delete/<slug:pk>/', views.PlaceViewSet.as_view({'post': 'destroy'})),
    path('favorite/get/all/', views.FavoriteViewSet.as_view({'get': 'list'})),
    path('favorite/handle/<slug:pk>/', views.FavoriteViewSet.as_view({'post': 'handle'})),
    path('category/get/', views.CategoryViewSet.as_view({'get': 'list'})),
    path('category/create/', views.CategoryViewSet.as_view({'post': 'create'})),
    path('category/update/<slug:pk>/', views.CategoryViewSet.as_view({'post': 'update'})),
    path('category/delete/<slug:pk>/', views.CategoryViewSet.as_view({'post': 'destroy'})),
    path('cuisine/get/', views.CuisineViewSet.as_view({'get': 'list'})),
    path('cuisine/create/', views.CuisineViewSet.as_view({'post': 'create'})),
    path('cuisine/update/<slug:pk>/', views.CuisineViewSet.as_view({'post': 'update'})),
    path('cuisine/delete/<slug:pk>/', views.CuisineViewSet.as_view({'post': 'destroy'})),
    path('additional_service/get/', views.AdditionalServiceViewSet.as_view({'get': 'list'})),
    path('additional_service/create/', views.AdditionalServiceViewSet.as_view({'post': 'create'})),
    path('additional_service/update/<slug:pk>/', views.AdditionalServiceViewSet.as_view({'post': 'update'})),
    path('additional_service/delete/<slug:pk>/', views.AdditionalServiceViewSet.as_view({'post': 'destroy'})),
]