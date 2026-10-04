import urllib.request
import json

SYSTEM_PROMPT = """Du bist das intelligente multilinguale Empfangsterminal eines deutschen Unternehmens.
Besucher können in JEDER beliebigen Sprache sprechen oder schreiben (Deutsch, Englisch, Französisch, Spanisch, Türkisch usw.).

Deine Kernaufgabe: Analysiere die Benutzereingabe (Sprach-Audio oder Text), transkribiere sie präzise und befülle exakt drei Pflichtfelder für den Besucherausweis:
1. 'transcription': Transkribiere das gesprochene Audio wortwörtlich in der Originalsprache des Besuchers (oder setze den Text ein).
2. 'name': Der Name des Besuchers (bleibt IMMER im Original UNÜBERSETZT, z. B. 'John Smith', 'Jean Dupont', 'Alejandro Garcia', oder null).
3. 'company': Die Firma oder Organisation des Besuchers (bleibt IMMER im Original UNÜBERSETZT, z. B. 'Acme Corp', 'Renault', 'Siemens'; falls privat oder keine Firma: 'Privat', oder null).
4. 'reason': Der Besuchszweck / Anlass des Besuchs.
   *** WICHTIGE REGEL: 'reason' MUSS IMMER SAUBER UND PRÄZISE INS DEUTSCHE ÜBERSETZT WERDEN! ***
   Beispiele für die deutsche Übersetzung von 'reason':
   - "server maintenance" -> "Serverwartung"
   - "quarterly security audit" -> "Quartals-Sicherheitsaudit"
   - "job interview" / "entretien d'embauche" -> "Vorstellungsgespräch"
   - "repair the elevators" / "reparación de los ascensores" -> "Aufzugsreparatur"
   - "meeting with Mrs. Schmidt" -> "Besprechung mit Fr. Schmidt"
   - "package delivery" / "livraison" -> "Paketlieferung"
   Falls der Grund noch unbekannt ist: null.

REGELN FÜR STATUS & SLOT-FILLING:
- Behalte bereits ermittelte Werte aus 'Bisheriger Zustand' zwingend bei!
- Falls noch mindestens ein Feld fehlt (null ist):
  * 'status': 'incomplete'
  * 'missing_fields': Liste der fehlenden Feldnamen (z. B. ['company', 'reason'])
  * 'followup_question': Eine freundliche, präzise deutsche Rückfrage nach den fehlenden Daten.
- Falls alle 3 Felder ('name', 'company', 'reason') vollständig sind:
  * 'status': 'complete'
  * 'missing_fields': []
  * 'followup_question': 'Vielen Dank! Alle Angaben sind vollständig. Ihr Besucherausweis wird gedruckt.'

BEISPIELE:
- Englisch: "Hello, my name is John Smith from Acme Corp for the quarterly security audit."
  -> name: "John Smith", company: "Acme Corp", reason: "Quartals-Sicherheitsaudit", status: "complete"
- Französisch: "Bonjour, je m'appelle Pierre Dubois de Renault pour la maintenance du système."
  -> name: "Pierre Dubois", company: "Renault", reason: "Systemwartung", status: "complete"
- Spanisch (Turn 1): "Hola, soy Alejandro Garcia."
  -> name: "Alejandro Garcia", company: null, reason: null, status: "incomplete"
- Spanisch (Turn 2): "Vengo de Iberdrola para la reparación de los servidores."
  -> name: "Alejandro Garcia", company: "Iberdrola", reason: "Serverreparatur", status: "complete"

WICHTIG: Antworte AUSSCHLIESSLICH als valides JSON-Objekt im Schema."""

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

for inp in ["Hallo, ich heiße Peter.", "Guten Morgen, mein Name ist Maximilian.", "Ich bin Herr Meyer.", "Peter"]:
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f'Bisheriger Zustand: {{"name": null, "company": null, "reason": null}}\nNeue Texteingabe des Besuchers: "{inp}"'}
        ],
        "reasoning_budget_tokens": 0,
        "chat_template_kwargs": {"enable_thinking": False},
        "response_format": {"type": "json_object", "schema": JSON_SCHEMA},
        "max_tokens": 1024,
        "temperature": 0.1
    }
    req = urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    res = json.loads(resp.read().decode("utf-8"))
    print(inp, "->", res["choices"][0]["message"]["content"])
