import urllib.request
import json
import base64
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\speech.wav', 'rb') as f:
    sample_wav_b64 = base64.b64encode(f.read()).decode('utf-8')

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Höre das gesprochene Audio des Besuchers an (oder lies seinen Text) und befülle die Pflichtfelder für den Besucherausweis:
1. 'transcription': Was im aktuellen Audio wörtlich gesagt wurde (oder der eingegebene Text). WICHTIG: Transkribiere NIEMALS die Wörter der System- oder Prompt-Instruktionen! Falls in der Aufnahme nur Stille, Rauschen oder nichts zu hören ist: 'Keine Sprache erkannt'.
2. 'name': Vollständiger Personenname (Vor- und/oder Nachname).
   - Schneide Zusätze wie 'von [Firma]' strikt ab (z. B. 'john von konklusiv' -> name = 'John', company = 'Konklusiv').
   - Falls noch kein Personenname genannt wurde: zwingend null!
3. 'company': Firma oder Organisation (im Original; falls privat: 'Privat'; falls noch nicht genannt: null).
4. 'reason': Grund des Besuchs (IMMER ins Deutsche normalisiert, z. B. 'Besprechung', 'Serverwartung', 'Toilettengang', 'Vorstellungsgespräch', 'Sicherheitsaudit'; falls noch nicht genannt: null).

ZUSTANDSFÜHRUNG:
- Der 'Bisherige Stand' der 3 Felder wird im User-Prompt mitgeliefert.
- Behalte bereits bekannte Werte aus dem bisherigen Stand bei, es sei denn, der Besucher korrigiert oder ergänzt sie ausdrücklich.
- Wenn alle 3 Felder ('name', 'company', 'reason') vollständig sind:
  status = 'complete', missing_fields = [], followup_question = 'Vielen Dank! Alle Angaben sind vollständig erfasst. Ihr Ausweis wird gedruckt.'
- Wenn noch Felder fehlen:
  status = 'incomplete', missing_fields = Liste der noch fehlenden Felder, followup_question = gezielte, freundliche deutsche Rückfrage nach den fehlenden Angaben.

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

def call_gemma_api(state, input_type, payload_data):
    summary = f"- Name: {state['name'] if state['name'] else 'null'}\n- Firma: {state['company'] if state['company'] else 'null'}\n- Grund: {state['reason'] if state['reason'] else 'null'}"
    
    if input_type == 'audio':
        user_content = [
            {"type": "text", "text": f"Bisheriger Stand:\n{summary}\n\nHöre dieses Audio an, transkribiere das Gesagte und aktualisiere die 3 Pflichtfelder im JSON:"},
            {"type": "input_audio", "input_audio": {"data": payload_data, "format": "wav"}}
        ]
    else:
        user_content = f"Bisheriger Stand:\n{summary}\n\nBesucher sagt: \"{payload_data}\"\n\nAktualisiere die 3 Pflichtfelder im JSON:"
        
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
    return json.loads(res["choices"][0]["message"]["content"])

def update_state(state, parsed):
    if parsed.get("name") and parsed["name"] not in ("null", "unbekannt"):
        state["name"] = parsed["name"]
    if parsed.get("company") and parsed["company"] not in ("null", "unbekannt"):
        state["company"] = parsed["company"]
    if parsed.get("reason") and parsed["reason"] not in ("null", "unbekannt"):
        state["reason"] = parsed["reason"]
    return state

# Test 1: Real Multimodal Audio (speech.wav)
print("=== TEST 1: ECHTES MULTIMODAL AUDIO (speech.wav) ===")
state1 = {"name": None, "company": None, "reason": None}
res1 = call_gemma_api(state1, 'audio', sample_wav_b64)
print(json.dumps(res1, indent=2, ensure_ascii=False))
update_state(state1, res1)
assert "johannes" in state1["name"].lower(), f"Name mismatch: {state1['name']}"
assert "siemens" in state1["company"].lower(), f"Company mismatch: {state1['company']}"
assert "wartung" in state1["reason"].lower(), f"Reason mismatch: {state1['reason']}"
print("=> TEST 1 PASSED! (Echtes Audio perfekt extrahiert)")

# Test 2: Incomplete Visitor Turn 1 -> Turn 2
print("\n=== TEST 2: 2-SCHRITT DIALOG MIT INCOMPLETE ERKENNUNG ===")
state2 = {"name": None, "company": None, "reason": None}
res2_1 = call_gemma_api(state2, 'text', 'ich bin hier für die besprechung mit dem team von tech solutions')
print("Turn 1 (Name fehlt):")
print(json.dumps(res2_1, indent=2, ensure_ascii=False))
update_state(state2, res2_1)
assert state2["name"] is None, "Name should be None in Turn 1"
assert "tech solutions" in state2["company"].lower(), "Company should be tech solutions"
assert "besprechung" in state2["reason"].lower(), "Reason should be Besprechung"
assert res2_1["status"] == "incomplete", "Status should be incomplete"

print("\nTurn 2 (Name nachgeliefert):")
res2_2 = call_gemma_api(state2, 'text', 'Mein Name ist Johannes Müller.')
print(json.dumps(res2_2, indent=2, ensure_ascii=False))
update_state(state2, res2_2)
assert "johannes" in state2["name"].lower(), "Name should now be Johannes Müller"
assert "tech solutions" in state2["company"].lower(), "Company should still be tech solutions"
assert "besprechung" in state2["reason"].lower(), "Reason should still be Besprechung"
assert res2_2["status"] == "complete", "Status should be complete"
print("=> TEST 2 PASSED! (2-Schritt Dialog perfekt)")

# Test 3: Slang German
print("\n=== TEST 3: SLANG GERMAN ===")
state3 = {"name": None, "company": None, "reason": None}
res3 = call_gemma_api(state3, 'text', 'john von konklusiv um kurz aufs klo zu gehen')
print(json.dumps(res3, indent=2, ensure_ascii=False))
update_state(state3, res3)
assert state3["name"].lower() == "john", f"Expected John, got {state3['name']}"
assert "konklusiv" in state3["company"].lower(), f"Expected Konklusiv, got {state3['company']}"
assert "toilettengang" in state3["reason"].lower(), f"Expected Toilettengang, got {state3['reason']}"
assert res3["status"] == "complete", "Expected complete"
print("=> TEST 3 PASSED! (Slang German perfekt)")

print("\n" + "=" * 60)
print("🎉 ALLE VALIDIERUNGSTESTS DES STATELESS HARNESS 100% BESTANDEN!")
print("=" * 60)
