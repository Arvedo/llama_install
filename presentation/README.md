# 📊 llama.cpp – Lokale Inferenz ohne Overhead (Präsentation)

> [!WARNING]
> ### 🚧 STATUS: WORK IN PROGRESS (ENTWURF)
> Diese Präsentation befindet sich aktuell noch in aktiver Ausarbeitung.  
> Die Folien und Sprechernotizen spiegeln den aktuellen Entwicklungs- und Prototypenstand wider.

---

## 📁 Verfügbare Dateien

| Datei | Format | Beschreibung |
| :--- | :--- | :--- |
| **[`llama_cpp_20min_praesentation.pptx`](llama_cpp_20min_praesentation.pptx)** | Microsoft PowerPoint (16:9) | Editierbare Master-Präsentation im minimalistischen DIN 1451 / Bahnschrift-Engineering-Stil |
| **[`llama_cpp_20min_praesentation.pdf`](llama_cpp_20min_praesentation.pdf)** | PDF-Dokument (16:9) | Präsentations- und druckfertiger Stand aller Folien |

---

## ⏱️ Folien- und Kapitelübersicht (20 Minuten)

1. **Kapitel 01: Landschaft & Positionierung (Folien 1–3)**
   - *Folie 1:* Titel & Eisbrecher (Single-Stream, Zero-to-Streaming)
   - *Folie 2:* Die Inferenz-Landschaft: Ollama vs. llama.cpp vs. K-Transformers vs. vLLM vs. SGLang
   - *Folie 3:* Positionierung: Wann llama.cpp? (Prototyping, Single-Stream, CPU, Apple Silicon, Mobile)

2. **Kapitel 02: Benchmarks & Story (Folien 4–8)**
   - *Folie 4:* KI-Einstieg: Wer nutzt ChatGPT oder Claude?
   - *Folie 5:* Benchmark 1: ChatGPT-Familie (GPT-4o bis GPT-6 Astra)
   - *Folie 6:* Benchmark 2: Claude-Familie (Claude 3 Opus bis Opus 5.5)
   - *Folie 7:* Benchmark 3: Open-Weights Realität (Empfehlungen & Nuancen)
   - *Folie 8:* Cheat Sheet: Empfohlene Modelle & VRAM-Footprint

3. **Kapitel 03: GGUF, Quants & Quellen (Folien 9–11)**
   - *Folie 9:* Das GGUF-Ökosystem (Single-File Container, mmap zero-copy)
   - *Folie 10:* Quantisierungs-Mastery (8-Bit No-Brainer, 4-Bit Sweet Spot, KV-Cache Quantisierung)
   - *Folie 11:* GGUF-Quellen auf Hugging Face (Unsloth & Underdog AesSedai)

4. **Kapitel 04: Setup & Kompass (Folien 12–15)**
   - *Folie 12:* Download-Kompass: Windows & Linux (CUDA 12 vs 13 vs CPU)
   - *Folie 13:* Download-Kompass: macOS Apple Silicon & Mobile
   - *Folie 14:* In 3 Schritten starten & CLI-Flags (`-m`, `-md`, `--mmproj`)
   - *Folie 15:* Zusatzmodelle: Vision (`--mmproj`) & Turbo mit Drafting (`-md`)

5. **Kapitel 05: Live-Demo (Folie 16)**
   - *Folie 16:* LIVE-DEMO: `llama-server` in Action & OpenAI API Drop-In

6. **Kapitel 06: Fazit & Ressourcen (Folien 17–18)**
   - *Folie 17:* Der Architektur-Kompass (Wann welches Tool?) & 5 Golden Takeaways
   - *Folie 18:* Handout, Ressourcen & GitHub Repository
