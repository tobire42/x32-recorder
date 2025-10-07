# X32 Recorder

**X32 Recorder** ist eine Django-basierte Webanwendung zur Steuerung und Verwaltung von Mehrkanal-Audioaufnahmen. Das System wurde ursprünglich für das Behringer X32 Mischpult entwickelt, funktioniert aber mit jedem sounddevice-kompatiblen Audio-Interface auf **Windows, macOS und Linux**.

## 🎯 Features

- **Cross-Platform**: Läuft auf Windows, macOS und Linux
- **Web-Interface**: Intuitive Bedienung zum Starten und Stoppen von Aufnahmen
- **REST API**: Vollständige API für alle Funktionen
- **Mehrkanal-Aufnahme**: Unterstützung für Mehrkanal-Audio-Aufnahmen
- **Recording-Management**: Übersicht und Verwaltung aller vergangenen Aufnahmen
- **Template-System**: Aufnahme-Templates mit konfigurierbaren Kanälen
- **Echtzeitsteuerung**: Separates Controller-Skript für die Hardware-Anbindung
- **Flexible Konfiguration**: Anpassbare Kanalzahl und Audio-Device-Einstellungen
- **Produktions-ready**: Waitress WSGI Server für stabile Deployments

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
- **PortAudio** (für sounddevice):
  - **Ubuntu/Debian**: `sudo apt-get install portaudio19-dev`
  - **Windows**: Automatisch mit sounddevice installiert
  - **macOS**: `brew install portaudio`
- Audio-Interface mit sounddevice-Unterstützung (cross-platform)

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

5. **Static Files sammeln (für Produktion)**
   ```bash
   uv run python x32recorder/manage.py collectstatic --noinput
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

#### Produktionsserver mit Waitress (Cross-platform)
```bash
# Einfacher Start
uv run waitress-serve --host=0.0.0.0 --port=8000 --chdir=x32recorder x32recorder.wsgi:application

# Mit mehr Threads für bessere Performance
uv run waitress-serve --host=0.0.0.0 --port=8000 --threads=6 --chdir=x32recorder x32recorder.wsgi:application
```

**Hinweis**: Static Files werden automatisch von WhiteNoise bereitgestellt. Bei Änderungen an CSS/JS-Dateien muss `collectstatic` erneut ausgeführt werden.

Zugriff unter: [http://localhost:8000](http://localhost:8000)

### 2. Controller starten

**Wichtig**: Der Controller muss auf dem System mit Audio-Hardware laufen!

```bash
uv run python x32recorder/controller.py
```

### 3. Cross-Platform Service Management (Empfohlen)

Verwenden Sie das neue `manage_services.py` Skript für einfaches Starten und Stoppen beider Services auf allen Plattformen:

#### Linux/macOS:
```bash
# Beide Services im Hintergrund starten
python manage_services.py start

# Status der Services prüfen
python manage_services.py status

# Beide Services stoppen
python manage_services.py stop

# Services neustarten
python manage_services.py restart

# Logs anzeigen
python manage_services.py logs
```

#### Windows:
```cmd
# Beide Services im Hintergrund starten
manage_services.bat start

# Status der Services prüfen
manage_services.bat status

# Beide Services stoppen
manage_services.bat stop

# Services neustarten
manage_services.bat restart

# Logs anzeigen
manage_services.bat logs
```

**Hinweis**: Das neue Service-Management verwendet Waitress statt Gunicorn für bessere Windows-Kompatibilität.

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
- Static Files nicht sichtbar: Prüfen ob WhiteNoise korrekt konfiguriert ist

### Static Files Probleme
- Static Files sammeln: `uv run python x32recorder/manage.py collectstatic --noinput`
- Cache leeren: Browser-Cache oder `collectstatic --clear`
- WhiteNoise-Konfiguration in `settings.py` prüfen

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
- Getestet auf Linux-Systemen, Windows-Kompatibilität durch Waitress und sounddevice
- Für Produktionsumgebungen `waitress` verwenden (cross-platform)
- Das neue `manage_services.py` Skript funktioniert auf allen Plattformen (Linux, macOS, Windows)