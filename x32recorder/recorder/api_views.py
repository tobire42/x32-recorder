from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Recording, RecordingTemplate, RecordingTemplateChannel
from .serializers import (
    RecordingSerializer,
    RecordingTemplateSerializer,
    RecordingTemplateChannelSerializer
)
import datetime
import sounddevice as sd
from pprint import pprint


class RecordingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Recording model providing full CRUD operations
    """
    queryset = Recording.objects.all().order_by('-date')
    serializer_class = RecordingSerializer

    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new recording"""
        # Check if there's already an active recording
        if Recording.get_active():
            return Response(
                {'error': 'There is already an active recording'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        name = request.data.get('name', '').strip()
        channels = request.data.get('channels', [1, 2])  # Default to channels 1 and 2

        audiodevice_index = request.data.get('audiodevice_index', 0)  # Default to device index 0
        
        # Ensure channels is a list of integers
        if not isinstance(channels, list):
            return Response(
                {'error': 'channels must be a list of integers'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            channels = [int(ch) - 1 for ch in channels]
        except (ValueError, TypeError):
            return Response(
                {'error': 'All channel values must be integers'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recording = Recording.objects.create(
            name=name,
            channels=channels,
            state=Recording.NEW,
            audiodevice_index=audiodevice_index
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

@api_view(['GET'])
def audiodevice_list(request):
    """List available audio devices"""
    try:
        devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        device_dict = {}
        
        for device in devices:
            if device['max_input_channels'] > 0:  # Only input devices
                device_index = device['index']
                device_name = device['name']
                hostapi_index = device['hostapi']
                hostapi_name = hostapis[hostapi_index]['name']
                
                # Normalize device name for comparison (remove extra spaces, parentheses variations)
                base_name = device_name.split('(')[0].strip()
                
                # Create a unique key based on the base name
                # Prefer ASIO > WDM-KS > WASAPI > DirectSound > MME
                # ASIO is best for professional audio interfaces, WASAPI for consumer devices
                priority = {
                    'ASIO': 0,
                    'Windows WDM-KS': 1,
                    'WASAPI': 2,
                    'Windows WASAPI': 2,
                    'Windows DirectSound': 3,
                    'MME': 4
                }
                current_priority = priority.get(hostapi_name, 99)
                
                if base_name not in device_dict:
                    device_dict[base_name] = {
                        'name': f"{device_name} [{hostapi_name}]",
                        'identifier': f"sounddevice:{device_index}",
                        'input_channel_count': device['max_input_channels'],
                        'index': device_index,
                        'hostapi': hostapi_name,
                        'priority': current_priority
                    }
                else:
                    # Replace with lower priority number (better API)
                    if current_priority < device_dict[base_name]['priority']:
                        device_dict[base_name] = {
                            'name': f"{device_name} [{hostapi_name}]",
                            'identifier': f"sounddevice:{device_index}",
                            'input_channel_count': device['max_input_channels'],
                            'index': device_index,
                            'hostapi': hostapi_name,
                            'priority': current_priority
                        }
        
        # Convert dict to list and remove priority field
        device_list = []
        for device_data in device_dict.values():
            device_data.pop('priority', None)
            device_list.append(device_data)
        
        # Sort by name
        device_list.sort(key=lambda x: x['name'])
        
        return Response(device_list)
    except Exception as e:
        return Response(
            {'error': f'Failed to list audio devices: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

