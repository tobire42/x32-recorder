# Roadmap

# erledigt
- ✅ Controller Umbau von SoX zu sounddevice Bibliothek - Cross-Platform und flexibler
- ✅ Neues, Vue basiertes Frontend
- ✅ Audio Device Enumeration und Auswahl im Frontend (sounddevice)
- ✅ Nach Recording Multichannel Wave File in mehrere Einzel-Wavefiles aufsplitten - Durch sounddevice Umbau umgesetzt

# todo
- API URL im Frontend je nach Host ändern, aktuell wird nur localhost gecalled. Evtl über relative URLs aufrufen?
- Mit Linux-System und X32 testen (!!)
- Recording-Download über Webinterface
- Bessere Ordnerstruktur (alle Kanäle in einem Folder speichern)
- Transcoding nach MP3 oä
- Aufnahme-Template mit Kanalkonfiguration im Frontend manage- und auswählbar machen.
- OSC integrieren für Plaback / Record Mixer Konfiguration - zB via https://pypi.org/project/python-osc/
