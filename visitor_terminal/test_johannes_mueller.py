import urllib.request
import json
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from test_user_reported import SYSTEM_PROMPT

prompt = """Bisheriger Stand:
- Name: null
- Firma: null
- Grund: null

Besucher sagt: "Hallo, ich bin Johannes von TechSolutions. Ich bin hier wegen der Serverwartung. Johannes Müller."

Aktualisiere die 3 Pflichtfelder im JSON:"""

payload = {
    "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
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
print(res["choices"][0]["message"]["content"])
