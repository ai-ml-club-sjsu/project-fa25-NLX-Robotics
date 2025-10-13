# -*- coding: utf-8 -*-
import json
import os
import pathlib
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "Schemas" / "plan.schema.json"

class SafetyError(Exception):
    pass

def _load_schema():
    return json.loads(SCHEMA.read_text(encoding="utf-8"))

def _inside_sandbox(path: pathlib.Path, sandbox: pathlib.Path) -> bool:
    try:
        path.resolve().relative_to(sandbox.resolve())
        return True
    except Exception:
        return False

def validate_plan(plan: dict, sandbox_dir: pathlib.Path):
    # 1) JSON Schema validation
    Draft202012Validator(_load_schema()).validate(plan)

    # 2) Safety checks
    MAX_TEXT_CHARS = 20000
    sandbox_dir.mkdir(parents=True, exist_ok=True)

    for i, step in enumerate(plan["steps"]):
        skill = step["skill"]
        params = step["params"]

        # Disallow absolute paths and traversal
        for key in ("path", "dest"):
            if key in params:
                raw = params[key]
                if os.path.isabs(raw) or ".." in pathlib.Path(raw).parts:
                    raise SafetyError(f"Step {i} ({skill}) has unsafe path component: {raw}")
                if not _inside_sandbox(sandbox_dir / raw, sandbox_dir):
                    raise SafetyError(f"Step {i} ({skill}) escapes sandbox: {raw}")

        if skill in ("write_text", "append_text"):
            txt = params.get("text", "")
            if len(txt) > MAX_TEXT_CHARS:
                raise SafetyError(f"Step {i} text too large ({len(txt)} chars)")

    return True
