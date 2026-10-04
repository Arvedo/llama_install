import urllib.request
import json
import time
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Besucher sprechen im Dialog mit dir (oft umgangssprachlich, stichpunktartig, ohne Großschreibung) in jeder Sprache (Deutsch, Englisch, Französisch, Spanisch usw.).

Deine Kernaufgabe: Führe den Check-in Dialog und befülle exakt drei Pflichtfelder für den Besucherausweis:
1. 'transcription': Das Gesprochene/Eingegebene wortwörtlich in der Originalsprache.
2. 'name': NUR der Personenname (Vor- und/oder Nachname).
   - WICHTIGSTE SYNTAKTISCHE REGEL:
     Muster '[Name] von [Firma]' oder '[Name] aus [Firma]':
     -> 'name' ist NUR der Personenname ('[Name]').
     -> Schneide 'von [Firma]' strikt ab, es gehört NIEMALS zum Namen!
     -> Beispiel: 'john von konklusiv' -> name: 'John', company: 'Konklusiv'.
   - Falls die Person ihren Namen noch NICHT genannt hat (z. B. nur 'von SAP zur Besprechung'): zwingend null!
3. 'company': Die Firma oder Organisation (im Original unübersetzt; falls privat: 'Privat'; falls noch nicht genannt: null).
4. 'reason': Der Besuchszweck / Anlass (IMMER ins Deutsche übersetzt, z. B. 'Toilettengang', 'Besprechung', 'Wartung', 'Sicherheitsaudit', 'Lieferung'; falls noch nicht genannt: null).

SYNTAKTISCHE ERKENNUNGSREGELN:
- Muster '[Name] von [Firma]' (z. B. 'john von konklusiv', 'max von siemens', 'sarah von bosch'):
  -> 'name': nur der Personenname ('John', 'Max', 'Sarah')
  -> 'company': die Organisation ('Konklusiv', 'Siemens', 'Bosch')
- Muster 'von [Firma] für/wegen/um ...' (ohne Name):
  -> 'name': null (fehlt noch!)
  -> 'company': [Firma]
- Muster 'um ... zu [Verb]', 'für [Zweck]', 'wegen [Zweck]' (z. B. 'um kurz aufs klo zu gehen', 'fürs meeting', 'wegen reparatur'):
  -> 'reason': der Besuchszweck ins Deutsche normalisiert ('Toilettengang', 'Besprechung', 'Reparatur')

DIALOGGEDÄCHTNIS (Multi-Turn):
- Wenn in einer vorherigen Nachricht bereits der Name, die Firma oder der Grund genannt wurde, BEHALTE DIESEN WERT UNBEDINGT BEI! Überschreibe ihn NICHT mit null!
- Kombiniere alle bisherigen Angaben aus dem Dialogverlauf.
- Wenn ALLE 3 Pflichtfelder aus dem Verlauf bekannt sind -> status = 'complete', missing_fields = [].
- Nur wenn ein Pflichtfeld auch im bisherigen Dialogverlauf fehlt -> null, status = 'incomplete'.

WICHTIGSTE REGEL ZUM AUSGABEFORMAT:
Du MUSST in JEDER Antwort IMMER exakt dieses JSON-Schema mit ALLEN 7 Feldern ausgeben. Wenn ein Wert fehlt, setze ihn auf null:
{
  "transcription": "Originaltext",
  "name": "Vorname Nachname oder null",
  "company": "Firma oder Privat oder null",
  "reason": "Besuchsgrund auf Deutsch oder null",
  "status": "complete oder incomplete",
  "missing_fields": ["name", "company", "reason"],
  "followup_question": "Höfliche deutsche Rückfrage oder Bestätigung"
}"""

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

def call_gemma(messages):
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": messages,
        "chat_template_kwargs": {"enable_thinking": False},
        "response_format": {"type": "json_object", "schema": JSON_SCHEMA},
        "temperature": 0.1
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    dur = round((time.time() - t0) * 1000)
    raw = res["choices"][0]["message"]["content"]
    parsed = json.loads(raw)
    return parsed, dur

tests = [
    {
        "name": "Klassisches Problemkind 1 (Umgangssprachlich)",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "john von konklusiv um kurz aufs klo zu gehen"}
        ],
        "expected": {"name": "John", "company": "Konklusiv", "reason": "Toilettengang", "status": "complete"}
    },
    {
        "name": "Klassisches Problemkind 2 (mit KG)",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "john von konklusiv kg um kurz aufs klo zu gehen"}
        ],
        "expected": {"name": "John", "status": "complete"}
    },
    {
        "name": "Englisch (Auto-Translation ins Deutsche)",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Hello, my name is John Smith from Acme Corp for the quarterly security audit."}
        ],
        "expected": {"name": "John Smith", "company": "Acme Corp", "status": "complete"}
    },
    {
        "name": "Französisch (Auto-Translation ins Deutsche)",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Bonjour, je m'appelle Pierre Dubois de Renault pour la maintenance du système."}
        ],
        "expected": {"name": "Pierre Dubois", "company": "Renault", "status": "complete"}
    },
    {
        "name": "Spanisch (Auto-Translation ins Deutsche)",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Hola, soy Alejandro Garcia de Iberdrola para la reparación de los servidores."}
        ],
        "expected": {"name": "Alejandro Garcia", "company": "Iberdrola", "status": "complete"}
    }
]

print("=" * 60)
print("TEST SUITE: Gemma 4 2B Inferenz & Syntaktische Extraktion")
print("=" * 60)

all_passed = True
for idx, test in enumerate(tests, 1):
    print(f"\n[{idx}/{len(tests)}] Test: {test['name']}")
    parsed, dur = call_gemma(test["messages"])
    print(f"Latenz: {dur} ms")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    
    passed = True
    for k, v in test["expected"].items():
        val = parsed.get(k)
        if isinstance(val, str) and isinstance(v, str):
            if v.lower() not in val.lower():
                print(f"❌ MISMATCH in '{k}': Erwartet '{v}', Erhalten '{val}'")
                passed = False
        elif val != v:
            print(f"❌ MISMATCH in '{k}': Erwartet '{v}', Erhalten '{val}'")
            passed = False
    
    if passed:
        print(f"✅ PASSED ({test['name']})")
    else:
        all_passed = False
        print(f"❌ FAILED ({test['name']})")

print("\n" + "=" * 60)
if all_passed:
    print("🎉 ALLE TESTS ERFOLGREICH BESTANDEN!")
else:
    print("⚠️ EINIGE TESTS FEHLGESCHLAGEN.")
print("=" * 60)
