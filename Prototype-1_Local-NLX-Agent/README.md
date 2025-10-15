# Prototype-1 Local NLX Agent (Stage-1)

Minimal LLM→Plan→Validate→Execute loop for **local** file-system tasks (no robotics).
- Planner: Ollama (llama3).
- Validator: JSON Schema + safety policy (sandboxed paths).
- Executor: safe file ops inside `runs/sandbox/`.

## Quickstart
1. Install and run Ollama:
   - https://ollama.com/download
   - `ollama pull llama3`
   - `ollama serve` (keep it running)
2. Python env (Windows PowerShell):
   ```pwsh
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r "Set Up/requirements.txt"
3. Run(Start Chat)
   python -m Run.main --chat

