from django.db import models


class Recording(models.Model):
    NEW = 0
    RECORD = 1
    STOP = 2

    STOPPED = 3

    PLAYING = 4

    date = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=256)
    channels = models.JSONField(default=list, help_text="List of integer channel numbers")
    duration = models.DurationField(default=None, blank=True, null=True)
    state = models.IntegerField(default=NEW)

    @classmethod
    def get_active(cls):
        active_recordings = cls.objects.exclude(state=cls.STOPPED)
        try:
            return active_recordings.get()
        except cls.DoesNotExist:
            return None

    @property
    def channel_count(self):
        """Backward compatibility property to get the number of channels"""
        return len(self.channels) if self.channels else 0

    def __str__(self) -> str:
        return f"Recorded on {self.date} - {self.duration}"


class RecordingTemplate(models.Model):
    name = models.CharField(max_length=256)
    channel_count = models.IntegerField()


class RecordingTemplateChannel(models.Model):
    template = models.ForeignKey(
        "RecordingTemplate", related_name="channels", on_delete=models.CASCADE
    )
    channel_no = models.IntegerField()
    name = models.CharField(max_length=256)
    stereo = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["template", "channel_no"], name="channel_no_unique_in_template"
            )
        ]
