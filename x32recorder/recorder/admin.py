from django.contrib import admin

from .models import Recording, RecordingTemplate, RecordingTemplateChannel, RecordingMarker

admin.site.register(Recording)
admin.site.register(RecordingTemplate)
admin.site.register(RecordingTemplateChannel)
admin.site.register(RecordingMarker)

