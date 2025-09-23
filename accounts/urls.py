from django.contrib import admin
from django.urls import path, include

from .views import RegisterView, LoginView, UserProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<uuid:pk>/', UserProfileView.as_view(), name='profile'),
]
