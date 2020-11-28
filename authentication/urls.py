from django.urls import path

from . import views

    
urlpatterns = [
    path('signup/', views.signup),
    path('login/', views.login),
    path('token/refresh/', views.token_refresh),
    path('activate/<uidb64>/<utoken>/', views.activateAccount),
    path('get_user/', views.UserViewSet.as_view({'get': 'retrieve'})),
]