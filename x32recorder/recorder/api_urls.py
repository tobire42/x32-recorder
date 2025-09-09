from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    RecordingViewSet,
    RecordingTemplateViewSet,
    RecordingTemplateChannelViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'recordings', RecordingViewSet, basename='recording')
router.register(r'templates', RecordingTemplateViewSet, basename='recordingtemplate')
router.register(r'template-channels', RecordingTemplateChannelViewSet, basename='recordingtemplatechannel')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
