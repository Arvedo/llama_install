# 🏢 KI-Besucherterminal – Pure Gemma STT & Extraktion

Interaktive Demonstration für die **llama.cpp Präsentation**:
Vollständig lokale Audio-Verarbeitung mit **Gemma 4 Multimodal** (`--mmproj mmproj-BF16.gguf`):
* **Kein Browser-STT:** Die Audio-WAV-Daten vom Mikrofon werden direkt per `input_audio` an das lokale Gemma-Modell gestreamt.
* **Kein TTS:** Reine Text- und visuelle Rückmeldung im Terminal sowie Druck des Ausweises.
* **Slot-Filling & State-Tracking:** Gemma transkribiert die Audiospur und extrahiert zeitgleich in einem Durchgang die JSON-Felder (`name`, `company`, `reason`).

---

## 🚀 Schnellstart

1. **Doppelklick** auf:
   ```text
   START_VISITOR_TERMINAL_DEMO.bat
   ```
   *(im Hauptverzeichnis der Präsentation)*
2. Öffnet die Web-App unter `http://localhost:3000/index.html`.
3. Der `llama-server` läuft mit Gemma 4 + MTP Drafter + Multimodal Projector auf Port `8080`.

---

## 🎤 Wie die reine Gemma-STT funktioniert

1. **Mikrofon klicken:** Der Browser nimmt unkomprimiertes 16-kHz-PCM-Audio auf.
2. **Klick zum Beenden:** Das Audio wird in ein Standard-WAV-Format gepackt, Base64-kodiert und an `/v1/chat/completions` geschickt:
   ```json
   {
     "type": "input_audio",
     "input_audio": {
       "data": "<BASE64_WAV>",
       "format": "wav"
     }
   }
   ```
3. **Gemma 4 erledigt alles in einem Pass:**
   * Transkribiert die Sprache (`transcription`).
   * Erkennt Name, Firma und Grund (`name`, `company`, `reason`).
   * Prüft den aktuellen Zustand und stellt bei Lücken präzise Text-Rückfragen.
   * Bei 3/3 vollständigen Daten wird der **Besucherausweis** freigegeben und gedruckt.
