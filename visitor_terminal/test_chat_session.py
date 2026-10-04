import urllib.request
import json
from test_multilingual import SYSTEM_PROMPT, JSON_SCHEMA

def chat_step(messages, user_input):
    messages.append({"role": "user", "content": user_input})
    payload = {
        "model": "gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf",
        "messages": messages,
        "reasoning_budget_tokens": 0,
        "chat_template_kwargs": {"enable_thinking": False},
        "response_format": {"type": "json_object", "schema": JSON_SCHEMA},
        "max_tokens": 1024,
        "temperature": 0.1
    }
    req = urllib.request.Request(
        "http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        content = res["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": content})
        return json.loads(content)

print("--- SESSION 1 (Anna Weber) ---")
session1 = [{"role": "system", "content": SYSTEM_PROMPT}]
r1 = chat_step(session1, "Guten Tag, mein Name ist Anna Weber.")
print("Turn 1:", r1["name"], "|", r1["company"], "|", r1["reason"], "| status:", r1["status"])
print("Bot fragt:", r1["followup_question"])

r2 = chat_step(session1, "Ich komme von BASF wegen der Umweltinspektion.")
print("Turn 2:", r2["name"], "|", r2["company"], "|", r2["reason"], "| status:", r2["status"])
print("Bot sagt:", r2["followup_question"])

print("\n--- SESSION 2 (COMPLETELY NEW CHAT: Peter Schmidt) ---")
session2 = [{"role": "system", "content": SYSTEM_PROMPT}]
r3 = chat_step(session2, "Hallo, ich bin Peter Schmidt von Bosch.")
print("Turn 1 New:", r3["name"], "|", r3["company"], "|", r3["reason"], "| status:", r3["status"])
print("Bot fragt:", r3["followup_question"])
