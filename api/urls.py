from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('activate/<uidb64>/<utoken>/', views.activateAccount, name='account_activation'),
    path('isit/', views.isit),
]