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
- **Poetry** (Dependency Management)
- **SoX** (`rec`-Befehl) für Audio-Aufnahmen
- **ALSA** (Linux Audio-System)
- Audio-Interface mit ALSA-Unterstützung

### Setup

1. **Repository klonen**
   ```bash
   git clone https://github.com/tobire42/x32-recorder.git
   cd x32-recorder
   ```

2. **Abhängigkeiten installieren**
   ```bash
   poetry install
   ```

3. **Datenbank initialisieren**
   ```bash
   poetry run python x32recorder/manage.py migrate
   ```

4. **Admin-User erstellen (optional)**
   ```bash
   poetry run python x32recorder/manage.py createsuperuser
   ```

## 🎛️ Konfiguration

### Audio-Setup

Bearbeiten Sie `x32recorder/controller.py` für Ihre Hardware-Konfiguration:

```python
CHANNEL_COUNT = 4                        # Anzahl Kanäle
RECORDING_PATH = "/home/pi/recordings/"  # Aufnahme-Verzeichnis  
AUDIODEV = "hw:2"                        # ALSA-Device
```

### ALSA-Device ermitteln

```bash
# Verfügbare Audio-Devices anzeigen
arecord -l

# Test-Aufnahme
arecord -D hw:2 -c 4 -f S24_LE test.wav
```

## 🎵 Verwendung

### 1. Web-Interface starten

```bash
poetry run python x32recorder/manage.py runserver
```

Zugriff unter: [http://localhost:8000](http://localhost:8000)

### 2. Controller starten

**Wichtig**: Der Controller muss auf dem System mit Audio-Hardware laufen!

```bash
poetry run python x32recorder/controller.py
```

### 3. Aufnahme bedienen

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
poetry run python x32recorder/manage.py runserver
```

### Code-Formatierung
```bash
poetry run black .
```

### Tests ausführen
```bash
poetry run python x32recorder/manage.py test
```

## 🐛 Troubleshooting

### Audio-Probleme
- ALSA-Device mit `arecord -l` prüfen
- Berechtigungen für Audio-Hardware prüfen
- SoX-Installation überprüfen: `rec --version`

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