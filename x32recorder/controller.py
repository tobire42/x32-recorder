import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x32recorder.settings")
import django
import subprocess

django.setup()

from recorder.models import Recording

CHANNEL_COUNT = 4
RECORDING_PATH = "/home/pi/recordings/"
AUDIODEV = "hw:2"


while True:
    recording = Recording.get_active()
    if not recording:
        time.sleep(1)
        continue

    assert recording.state == Recording.NEW

    # Start actual recording here
    print("Starting recording")
    process = subprocess.Popen(
        [
            "rec",
            "-q", "--buffer", "1048576", "-b", "24",
            "-c", str(CHANNEL_COUNT),
            recording.filename
        ],
        cwd=RECORDING_PATH,
        env={"AUDIODEV": AUDIODEV}
    )

    recording.state = Recording.RECORD
    recording.save()

    while recording.state == Recording.RECORD:
        time.sleep(1)
        recording.refresh_from_db()

    assert recording.state == Recording.STOP

    # Stop recording here
    print("Stopping recording")
    process.terminate()
    process.wait()

    recording.state = Recording.STOPPED
    recording.save()
