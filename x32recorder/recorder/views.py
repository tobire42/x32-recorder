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


def startrecording(request):
    rec = Recording(channel_count=2, filename="new.wav")
    rec.save()
    return redirect(index)


def stoprecording(request):
    recording_active = Recording.get_active()
    recording_active.state = Recording.STOP
    recording_active.save()
    return redirect(index)
