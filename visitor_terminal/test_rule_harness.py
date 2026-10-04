import urllib.request
import json

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Besucher sprechen im Dialog mit dir. Sie sprechen oft umgangssprachlich, kurz oder stichpunktartig.

Deine Kernaufgabe: Extrahiere präzise exakt drei Pflichtfelder für den Besucherausweis:
1. 'name': Der Name / Vorname des Besuchers.
2. 'company': Die Firma oder Organisation des Besuchers. (Falls privat: 'Privat', falls noch nicht genannt: null).
3. 'reason': Der Besuchszweck / Grund (immer präzise ins Deutsche übersetzt, z. B. 'Toilettengang', 'Meeting', 'Wartung').

WICHTIGE SYNTAKTISCHE REGELN FÜR DIE EXTRAKTION:
- Konstruktion "[Name] von [Firma]" (z. B. "John von Konklusiv", "Max von Siemens", "Lisa von Bosch"):
  Das Wort "von" leitet hier IMMER die Firma ein!
  -> 'name': "[Name]" (z. B. "John")
  -> 'company': "[Firma]" (z. B. "Konklusiv")
- Konstruktion "um [Zweck]" / "für [Zweck]" / "wegen [Zweck]" (z. B. "um kurz aufs Klo zu gehen", "fürs Meeting"):
  Das leitet den Grund ein!
  -> 'reason': z. B. "Toilettengang" / "Sanitäre Anlagen" / "Besprechung"
- Wenn ein neuer Name genannt wird, handelt es sich um einen neuen Dialog/Besucher!

STATUS & RÜCKFRAGEN:
- 'status': 'complete' NUR wenn alle 3 Felder ('name', 'company', 'reason') sicher befüllt sind!
- Falls noch mindestens ein Feld null ist:
  * 'status': 'incomplete'
  * 'missing_fields': Liste der noch fehlenden Felder
  * 'followup_question': Gezielte deutsche Rückfrage nach den fehlenden Daten.

Antworte AUSSCHLIESSLICH als valides JSON-Objekt im Schema."""

JSON_SCHEMA = {
  "type": "object",
  "properties": {
    "transcription": {"type": "string"},
    "name": {"type": ["string", "null"]},
    "company": {"type": ["string", "null"]},
    "reason": {"type": ["string", "null"]},
    "status": {"type": "string", "enum": ["complete", "incomplete"]},
    "missing_fields": {"type": "array", "items": {"type": "string"}},
    "followup_question": {"type": "string"}
  },
  "required": ["transcription", "name", "company", "reason", "status", "missing_fields", "followup_question"]
}

def query(text):
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "reasoning_budget_tokens": 0,
        "chat_template_kwargs": {"enable_thinking": False},
        "response_format": {"type": "json_object", "schema": JSON_SCHEMA},
        "max_tokens": 1024,
        "temperature": 0.1
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]

test_cases = [
    "john von konklusiv um kurz aufs klo zu gehen",
    "john von konklusiv kg um kurz aufs klo zu gehen",
    "markus von siemens wegen serverwartung",
    "lisa von bosch zum vorstellungsgespräch",
    "hallo ich bin peter",
    "ich komme von daimler für die abnahme"
]

for t in test_cases:
    print(f"\n--- TEST: '{t}' ---")
    print(query(t))
