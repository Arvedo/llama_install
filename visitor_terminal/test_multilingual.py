import urllib.request
import json

SYSTEM_PROMPT = """Du bist das intelligente multilinguale Empfangsterminal eines deutschen Unternehmens.
Besucher können in JEDER beliebigen Sprache sprechen (Deutsch, Englisch, Französisch, Spanisch usw.).

Deine Kernaufgabe:
1. 'transcription': Transkribiere die gesprochene Sprache wortwörtlich in der Originalsprache des Besuchers.
2. 'name': Der Name des Besuchers (bleibt IMMER im Original unübersetzt, z. B. 'John Smith', 'Jean Dupont', oder null).
3. 'company': Die Firma oder Organisation des Besuchers (bleibt IMMER im Original unübersetzt, z. B. 'Acme Corp', 'Renault'; falls privat oder keine Firma: 'Privat', oder null).
4. 'reason': Der Besuchszweck / Grund des Besuchs.
   *** WICHTIGE REGEL: 'reason' MUSS IMMER SAUBER UND PRÄZISE INS DEUTSCHE ÜBERSETZT WERDEN! ***
   Beispiele für die Übersetzung von 'reason':
   - "server maintenance" -> "Serverwartung"
   - "quarterly security audit" -> "Quartals-Sicherheitsaudit"
   - "job interview" -> "Vorstellungsgespräch"
   - "entretien d'embauche" -> "Vorstellungsgespräch"
   - "inspección técnica de los ascensores" -> "Technische Aufzugsprüfung"
   - "meeting with Mrs. Schmidt" -> "Besprechung mit Fr. Schmidt"
   Falls der Grund noch nicht genannt wurde: null.

REGELN FÜR STATUS & RÜCKFRAGEN:
- Behalte bekannte Werte aus 'Bisheriger Zustand' zwingend bei!
- Falls noch mindestens ein Feld fehlt (null ist):
  * 'status': 'incomplete'
  * 'missing_fields': Liste der noch fehlenden Felder
  * 'followup_question': Eine kurze, freundliche deutsche Rückfrage nach den fehlenden Daten.
- Falls alle 3 Felder ('name', 'company', 'reason') vollständig sind:
  * 'status': 'complete'
  * 'missing_fields': []
  * 'followup_question': 'Vielen Dank! Alle Angaben sind vollständig. Ihr Besucherausweis wird gedruckt.'

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

def query(text, state=None):
    if state is None:
        state = {"name": None, "company": None, "reason": None}
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Bisheriger Zustand: {json.dumps(state, ensure_ascii=False)}\nEingabe des Besuchers: \"{text}\""}
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
        return json.loads(json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"])

if __name__ == "__main__":
    print("--- Test 1: English ---")
    res_en = query("Hello, my name is John Smith from Acme Corp for the quarterly security audit.")
    print(json.dumps(res_en, indent=2, ensure_ascii=False))

    print("\n--- Test 2: French ---")
    res_fr = query("Bonjour, je m'appelle Pierre Dubois de Renault pour la maintenance du système.")
    print(json.dumps(res_fr, indent=2, ensure_ascii=False))

    print("\n--- Test 3: Spanish (Slot filling 2 turns) ---")
    res_es1 = query("Hola, soy Alejandro Garcia.")
    print("Turn 1:", json.dumps(res_es1, indent=2, ensure_ascii=False))
    res_es2 = query("Vengo de Iberdrola para la reparación de los servidores.", res_es1)
    print("Turn 2:", json.dumps(res_es2, indent=2, ensure_ascii=False))
