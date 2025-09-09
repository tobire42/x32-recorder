from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    RecordingViewSet,
    RecordingTemplateViewSet,
    RecordingTemplateChannelViewSet,
    audiodevice_list,
    recording_start,
    status_get,
    recording_play,
    recording_stop
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'recordings', RecordingViewSet, basename='recording')
router.register(r'templates', RecordingTemplateViewSet, basename='recordingtemplate')
router.register(r'template-channels', RecordingTemplateChannelViewSet, basename='recordingtemplatechannel')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    # Custom API endpoints as specified in API.md
    path('audiodevice/', audiodevice_list, name='audiodevice-list'),
    path('recording/start/', recording_start, name='recording-start'),
    path('status/', status_get, name='status'),
    path('recording/play/', recording_play, name='recording-play'),
    path('recording/stop/', recording_stop, name='recording-stop'),
]
