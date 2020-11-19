from django.urls import path

from . import views


urlpatterns = [
    path('place/<id>/', views.getPlace, name='place_getter'),
]