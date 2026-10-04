import urllib.request
import json
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
- 'transcription': Transkribiere wörtlich und präzise, was der Besucher im aktuellen Audio/Text gesagt hat.
- WICHTIG ZUR AKTUALISIERUNG: Wenn der Besucher einen neuen oder anderen Namen, Firma oder Grund nennt, überschreibt dies IMMER den bisherigen Stand!
- Behalte bisherige Werte nur dann bei, wenn der Besucher in seiner neuen Eingabe nichts zu diesem Feld erwähnt.
- Falls noch mindestens ein Feld fehlt (null ist):
  * 'status': 'incomplete'
  * 'missing_fields': Liste der noch fehlenden Feldnamen
  * 'followup_question': Eine kurze, freundliche deutsche Rückfrage nach den fehlenden Angaben.
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

prompt = """Bisheriger Stand:
- Name: John Smith
- Firma: null
- Grund: Meeting

Neue Benutzereingabe (Text): "Bonjour, je m'appelle Pierre Dubois de Renault pour la maintenance du système."
Aktualisiere die Felder:"""

payload = {
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ],
    "response_format": {"type": "json_object"},
    "max_tokens": 1024,
    "temperature": 0.1
}

req = urllib.request.Request(
    "http://127.0.0.1:8080/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
print("RESULT:\n", res["choices"][0]["message"]["content"])
