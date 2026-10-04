import urllib.request
import json
import base64
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Besucher registrieren sich über Sprach- oder Texteingaben, um einen Besucherausweis zu erhalten.

Deine Aufgabe ist es, exakt DREI Pflichtfelder für den Besucherausweis strukturiert zu erfassen:
1. 'name': Vollständiger Personenname (Vor- und/oder Nachname). Schneide Firmenzusätze wie 'von [Firma]' strikt ab (z. B. 'John von Microsoft' -> name = 'John', company = 'Microsoft'). Falls noch unbekannt: null.
2. 'company': Firma oder Organisation des Besuchers (im Original unübersetzt; falls privat: 'Privat'). Falls noch unbekannt: null.
3. 'reason': Grund des Besuchs. Übersetze den Grund IMMER VOLLSTÄNDIG ins DEUTSCHE (z. B. 'Meeting', 'Serverwartung', 'Vorstellungsgespräch', 'Lieferung'). Falls noch unbekannt: null.

REGELN:
- 'transcription': Transkribiere wörtlich und präzise, was der Besucher im Audio gesagt hat.
- Behalte bereits ermittelte Werte aus 'Bisheriger Stand' bei!
- Falls noch mindestens ein Feld fehlt (null ist):
  * 'status': 'incomplete'
  * 'missing_fields': Liste der noch fehlenden Feldnamen
  * 'followup_question': Eine kurze, freundliche Rückfrage auf Deutsch nach den fehlenden Angaben.
- Falls alle 3 Felder ('name', 'company', 'reason') vollständig sind:
  * 'status': 'complete'
  * 'missing_fields': []
  * 'followup_question': 'Vielen Dank! Alle Angaben sind vollständig. Ihr Besucherausweis wird gedruckt.'

Antworte AUSSCHLIESSLICH als valides JSON-Objekt in folgendem Format:
{
  "transcription": string,
  "name": string or null,
  "company": string or null,
  "reason": string or null,
  "status": "complete" or "incomplete",
  "missing_fields": string[],
  "followup_question": string
}"""

wav_path = r"c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\logs\audio\audio_20261004_133352_VIS-52712.wav"
with open(wav_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

user_prompt = "Bisheriger Stand:\n- Name: null\n- Firma: null\n- Grund: null\n\nHöre das beigefügte Audio des Besuchers an und extrahiere die Pflichtfelder:"

payload = {
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": [
            {"type": "text", "text": user_prompt},
            {"type": "input_audio", "input_audio": {"data": b64, "format": "wav"}}
        ]}
    ],
    "response_format": {"type": "json_object"},
    "max_tokens": 2048,
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
        print("CONTENT:\n", res["choices"][0]["message"].get("content"))
        print("REASONING:\n", res["choices"][0]["message"].get("reasoning_content")[:300] if res["choices"][0]["message"].get("reasoning_content") else "None")
except Exception as e:
    print("Error:", e)
