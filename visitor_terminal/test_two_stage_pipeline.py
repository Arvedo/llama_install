import urllib.request
import json
import base64
import sys
import time

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\speech.wav', 'rb') as f:
    sample_wav_b64 = base64.b64encode(f.read()).decode('utf-8')

# ========================================================
# STAGE 1: PURE GEMMA AUDIO TRANSCRIPTION (STT)
# ========================================================
def stage1_transcribe_audio(audio_b64):
    t0 = time.time()
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional audio transcriber. Listen carefully to the audio and transcribe exactly what is spoken verbatim in its original language. Output ONLY a JSON object: {\"transcription\": \"<exact spoken text>\"}. If there is only silence or unintelligible noise, output {\"transcription\": \"Keine Sprache erkannt\"}."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Transcribe this audio recording:"},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}}
                ]
            }
        ],
        "reasoning_budget_tokens": 0,
        "chat_template_kwargs": {"enable_thinking": False},
        "response_format": {"type": "json_object"},
        "max_tokens": 256,
        "temperature": 0.1
    }
    
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    dur = round((time.time() - t0) * 1000)
    raw = res["choices"][0]["message"]["content"]
    parsed = json.loads(raw)
    transcript = parsed.get("transcription", "").strip()
    return transcript, dur

# ========================================================
# STAGE 2: PURE GEMMA TEXT EXTRACTION & NORMALIZATION
# ========================================================
EXTRACTION_SYSTEM_PROMPT = """Du bist das intelligente Empfangsterminal eines Unternehmens.
Lies den transkribierten Text des Besuchers und befülle die 3 Pflichtfelder für den Besucherausweis:
1. 'name': Vollständiger Personenname (Vor- und/oder Nachname).
   - Schneide Firmenzusätze wie 'von [Firma]' strikt ab (z. B. 'john von konklusiv' -> name = 'John', company = 'Konklusiv').
   - Falls noch kein Personenname genannt wurde: null.
2. 'company': Firma oder Organisation (im Original unübersetzt; falls privat: 'Privat'; falls noch nicht genannt: null).
3. 'reason': Grund des Besuchs.
   - WICHTIG: Übersetze den Besuchszweck IMMER VOLLSTÄNDIG ins DEUTSCHE (z. B. 'Praktikum', 'Besprechung', 'Serverwartung', 'Hardware-Beratung', 'Toilettengang', 'Vorstellungsgespräch', 'Sicherheitsaudit').
   - Belasse NIEMALS fremdsprachige Wörter im Grund. Falls noch nicht genannt: null.

REGELN:
- Der 'Bisherige Stand' der 3 Felder wird im User-Prompt mitgeliefert. Behalte bereits bekannte Werte bei.
- Wenn alle 3 Pflichtfelder ('name', 'company', 'reason') vollständig sind:
  status = 'complete', missing_fields = [], followup_question = 'Vielen Dank! Alle Angaben sind vollständig erfasst. Ihr Ausweis wird gedruckt.'
- Wenn noch Felder fehlen:
  status = 'incomplete', missing_fields = Liste der noch fehlenden Felder, followup_question = gezielte deutsche Rückfrage.

Antworte AUSSCHLIESSLICH als valides JSON-Objekt:
{
  "name": string or null,
  "company": string or null,
  "reason": string or null,
  "status": "complete" or "incomplete",
  "missing_fields": string[],
  "followup_question": string
}"""

def stage2_extract_fields(state, text):
    t0 = time.time()
    summary = f"- Name: {state['name'] if state['name'] else 'null'}\n- Firma: {state['company'] if state['company'] else 'null'}\n- Grund: {state['reason'] if state['reason'] else 'null'}"
    user_prompt = f"Bisheriger Stand:\n{summary}\n\nBesucher sagt: \"{text}\"\n\nAktualisiere die 3 Pflichtfelder im JSON:"
    
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
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
    dur = round((time.time() - t0) * 1000)
    raw = res["choices"][0]["message"]["content"]
    parsed = json.loads(raw)
    return parsed, dur

print("=== TESTE 2-STUFIGE PIPELINE (STAGE 1: STT -> STAGE 2: EXTRACTION) ===")

# Test with speech.wav
print("\n--- Test Audio: speech.wav ---")
transcript, t1_ms = stage1_transcribe_audio(sample_wav_b64)
print(f"Stage 1 (Pure Audio STT in {t1_ms} ms):")
print(f"Transkript: \"{transcript}\"")

state = {"name": None, "company": None, "reason": None}
fields, t2_ms = stage2_extract_fields(state, transcript)
print(f"\nStage 2 (Pure Text Extraction in {t2_ms} ms):")
print(json.dumps(fields, indent=2, ensure_ascii=False))

# Test with user's exact case:
user_text = "Hello, I'm John. I'm here for the internship and I'm from Microsoft."
print(f"\n--- Test Text Case: \"{user_text}\" ---")
fields2, t3_ms = stage2_extract_fields(state, user_text)
print(f"Extraction (in {t3_ms} ms):")
print(json.dumps(fields2, indent=2, ensure_ascii=False))

# Test French
fr_text = "Bonjour, je m'appelle Pierre Dubois de Renault pour la maintenance du système."
print(f"\n--- Test French: \"{fr_text}\" ---")
fields_fr, t_fr = stage2_extract_fields(state, fr_text)
print(f"French Extraction (in {t_fr} ms):")
print(json.dumps(fields_fr, indent=2, ensure_ascii=False))

# Test Italian (Pietro Rossi user case)
it_text = "Buongiorno, sono Pietro Rossi di Tech Solutions per una consultazione dell'hardware."
print(f"\n--- Test Italian: \"{it_text}\" ---")
fields_it, t_it = stage2_extract_fields(state, it_text)
print(f"Italian Extraction (in {t_it} ms):")
print(json.dumps(fields_it, indent=2, ensure_ascii=False))

# Test Slang
slang_text = "john von konklusiv um kurz aufs klo zu gehen"
print(f"\n--- Test Slang: \"{slang_text}\" ---")
fields_slang, t_slang = stage2_extract_fields(state, slang_text)
print(f"Slang Extraction (in {t_slang} ms):")
print(json.dumps(fields_slang, indent=2, ensure_ascii=False))

# Test Multi-Turn (Turn 1 -> Turn 2)
print("\n--- Test Multi-Turn Dialog ---")
t1_state = {"name": None, "company": None, "reason": None}
res_turn1, _ = stage2_extract_fields(t1_state, "Hey, ich bin der Johannes.")
print("Turn 1 ('Hey, ich bin der Johannes.'):")
print(json.dumps(res_turn1, indent=2, ensure_ascii=False))

t2_state = {
    "name": res_turn1.get("name") or t1_state["name"],
    "company": res_turn1.get("company") or t1_state["company"],
    "reason": res_turn1.get("reason") or t1_state["reason"],
}
res_turn2, _ = stage2_extract_fields(t2_state, "Dienstleister von TechSolutions wegen Serverwartung.")
print("Turn 2 ('Dienstleister von TechSolutions wegen Serverwartung.'):")
print(json.dumps(res_turn2, indent=2, ensure_ascii=False))

