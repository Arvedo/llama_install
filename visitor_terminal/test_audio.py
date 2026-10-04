import urllib.request
import io
import wave
import struct
import math
import json
import base64

# 1. Create a 2-second WAV file with a tone
buf = io.BytesIO()
with wave.open(buf, 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)
    for i in range(32000):
        val = int(32767.0 * 0.4 * math.sin(2.0 * math.pi * 440.0 * i / 16000))
        wav_file.writeframes(struct.pack('<h', val))
wav_data = buf.getvalue()
wav_b64 = base64.b64encode(wav_data).decode('utf-8')

# Test 1: Chat Completions with input_audio
print("--- Test 1: POST /v1/chat/completions with input_audio ---")
payload = {
    "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What do you hear in this audio recording? Please describe it briefly."},
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": wav_b64,
                        "format": "wav"
                    }
                }
            ]
        }
    ],
    "max_tokens": 100,
    "temperature": 0.2
}

req = urllib.request.Request(
    "http://127.0.0.1:8080/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("Model answer:\n", res["choices"][0]["message"]["content"])
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("Error:", e)

# Test 2: Audio Transcriptions
print("\n--- Test 2: POST /v1/audio/transcriptions ---")
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = bytearray()
body.extend(f"--{boundary}\r\n".encode("utf-8"))
body.extend(b'Content-Disposition: form-data; name="file"; filename="audio.wav"\r\n')
body.extend(b"Content-Type: audio/wav\r\n\r\n")
body.extend(wav_data)
body.extend(b"\r\n")
body.extend(f"--{boundary}\r\n".encode("utf-8"))
body.extend(b'Content-Disposition: form-data; name="model"\r\n\r\n')
body.extend(b"gemma-4\r\n")
body.extend(f"--{boundary}--\r\n".encode("utf-8"))

req2 = urllib.request.Request(
    "http://127.0.0.1:8080/v1/audio/transcriptions",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)

try:
    with urllib.request.urlopen(req2) as resp:
        print("Transcription Result:\n", resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("Error:", e)
