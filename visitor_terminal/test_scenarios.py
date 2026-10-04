import urllib.request
import json

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Besucher sprechen im Dialog mit dir (oft umgangssprachlich, kurz oder stichpunktartig) in jeder Sprache (Deutsch, Englisch, usw.).

Deine Kernaufgabe: Führe den Check-in Dialog und befülle exakt drei Pflichtfelder für den Besucherausweis:
1. 'transcription': Das Gesprochene/Eingegebene wortwörtlich.
2. 'name': Der Name / Vorname des Besuchers (im Original unübersetzt).
3. 'company': Die Firma oder Organisation des Besuchers (im Original unübersetzt; falls privat: 'Privat', falls noch nicht genannt: null).
4. 'reason': Der Besuchszweck / Anlass des Besuchs (IMMER ins Deutsche übersetzt, z. B. 'Toilettengang', 'Besprechung', 'Wartung', 'Sicherheitsaudit').

WICHTIGE SYNTAKTISCHE REGELN:
- "[Name] von [Firma]" (z. B. "John von Konklusiv", "Max von Siemens", "Lisa von Bosch"):
  Das Wort "von" leitet hier IMMER die Firma ein! -> 'name': "[Name]", 'company': "[Firma]"
- "um [X] zu ..." / "für [X]" / "wegen [X]" (z. B. "um kurz aufs Klo zu gehen", "fürs Meeting"):
  Leitet IMMER den Grund ein! -> 'reason' (z. B. "Toilettengang", "Besprechung")
- SITZUNG & NEUE BESUCHER:
  Wenn der vorherige Ausweis bereits vollständig war ODER ein völlig neuer Name genannt wird, gilt dies als NEUER Besucher (alte Angaben verwerfen)!
  In einem noch unvollständigen Dialog ergänzen neue Angaben den bisherigen Besucher.

STATUS:
- 'status': 'complete' NUR wenn alle 3 Felder ('name', 'company', 'reason') befüllt sind.
- Falls noch Felder fehlen: 'status': 'incomplete', 'missing_fields': Liste der fehlenden Felder, 'followup_question': gezielte deutsche Rückfrage.

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

def chat(messages, user_msg):
    messages.append({"role": "user", "content": user_msg})
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
        ans = res["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": ans})
        return json.loads(ans)

print("=== SCENARIO 1: 2-Turn Slot-Filling for same visitor ===")
conv1 = [{"role": "system", "content": SYSTEM_PROMPT}]
t1 = chat(conv1, "Hey, ich bin der Johannes.")
print("Turn 1:", t1["name"], "|", t1["company"], "|", t1["reason"], "| status:", t1["status"])
t2 = chat(conv1, "Ich komme von Konklusiv KG um kurz aufs Klo zu gehen.")
print("Turn 2:", t2["name"], "|", t2["company"], "|", t2["reason"], "| status:", t2["status"])

print("\n=== SCENARIO 2: Complete John Smith, then immediately John von Konklusiv in same chat ===")
conv2 = [{"role": "system", "content": SYSTEM_PROMPT}]
t3 = chat(conv2, "Hello, my name is John Smith from Acme Corp for the quarterly security audit.")
print("Turn 1 (John Smith):", t3["name"], "|", t3["company"], "|", t3["reason"], "| status:", t3["status"])
t4 = chat(conv2, "john von konklusiv um kurz aufs klo zu gehen")
print("Turn 2 (Next Visitor):", t4["name"], "|", t4["company"], "|", t4["reason"], "| status:", t4["status"])
