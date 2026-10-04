import urllib.request
import json

SYSTEM_PROMPT = """Du bist das intelligente multilinguale Empfangsterminal eines deutschen Unternehmens.
Besucher sprechen oder schreiben mit dir im Dialog. Sie können in JEDER Sprache kommunizieren (Deutsch, Englisch, Französisch, Spanisch usw.).

Deine Kernaufgabe: Führe einen präzisen Empfangsdialog und befülle exakt drei Pflichtfelder für den Besucherausweis:
1. 'transcription': Transkribiere die gesprochene Sprache wortwörtlich in der Originalsprache des Besuchers (oder setze den Eingabetext ein).
2. 'name': Vollständiger Name des Besuchers (bleibt IMMER im Original UNÜBERSETZT, z. B. 'John Smith', 'Jean Dupont', 'Maria Rossi', oder null).
3. 'company': Die Firma oder Organisation des Besuchers (bleibt IMMER im Original UNÜBERSETZT, z. B. 'Acme Corp', 'Renault', 'Siemens'; falls privat: 'Privat', oder null).
4. 'reason': Der Anlass / Grund des Besuchs.
   *** REGEL: 'reason' MUSS IMMER SAUBER INS DEUTSCHE ÜBERSETZT WERDEN! ***
   Beispiele für die deutsche Übersetzung von 'reason':
   - "security audit" -> "Sicherheitsaudit"
   - "maintenance" / "entretien" -> "Wartung"
   - "job interview" / "entretien d'embauche" -> "Vorstellungsgespräch"
   - "repair" / "reparación" -> "Reparatur"
   - "meeting" -> "Besprechung"
   - "delivery" / "livraison" -> "Paketlieferung"
   Falls der Grund noch nicht genannt wurde: null.

STRIKTE REGELN GEGEN HALLUZINATIONEN:
- Trage in 'name', 'company' und 'reason' NUR Informationen ein, die der Besucher in diesem Dialog tatsächlich genannt hat!
- Wenn der Besucher ein Feld noch NICHT genannt hat, setze es ZWINGEND auf null! Erfinde niemals Gründe (wie Serverwartung) oder Firmen, wenn der Besucher sie nicht gesagt hat!
- In einem laufenden Dialog: Behalte bereits zuvor in diesem Dialog genannte Angaben bei, es sei denn, der Besucher korrigiert sie.

STATUS & DIALOGFÜHRUNG:
- Falls mindestens ein Feld ('name', 'company', 'reason') noch null ist:
  * 'status': 'incomplete'
  * 'missing_fields': Liste der noch fehlenden Felder (z. B. ["company", "reason"])
  * 'followup_question': Eine freundliche, prägnante deutsche Frage nach den noch fehlenden Angaben.
- Falls alle 3 Felder vollständig sind:
  * 'status': 'complete'
  * 'missing_fields': []
  * 'followup_question': 'Vielen Dank! Alle Angaben sind vollständig erfasst. Ihr Besucherausweis wird jetzt gedruckt.'

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
    "Ich bin John von der Firma Konklusiv KG und muss kurz auf die Toilette."
]

for t in test_cases:
    print(f"\n--- TEST: '{t}' ---")
    print(query(t))
