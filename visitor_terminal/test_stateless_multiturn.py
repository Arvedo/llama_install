import urllib.request
import json
import base64
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Höre das gesprochene Audio des Besuchers an (oder lies seinen Text) und befülle die Pflichtfelder für den Besucherausweis:
1. 'transcription': Was im aktuellen Audio wörtlich gesagt wurde. Bei Stille/unverständlich: 'Keine Sprache erkannt'.
2. 'name': Vollständiger Personenname (oder null). Schneide 'von [Firma]' strikt ab. Falls kein Personenname genannt: null!
3. 'company': Firma des Besuchers (oder 'Privat', falls privat; sonst null).
4. 'reason': Grund des Besuchs (IMMER auf Deutsch normalisiert, z. B. 'Besprechung', 'Serverwartung', 'Toilettengang'; sonst null).

ZUSTANDSFÜHRUNG:
- Der 'Bisherige Stand' der 3 Felder wird im Prompt mitgeliefert.
- Behalte bereits bekannte Werte aus dem bisherigen Stand bei, es sei denn, der Besucher korrigiert oder ergänzt sie.
- Wenn alle 3 Pflichtfelder ('name', 'company', 'reason') vollständig sind:
  status = 'complete', missing_fields = [], followup_question = 'Vielen Dank! Alle Angaben sind vollständig erfasst. Ihr Ausweis wird gedruckt.'
- Wenn noch Felder fehlen:
  status = 'incomplete', missing_fields = Liste der fehlenden Felder, followup_question = gezielte deutsche Rückfrage nach den fehlenden Angaben.

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

def call_stateless(state, input_type, input_payload):
    current_summary = f"- Name: {state['name'] if state['name'] else 'null'}\n- Firma: {state['company'] if state['company'] else 'null'}\n- Grund: {state['reason'] if state['reason'] else 'null'}"
    
    if input_type == "text":
        user_content = f"Bisheriger Stand:\n{current_summary}\n\nBesucher sagt: \"{input_payload}\"\n\nAktualisiere die 3 Felder im JSON:"
    else:
        user_content = [
            {"type": "text", "text": f"Bisheriger Stand:\n{current_summary}\n\nHöre dieses Audio an, transkribiere es und aktualisiere die 3 Felder im JSON:"},
            {"type": "input_audio", "input_audio": {"data": input_payload, "format": "wav"}}
        ]
        
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
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
    parsed = json.loads(res["choices"][0]["message"]["content"])
    return parsed

# State maintained by CLIENT HARNESS
client_state = {"name": None, "company": None, "reason": None}

print("=== SCENARIO 1: User says 'ich bin hier für die besprechung mit dem team von tech solutions' ===")
res1 = call_stateless(client_state, "text", "ich bin hier für die besprechung mit dem team von tech solutions")
print("Response Turn 1:")
print(json.dumps(res1, indent=2, ensure_ascii=False))

# Update client state with non-null values
if res1.get("name"): client_state["name"] = res1["name"]
if res1.get("company"): client_state["company"] = res1["company"]
if res1.get("reason"): client_state["reason"] = res1["reason"]

print("\nClient State after Turn 1:", client_state)

print("\n=== SCENARIO 2: In Turn 2, User answers followup question: 'Mein Name ist Johannes.' ===")
res2 = call_stateless(client_state, "text", "Mein Name ist Johannes.")
print("Response Turn 2:")
print(json.dumps(res2, indent=2, ensure_ascii=False))

if res2.get("name"): client_state["name"] = res2["name"]
if res2.get("company"): client_state["company"] = res2["company"]
if res2.get("reason"): client_state["reason"] = res2["reason"]

print("\nClient State after Turn 2:", client_state)
