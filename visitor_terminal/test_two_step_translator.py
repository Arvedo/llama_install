import urllib.request
import json
import base64
import sys
import time

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

STT_SYSTEM_PROMPT = """Du bist ein hochpräziser Transkriptions-Assistent.
Höre das beigefügte gesprochene Audio an.

Deine einzige Aufgabe:
- 'transcription': Transkribiere das gesprochene Audio exakt, wörtlich und vollständig in der tatsächlich gesprochenen ORIGINALSPRACHE (z. B. auf Deutsch, Englisch, Französisch, Spanisch, etc.).
- Übersetze die Transkription NIEMALS! Erfinde keine Worte.

Antworte AUSSCHLIESSLICH als valides JSON-Objekt:
{
  "transcription": string
}"""

TRANSLATE_SYSTEM_PROMPT = """Du bist ein professioneller Übersetzer.
Analysiere den gegebenen Text und übersetze ihn.

Deine Aufgaben:
1. 'detected_language': Name der erkannten Ausgangssprache auf Deutsch (z. B. 'Deutsch', 'Englisch', 'Französisch', 'Spanisch').
2. 'german_version': Natürliche, präzise Übersetzung ins Deutsche. Wenn der Originaltext bereits Deutsch ist, gib den bereinigten deutschen Text aus.
3. 'english_version': Natürliche, präzise Übersetzung ins Englische. Wenn der Originaltext bereits Englisch ist, gib den bereinigten englischen Text aus.

Antworte AUSSCHLIESSLICH als valides JSON-Objekt:
{
  "detected_language": string,
  "german_version": string,
  "english_version": string
}"""

def run_two_step(wav_path):
    print(f"\n=======================================================")
    print(f"Testing: {wav_path}")
    with open(wav_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')

    # STEP 1: STT
    t0 = time.time()
    payload_stt = {
        'messages': [
            {'role': 'system', 'content': STT_SYSTEM_PROMPT},
            {'role': 'user', 'content': [
                {'type': 'text', 'text': "Transkribiere das gesprochene Audio exakt in der gesprochenen Originalsprache:"},
                {'type': 'input_audio', 'input_audio': {'data': b64, 'format': 'wav'}}
            ]}
        ],
        'response_format': {'type': 'json_object'},
        'max_tokens': 2048,
        'temperature': 0.1
    }
    req1 = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload_stt).encode('utf-8'), headers={'Content-Type': 'application/json'})
    resp1 = json.loads(urllib.request.urlopen(req1).read().decode('utf-8'))
    stt_duration = round((time.time() - t0) * 1000)
    raw_stt = resp1['choices'][0]['message'].get('content', '')
    print(f"RAW STT: {repr(raw_stt)}")
    reasoning = resp1['choices'][0]['message'].get('reasoning_content', '')
    if not raw_stt and reasoning:
        print(f"STT REASONING: {reasoning[:200]}")
    import re
    m = re.search(r'\{[\s\S]*\}', raw_stt)
    if m:
        try:
            parsed_stt = json.loads(m.group(0))
        except Exception:
            parsed_stt = {}
    else:
        parsed_stt = {"transcription": raw_stt.strip()}
    transcript = parsed_stt.get('transcription', raw_stt.strip())
    print(f"STEP 1 [STT in {stt_duration} ms]:\n  Transcript: '{transcript}'")

    if not transcript or transcript.strip() == "":
        print("  STT returned empty transcript.")
        return

    # STEP 2: Translation (Text-only)
    t1 = time.time()
    payload_trans = {
        'messages': [
            {'role': 'system', 'content': TRANSLATE_SYSTEM_PROMPT},
            {'role': 'user', 'content': f'Originaltext:\n"{transcript}"\n\nErkenne die Sprache und übersetze:'}
        ],
        'response_format': {'type': 'json_object'},
        'max_tokens': 2048,
        'temperature': 0.1
    }
    req2 = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload_trans).encode('utf-8'), headers={'Content-Type': 'application/json'})
    resp2 = json.loads(urllib.request.urlopen(req2).read().decode('utf-8'))
    trans_duration = round((time.time() - t1) * 1000)
    raw_trans = resp2['choices'][0]['message'].get('content', '{}')
    m2 = re.search(r'\{[\s\S]*\}', raw_trans)
    try:
        parsed_trans = json.loads(m2.group(0)) if m2 else {}
    except Exception:
        parsed_trans = {}
    print(f"STEP 2 [TRANSLATION in {trans_duration} ms]:")
    print(f"  Detected Language: {parsed_trans.get('detected_language')}")
    print(f"  German:  {parsed_trans.get('german_version')}")
    print(f"  English: {parsed_trans.get('english_version')}")
    print(f"TOTAL TIME: {stt_duration + trans_duration} ms")

for test_wav in [
    r"c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\logs\audio\audio_20261004_134554_VIS-32057.wav", # German (Johannes Müller)
    r"c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\logs\audio\audio_20261004_142604_VIS-98534.wav", # English (John)
    r"c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\logs\audio\audio_20261004_142912_VIS-15479.wav", # French (Pierre)
]:
    run_two_step(test_wav)
