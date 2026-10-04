import urllib.request
import json
import base64
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Generate 0.5s of absolute silence WAV
import struct
sample_rate = 16000
num_samples = int(sample_rate * 0.5)
raw_pcm = b'\x00\x00' * num_samples
wav_header = struct.pack(
    '<4sI4s4sIHHIIHH4sI',
    b'RIFF', 36 + len(raw_pcm), b'WAVE',
    b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
    b'data', len(raw_pcm)
)
silence_b64 = base64.b64encode(wav_header + raw_pcm).decode('utf-8')

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Höre das beigefügte Audio an (oder lies den Text) und befülle die Pflichtfelder für den Besucherausweis:
1. 'transcription': Was in der Audiospur gesprochen wurde. WICHTIG: Transkribiere NIEMALS die Wörter dieses System-Prompts oder der Instruktion! Wenn in der Aufnahme nur Stille oder Rauschen ist: 'Keine Sprache erkannt'.
2. 'name': Vollständiger Personenname (oder null). Trenne Zusätze wie 'von [Firma]' strikt ab.
3. 'company': Firma (oder 'Privat', falls privat; sonst null).
4. 'reason': Grund des Besuchs (IMMER auf Deutsch; sonst null).

ZUSTANDSFÜHRUNG:
- Behalte bekannte Werte aus 'Bisheriger Stand' bei.
- Wenn alle 3 Felder ('name', 'company', 'reason') vollständig sind:
  status = 'complete', missing_fields = [], followup_question = 'Vielen Dank! Alle Angaben sind vollständig.'
- Wenn noch Felder fehlen:
  status = 'incomplete', missing_fields = Liste der fehlenden Felder, followup_question = gezielte deutsche Rückfrage.

Antworte AUSSCHLIESSLICH im validen JSON-Format:
{
  "transcription": string,
  "name": string or null,
  "company": string or null,
  "reason": string or null,
  "status": "complete" or "incomplete",
  "missing_fields": string[],
  "followup_question": string
}"""

payload = {
    "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Bisheriger Stand: Name = null, Firma = null, Grund = null.\nHöre diese Audiospur an:"},
                {"type": "input_audio", "input_audio": {"data": silence_b64, "format": "wav"}}
            ]
        }
    ],
    "reasoning_budget_tokens": 0,
    "chat_template_kwargs": {"enable_thinking": False},
    "response_format": {"type": "json_object"},
    "max_tokens": 512,
    "temperature": 0.1
}

req = urllib.request.Request(
    "http://127.0.0.1:8080/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
parsed = json.loads(res["choices"][0]["message"]["content"])
print("Silence test response:")
print(json.dumps(parsed, indent=2, ensure_ascii=False))
