# -*- coding: utf-8 -*-
import shutil
import pathlib
from typing import Any, Dict, List, Tuple

class ExecError(Exception):
    pass

def run_plan(plan: Dict[str, Any], sandbox_dir: pathlib.Path) -> Tuple[List[Dict[str, Any]], pathlib.Path]:
    """
    Execute a validated plan inside sandbox_dir.
    Returns (logs, output_path). output_path is last artifact if produced, else sandbox_dir.
    """
    logs: List[Dict[str, Any]] = []
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    last_artifact: pathlib.Path | None = None

    for idx, step in enumerate(plan["steps"]):
        skill = step["skill"]
        params = step["params"]
        on_fail = step.get("on_fail", "abort")

        def rel(p: str) -> pathlib.Path:
            return (sandbox_dir / p).resolve()

        try:
            if skill == "create_file":
                path = rel(params["path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"")
                result = {"ok": True, "step": idx, "skill": skill, "path": str(path)}
                last_artifact = path

            elif skill == "write_text":
                path = rel(params["path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                text = params.get("text", "")
                path.write_text(text, encoding="utf-8")
                result = {"ok": True, "step": idx, "skill": skill, "bytes": len(text), "path": str(path)}
                last_artifact = path

            elif skill == "append_text":
                path = rel(params["path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as f:
                    f.write(params.get("text", ""))
                result = {"ok": True, "step": idx, "skill": skill, "path": str(path)}
                last_artifact = path

            elif skill == "replace_text" or skill == "remove_text":
                path = rel(params["path"])
                original = path.read_text(encoding="utf-8")
                find = params.get("find", "")
                repl = "" if skill == "remove_text" else params.get("replace", "")
                # count: 0/None → replace all
                count_param = params.get("count", 0)
                count_effective = -1 if (count_param is None or count_param == 0) else int(count_param)

                occurrences = original.count(find) if find else 0
                new_text = original.replace(find, repl, count_effective)

                if new_text != original:
                    path.write_text(new_text, encoding="utf-8")

                replaced = occurrences if count_effective == -1 else min(occurrences, count_effective)
                result = {
                    "ok": True,
                    "step": idx,
                    "skill": skill,
                    "path": str(path),
                    "find": find,
                    "replacements": replaced
                }
                last_artifact = path

            elif skill == "read_file":
                path = rel(params["path"])
                text = path.read_text(encoding="utf-8")
                result = {"ok": True, "step": idx, "skill": skill, "path": str(path), "preview": text[:200]}

            elif skill == "list_dir":
                path = rel(params["path"])
                items = sorted([p.name for p in path.iterdir()])
                result = {"ok": True, "step": idx, "skill": skill, "path": str(path), "items": items}

            elif skill == "move_file":
                src = rel(params["path"])
                dst = rel(params["dest"])
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                result = {"ok": True, "step": idx, "skill": skill, "from": str(src), "to": str(dst)}
                last_artifact = dst

            elif skill == "copy_file":
                src = rel(params["path"])
                dst = rel(params["dest"])
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                result = {"ok": True, "step": idx, "skill": skill, "from": str(src), "to": str(dst)}
                last_artifact = dst

            elif skill == "delete_file":
                path = rel(params["path"])
                if path.exists():
                    path.unlink()
                result = {"ok": True, "step": idx, "skill": skill, "deleted": str(path)}

            else:
                raise ExecError(f"Unknown skill: {skill}")

        except Exception as e:
            logs.append({"ok": False, "step": idx, "skill": skill, "error": str(e)})
            if on_fail == "abort":
                return logs, last_artifact or sandbox_dir
            continue

        logs.append(result)

    return logs, last_artifact or sandbox_dir
