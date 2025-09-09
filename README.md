# X32 Recorder

**X32 Recorder** ist eine Django-basierte Webanwendung zur Steuerung und Verwaltung von Mehrkanal-Audioaufnahmen. Das System wurde ursprünglich für das Behringer X32 Mischpult entwickelt, funktioniert aber mit jedem ALSA-kompatiblen Audio-Interface.

## 🎯 Features

- **Web-Interface**: Intuitive Bedienung zum Starten und Stoppen von Aufnahmen
- **Mehrkanal-Aufnahme**: Unterstützung für Mehrkanal-Audio-Aufnahmen
- **Recording-Management**: Übersicht und Verwaltung aller vergangenen Aufnahmen
- **Template-System**: Aufnahme-Templates mit konfigurierbaren Kanälen
- **Echtzeitsteuerung**: Separates Controller-Skript für die Hardware-Anbindung
- **Flexible Konfiguration**: Anpassbare Kanalzahl und Audio-Device-Einstellungen

## 🏗️ Architektur

Das System besteht aus zwei Hauptkomponenten:

1. **Django Web-App** (`x32recorder/`): Webinterface für die Bedienung
2. **Controller-Skript** (`controller.py`): Hardware-nahe Aufnahmesteuerung

```
x32recorder/
├── controller.py              # Hardware-Controller für Aufnahmen
├── manage.py                  # Django Management-Skript
├── db.sqlite3                 # SQLite-Datenbank
├── recorder/                  # Django-App
│   ├── models.py             # Datenmodelle (Recording, Template)
│   ├── views.py              # Web-Views
│   ├── urls.py               # URL-Routing
│   ├── admin.py              # Django-Admin Integration
│   ├── templates/            # HTML-Templates
│   │   └── index.html        # Hauptinterface
│   ├── static/               # CSS, Icons
│   │   ├── css/style.css
│   │   └── icons/            # Play/Stop/Pause Icons
│   └── migrations/           # Datenbank-Migrationen
└── x32recorder/              # Django-Projekt-Konfiguration
    ├── settings.py           # Django-Einstellungen
    ├── urls.py               # Haupt-URL-Konfiguration
    └── wsgi.py               # WSGI-Konfiguration
```

## 🚀 Installation

### Voraussetzungen

- **Python 3.8-3.11**
- **uv** (Dependency Management) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **PortAudio** (für sounddevice) - Install with: `sudo apt-get install portaudio19-dev` (Ubuntu/Debian)
- Audio-Interface mit sounddevice-Unterstützung

### Setup

1. **Repository klonen**
   ```bash
   git clone https://github.com/tobire42/x32-recorder.git
   cd x32-recorder
   ```

2. **Abhängigkeiten installieren**
   ```bash
   uv sync
   ```

3. **Datenbank initialisieren**
   ```bash
   uv run python x32recorder/manage.py migrate
   ```

4. **Admin-User erstellen (optional)**
   ```bash
   uv run python x32recorder/manage.py createsuperuser
   ```

## 🎛️ Konfiguration

### Audio-Setup

Bearbeiten Sie `x32recorder/controller.py` für Ihre Hardware-Konfiguration:

```python
CHANNEL_COUNT = 4                        # Anzahl Kanäle
RECORDING_PATH = "/home/pi/recordings/"  # Aufnahme-Verzeichnis  
AUDIODEV = "hw:2"                        # Audio-Device Name oder Index
```

### Audio-Device ermitteln

```bash
# Verfügbare Audio-Devices anzeigen (mit sounddevice)
uv run python -c "import sounddevice; print(sounddevice.query_devices())"

# Oder direkt im Controller starten um Devices zu sehen
uv run python x32recorder/controller.py
```

## 🎵 Verwendung

### 1. Web-Interface starten

#### Entwicklungsserver
```bash
uv run python x32recorder/manage.py runserver
```

