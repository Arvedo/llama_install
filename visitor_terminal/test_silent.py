import urllib.request
import json
import base64
import io, wave, struct

# Create 0.5s of silent WAV
buf = io.BytesIO()
with wave.open(buf, 'wb') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(16000)
    f.writeframes(struct.pack('<' + 'h'*8000, *([0]*8000)))
b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

payload = {
    'model': 'gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf',
    'messages': [
        {'role': 'system', 'content': 'Du bist ein Terminal. Antworte in JSON.'},
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Audio analysieren:'},
                {'type': 'input_audio', 'input_audio': {'data': b64, 'format': 'wav'}}
            ]
        }
    ],
    'response_format': {'type': 'json_object'},
    'max_tokens': 600
}

req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print('Message Content:', repr(res['choices'][0]['message'].get('content')))
    print('Finish Reason:', res['choices'][0].get('finish_reason'))
    if 'reasoning_content' in res['choices'][0]['message']:
        print('Reasoning:', repr(res['choices'][0]['message']['reasoning_content'])[:120])
