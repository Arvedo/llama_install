# 🦙 Bring your device, get your AI

[![Event: 58. Kasseler Webmontag](https://img.shields.io/badge/Event-58._Kasseler_Webmontag-ff4a79.svg)](https://www.meetup.com/de-de/webmontag-kassel/events/315057949/)
[![Speaker: Arved](https://img.shields.io/badge/Speaker-Arved-blue.svg)](https://github.com/Arvedo)
[![Status: WIP](https://img.shields.io/badge/status-work--in--progress-orange.svg)](presentation/)
[![Engine: llama.cpp](https://img.shields.io/badge/engine-llama.cpp-blue.svg)](https://github.com/ggml-org/llama.cpp)
[![Format: GGUF](https://img.shields.io/badge/format-GGUF-purple.svg)](self-service/models_list.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Dieses Repository begleitet den StandUp-Vortrag **„bring your device, get your AI“** von **Arved** auf dem **[58. Kasseler Webmontag](https://www.meetup.com/de-de/webmontag-kassel/events/315057949/)** (bei der Micromata GmbH).

Das Ziel: **Jeder bringt sein eigenes Gerät (Laptop, MacBook, Mini-PC) mit und geht mit einer startklaren, rein lokalen KI nach Hause!**  
Hier findest du das komplette Self-Service-Setup für die vor Ort verteilten USB-Stick-Modelle, alle Cheat Sheets zum Download der passenden llama.cpp-Binaries, die Vortragsfolien sowie den Quellcode des im Vortrag demonstrierten interaktiven KI-Besucherterminals.

---

## 🗂️ Repository-Übersicht

```text
├── self-service/                     # 🚀 Schnelleinstieg & Modell-Download für Teilnehmer
│   ├── README.md                     # Schritt-für-Schritt Schnellstart-Anleitung (Vanilla Commands)
│   ├── models_list.md                # Vollständiger Modellkatalog mit VRAM-Footprint & HuggingFace-Links
│   ├── download_windows.png          # Download-Kompass für Windows (Nvidia CUDA / CPU)
│   ├── download_apple_mobile.png     # Download-Kompass für Apple Silicon (macOS Metal) & Mobile
│   ├── download_linux.png            # Download-Kompass für Linux (CUDA / CPU)
│   └── handout.pdf                   # Druckfertiges A4-Handout für Teilnehmer
│
├── visitor-terminal/                 # 🏢 Interaktive Live-Demo (Web-App)
│   ├── index.html                    # Benutzeroberfläche des KI-Besucherterminals
│   ├── server.py                     # Lokaler Python-Webserver & API-Bridge
│   ├── start_demo.bat                # Startskript für die Demo
│   └── README.md                     # Dokumentation zur Pure-Gemma Audio/Vision Architektur
│
├── presentation/                     # 📊 Vortragsfolien (Work In Progress)
│   ├── llama_cpp_20min_praesentation.pptx # Master-Folien (PowerPoint 16:9, editierbar)
│   ├── llama_cpp_20min_praesentation.pdf  # Druck- und präsentationsfertiges PDF
│   └── README.md                     # Kapitelübersicht & WIP-Hinweis
│
├── START_VISITOR_TERMINAL_DEMO.bat   # ⚡ 1-Klick-Starter für das Besucherterminal (Root)
├── .gitignore                        # Ignoriert lokale Tests, Logs und den stuff/-Ordner
└── stuff/                            # 🔒 Lokaler Entwickler-Ordner (Tests, Generatoren, Logs - gitignored)
```

---

## 🚀 Schnellstart für Teilnehmer (`self-service/`)

Möchtest du ein lokales Modell direkt auf deinem Rechner starten?

👉 **Öffne die Anleitung: [`self-service/README.md`](self-service/README.md)**

1. **Modell wählen:** Siehe [`self-service/models_list.md`](self-service/models_list.md) *(Dateien sind auf den verteilten USB-Sticks vorrätig)*.
2. **llama.cpp herunterladen:** Direkt von den [offiziellen GitHub Releases](https://github.com/ggml-org/llama.cpp/releases) anhand der [Cheat Sheets](self-service/).
3. **In einen Ordner entpacken & starten:**
   ```bash
   # Vanilla Startbefehl (Windows: llama-server.exe | Mac/Linux: ./llama-server)
   llama-server -m <modell.gguf> --mmproj <mmproj.gguf> -md <draft.gguf>
   ```
   *(macOS-Hinweis: Quarantäne vorher mit `xattr -r -d com.apple.quarantine .` entfernen)*.

---

## 🏢 Live-Demo: KI-Besucherterminal (`visitor-terminal/`)

Die im Vortrag gezeigte Demo demonstriert modernste lokale Sprach- und Vision-Fähigkeiten ohne Cloud-Abhängigkeit:
- **Pure Gemma 4 Audio:** Keine externe Speech-to-Text-Engine nötig; rohe Audio-WAVs werden direkt multimodal transkribiert und strukturiert (`name`, `company`, `reason`).
- **Ausweis-Druck & Slot-Filling:** Nach erfolgreicher Registrierung wird live ein digitaler Besucherausweis ausgestellt.
- **Start:** Einfach per Doppelklick auf [`START_VISITOR_TERMINAL_DEMO.bat`](START_VISITOR_TERMINAL_DEMO.bat).

---

## 📊 Präsentation (`presentation/`)

> [!NOTE]
> Die Präsentation befindet sich aktuell im Status **Work in Progress (WIP)**. Der aktuelle Folienstand steht sowohl als [PowerPoint `.pptx`](presentation/llama_cpp_20min_praesentation.pptx) als auch als [PDF `.pdf`](presentation/llama_cpp_20min_praesentation.pdf) bereit.