#### Produktionsserver mit Gunicorn
```bash
# Einfacher Start
uv run gunicorn --chdir x32recorder x32recorder.wsgi:application

# Mit Konfiguration für Produktion
uv run gunicorn --chdir x32recorder \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile - \
    x32recorder.wsgi:application
```

Zugriff unter: [http://localhost:8000](http://localhost:8000)

### 2. Controller starten

**Wichtig**: Der Controller muss auf dem System mit Audio-Hardware laufen!

```bash
uv run python x32recorder/controller.py
```

### 3. Automatisiertes Management (Empfohlen)

Verwenden Sie das `manage_services.sh` Skript für einfaches Starten und Stoppen beider Services:

```bash
# Beide Services im Hintergrund starten
./manage_services.sh start

# Status der Services prüfen
./manage_services.sh status

# Beide Services stoppen
./manage_services.sh stop

# Services neustarten
./manage_services.sh restart

# Logs anzeigen
./manage_services.sh logs
```

Das Skript erstellt PID-Dateien in `./pids/` und Log-Dateien in `./logs/`.

### 4. Aufnahme bedienen

- **Aufnahme starten**: Button im Web-Interface klicken
- **Aufnahme stoppen**: Stop-Button während laufender Aufnahme
- **Vergangene Aufnahmen**: Automatische Anzeige in der Übersicht

## 📊 Datenmodell

### Recording
- `date`: Aufnahme-Zeitstempel
- `filename`: Dateiname der Aufnahme
- `channel_count`: Anzahl Kanäle
- `duration`: Aufnahmedauer
- `state`: Status (NEW, RECORD, STOP, STOPPED, PLAYING)

### RecordingTemplate
- `name`: Template-Name
- `channel_count`: Kanalanzahl

### RecordingTemplateChannel
- `template`: Zugehöriges Template
- `channel_no`: Kanalnummer
- `name`: Kanalbezeichnung
- `stereo`: Stereo-Flag

## 🔧 Admin-Interface

Django-Admin verfügbar unter: [http://localhost:8000/admin/](http://localhost:8000/admin/)

Funktionen:
- Recording-Verwaltung
- Template-Konfiguration
- Kanal-Setup

## 🗺️ Roadmap

Geplante Features (siehe `ROADMAP.md`):

- **Controller-Modernisierung**: Umstellung von SoX auf Python `alsaaudio`
- **Vue.js Frontend**: Modernes, reaktives Web-Interface
- **Device-Enumeration**: Automatische ALSA-Device-Erkennung
- **OSC-Integration**: Mixer-Steuerung via Open Sound Control
- **Multichannel-Split**: Automatische Aufteilung in Einzeldateien
- **Download-Feature**: Aufnahmen über Web-Interface herunterladen
- **Template-Management**: Erweiterte Template-Verwaltung im Frontend

## 🛠️ Entwicklung

### Entwicklungsserver starten
```bash
uv run python x32recorder/manage.py runserver
```

### Code-Formatierung
```bash
uv run black .
```

### Tests ausführen
```bash
uv run python x32recorder/manage.py test
```

## 🐛 Troubleshooting

### Audio-Probleme
- Audio-Device mit `uv run python -c "import sounddevice; print(sounddevice.query_devices())"` prüfen
- PortAudio-Installation überprüfen: `sudo apt-get install portaudio19-dev` (Ubuntu/Debian)
- sounddevice-Installation: `uv add sounddevice`

### Django-Probleme
- Datenbank-Migrationen: `python manage.py migrate`
- Static Files: `python manage.py collectstatic`

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

## 👨‍💻 Autor

**Tobias Reineke** - [tobi@g3th.net](mailto:tobi@g3th.net)

## 🤝 Beitragen

Beiträge sind willkommen! Bitte:
1. Fork das Repository
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request erstellen

## ⚠️ Hinweise

- Das Projekt befindet sich in aktiver Entwicklung
- Getestet auf Linux-Systemen mit ALSA
- Für Produktionsumgebungen `gunicorn` verwenden
- Das `manage_services.sh` Skript vereinfacht das Management beider Services