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
   - "delivery" / "livraison" -> "Lieferung"
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

def send_chat(messages):
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": messages,
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
        content = res["choices"][0]["message"]["content"]
        return json.loads(content)

print("Test 1: Only name")
sess1 = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": "Hallo, ich bin Lisa."}]
r1 = send_chat(sess1)
print("Result 1:", json.dumps(r1, ensure_ascii=False, indent=2))

print("\nTest 2: Turn 2 with company and reason")
sess1.append({"role": "assistant", "content": json.dumps(r1)})
sess1.append({"role": "user", "content": "Ich komme von Apple zum Bewerbungsgespräch."})
r2 = send_chat(sess1)
print("Result 2:", json.dumps(r2, ensure_ascii=False, indent=2))

print("\nTest 3: Fresh session with Spanish input")
sess2 = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": "Hola, soy Carlos de Telefónica para la inspección."}]
r3 = send_chat(sess2)
print("Result 3:", json.dumps(r3, ensure_ascii=False, indent=2))
