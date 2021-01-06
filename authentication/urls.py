from django.urls import path

from . import views


urlpatterns = [
    path('signup/', views.signup),
    path('login/', views.login),
    path('logout/', views.logout),
    path('token/refresh/', views.refresh_tokens),
    path('activate/<uidb64>/<utoken>/', views.activate_account),
    path('user/get/', views.UserViewSet.as_view({'get': 'retrieve'})),
    path('user/check/login/', views.UserViewSet.as_view({'get': 'check_login'})),
]