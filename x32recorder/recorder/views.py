import datetime
from django.shortcuts import render, redirect

from .models import Recording



def index(request):
    recording_active = Recording.get_active()

    return render(
        request,
        "index.html",
        {
            "name": "Marten",
            "recordings": Recording.objects.all(),
            "recording_active": recording_active,
        },
    )

