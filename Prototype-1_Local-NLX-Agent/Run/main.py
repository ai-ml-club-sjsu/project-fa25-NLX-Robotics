# -*- coding: utf-8 -*-
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Planner.planner import plan_from_prompt
from Validator.validator import validate_plan, SafetyError
from Executor.executor import run_plan

CONF = ROOT / "config.json"
SANDBOX = ROOT / "runs" / "sandbox"


def _ensure_dirs():
    SANDBOX.mkdir(parents=True, exist_ok=True)
    (ROOT / "runs").mkdir(parents=True, exist_ok=True)


def interactive_chat():
    """Continuous natural-language conversation with automatic plan → validate → execute."""
    print("🧠 NLX Local Agent is ready. Type 'exit' or 'quit' to stop.\n")
    while True:
        user = input("You> ").strip()
        if user.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        if not user:
            continue

        try:
            print("\n🤖 Thinking...")
            plan = plan_from_prompt(user)
            print("\n--- PLAN ---")
            print(json.dumps(plan, indent=2))

            validate_plan(plan, SANDBOX)
            print("✅ Validation passed")

            logs, artifact = run_plan(plan, SANDBOX)
            log_path = ROOT / "runs" / "last_run.json"
            log_path.write_text(
                json.dumps({"plan": plan, "logs": logs, "artifact": str(artifact)}, indent=2),
                encoding="utf-8",
            )

            print(f"✨ Done. Artifact: {artifact}\n")
        except SafetyError as e:
            print(f"❌ Safety error: {e}\n")
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Stage-1 NLX (local) – plan/validate/execute")
    parser.add_argument("--prompt", type=str, help="One-shot natural language request")
    parser.add_argument("--plan", type=pathlib.Path, help="Path to a JSON plan file")
    parser.add_argument("--dry", action="store_true", help="Stop after validation")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat mode")
    args = parser.parse_args()

    _ensure_dirs()

    if args.chat:
        interactive_chat()
        return

    if args.prompt:
        print("Planning with local LLM (Ollama)…")
        plan = plan_from_prompt(args.prompt)
    elif args.plan:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    else:
        print("Please provide --prompt, --plan, or --chat")
        return

    print("\n--- PLAN ---")
    print(json.dumps(plan, indent=2))
    print("\nValidating…")
    validate_plan(plan, SANDBOX)
    print("Validation passed ✅")

    if args.dry:
        print("Dry run – not executing.")
        return

    print("\nExecuting…")
    logs, artifact = run_plan(plan, SANDBOX)
    (ROOT / "runs").mkdir(exist_ok=True, parents=True)
    log_path = ROOT / "runs" / "last_run.json"
    log_path.write_text(json.dumps({"plan": plan, "logs": logs, "artifact": str(artifact)}, indent=2), encoding="utf-8")

    print("Done. Logs at runs/last_run.json")
    print(f"Final artifact: {artifact}")


if __name__ == "__main__":
    main()
