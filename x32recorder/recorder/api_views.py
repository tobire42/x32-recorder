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
import threading
import time


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


# Global variables to track recording state
current_recording = None
recording_thread = None
playback_state = {
    'status': 'idle',
    'recording_id': None,
    'start_time': None,
    'duration': None,
    'channels': []
}


@api_view(['GET'])
def audiodevice_list(request):
    """List available audio devices"""
    try:
        devices = sd.query_devices()
        device_list = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:  # Only input devices
                device_list.append({
                    'name': device['name'],
                    'identifier': f"sounddevice:{i}",
                    'input_channel_count': device['max_input_channels']
                })
        
        return Response(device_list)
    except Exception as e:
        return Response(
            {'error': f'Failed to list audio devices: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def recording_start(request):
    """Start a new recording"""
    global current_recording, recording_thread, playback_state
    
    # Check if already recording
    if playback_state['status'] == 'recording':
        return Response(
            {'error': 'Already recording'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audiodevice_identifier = request.data.get('audiodevice_identifier')
    channel_list = request.data.get('channel_list', [1, 2])
    
    if not audiodevice_identifier:
        return Response(
            {'error': 'audiodevice_identifier is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate channel_list
    if not isinstance(channel_list, list) or not all(isinstance(ch, int) for ch in channel_list):
        return Response(
            {'error': 'channel_list must be a list of integers'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create new recording
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav"
        recording = Recording.objects.create(
            filename=filename,
            channels=channel_list,
            state=Recording.RECORD
        )
        
        # Update global state
        current_recording = recording
        playback_state = {
            'status': 'recording',
            'recording_id': recording.id,
            'start_time': time.time(),
            'duration': None,
            'channels': channel_list
        }
        
        # TODO: Start actual recording with the specified audiodevice and channels
        # For now, we'll just simulate the recording
        
        return Response({'id': recording.id})
        
    except Exception as e:
        return Response(
            {'error': f'Failed to start recording: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def status_get(request):
    """Get current recording/playback status"""
    global playback_state
    
    if playback_state['status'] == 'idle':
        return Response({'status': 'idle'})
    
    response = {
        'status': playback_state['status'],
        'recording_id': playback_state['recording_id'],
        'channel_list': playback_state['channels']
    }
    
    # Calculate time for recording
    if playback_state['status'] == 'recording' and playback_state['start_time']:
        elapsed = time.time() - playback_state['start_time']
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        response['time'] = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    # Add total_time for playing/paused
    if playback_state['status'] in ['playing', 'paused'] and playback_state['duration']:
        hours, remainder = divmod(playback_state['duration'], 3600)
        minutes, seconds = divmod(remainder, 60)
        response['total_time'] = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        # Calculate current time for playing
        if playback_state['status'] == 'playing' and playback_state['start_time']:
            elapsed = time.time() - playback_state['start_time']
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            response['time'] = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    return Response(response)


@api_view(['POST'])
def recording_play(request):
    """Start playing a recording"""
    global playback_state
    
    recording_id = request.data.get('recording_id')
    if not recording_id:
        return Response(
            {'error': 'recording_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        recording = Recording.objects.get(id=recording_id)
        
        # Update playback state
        playback_state = {
            'status': 'playing',
            'recording_id': recording.id,
            'start_time': time.time(),
            'duration': recording.duration if recording.duration else 1800,  # Default 30 min
            'channels': recording.channels
        }
        
        # TODO: Start actual playback
        
        return Response({'message': 'Playback started'})
        
    except Recording.DoesNotExist:
        return Response(
            {'error': 'Recording not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to start playback: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def recording_stop(request):
    """Stop recording or playback"""
    global current_recording, playback_state
    
    if playback_state['status'] == 'idle':
        return Response(
            {'error': 'No active recording or playback'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    recording_id = playback_state['recording_id']
    channel_list = playback_state['channels']
    
    # Calculate total time
    total_time = "00:00:00"
    if playback_state['start_time']:
        if playback_state['status'] == 'recording':
            # For recording, calculate actual elapsed time
            elapsed = time.time() - playback_state['start_time']
        else:
            # For playback, use the recording's duration
            elapsed = playback_state['duration'] or 0
            
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    # Update recording in database if it was a recording session
    if playback_state['status'] == 'recording' and current_recording:
        current_recording.state = Recording.STOP
        if playback_state['start_time']:
            current_recording.duration = int(time.time() - playback_state['start_time'])
        current_recording.save()
    
    # Reset state
    current_recording = None
    playback_state = {
        'status': 'idle',
        'recording_id': None,
        'start_time': None,
        'duration': None,
        'channels': []
    }
    
    return Response({
        'recording_id': recording_id,
        'total_time': total_time,
        'channel_list': channel_list
    })
