from django.db import models


class Recording(models.Model):
    NEW = 0
    RECORD = 1
    STOP = 2

    STOPPED = 3

    PLAYING = 4

    date = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=256)
    channel_count = models.IntegerField()
    duration = models.DurationField(default=None, blank=True, null=True)
    state = models.IntegerField(default=NEW)

    @classmethod
    def get_active():
        active_recordings = Recording.objects.exclude(state=Recording.STOPPED)
        try:
            return active_recordings.get()
        except Recording.DoesNotExist:
            return None

    def __str__(self) -> str:
        return f"Recorded on {self.date} - {self.duration}"
