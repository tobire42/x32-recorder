from rest_framework import serializers
from .models import Recording, RecordingTemplate, RecordingTemplateChannel


class RecordingSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Recording model with all fields and hyperlinked URLs"""
    
    class Meta:
        model = Recording
        fields = [
            'url',
            'id',
            'date',
            'filename',
            'channel_count',
            'duration',
            'state',
        ]
        read_only_fields = ['id', 'date']


class RecordingTemplateChannelSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for RecordingTemplateChannel model with all fields and hyperlinked URLs"""
    
    class Meta:
        model = RecordingTemplateChannel
        fields = [
            'url',
            'id',
            'template',
            'channel_no',
            'name',
            'stereo',
        ]
        read_only_fields = ['id']


class RecordingTemplateSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for RecordingTemplate model with all fields and hyperlinked URLs"""
    channels = RecordingTemplateChannelSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecordingTemplate
        fields = [
            'url',
            'id',
            'name',
            'channel_count',
            'channels',
        ]
        read_only_fields = ['id']
