# -*- coding: utf-8 -*-
import json
import pathlib
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3"  # adjust if you use a different local tag

SCHEMA_PATH = pathlib.Path(__file__).resolve().parents[1] / "Schemas" / "plan.schema.json"

SYSTEM = (
    "You are a planning function that outputs ONLY JSON matching the provided schema. "
    "Allowed skills: create_file, write_text, append_text, read_file, list_dir, "
    "move_file, copy_file, delete_file, replace_text, remove_text. "
    "Preserve user-provided filenames/paths verbatim; do not rename or add folders. "
    "Never use absolute paths; always use relative paths under the sandbox root. "
    "Prefer small, safe steps. Use 'on_fail':'abort' unless the user requests otherwise."
)

def plan_from_prompt(user_prompt: str) -> dict:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Schema:\n{schema}\n\nUser request:\n{user_prompt}\nReturn ONLY the JSON plan."},
    ]
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "format": "json",   # request strict JSON back
            "stream": False
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["message"]["content"]
    return json.loads(content)
