# Agent Instructions & System Rules

## ⚠️ CRITICAL RULE 1: NEVER START OR KILL LLAMA.CPP / LLAMA-SERVER PROCESSES
- **DO NOT** run commands that start, restart, kill, or manage `llama-server.exe` or `llama.cpp` processes in background tasks or subshells.
- The user starts, manages, and tests their own `llama-server` instances manually.
- Spawning background `llama-server` tasks causes port conflicts (port 8080), destroys the user's running environment, and breaks active sessions.
- You may write or edit `.bat` scripts or config files when requested, but you must **NEVER** launch `llama-server` yourself.

---

## ⚠️ CRITICAL RULE 2: Context Window Sizing (NEVER Use Outdated / Low Context Limits)

1. **Outdated Context Assumptions:**
   - The default context numbers you (the agent) may assume from older training data (e.g., 2048, 4096, 8192, 16384, 32768) are **strictly outdated** and must **NEVER** be used.
   - Do not arbitrarily artificially constrain model context to tiny values.

2. **Modern Baseline Context (260k+):**
   - Standard modern LLM context windows are **260k+ tokens**.
   - Context configurations below 260k are rare exceptions and should **not** be chosen or configured unless a specific model architecture explicitly dictates otherwise.

3. **Gemma Models Rule (62k+ Minimum, Nothing Below):**
   - Gemma models have smaller context than 260k+, but even for Gemma, the context window is **62k tokens or more** (native training context up to 131,072 / 128k).
   - **ABSOLUTE RULE FOR GEMMA:** **Nothing under 62k.** Never use 4k, 8k, 16k, or 32k.
   - For Gemma invocations (e.g., `llama-server.exe` flag `-c`), use at least `-c 65536` (64k) or the native `-c 131072` (128k).

4. **Batch & Launch Script Generation:**
   - Whenever writing `.bat`, PowerShell, shell scripts, or configuration files for `llama-server`, `llama-cli`, or API clients:
     - For Gemma: Set `-c 65536` (or `-c 131072`).
     - For general modern models: Default to 260k+ or model native capacity.
     - Never hardcode restrictive limits like `-c 8192`.

---

## ⚠️ CRITICAL RULE 3: AUDIO TRANSCRIPTION MUST ALWAYS BE IN THE SPOKEN ORIGINAL LANGUAGE
1. **Verbatim Original Language Transcription:**
   - In all prompts, terminal systems, and translator pipelines, the `transcription` field **MUST ALWAYS** be 100% in the speaker's actual spoken original language.
   - If the user speaks German, the transcription must be verbatim German (e.g. "Hallo, moin, ich bin Johannes...").
   - If the user speaks English, the transcription must be verbatim English.
   - If the user speaks French, Spanish, etc., the transcription must be verbatim French, Spanish, etc.
2. **NEVER Translate the `transcription` Field:**
   - The `transcription` field must **NEVER** be translated into English, German, or any other language.
   - Never invent, translate, or replace greetings or colloquial words into another language (e.g. turning "Moin" into "Hello" or "Good morning").
3. **Strict Separation of Transcription and Translation:**
   - Translations belong **exclusively** in designated translation fields:
     - For the visitor terminal check-in: the `reason` field (which is translated to German for internal company records).
     - For the audio translator: the `german_version` and `english_version` fields.

---

## Architecture & Project Principles

- **No Artificial Blockers or Canned Failure Messages:**
  - Never add client-side gatekeeping checks (e.g. `if (!transcription || transcription === 'Keine Sprache erkannt') return;`) that cut off the user with hardcoded error messages.
  - Send the multimodal input (audio or text) directly to the model. Let the model naturally understand, transcribe, extract, and formulate follow-up questions.
- **No Device STT / TTS:**
  - All speech-to-text (STT) must run 100% natively through the active multimodally-equipped Gemma model via `input_audio`.
  - Never introduce browser Web Speech API (`SpeechRecognition` or `webkitSpeechRecognition`) or browser speech synthesis (`speechSynthesis`).
- **Dynamic Model Binding:**
  - Do not hardcode specific model names in client requests. Detect the active model dynamically from `http://127.0.0.1:8080/v1/models` or omit the `model` key so `llama-server` automatically serves the loaded model.
- **Thinking / Reasoning Handling:**
  - For JSON-formatted structured extraction with multimodal audio, use clean prompts and appropriate token budgets (2048+ tokens). Avoid forcing contradictory thinking loops that burn tokens before JSON generation.
- **Audio Translator Pipeline Architecture (Two-Step Pipeline):**
  - **Step 1 (STT):** Send audio to Gemma with a focused transcription prompt (`TRANSLATOR_STT_SYSTEM_PROMPT`) to get the exact verbatim transcript in the spoken original language (`{"transcription": "..."}`). Displays immediately in the UI.
  - **Step 2 (Translation):** Send the transcript text to Gemma with a dedicated text translation prompt (`TRANSLATOR_TEXT_SYSTEM_PROMPT`) to produce the language detection, German version, and English version. If the user types text directly, Step 1 is bypassed.
