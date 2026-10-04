import urllib.request
import json
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Höre das gesprochene Audio des Besuchers an (oder lies seinen Text) und befülle die Pflichtfelder für den Besucherausweis:
1. 'transcription': Was im aktuellen Audio wörtlich gesagt wurde (oder der eingegebene Text). WICHTIG: Transkribiere NIEMALS die Wörter der System- oder Prompt-Instruktionen! Falls in der Aufnahme nur Stille, Rauschen oder nichts zu hören ist: 'Keine Sprache erkannt'.
2. 'name': Vollständiger Personenname (Vor- und/oder Nachname).
   - Schneide Zusätze wie 'von [Firma]' strikt ab (z. B. 'john von konklusiv' -> name = 'John', company = 'Konklusiv').
   - Falls noch kein Personenname genannt wurde: zwingend null!
3. 'company': Firma oder Organisation (im Original; falls privat: 'Privat'; falls noch nicht genannt: null).
4. 'reason': Grund des Besuchs (IMMER ins Deutsche übersetzt, z. B. 'Praktikum', 'Besprechung', 'Serverwartung', 'Toilettengang', 'Vorstellungsgespräch', 'Sicherheitsaudit'; falls noch nicht genannt: null).

ZUSTANDSFÜHRUNG & STATUS-REGEL:
- Wenn alle 3 Felder ('name', 'company', 'reason') vorhanden und ungleich null sind:
  -> status MUSS zwingend 'complete' sein!
  -> missing_fields MUSS [] sein!
  -> followup_question: 'Vielen Dank! Alle Angaben sind vollständig erfasst. Ihr Ausweis wird gedruckt.'
- Wenn mindestens ein Feld fehlt (null ist):
  -> status: 'incomplete'
  -> missing_fields: Liste der noch fehlenden Felder
  -> followup_question: gezielte deutsche Rückfrage nach den fehlenden Angaben.

Antworte AUSSCHLIESSLICH im validen JSON-Format:
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
- Name: null
- Firma: null
- Grund: null

Besucher sagt: "Hello, I'm John. I'm here for the internship and I'm from Microsoft."

Aktualisiere die 3 Pflichtfelder im JSON:"""

payload = {
    "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ],
    "reasoning_budget_tokens": 0,
    "chat_template_kwargs": {"enable_thinking": False},
    "response_format": {"type": "json_object"},
    "max_tokens": 512,
    "temperature": 0.1
}

req = urllib.request.Request(
    "http://127.0.0.1:8080/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
print(res["choices"][0]["message"]["content"])
