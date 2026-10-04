import urllib.request
import json

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Besucher registrieren sich über Sprach- oder Texteingaben, um einen Besucherausweis zu erhalten.

Deine Aufgabe ist es, exakt DREI Pflichtfelder für den Besucherausweis strukturiert zu erfassen:
1. 'name': Vollständiger Name oder Vorname des Besuchers. (Falls noch unbekannt: null)
2. 'company': Firma oder Organisation, von der der Besucher kommt. Falls der Besucher privat da ist, keine Firma hat oder 'privat' angibt, trage 'Privat' ein. (Falls noch unbekannt: null)
3. 'reason': Grund oder Zweck des Besuchs (z. B. 'Serverwartung', 'Vorstellungsgespräch', 'Lieferung', 'Meeting mit Fr. Müller'). (Falls noch unbekannt: null)

REGELN:
- Behalte bereits ermittelte Werte aus 'bisheriger_zustand' bei! Überschreibe sie nur, wenn der Benutzer sie explizit korrigiert.
- Prüfe, welche der 3 Felder noch 'null' sind.
- Falls noch mindestens ein Feld fehlt (null ist):
  * Setze 'status': 'incomplete'
  * Liste in 'missing_fields' die noch fehlenden Feldnamen auf.
  * Formuliere in 'followup_question' eine kurze, freundliche und präzise Rückfrage auf Deutsch, die den Besucher nach den genau noch fehlenden Informationen fragt.
- Falls alle 3 Felder ('name', 'company', 'reason') erfolgreich befüllt sind:
  * Setze 'status': 'complete'
  * Setze 'missing_fields': []
  * Setze 'followup_question': 'Vielen Dank! Alle Angaben sind vollständig. Ihr Besucherausweis wird gedruckt.'

Antworte AUSSCHLIESSLICH als valides JSON-Objekt in folgendem Format:
{
  "name": string | null,
  "company": string | null,
  "reason": string | null,
  "status": "complete" | "incomplete",
  "missing_fields": string[],
  "followup_question": string
}"""

def query_terminal(state, user_text):
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Bisheriger Zustand:\n{json.dumps(state, ensure_ascii=False)}\n\nNeue Benutzereingabe:\n\"{user_text}\""}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        raw = body["choices"][0]["message"]["content"]
        # In case the model wrapped it in markdown codeblocks
        if "```" in raw:
            raw = raw.split("```json")[-1].split("```")[0].strip()
        return json.loads(raw)

if __name__ == "__main__":
    state0 = {"name": None, "company": None, "reason": None}
    print("--- Test Turn 1: 'Hey, ich bin der Johannes' ---")
    res1 = query_terminal(state0, "Hey, ich bin der Johannes")
    print(json.dumps(res1, indent=2, ensure_ascii=False))

    print("\n--- Test Turn 2: 'Ich bin Dienstleister von der TechSolutions GmbH wegen der Serverwartung.' ---")
    res2 = query_terminal(res1, "Ich bin Dienstleister von der TechSolutions GmbH wegen der Serverwartung.")
    print(json.dumps(res2, indent=2, ensure_ascii=False))

    print("\n--- Test Alternative: 'Guten Tag, ich bin privat hier wegen dem Elternsprechtag, mein Name ist Claudia' ---")
    res_privat = query_terminal(state0, "Guten Tag, ich bin privat hier wegen dem Elternsprechtag, mein Name ist Claudia")
    print(json.dumps(res_privat, indent=2, ensure_ascii=False))
