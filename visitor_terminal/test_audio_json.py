import urllib.request
import json
import base64

wav_path = r"c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\speech.wav"
with open(wav_path, "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode("utf-8")

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Höre das gesprochene Audio des Besuchers an und extrahiere exakt drei Pflichtfelder für den Besucherausweis:
1. 'name': Vollständiger Name des Besuchers (oder null).
2. 'company': Firma des Besuchers (oder 'Privat', falls privat; sonst null).
3. 'reason': Grund des Besuchs (oder null).

REGELN:
- Behalte bereits erfasste Daten aus 'bisheriger_zustand' bei!
- Transkribiere in 'transcription' wörtlich auf Deutsch, was im Audio gesagt wurde.
- Falls Angaben fehlen (mindestens ein Feld noch null):
  * Setze 'status': 'incomplete'
  * Liste in 'missing_fields' die noch fehlenden Felder auf.
  * Formuliere in 'followup_question' eine kurze, freundliche deutsche Rückfrage nach den fehlenden Angaben.
- Falls alle 3 Felder ('name', 'company', 'reason') vollständig sind:
  * Setze 'status': 'complete'
  * Setze 'missing_fields': []
  * Setze 'followup_question': 'Vielen Dank! Alle Angaben sind vollständig. Ihr Besucherausweis wird gedruckt.'

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
                {"type": "text", "text": "Bisheriger Zustand: {\"name\": null, \"company\": null, \"reason\": null}\nAnalysiere dieses Audio:"},
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_b64,
                        "format": "wav"
                    }
                }
            ]
        }
    ],
    "reasoning_budget_tokens": 0,
    "chat_template_kwargs": {"enable_thinking": False},
    "response_format": {"type": "json_object"},
    "max_tokens": 1024,
    "temperature": 0.1
}

req = urllib.request.Request(
    "http://127.0.0.1:8080/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("Tokens used:", res.get("usage"))
        print("Direct Audio-to-JSON Response:\n", res["choices"][0]["message"]["content"])
except Exception as e:
    if hasattr(e, "read"):
        print("Error:", e.read().decode())
    else:
        print("Error:", e)
