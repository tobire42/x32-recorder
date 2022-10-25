from urllib.parse import urlparse
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("startrecording/", views.startrecording, name="startrecording"),
    path("stoprecording/", views.stoprecording, name="stoprecording"),
]
