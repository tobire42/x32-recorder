# Roadmap

# erledigt
- ✅ Controller Umbau von SoX zu sounddevice Bibliothek - Cross-Platform und flexibler
- ✅ Neues, Vue basiertes Frontend
- ✅ Audio Device Enumeration und Auswahl im Frontend (sounddevice)
- ✅ Nach Recording Multichannel Wave File in mehrere Einzel-Wavefiles aufsplitten - Durch sounddevice Umbau umgesetzt
- Transition Recording.filename -> Recording.uuid abschließen: Controller, API testen, Frontend Implementation
- Recording-Download über Webinterface (via Zip File)

# todo
- API URL im Frontend je nach Host ändern, aktuell wird nur localhost gecalled. Evtl über relative URLs aufrufen?
- Möglichkeit, während eines Recordings Marker zu setzen. Diese sollen erstmal in der Datenbank gespeichert werden - in Zukunft dann in irgendeiner Form exportiert werden.
- Mit Linux-System und X32 testen (!!)
- Bessere Ordnerstruktur (alle Kanäle in einem Folder speichern)
- Transcoding nach MP3 oä
- Aufnahme-Template mit Kanalkonfiguration im Frontend manage- und auswählbar machen.
- OSC integrieren für Plaback / Record Mixer Konfiguration - zB via https://pypi.org/project/python-osc/
