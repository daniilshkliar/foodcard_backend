from django.urls import path

from . import views


urlpatterns = [
    path('get_user/', views.get_user),
    path('signup/', views.signup),
]