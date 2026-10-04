import urllib.request
import json

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Besucher sprechen im Dialog mit dir (oft umgangssprachlich, stichpunktartig, ohne Großschreibung) in jeder Sprache (Deutsch, Englisch, usw.).

Deine Kernaufgabe: Führe den Check-in Dialog und befülle exakt drei Pflichtfelder für den Besucherausweis:
1. 'transcription': Das Gesprochene/Eingegebene wortwörtlich.
2. 'name': NUR der Name der Person (Vor- und/oder Nachname).
   - Schneide Firmenzusätze wie 'von ...' strikt ab (aus 'john von konklusiv' wird name = 'John')!
   - Falls die Person ihren Namen noch NICHT genannt hat: zwingend null! Setze niemals Firmen als Namen ein!
3. 'company': Die Firma oder Organisation (im Original unübersetzt; falls privat: 'Privat'; falls noch nicht genannt: null).
4. 'reason': Der Besuchszweck / Anlass (IMMER ins Deutsche übersetzt, z. B. 'Toilettengang', 'Besprechung', 'Wartung', 'Sicherheitsaudit', 'Lieferung'; falls noch nicht genannt: null).

SYNTAKTISCHE ERKENNUNGSREGELN:
- Muster '[Name] von [Firma]' (z. B. 'john von konklusiv', 'max von siemens', 'sarah von bosch'):
  -> 'name': nur der Personenname ('John', 'Max', 'Sarah')
  -> 'company': die Organisation ('Konklusiv', 'Siemens', 'Bosch')
- Muster 'von [Firma] für/wegen/um ...' (ohne Name):
  -> 'name': null (fehlt noch!)
  -> 'company': [Firma]
- Muster 'um ... zu [Verb]', 'für [Zweck]', 'wegen [Zweck]' (z. B. 'um kurz aufs klo zu gehen', 'fürs meeting', 'wegen reparatur'):
  -> 'reason': der Besuchszweck ins Deutsche normalisiert ('Toilettengang', 'Besprechung', 'Reparatur')

SITZUNGS-LOGIK:
- Wenn ein neuer Besucher spricht oder der vorherige Ausweis schon komplett war: Beginne eine frische Extraktion für den neuen Besucher!
- Wenn in einem unvollständigen Dialog ein Feld ergänzt wird: Ergänze den bisherigen Besucher.

STATUS:
- 'status': 'complete' NUR wenn alle 3 Pflichtfelder ('name', 'company', 'reason') ungleich null und sicher bekannt sind.
- Falls noch Felder fehlen (null sind): 'status': 'incomplete', 'missing_fields': Liste der fehlenden Felder, 'followup_question': gezielte deutsche Rückfrage.

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
    "von sap zum vorstellungsgespräch",
    "john von konklusiv um kurz aufs klo zu gehen",
    "hallo ich bin claudia",
    "dienstleister von techsolutions wegen serverwartung"
]

for t in test_cases:
    print(f"\n--- TEST: '{t}' ---")
    print(query(t))
