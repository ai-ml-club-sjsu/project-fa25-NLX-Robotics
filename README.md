
# NLX Robotics — LLM‑to‑Action Platform

**Academic Year:** 2025–2026  
**Project Duration:** September 2025 – December 2025 (MVP); extensions in Spring 2026

> One‑sentence pitch: Natural language → constrained JSON action plans → validated, safe execution on a small robotic arm, with simulation first and a light hardware demo.

---

## Overview

This project builds a production‑quality, portfolio‑ready platform where a user types a command in natural language and a constrained planner (LLM) emits a JSON action plan. That plan is validated against schema, limits, and reachability, then executed in simulation (PyBullet) and on a 2–3 DOF tabletop robotic arm with a claw. The MVP focuses on fiducial‑guided pick‑and‑place and publishes clear metrics, logs, and documentation.

**Deliverables (MVP):**
- Public repository with tests, docs, and CI
- 90–120s demo video
- Metrics report (plan validity, task success, latency, safety)
- Minimal UI (CLI; small web panel optional)

---

## Key Objectives

- Convert user text/voice into a validated JSON skills plan
- Enforce safety via schema, unit checks, limits, and timeouts
- Execute plans in PyBullet and on a small arm (2–3 DOF + claw)
- Log telemetry and publish reproducible results with documentation

---

## MVP Scope (Fall 2025)

- 2–3 DOF tabletop arm + claw (simulation + light hardware)
- Skill DSL (allow‑listed actions), LLM planner (function‑calling to JSON), validator/safety gate
- Pick‑and‑place of a single fiducial‑marked object between two pads
- Telemetry logs, plots, and a minimal CLI (web panel optional)

**Out of scope (AY 2025–26):** high‑payload arms, force control, general object detection without fiducials, multi‑robot.

---

## Success Criteria (Pass/Fail)

- **Plan validity:** ≥ 95% JSON plans pass schema/limits on first try  
- **Task success:** ≥ 90% pick‑and‑place success over 20 randomized trials  
- **Safety:** 0 limit violations; watchdog never missed; e‑stop functional  
- **Latency:** ≤ 5 s from text entry to motion start

---

## Architecture

- Working On This

**Core data contracts:**
- **Skill JSON:** `task`, `steps[]` with `{ skill, params, constraints, on_fail }`
- **Waypoints:** timestamped Cartesian poses or joint targets
- **HW frames:** `skill_id`, `params`, `checksum`, `seq_no` with `ack/nack`

---

## Quick Start

### Prerequisites
- Python 3.11+  
- Git  
- (Recommended) `uv` or Poetry for environment management  
- Platform builds for PyBullet (Linux/macOS/Windows OK)

### Setup

**Option A — `uv`:**
```bash
git clone https://github.com/aiml-club/[repo-name].git
cd [repo-name]
uv sync
```

**Option B — Poetry:**
```bash
poetry install
poetry shell
```

**Option C — pip + venv:**
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the demos

```bash
# 1) Open PyBullet scene and run a canned plan
make sim_demo

# 2) Turn NL → validated JSON plan
make plan "move the red block to the right pad"

# 3) Execute a saved plan in sim and write logs to runs/
make run --plan plans/example.json

# 4) (Hardware) Bring-up & safety checks, then run
make hw_bringup
make hw_run
```

---

## Skills DSL (JSON Schema) — v0.1

- Location: `planner/schema/skill_schema.json`  
- Design: **allow‑listed** skills with explicit units, bounds, and timeouts.  
- Example (excerpt):
```json
{
  "task": "pick_and_place",
  "steps": [
    {"skill":"move_to","params":{"target":"tag:BLOCK_A"},"constraints":{"speed_mm_s": 120}},
    {"skill":"lower","params":{"dz_mm": 35}},
    {"skill":"close_gripper"},
    {"skill":"lift","params":{"dz_mm": 50}},
    {"skill":"move_to","params":{"target":"pad:B"}},
    {"skill":"open_gripper"},
    {"skill":"lift","params":{"dz_mm": 30}}
  ]
}
```

---

## Toolchain & Standards

- **Language:** Python 3.11; VS Code; Arduino C/C++;
- **Planner:** LLM with function‑calling to a JSON Schema; self‑check re‑prompt
- **Simulation:** PyBullet (fast start). Optional ROS 2/Gazebo in Spring
- **Vision:** OpenCV + AprilTag/ArUco (tabletop; pads + block)
- **Control:** PID + trapezoidal velocity profile; 50–100 Hz on hardware
- **Hardware:** 2–3 hobby servos, claw, MCU (Arduino/STM32) or Raspberry Pi; USB webcam
- **Docs:** mkdocs; Mermaid diagrams
- **CI:** GitHub Actions (lint, tests, schema checks)
- **Pre‑commit:** ruff/black, trailing whitespace
- **Repo conventions:** Conventional Commits; PR template and issue labels
- **License:** MIT; include CODE_OF_CONDUCT.md and CONTRIBUTING.md

