import urllib.request
import json
import base64

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Deine Kernaufgabe: Analysiere die Benutzereingabe (Sprach-Audio oder Text), transkribiere sie präzise und befülle exakt drei Pflichtfelder für den Besucherausweis:
1. 'name': Vollständiger Name oder Vorname des Besuchers. (Falls noch unbekannt: null)
2. 'company': Firma oder Organisation des Besuchers. WICHTIG: Wenn der Besucher privat da ist, keine Firma hat oder 'privat' sagt, trage 'Privat' ein. (Falls noch unbekannt: null)
3. 'reason': Konkreter Anlass / Grund des Besuchs (z. B. 'Serverwartung', 'Meeting', 'Vorstellungsgespräch', 'Lieferung'). (Falls noch unbekannt: null)

REGELN FÜR DIE TRANSKRIPTION ('transcription'):
- Falls eine Audioaufnahme übergeben wird: Transkribiere das gesprochene Audio wortwörtlich und vollständig in das Feld 'transcription'.
- Falls nur Text übergeben wird: Setze den übergebenen Text als 'transcription'.
- Falls das Audio unklar oder nur Rauschen ist: Setze 'transcription': '[Unverständliche Sprache oder Geräusch]'.

REGELN FÜR DEN STATUS & SLOT-FILLING:
- Behalte bereits ermittelte Werte aus 'Bisheriger Zustand' zwingend bei! Überschreibe sie nur, wenn der Benutzer sie explizit korrigiert.
- Prüfe, welche der 3 Felder ('name', 'company', 'reason') noch null sind.
- Falls noch mindestens ein Feld null ist:
  * 'status': 'incomplete'
  * 'missing_fields': Liste der fehlenden Feldnamen (z. B. ['company', 'reason'])
  * 'followup_question': Eine freundliche, präzise deutsche Rückfrage, die gezielt nach den noch fehlenden Angaben fragt.
- Falls alle 3 Felder ('name', 'company', 'reason') befüllt sind:
  * 'status': 'complete'
  * 'missing_fields': []
  * 'followup_question': 'Vielen Dank! Alle Angaben sind vollständig. Ihr Besucherausweis wird gedruckt.'

BEISPIELE (FEW-SHOT):
Beispiel 1 (Nur Name genannt):
Zustand: {"name": null, "company": null, "reason": null}
Eingabe: "Hey, ich bin der Johannes."
-> {"transcription": "Hey, ich bin der Johannes.", "name": "Johannes", "company": null, "reason": null, "status": "incomplete", "missing_fields": ["company", "reason"], "followup_question": "Hallo Johannes! Von welcher Firma kommen Sie und was ist der Grund Ihres Besuchs?"}

Beispiel 2 (Ergänzung in Turn 2):
Zustand: {"name": "Johannes", "company": null, "reason": null}
Eingabe: "Ich bin Dienstleister von der TechSolutions GmbH wegen der Serverwartung."
-> {"transcription": "Ich bin Dienstleister von der TechSolutions GmbH wegen der Serverwartung.", "name": "Johannes", "company": "TechSolutions GmbH", "reason": "Serverwartung", "status": "complete", "missing_fields": [], "followup_question": "Vielen Dank! Alle Angaben sind vollständig. Ihr Besucherausweis wird gedruckt."}

Beispiel 3 (Privater Besuch):
Zustand: {"name": null, "company": null, "reason": null}
Eingabe: "Guten Tag, ich bin privat hier für den Elternsprechtag, mein Name ist Claudia."
-> {"transcription": "Guten Tag, ich bin privat hier für den Elternsprechtag, mein Name ist Claudia.", "name": "Claudia", "company": "Privat", "reason": "Elternsprechtag", "status": "complete", "missing_fields": [], "followup_question": "Vielen Dank! Alle Angaben sind vollständig. Ihr Besucherausweis wird gedruckt."}

WICHTIG: Antworte AUSSCHLIESSLICH als valides JSON-Objekt ohne Erklärungen oder Markdown-Codeblöcke."""

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

def query(current_state, text_or_audio):
    content = [
        {"type": "text", "text": f"Bisheriger Zustand: {json.dumps(current_state, ensure_ascii=False)}\nEingabe:"}
    ]
    if isinstance(text_or_audio, dict) and "audio_b64" in text_or_audio:
        content.append({
            "type": "input_audio",
            "input_audio": {"data": text_or_audio["audio_b64"], "format": "wav"}
        })
    else:
        content[0]["text"] += f' "{str(text_or_audio)}"'

    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content}
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
        return json.loads(res["choices"][0]["message"]["content"])

if __name__ == "__main__":
    s0 = {"name": None, "company": None, "reason": None}
    print("--- Turn 1 (Only Name) ---")
    r1 = query(s0, "Hey, ich bin der Johannes.")
    print(json.dumps(r1, indent=2, ensure_ascii=False))

    print("\n--- Turn 2 (Company + Reason added) ---")
    r2 = query({"name": r1["name"], "company": r1["company"], "reason": r1["reason"]}, "Ich bin Dienstleister von der TechSolutions GmbH wegen der Serverwartung.")
    print(json.dumps(r2, indent=2, ensure_ascii=False))
