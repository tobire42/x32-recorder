from django.shortcuts import render, redirect

from .models import Recording


def index(request):
    return render(
        request, "index.html", {"name": "Marten", "recordings": Recording.objects.all()}
    )


def startrecording(request):
    rec = Recording(channel_count=2, filename="new.wav")
    rec.save()
    return redirect(index)
