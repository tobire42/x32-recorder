import os
import time
import threading
import wave
import struct
import platform
from datetime import datetime
import numpy as np
import sounddevice as sd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x32recorder.settings")
import django

django.setup()

from recorder.models import Recording

print("Using sounddevice backend (cross-platform)")

CHANNEL_COUNT = 4
RECORDING_PATH = "/home/pi/recordings/"
AUDIODEV = "hw:2"  # Device name or index for sounddevice
SAMPLE_RATE = 48000
PERIOD_SIZE = 1024
BUFFER_SIZE = 8192


class MultiChannelRecorder:
    def __init__(self, device, channels, sample_rate, recording_path):
        self.device = device
        self.channels = channels
        self.sample_rate = sample_rate
        self.recording_path = recording_path
        self.recording = False
        self.wave_files = []
        self.wave_writers = []
        self.audio_data_queue = []
        self.stream = None
            
    def setup_audio_device(self):
        """Setup sounddevice for recording"""
        try:
            # Parse device if it's a string like "hw:2" (convert to device index)
            device_idx = self.device
            if isinstance(self.device, str) and self.device.startswith("hw:"):
                # For sounddevice, we'll use the default device or parse as integer
                try:
                    device_idx = int(self.device.split(":")[1])
                except:
                    device_idx = None  # Use default device
            
            # Test the device
            sd.check_input_settings(
                device=device_idx,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=np.float32
            )
            
            print(f"sounddevice configured: device={device_idx}, {self.channels} channels, {self.sample_rate}Hz")
            return True
            
        except Exception as e:
            print(f"Failed to setup sounddevice: {e}")
            return False
    
    def setup_wave_files(self, base_filename):
        """Setup wave files for each channel"""
        self.wave_files = []
        self.wave_writers = []
        
        # Remove .wav extension if present to add channel number
        if base_filename.endswith('.wav'):
            base_filename = base_filename[:-4]
        
        for channel in range(self.channels):
            filename = f"{base_filename}_ch{channel + 1:02d}.wav"
            filepath = os.path.join(self.recording_path, filename)
            
            # Ensure recording directory exists
            os.makedirs(self.recording_path, exist_ok=True)
            
            wave_file = wave.open(filepath, 'wb')
            wave_file.setnchannels(1)  # Mono file per channel
            wave_file.setsampwidth(3)  # 24-bit = 3 bytes
            wave_file.setframerate(self.sample_rate)
            
            self.wave_files.append(wave_file)
            self.wave_writers.append(filepath)
            
        print(f"Created {len(self.wave_files)} wave files for channels")
    
    def start_recording(self, base_filename):
        """Start multi-channel recording"""
        if not self.setup_audio_device():
            return False
            
        self.setup_wave_files(base_filename)
        self.recording = True
        self.audio_data_queue = []
        
        # Start recording with sounddevice
        self.record_thread = threading.Thread(target=self._sounddevice_record_loop)
        self.record_thread.start()
        
        print(f"Multi-channel recording started using sounddevice")
        return True
    
    def stop_recording(self):
        """Stop recording and close files"""
        if not self.recording:
            return
            
        self.recording = False
        
        # Stop sounddevice stream if running
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
        
        # Wait for recording thread to finish
        if hasattr(self, 'record_thread'):
            self.record_thread.join()
        
        # Close wave files
        for wave_file in self.wave_files:
            wave_file.close()
            
        print("Recording stopped and files closed")
        return self.wave_writers
    
    def _sounddevice_record_loop(self):
        """sounddevice recording loop"""
        try:
            device_idx = self.device
            if isinstance(self.device, str) and self.device.startswith("hw:"):
                try:
                    device_idx = int(self.device.split(":")[1])
                except:
                    device_idx = None
            
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"Audio callback status: {status}")
                if self.recording:
                    # Convert float32 to int32 for 24-bit processing
                    audio_int32 = (indata * (2**23 - 1)).astype(np.int32)
                    self._process_sounddevice_data(audio_int32)
            
            # Start stream
            self.stream = sd.InputStream(
                device=device_idx,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=audio_callback,
                blocksize=PERIOD_SIZE,
                dtype=np.float32
            )
            
            self.stream.start()
            
            # Keep thread alive while recording
            while self.recording:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"sounddevice recording error: {e}")
    
    def _process_sounddevice_data(self, audio_data):
        """Process sounddevice audio data (convert int32 to 24-bit)"""
        frames, channels = audio_data.shape
        
        for channel in range(min(channels, len(self.wave_files))):
            # Extract channel data and convert to 24-bit
            channel_data = audio_data[:, channel]
            
            # Convert int32 to 24-bit bytes
            channel_24bit = bytearray()
            for sample in channel_data:
                # Clamp to 24-bit range
                sample_24 = max(-2**23, min(2**23 - 1, sample))
                # Convert to 3 bytes (little endian)
                sample_bytes = sample_24.to_bytes(4, byteorder='little', signed=True)[:3]
                channel_24bit.extend(sample_bytes)
            
            # Write to wave file
            self.wave_files[channel].writeframes(bytes(channel_24bit))


def list_audio_devices():
    """List available audio devices"""
    print("\nAvailable sounddevice audio devices:")
    print(sd.query_devices())


def main():
    print(f"X32 Recorder Controller started")
    print(f"Audio backend: sounddevice")
    print(f"Device: {AUDIODEV}, Channels: {CHANNEL_COUNT}, Sample Rate: {SAMPLE_RATE}Hz")
    print(f"Recording path: {RECORDING_PATH}")
    
    # List available devices for debugging
    list_audio_devices()
    
    recorder = MultiChannelRecorder(
        device=AUDIODEV,
        channels=CHANNEL_COUNT,
        sample_rate=SAMPLE_RATE,
        recording_path=RECORDING_PATH
    )
    
    current_recorder_instance = None
    
    while True:
        try:
            recording = Recording.get_active()
            if not recording:
                time.sleep(1)
                continue

            if recording.state == Recording.NEW:
                print(f"Starting new recording: {recording.filename}")
                
                # Start recording
                success = recorder.start_recording(recording.filename)
                if success:
                    recording.state = Recording.RECORD
                    recording.save()
                    current_recorder_instance = recorder
                else:
                    print("Failed to start recording")
                    recording.state = Recording.STOPPED
                    recording.save()
                    continue

            elif recording.state == Recording.RECORD:
                # Recording is ongoing, just wait
                time.sleep(1)
                recording.refresh_from_db()

            elif recording.state == Recording.STOP:
                print("Stopping recording")
                
                if current_recorder_instance:
                    files_created = current_recorder_instance.stop_recording()
                    print(f"Recording stopped. Files created: {files_created}")
                
                recording.state = Recording.STOPPED
                recording.save()
                current_recorder_instance = None
                
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
