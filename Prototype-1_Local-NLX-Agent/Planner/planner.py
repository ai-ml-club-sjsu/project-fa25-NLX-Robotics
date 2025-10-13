# -*- coding: utf-8 -*-
import json
import pathlib
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"  # change if you pulled a different tag

SCHEMA_PATH = pathlib.Path(__file__).resolve().parents[1] / "Schemas" / "plan.schema.json"

SYSTEM = (
    "You are a planning function that outputs ONLY JSON matching the provided schema. "
    "The user will ask for a file-related task inside a sandbox directory. "
    "Allowed skills: create_file, write_text, append_text, read_file, list_dir, move_file, copy_file, delete_file. "
    "Never use absolute paths; always use relative paths under the sandbox root. "
    "Prefer small, safe steps. Use 'on_fail':'abort' unless the user requests otherwise."
)

def plan_from_prompt(user_prompt: str) -> dict:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": (
                f"Schema:\n{schema}\n\n"
                f"User request:\n{user_prompt}\n"
                f"Return ONLY the JSON plan."
            ),
        },
    ]
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "format": "json",   # ask Ollama to produce strict JSON
            "stream": False,    # return a single JSON object
            "options": {"temperature": 0.2},
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["message"]["content"]
    return json.loads(content)