---

## Testing Strategy

**Levels:** unit (schema validator, IK, PID, profiles, protocol codec) → integration (planner→validator→sim executor; vision→mapping→move_to) → hardware‑in‑the‑loop.  

**Matrix (excerpt):**
| ID   | Scenario         | Initial State                       | Command                               | Expected Plan                                   | Expected Outcome                            |
|------|------------------|-------------------------------------|----------------------------------------|-------------------------------------------------|---------------------------------------------|
| T‑001| Simple move      | Home pose                            | “rotate base 30 degrees”               | one step `rotate_base(30deg)`                   | Joint within limits, ≤ 1s                   |
| T‑010| Pick & place     | Block @ pad A; pad B empty           | “move red block to right pad”          | lower→close→lift→move_to(B)→open→lift           | Block at B; no violations                   |
| T‑020| Safety limit     | Block beyond reach                    | “move block off table”                 | Planner refuses / error                         | No motion                                   |

**Fuzzing:** Hypothesis tests on random NL phrasings to constrained plans; random controller disturbances in sim.  
**Metrics:** `plan_validity_rate`, `task_success_rate_{sim,hw}`, `violations`, `latency`, `token_cost`.

---

## Safety Plan & Checklists

**Pre‑run:** workspace clear; e‑stop reachable; power within limits; cables strain‑relieved; soft limits set; watchdog armed; logs enabled.  
**Runtime guards:** step timeouts; position‑error threshold; rate limits & jerk caps; abort on `nack` or sensor dropout.  
**Post‑run:** export logs; annotate anomalies; update risk log.

---

## Roadmap (Fall 2025, Weeks 1–12)

- **W1:** Repo init, CI, pre‑commit; Skill Schema v0.1; PyBullet scaffold; planner/validator stubs  
- **W2:** JSON Schema + validator tests; planner stub function‑calling; few‑shot examples  
- **W3:** Kinematics (FK/IK), PID, trapezoidal profiles; offline trajectory plots  
- **W4:** End‑to‑end in sim (no vision); logger (CSV + plots)  
- **W5:** LLM in the loop; measure plan validity and latency; demo clip  
- **W6:** Vision baseline (AprilTag/ArUco); calibration; homography mapping  
- **W7:** Hardware bring‑up; serial protocol; bench tests & e‑stop  
- **W8:** HW integration; watchdog; rate limits; latency/jitter measurements  
- **W9:** Vision‑in‑loop on hardware; first full pick‑and‑place  
- **W10:** Reliability pass (20 randomized trials); fix flakes; metrics v1  
- **W11:** Docs & tests; coverage ≥ 75%; CI badges; instructor dry‑run  
- **W12:** MVP freeze; record 90–120s video; release v0.1.0

*(Winter/Spring: macro skills, plan cache, safety envelopes, better IK, web UI.)*

---

## Communication & Links
 
- **Docs site:** https://aiml-club.github.io/[repo-name]/ (mkdocs)  
- **Demo video:** [link‑to‑be‑added]

---

## Contributors

*For detailed member info including LinkedIn profiles and Discord handles, see `docs/members.csv`.*

| Name | Role | Email | GitHub |
|------|------|-------|--------|
| [Lead Name] | Project Lead & [Primary Role] | [email@university.edu] | [@github-username](https://github.com/username) |
| [Member Name 2] | [Role] | [email@university.edu] | [@github-username](https://github.com/username) |
| [Member Name 3] | [Role] | [email@university.edu] | [@github-username](https://github.com/username) |
| [Member Name 4] | [Role] | [email@university.edu] | [@github-username](https://github.com/username) |

---

## How to Contribute

- No Contribution So Far

---

## License

No Liceses So Far

---

## Acknowledgments

- [Advisor / Mentor Name]
- [Collaborators / Libraries / Inspiration]

---

## Contact

**Project Lead:** Manny Han · 📧 taoxu.han@sjsu.edu · 💼 linkedin.com/in/mannyhan  
**Faculty Advisor:** [Advisor Name] · 📧 [advisor.email@university.edu]

---

**Last Updated:** 2025-09-29  
**Next Review:** [YYYY-MM-DD]
