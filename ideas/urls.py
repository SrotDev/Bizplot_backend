from django.contrib import admin
from django.urls import path, include

from .views import *

urlpatterns = [
    path('idea/', IdeaViewSet.as_view({'get': 'list', 'post': 'create'}), name='idea-list-create'),
    path('idea/<uuid:pk>/', IdeaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='idea-detail'),

    path('ideacard/', IdeaCardViewSet.as_view({'get': 'list'}), name='ideacard-list'),
    path('ideacard/<uuid:pk>/', IdeaCardViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='ideacard-detail'),

    path('ideacard/generate/<uuid:pk>/', IdeaCardGenerateView.as_view(), name='ideacard-generate'),
]
