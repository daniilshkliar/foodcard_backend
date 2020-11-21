from django.urls import path

from . import views


urlpatterns = [
    path('upload/place/', views.PlaceSetter.as_view()),
]