from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Recording, RecordingTemplate, RecordingTemplateChannel
from .serializers import (
    RecordingSerializer,
    RecordingTemplateSerializer,
    RecordingTemplateChannelSerializer
)
import datetime


class RecordingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Recording model providing full CRUD operations
    """
    queryset = Recording.objects.all().order_by('-date')
    serializer_class = RecordingSerializer

    @action(detail=False, methods=['get'])
    def hello(self, request):
        return Response({"message": "Hello, this is the Recording API!"})

    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new recording"""
        # Check if there's already an active recording
        if Recording.get_active():
            return Response(
                {'error': 'There is already an active recording'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new recording
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav"
        channels = request.data.get('channels', [1, 2])  # Default to channels 1 and 2
        
        # Ensure channels is a list of integers
        if not isinstance(channels, list):
            return Response(
                {'error': 'channels must be a list of integers'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            channels = [int(ch) for ch in channels]
        except (ValueError, TypeError):
            return Response(
                {'error': 'All channel values must be integers'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recording = Recording.objects.create(
            filename=filename,
            channels=channels,
            state=Recording.NEW
        )
        
        serializer = self.get_serializer(recording)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop a specific recording"""
        recording = self.get_object()
        
        if recording.state not in [Recording.NEW, Recording.RECORD]:
            return Response(
                {'error': 'Recording is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recording.state = Recording.STOP
        recording.save()
        
        serializer = self.get_serializer(recording)
        return Response(serializer.data)


class RecordingTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RecordingTemplate model providing full CRUD operations
    """
    queryset = RecordingTemplate.objects.all().order_by('name')
    serializer_class = RecordingTemplateSerializer


class RecordingTemplateChannelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RecordingTemplateChannel model providing full CRUD operations
    """
    queryset = RecordingTemplateChannel.objects.all().order_by('template', 'channel_no')
    serializer_class = RecordingTemplateChannelSerializer
    
    def get_queryset(self):
        """
        Optionally filter channels by template
        """
        queryset = RecordingTemplateChannel.objects.all()
        template_id = self.request.query_params.get('template', None)
        if template_id is not None:
            queryset = queryset.filter(template=template_id)
        return queryset.order_by('template', 'channel_no')
