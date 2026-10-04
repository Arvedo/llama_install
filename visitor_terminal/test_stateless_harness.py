import urllib.request
import json
import base64
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\speech.wav', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode('utf-8')

SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Höre das gesprochene Audio des Besuchers an (oder lies seinen Text) und befülle die Pflichtfelder für den Besucherausweis:
1. 'transcription': Was im aktuellen Audio wörtlich gesagt wurde. Bei Stille/unverständlich: 'Keine Sprache erkannt'.
2. 'name': Vollständiger Personenname (oder null). Trenne Firmenzusätze wie 'von [Firma]' strikt ab.
3. 'company': Firma des Besuchers (oder 'Privat', falls privat; sonst null).
4. 'reason': Grund des Besuchs (IMMER auf Deutsch normalisiert, z. B. 'Besprechung', 'Serverwartung', 'Toilettengang'; sonst null).

ZUSTANDSFÜHRUNG:
- Im User-Prompt wird der 'Bisherige Stand' der 3 Felder mitgeliefert.
- Behalte bereits bekannte Werte aus dem bisherigen Stand bei, es sei denn, der Besucher korrigiert oder ergänzt sie.
- Wenn alle 3 Felder ('name', 'company', 'reason') vollständig sind:
  status = 'complete', missing_fields = [], followup_question = 'Vielen Dank! Alle Angaben sind vollständig erfasst.'
- Wenn noch Felder fehlen:
  status = 'incomplete', missing_fields = Liste der fehlenden Felder, followup_question = höfliche deutsche Rückfrage nach den fehlenden Angaben.

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

# Turn 1: Audio with speech.wav ('Johannes Müller von Siemens')
payload1 = {
    'model': 'gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf',
    'messages': [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Bisheriger Stand:\n- Name: null\n- Firma: null\n- Grund: null\n\nHöre dieses Audio an, transkribiere das Gesagte und aktualisiere die 3 Felder:'},
                {'type': 'input_audio', 'input_audio': {'data': audio_b64, 'format': 'wav'}}
            ]
        }
    ],
    'reasoning_budget_tokens': 0,
    'chat_template_kwargs': {'enable_thinking': False},
    'response_format': {'type': 'json_object'},
    'max_tokens': 1024,
    'temperature': 0.1
}

req1 = urllib.request.Request(
    'http://127.0.0.1:8080/v1/chat/completions',
    data=json.dumps(payload1).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
res1 = json.loads(urllib.request.urlopen(req1).read().decode('utf-8'))
content1 = json.loads(res1['choices'][0]['message']['content'])
print('--- Turn 1 (Audio: speech.wav) ---')
print(json.dumps(content1, indent=2, ensure_ascii=False))

# Now client harness updates its state:
state = {
    'name': content1.get('name'),
    'company': content1.get('company'),
    'reason': content1.get('reason')
}

# Turn 2: User provides missing reason via text or second audio
# Notice: ONLY 2 messages in payload! No historical audio blobs! No context pollution!
user_turn_2 = "Ich bin für die Serverwartung hier."
payload2 = {
    'model': 'gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf',
    'messages': [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {
            'role': 'user',
            'content': f"Bisheriger Stand:\n- Name: {state['name']}\n- Firma: {state['company']}\n- Grund: {state['reason']}\n\nNeue Benutzereingabe: \"{user_turn_2}\"\n\nAktualisiere die 3 Felder im JSON:"
        }
    ],
    'reasoning_budget_tokens': 0,
    'chat_template_kwargs': {'enable_thinking': False},
    'response_format': {'type': 'json_object'},
    'max_tokens': 1024,
    'temperature': 0.1
}

req2 = urllib.request.Request(
    'http://127.0.0.1:8080/v1/chat/completions',
    data=json.dumps(payload2).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
res2 = json.loads(urllib.request.urlopen(req2).read().decode('utf-8'))
content2 = json.loads(res2['choices'][0]['message']['content'])
print('\n--- Turn 2 (Text: "Ich bin für die Serverwartung hier.") ---')
print(json.dumps(content2, indent=2, ensure_ascii=False))
