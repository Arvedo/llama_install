import base64
import os

dir_path = os.path.dirname(os.path.abspath(__file__))
wav_path = os.path.join(dir_path, "speech.wav")
js_path = os.path.join(dir_path, "sample_audio_data.js")

with open(wav_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

with open(js_path, "w", encoding="utf-8") as out:
    out.write(f'window.SAMPLE_AUDIO_BASE64 = "{b64}";\n')

print("sample_audio_data.js written successfully!")
