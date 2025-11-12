# API For Recorder

- GET /audiodevice
[
    {
        "name": "X32",
        "identifier": "alsa:card1"
    }
]
- POST /recording/start
Parameter:
{
    "audiodevice_identifier": "alsa:card1",
    "channel_list": [1, 2, 3, 8]
}
Response 200 heißt: Recording wurde gestartet.
Antwort:
{
    "id": 29
}
- GET /status
{
    "status": "recording", // oder playing, paused, idle
    "recording_id": 29, // nicht in idle vorhanden
    "time": "00:15:09", // nicht in idle
    "total_time": "00:30:00", // Nur in playing oder paused
    "channel_list": [1, 2, 3, 8]
}
- POST /recording/play
Parameter:
{
    "recording_id": 29
}
- POST /recording/stop - sowohl für Abspielen wie auch für Aufzeichnen
{
    "recording_id": 29,
    "total_time": "00:30:00",
    "channel_list": [1, 2, 3, 8]
}
