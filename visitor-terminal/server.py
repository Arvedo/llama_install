import http.server
import socketserver
import webbrowser
import os
import sys
import json
import base64
import time
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(DIRECTORY, "logs")
AUDIO_LOGS_DIR = os.path.join(LOGS_DIR, "audio")
PASSPORT_LOGS_DIR = os.path.join(LOGS_DIR, "passports")
LOG_FILE = os.path.join(LOGS_DIR, "terminal.log")
JSONL_FILE = os.path.join(LOGS_DIR, "terminal_sessions.jsonl")

os.makedirs(AUDIO_LOGS_DIR, exist_ok=True)
os.makedirs(PASSPORT_LOGS_DIR, exist_ok=True)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/version':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            idx_path = os.path.join(DIRECTORY, "index.html")
            mtime = os.path.getmtime(idx_path) if os.path.exists(idx_path) else 0
            self.wfile.write(json.dumps({"mtime": mtime, "version": "3.1"}).encode('utf-8'))
            return

        if self.path == '/api/logs':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                    tail = "".join(lines[-200:])
                    self.wfile.write(tail.encode('utf-8'))
            else:
                self.wfile.write(b"No logs recorded yet.\n")
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/log':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON"}')
                return

            session_id = data.get('sessionId', 'UNKNOWN_SESSION')
            stage = data.get('stage', 'GENERAL')
            title = data.get('title', '')
            details = data.get('details', {})
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # If audio is passed, save to a real .wav file for inspection!
            audio_b64 = details.get('audioBase64') or details.get('base64Audio')
            saved_audio_path = None
            if audio_b64 and isinstance(audio_b64, str) and len(audio_b64) > 100:
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    fname = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_id}.wav"
                    fpath = os.path.join(AUDIO_LOGS_DIR, fname)
                    with open(fpath, "wb") as af:
                        af.write(audio_bytes)
                    saved_audio_path = fpath
                    details['saved_audio_file'] = fpath
                    details['audio_size_bytes'] = len(audio_bytes)
                    details['audio_duration_sec_est'] = round(len(audio_bytes) / 32000, 2)
                    if 'audioBase64' in details:
                        del details['audioBase64']
                    if 'base64Audio' in details:
                        del details['base64Audio']
                except Exception as ex:
                    details['audio_save_error'] = str(ex)

            # Human-readable formatted entry for terminal.log
            divider = "=" * 80
            entry = [
                divider,
                f"[{now_str}] [SESSION: {session_id}] [STAGE: {stage}]",
                f"ACTION / TITLE: {title}",
            ]
            if saved_audio_path:
                entry.append(f"SAVED AUDIO FILE: {saved_audio_path} ({len(audio_bytes)} bytes)")

            # Format details nicely
            if details:
                entry.append("DETAILS / PAYLOAD:")
                formatted_details = json.dumps(details, indent=2, ensure_ascii=False)
                entry.append(formatted_details)
            entry.append(divider)
            entry.append("\n")

            log_text = "\n".join(entry)

            # 1. Write to terminal.log
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_text)
                f.flush()

            # 2. Write to terminal_sessions.jsonl
            jsonl_obj = {
                "timestamp": now_str,
                "sessionId": session_id,
                "stage": stage,
                "title": title,
                "details": details
            }
            with open(JSONL_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(jsonl_obj, ensure_ascii=False) + "\n")
                f.flush()

            # 3. Print clean summary line to stdout
            print(f"[{now_str}] [{stage}] [{session_id}] {title}")
            if 'rawResponse' in details:
                print(f"   ↳ RAW MODEL: {details['rawResponse']}")
            if 'parsedTranscription' in details:
                print(f"   ↳ TRANSCRIPT: \"{details['parsedTranscription']}\"")
            if 'parsed' in details or 'parsedResult' in details:
                p = details.get('parsed') or details.get('parsedResult')
                if isinstance(p, dict):
                    print(f"   ↳ EXTRACTED: name={p.get('name')}, company={p.get('company')}, reason={p.get('reason')}, status={p.get('status')}")
            sys.stdout.flush()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "logged"}')
            return

        elif self.path == '/api/save_passport':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                session_id = data.get('sessionId', 'VIS-00000')
                side = data.get('side', 'front')
                img_b64 = data.get('imageBase64', '')
                if ',' in img_b64:
                    img_b64 = img_b64.split(',', 1)[1]
                img_bytes = base64.b64decode(img_b64)
                fname = f"passport_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_id}_{side}.jpg"
                fpath = os.path.join(PASSPORT_LOGS_DIR, fname)
                with open(fpath, "wb") as f:
                    f.write(img_bytes)
                print(f"[PASSPORT SAVED] {fpath} ({len(img_bytes)} bytes)")
                sys.stdout.flush()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "saved", "path": fpath, "filename": fname}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                return

        super().do_POST()

def run():
    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 70)
        print("KI-BESUCHERTERMINAL // LLAMA.CPP LIVE DEMO & AUDIT LOGGER")
        print("=" * 70)
        print(f"Web-App laeuft auf:      {url}")
        print(f"Log-Datei (Text):        {LOG_FILE}")
        print(f"Log-Datei (JSONL):       {JSONL_FILE}")
        print(f"Audio-Aufnahmen Ordner:  {AUDIO_LOGS_DIR}")
        print("llama.cpp Backend:       http://127.0.0.1:8080")
        print("Druecke Strg + C zum Beenden des Demo-Servers.")
        print("=" * 70)
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer wird beendet...")

if __name__ == "__main__":
    run()
