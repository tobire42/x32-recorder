from django.contrib import admin

from .models import Recording, RecordingTemplate, RecordingTemplateChannel

admin.site.register(Recording)
admin.site.register(RecordingTemplate)
admin.site.register(RecordingTemplateChannel)
