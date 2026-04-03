#!/usr/bin/env python3
"""
solve_tasks.py
--------------
Run this from INSIDE Claude Code (backed by GLM).

Claude Code will read this script's output, then autonomously solve
each task and write solutions to results/solutions/<TASK_ID>.ts

The agent should:
  1. Read each task prompt below
  2. Solve it
  3. Write ONLY the solution code (no test harness) to the specified file
  4. Move on to the next task

Usage:
  python scripts/solve_tasks.py              # all 10 tasks
  python scripts/solve_tasks.py --tasks BUG_001,API_002
  python scripts/solve_tasks.py --list       # just show task IDs
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
TASKS_FILE = ROOT / "tasks" / "eval_tasks.json"
SOLUTIONS_DIR = ROOT / "results" / "solutions"
SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", help="Comma-separated task IDs to solve (default: all)")
    parser.add_argument("--list", action="store_true", help="List task IDs and exit")
    args = parser.parse_args()

    tasks = json.loads(TASKS_FILE.read_text())

    if args.list:
        for t in tasks:
            solved = "✅" if (SOLUTIONS_DIR / f"{t['id']}.ts").exists() else "  "
            print(f"  {solved} {t['id']:<16} [{t['category']}]  {t['title']}")
        return

    if args.tasks:
        ids = {t.strip() for t in args.tasks.split(",")}
        tasks = [t for t in tasks if t["id"] in ids]

    # Check which are already solved
    pending = [t for t in tasks if not (SOLUTIONS_DIR / f"{t['id']}.ts").exists()]
    already = [t for t in tasks if (SOLUTIONS_DIR / f"{t['id']}.ts").exists()]

    if already:
        print(f"# Already solved ({len(already)} skipped): {', '.join(t['id'] for t in already)}")
        print(f"# Delete results/solutions/<TASK_ID>.ts to re-solve\n")

    if not pending:
        print("# All tasks already solved. Run: python scripts/grade.py")
        return

    print(f"# {'='*60}")
    print(f"# GLM EVAL — SOLVE PHASE")
    print(f"# {len(pending)} tasks to solve | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"# For each task: write solution code to results/solutions/<TASK_ID>.ts")
    print(f"# {'='*60}\n")

    for task in pending:
        out_path = f"results/solutions/{task['id']}.ts"
        print(f"# {'─'*60}")
        print(f"# TASK {task['id']}  [{task['category']}]  [{task['difficulty']}]")
        print(f"# {task['title']}")
        print(f"# Output file: {out_path}")
        print(f"# {'─'*60}")
        print(task["prompt"])
        print(f"\n# END TASK {task['id']}\n")

    print(f"# {'='*60}")
    print(f"# Solve all {len(pending)} tasks above.")
    print(f"# Write each solution to results/solutions/<TASK_ID>.ts")
    print(f"# Only write the solution code — no test harness, no main().")
    print(f"# Once all files are written, run: python scripts/grade.py")
    print(f"# {'='*60}")


if __name__ == "__main__":
    main()
