from django.shortcuts import render, redirect

from .models import Recording


def get_active_recording():
    active_recordings = Recording.objects.exclude(state=Recording.STOPPED)
    try:
        return active_recordings.get()
    except Recording.DoesNotExist:
        return None


def index(request):
    recording_active = get_active_recording()

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
    recording_active = get_active_recording()
    recording_active.state = Recording.STOP
    recording_active.save()
    return redirect(index)
