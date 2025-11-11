from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import StreamingHttpResponse
from django.conf import settings
from .models import Recording, RecordingTemplate, RecordingTemplateChannel
from .serializers import (
    RecordingSerializer,
    RecordingTemplateSerializer,
    RecordingTemplateChannelSerializer
)
import datetime
import sounddevice as sd
from pprint import pprint
import os
import zipfile
from pathlib import Path


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
        
        template_id = request.data.get('template_id', None)

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
            audiodevice_index=audiodevice_index,
            template_id=template_id
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
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download recording files as a ZIP archive"""
        recording = self.get_object()
        
        # Get the recordings directory from settings or use default
        recordings_dir = os.path.join(settings.RECORDING_PATH, str(recording.uuid))
        
        recording_dir = Path(recordings_dir)
        
        # Find all files that match this recording
        matching_files = []
        if recording_dir.exists():
            # Look for files starting with the recording name
            for file_path in recording_dir.iterdir():
                if file_path.is_file():
                    matching_files.append(file_path)
        
        if not matching_files:
            return Response(
                {'error': 'Recording files not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create a generator function for streaming ZIP
        def zip_generator():
            """Generator that yields ZIP file chunks"""
            import io
            
            # Create an in-memory buffer for the ZIP
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add all matching files
                for file_path in matching_files:
                    zip_file.write(file_path, file_path.name)
            
            # Get the ZIP data
            zip_buffer.seek(0)
            
            # Yield the ZIP file in chunks
            chunk_size = 8192
            while True:
                chunk = zip_buffer.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        
        # Create the streaming response
        zip_filename = f"{recording.name or recording.uuid}.zip"
        response = StreamingHttpResponse(
            zip_generator(),
            content_type='application/zip'
        )
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        
        return response


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

