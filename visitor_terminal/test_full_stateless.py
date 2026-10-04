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
   - Falls kein Personenname genannt wurde: zwingend null!
3. 'company': Firma oder Organisation (im Original; falls privat: 'Privat'; falls noch nicht genannt: null).
4. 'reason': Grund des Besuchs (IMMER ins Deutsche normalisiert, z. B. 'Besprechung', 'Serverwartung', 'Toilettengang', 'Vorstellungsgespräch', 'Sicherheitsaudit'; falls noch nicht genannt: null).

ZUSTANDSFÜHRUNG:
- Der 'Bisherige Stand' der 3 Felder wird im User-Prompt mitgeliefert.
- Behalte bereits bekannte Werte aus dem bisherigen Stand bei, es sei denn, der Besucher korrigiert oder ergänzt sie ausdrücklich.
- Wenn alle 3 Felder ('name', 'company', 'reason') vollständig sind:
  status = 'complete', missing_fields = [], followup_question = 'Vielen Dank! Alle Angaben sind vollständig erfasst. Ihr Ausweis wird gedruckt.'
- Wenn noch Felder fehlen:
  status = 'incomplete', missing_fields = Liste der noch fehlenden Felder, followup_question = gezielte, freundliche deutsche Rückfrage nach den fehlenden Angaben.

Antworte AUSSCHLIESSLICH als valides JSON-Objekt:
{
  "transcription": string,
  "name": string or null,
  "company": string or null,
  "reason": string or null,
  "status": "complete" or "incomplete",
  "missing_fields": string[],
  "followup_question": string
}"""

def call_gemma_stateless(state, text_input):
    summary = f"- Name: {state['name'] if state['name'] else 'null'}\n- Firma: {state['company'] if state['company'] else 'null'}\n- Grund: {state['reason'] if state['reason'] else 'null'}"
    user_prompt = f"Bisheriger Stand:\n{summary}\n\nBesucher sagt: \"{text_input}\"\n\nAktualisiere die 3 Felder im JSON:"
    
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "reasoning_budget_tokens": 0,
        "chat_template_kwargs": {"enable_thinking": False},
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
    return json.loads(res["choices"][0]["message"]["content"])

# Test 1: Turn 1 (Incomplete visitor)
state = {"name": None, "company": None, "reason": None}
print("--- Turn 1: 'ich bin hier für die besprechung mit dem team von tech solutions' ---")
r1 = call_gemma_stateless(state, "ich bin hier für die besprechung mit dem team von tech solutions")
print(json.dumps(r1, indent=2, ensure_ascii=False))

if r1.get("name"): state["name"] = r1["name"]
if r1.get("company"): state["company"] = r1["company"]
if r1.get("reason"): state["reason"] = r1["reason"]

# Test 2: Turn 2 (Supply missing name)
print("\n--- Turn 2: 'Mein Name ist Johannes Müller' ---")
r2 = call_gemma_stateless(state, "Mein Name ist Johannes Müller")
print(json.dumps(r2, indent=2, ensure_ascii=False))

if r2.get("name"): state["name"] = r2["name"]
if r2.get("company"): state["company"] = r2["company"]
if r2.get("reason"): state["reason"] = r2["reason"]

# Check if complete
if state["name"] and state["company"] and state["reason"]:
    state_status = "complete"
else:
    state_status = "incomplete"
print("\nFinal State:", state, "Status:", state_status)

# Test 3: New visitor after complete
if state_status == "complete":
    print("\n--- Auto-Reset: New visitor arrives ---")
    state = {"name": None, "company": None, "reason": None}

print("\n--- Turn 3 (New Visitor): 'john von konklusiv um kurz aufs klo zu gehen' ---")
r3 = call_gemma_stateless(state, "john von konklusiv um kurz aufs klo zu gehen")
print(json.dumps(r3, indent=2, ensure_ascii=False))
