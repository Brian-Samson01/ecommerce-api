from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    ProfileView,
    ChangePasswordView,
    LogoutView,
    UserListView,
)

urlpatterns = [
    # Auth
    path('register/',        RegisterView.as_view(),       name='register'),
    path('login/',           TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/',   TokenRefreshView.as_view(),   name='token_refresh'),
    path('logout/',          LogoutView.as_view(),         name='logout'),

    # Profile
    path('profile/',         ProfileView.as_view(),        name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Admin
    path('',                 UserListView.as_view(),       name='user_list'),
]