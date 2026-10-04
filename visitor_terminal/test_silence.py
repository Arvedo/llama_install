import urllib.request
import json
import base64
import wave
import struct
from test_hardened import SYSTEM_PROMPT, JSON_SCHEMA

# Create 2 seconds of silence
with wave.open('silence.wav', 'w') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(16000)
    for _ in range(32000):
        f.writeframes(struct.pack('<h', 0))

with open('silence.wav', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

payload = {
    'model': 'gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf',
    'messages': [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Bisheriger Zustand: {"name": null, "company": null, "reason": null}\nAnalysiere dieses Audio, transkribiere und aktualisiere den Zustand im JSON-Format:'},
                {'type': 'input_audio', 'input_audio': {'data': b64, 'format': 'wav'}}
            ]
        }
    ],
    'reasoning_budget_tokens': 0,
    'chat_template_kwargs': {'enable_thinking': False},
    'response_format': {'type': 'json_object', 'schema': JSON_SCHEMA},
    'max_tokens': 1024,
    'temperature': 0.1
}

req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
print(resp.read().decode('utf-8'))
