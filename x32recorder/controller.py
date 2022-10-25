import os
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x32recorder.settings")
import django

django.setup()

from recorder.models import Recording


while True:
    recording = Recording.get_active()
    if not recording:
        time.sleep(1)
        continue

    assert recording.state == Recording.NEW

    # Start actual recording here
    print("Starting recording")

    recording.state = Recording.RECORD
    recording.save()

    while recording.state == Recording.RECORD:
        time.sleep(1)
        recording.refresh_from_db()

    assert recording.state == Recording.STOP

    # Stop recording here
    print("Stopping recording")

    recording.state = Recording.STOPPED
    recording.save()
