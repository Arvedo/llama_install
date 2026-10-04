import sys
import os
import base64
import json
import urllib.request

def query_audio(audio_path, prompt="Transkribiere und beantworte dieses Audio auf Deutsch:"):
    if not os.path.exists(audio_path):
        print(f"Fehler: Datei '{audio_path}' nicht gefunden!")
        return

    # Read audio and encode to base64
    with open(audio_path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(audio_path)[1].lower().replace(".", "")
    if ext not in ["wav", "mp3", "flac", "ogg"]:
        ext = "wav"

    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": ext
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }

    print(f"Sende '{audio_path}' an http://127.0.0.1:8080/v1/chat/completions...")
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            answer = data["choices"][0]["message"]["content"]
            print("\n" + "="*50)
            print("ANTWORT VOM MODELL:")
            print("="*50)
            print(answer)
            print("="*50)
    except urllib.error.HTTPError as e:
        print("HTTP Fehler:", e.code, e.read().decode("utf-8"))
    except Exception as e:
        print("Fehler:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        p = sys.argv[2] if len(sys.argv) > 2 else "Transkribiere und fasse den Inhalt kurz zusammen:"
        query_audio(path, p)
    else:
        # Default test file
        test_wav = os.path.join(os.path.dirname(__file__), "visitor_terminal", "speech.wav")
        if os.path.exists(test_wav):
            query_audio(test_wav)
        else:
            print("Verwendung: python send_audio.py <pfad_zu_audio.wav_oder_mp3>")
