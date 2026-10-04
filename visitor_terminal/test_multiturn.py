import urllib.request
import json

SYSTEM_PROMPT = """Du bist ein extrem präziser Empfangs-KI-Assistent an einem Terminal für Besucherausweise.
Deine einzige Aufgabe ist es, aus den Angaben des Besuchers drei Pflichtfelder zu extrahieren:
1. name: Vollständiger Name der Person.
   - WICHTIGE SYNTAKTISCHE REGEL:
     Muster '[Name] von [Firma]' oder '[Name] aus [Firma]':
     -> 'name' ist NUR der Vor- und Nachname ('[Name]').
     -> Schneide 'von [Firma]' oder 'aus [Firma]' strikt ab, es gehört NIEMALS zum Namen!
     -> Beispiel: 'john von konklusiv' -> name: 'John', company: 'Konklusiv'.

2. company: Firma, Organisation oder Arbeitgeber des Besuchers.
   - Wenn der Besucher 'von [Firma]', 'bei [Firma]' oder '[Firma] GmbH/AG/KG/Inc' erwähnt -> company = '[Firma]'.
   - Wenn privat, 'privat' oder kein Firmenbezug -> 'Privat'.
   - Firmennamen bleiben exakt im Original.

3. reason: Der Grund des Besuchs.
   - WICHTIG: Der Besuchsgrund muss IMMER auf DEUTSCH zusammengefasst werden (z.B. 'Toilettengang', 'Serverwartung', 'Vorstellungsgespräch', 'Sicherheitsaudit', 'Meeting', 'Lieferung').
   - Umgangssprachliche Gründe präzise übersetzen: 'aufs klo gehen' -> 'Toilettengang'.

4. DIALOGGEDÄCHTNIS (Multi-Turn):
   - WICHTIG: Wenn in einer vorherigen Nachricht bereits der Name, die Firma oder der Grund genannt wurde, BEHALTE DIESEN WERT UNBEDINGT BEI! Setze ihn NICHT wieder auf null!
   - Kombiniere alle bisherigen Angaben aus dem Chatverlauf.
   - Wenn ALLE 3 Felder aus dem gesamten Verlauf bekannt sind -> status = 'complete', missing_fields = [].
   - Nur wenn ein Feld auch im bisherigen Verlauf NIEMALS genannt wurde -> null, status = 'incomplete'.

WICHTIGSTE REGEL ZUM AUSGABEFORMAT:
Du MUSST in JEDER Antwort IMMER exakt dieses JSON-Schema mit ALLEN 6 Feldern ausgeben. Wenn ein Wert unbekannt ist, MUSS er null sein (nicht weglassen!):
{
  "name": "Vorname Nachname oder null",
  "company": "Original Firma oder Privat oder null",
  "reason": "Besuchsgrund auf Deutsch oder null",
  "status": "complete oder incomplete",
  "missing_fields": ["name", "company", "reason"],
  "followup_question": "Höfliche deutsche Rückfrage oder Bestätigung"
}"""

conv = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Hey, ich bin der Johannes."}
]

def call_gemma(messages):
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": messages,
        "chat_template_kwargs": {"enable_thinking": False},
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    return res["choices"][0]["message"]["content"]

print("--- Turn 1: 'Hey, ich bin der Johannes.' ---")
out1 = call_gemma(conv)
print(out1)

conv.append({"role": "assistant", "content": out1})
conv.append({"role": "user", "content": "Dienstleister von TechSolutions wegen Serverwartung."})

print("\n--- Turn 2: 'Dienstleister von TechSolutions wegen Serverwartung.' ---")
out2 = call_gemma(conv)
print(out2)
