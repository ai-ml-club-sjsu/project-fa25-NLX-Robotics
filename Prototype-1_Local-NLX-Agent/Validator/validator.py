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
    # Schema validation
    Draft202012Validator(_load_schema()).validate(plan)

    # Safety checks
    MAX_TEXT_CHARS = 20000
    MAX_FIND_CHARS = 20000

    sandbox_dir.mkdir(parents=True, exist_ok=True)

    for i, step in enumerate(plan["steps"]):
        skill = step["skill"]
        params = step["params"]

        # Paths must be relative and inside sandbox
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

        if skill in ("replace_text", "remove_text"):
            if "path" not in params:
                raise SafetyError(f"Step {i} ({skill}) missing 'path'")
            find = params.get("find", "")
            if not isinstance(find, str) or len(find) == 0:
                raise SafetyError(f"Step {i} ({skill}) must include non-empty 'find' string")
            if len(find) > MAX_FIND_CHARS:
                raise SafetyError(f"Step {i} ({skill}) 'find' too large ({len(find)} chars)")
            if skill == "replace_text" and "replace" not in params:
                raise SafetyError(f"Step {i} ({skill}) missing 'replace'")
            # Require source to exist (editing a non-existent file is suspicious)
            target = (sandbox_dir / params["path"]).resolve()
            if not target.exists():
                raise SafetyError(f"Step {i} ({skill}) target does not exist: {params['path']}")

    return True
