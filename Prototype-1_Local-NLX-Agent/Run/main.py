# -*- coding: utf-8 -*-
import argparse
import json
import pathlib
import sys
from typing import Any, Dict

# Make sure the project root is on sys.path whether we run with -m or as a script
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Planner.planner import plan_from_prompt  # noqa: E402
from Validator.validator import validate_plan, SafetyError  # noqa: E402
from Executor.executor import run_plan  # noqa: E402

CONF = ROOT / "config.json"
SANDBOX = ROOT / "runs" / "sandbox"

DEFAULT_CONFIG = {"model": "llama3", "sandbox_dir": str(SANDBOX)}

def load_config() -> Dict[str, Any]:
    if not CONF.exists():
        CONF.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    return json.loads(CONF.read_text(encoding="utf-8"))

def main():
    parser = argparse.ArgumentParser(description="Stage-1 NLX (local) – plan/validate/execute")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt", type=str, help="Natural language request")
    g.add_argument("--plan", type=pathlib.Path, help="Path to a JSON plan file")
    parser.add_argument("--dry", action="store_true", help="Stop after validation")
    args = parser.parse_args()

    cfg = load_config()
    sandbox = pathlib.Path(cfg["sandbox_dir"])

    if args.prompt:
        print("Planning with local LLM (Ollama)…")
        plan = plan_from_prompt(args.prompt)
    else:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))

    print("\n--- PLAN ---")
    print(json.dumps(plan, indent=2))

    print("\nValidating…")
    try:
        validate_plan(plan, sandbox)
    except (SafetyError, Exception) as e:
        print(f"VALIDATION FAILED: {e}")
        raise SystemExit(1)
    print("Validation passed ✅")

    if args.dry:
        print("Dry run – not executing.")
        return

    print("\nExecuting…")
    logs, artifact = run_plan(plan, sandbox)
    (ROOT / "runs").mkdir(exist_ok=True, parents=True)
    log_path = ROOT / "runs" / "last_run.json"
    log_path.write_text(json.dumps({"plan": plan, "logs": logs, "artifact": str(artifact)}, indent=2), encoding="utf-8")

    print("Done. Logs at runs/last_run.json")
    print(f"Final artifact: {artifact}")

if __name__ == "__main__":
    main()
