import urllib.request
import json
import base64

with open(r'c:\Users\Arved\Desktop\llama_präsi\visitor_terminal\speech.wav', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

payload = {
    'model': 'gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf',
    'messages': [
        {'role': 'system', 'content': 'Du bist ein Terminal. Antworte immer im JSON-Format.'},
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Transkribiere und extrahiere in JSON: {"transcription": string, "name": string, "company": string, "reason": string}'},
                {'type': 'input_audio', 'input_audio': {'data': b64, 'format': 'wav'}}
            ]
        }
    ],
    'reasoning_effort': 'none',
    'response_format': {'type': 'json_object'},
    'max_tokens': 300
}

req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print('Tokens used:', res.get('usage'))
    print('Content:', res['choices'][0]['message'].get('content'))
    print('Reasoning content:', res['choices'][0]['message'].get('reasoning_content'))
