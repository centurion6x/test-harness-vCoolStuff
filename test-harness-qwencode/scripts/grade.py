#!/usr/bin/env python3
"""
grade.py
--------
Run this OUTSIDE Claude Code, after qwen/qwen3-coder-next has solved all tasks.

Reads solution files from results/solutions/<TASK_ID>.ts,
runs automated Node.js tests, then optionally scores with Claude as judge.

Usage:
  python scripts/grade.py                              # tests only
  python scripts/grade.py --judge-key sk-ant-xxx       # tests + LLM judge
  python scripts/grade.py --tasks BUG_001,API_002      # specific tasks only
  ANTHROPIC_API_KEY=sk-ant-xxx python scripts/grade.py # key from env
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
TASKS_FILE   = ROOT / "tasks" / "eval_tasks.json"
SOLUTIONS_DIR = ROOT / "results" / "solutions"
RESULTS_DIR  = ROOT / "results"
TMP_DIR      = ROOT / "results" / "_tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

JUDGE_MODEL = "claude-opus-4-6"


# ─── Node test runner ─────────────────────────────────────────────────────────

def run_node_test(solution_code: str, test_code: str, task_id: str) -> dict:
    """Inject solution + test into a temp TS file and run with tsx."""
    full_test = test_code.replace("SOLUTION_CODE", json.dumps(solution_code))
    # If the test only inspects the solution as a string (SOLUTION_CODE placeholder),
    # skip injecting the raw source to avoid import/require errors (e.g. React).
    if "SOLUTION_CODE" in test_code:
        preamble = ""
    else:
        preamble = "// ── Solution ──\n" + solution_code + "\n\n"
    script = (
        preamble
        + "// ── Test ──\ntry {\n  "
        + full_test
        + "\n} catch (e) {\n  console.error('TEST FAILED:', e.message);\n  process.exit(1);\n}\n"
    )
    tmp = TMP_DIR / f"_{task_id}.ts"
    tmp.write_text(script, encoding='utf-8')
    try:
        tsx_bin = ROOT / "node_modules" / ".bin" / "tsx"
        r = subprocess.run([str(tsx_bin), str(tmp)], capture_output=True, text=True, timeout=10, shell=True)
        passed = r.returncode == 0 and "PASSED" in r.stdout
        return {"passed": passed, "output": r.stdout.strip(), "error": r.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": "", "error": "Timeout after 10s"}
    except FileNotFoundError:
        return {"passed": False, "output": "", "error": "tsx not found — run: npm install tsx"}
    finally:
        tmp.unlink(missing_ok=True)


# ─── LLM judge ────────────────────────────────────────────────────────────────

def judge_solution(client, task: dict, solution_code: str) -> dict:
    prompt = f"""You are an expert software engineer evaluating an AI model's coding solution.
Your job is to find flaws and differentiate good solutions from bad ones. Do NOT default to high scores.

## Task
ID: {task['id']}  |  Category: {task['category']}  |  Difficulty: {task['difficulty']}
Title: {task['title']}

## Original prompt given to the model
{task['prompt']}

## Model's solution
```typescript
{solution_code}
```

## Scoring rubric (apply strictly)

**correctness** — Does the code produce the right output for all inputs, including edge cases?
- 5: Handles all cases correctly including non-obvious edge cases
- 4: Correct for all common cases, misses a subtle edge case
- 3: Works for the happy path but fails on important edge cases
- 2: Partially correct — core logic has a flaw
- 1: Fundamentally wrong or does not compile

**code_quality** — Is the code clean, idiomatic TypeScript, and well-structured?
- 5: Idiomatic TS, proper typing, no unnecessary code, good naming
- 4: Good but has a minor style issue (e.g. any type where a generic would work)
- 3: Works but uses poor patterns (e.g. type assertions instead of proper generics, overly verbose)
- 2: Messy, hard to read, significant style problems
- 1: Unreadable or ignores TypeScript entirely

**completeness** — Does the solution address every requirement in the prompt?
- 5: Every requirement met, nothing missing
- 4: All major requirements met, one minor aspect missing
- 3: Missing a clearly stated requirement
- 2: Multiple requirements missing
- 1: Barely addresses the prompt

**explanation** — If the prompt asked for explanation or the task benefits from it, did the model explain its reasoning? (If no explanation was needed, score based on whether inline comments clarify non-obvious logic)
- 5: Clear explanation of the why, not just the what
- 4: Adequate explanation, slightly surface-level
- 3: Minimal or boilerplate comments only
- 2: No explanation where one was clearly needed
- 1: Misleading or incorrect explanation

**overall** — Holistic score. This is NOT an average — weight correctness and completeness most heavily.
- 5: Production-ready, no issues
- 4: Solid, one minor issue
- 3: Acceptable but has a notable weakness
- 2: Significant problems
- 1: Not usable

## Task-specific criteria (these are MANDATORY checkpoints — check each one)
{task['judge_criteria']}

Be harsh. A solution that merely "works" but uses poor patterns, misses edge cases, or ignores specific requirements should NOT score above 3.

Respond ONLY with valid JSON, no markdown fences:
{{
  "correctness": <1-5>,
  "code_quality": <1-5>,
  "completeness": <1-5>,
  "explanation": <1-5>,
  "overall": <1-5>,
  "reasoning": "<2-3 sentence summary explaining the weakest aspects>"
}}"""

    try:
        import anthropic
        response = client.messages.create(
            model=JUDGE_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = re.sub(r"```json\n?|```", "", response.content[0].text).strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "correctness": 0, "code_quality": 0, "completeness": 0,
            "explanation": 0, "overall": 0,
            "reasoning": f"Judge error: {e}"
        }


# ─── Grading loop ─────────────────────────────────────────────────────────────

def grade_task(task: dict, judge_client=None) -> dict:
    task_id = task["id"]
    sol_file = SOLUTIONS_DIR / f"{task_id}.ts"

    print(f"\n{'─'*60}")
    print(f"  {task_id}  [{task['category']}]  {task['title']}")

    # ── Load solution ─────────────────────────────────────────────────────────
    if not sol_file.exists():
        print(f"  ⚠️  No solution file found: results/solutions/{task_id}.ts")
        return {
            "task_id": task_id,
            "category": task["category"],
            "title": task["title"],
            "difficulty": task["difficulty"],
            "solution_file": str(sol_file),
            "solution_code": None,
            "missing": True,
            "test_passed": False,
            "test_output": "",
            "test_error": "Solution file not found",
            "judge_scores": None,
        }

    solution_code = sol_file.read_text().strip()
    print(f"  Solution: {len(solution_code)} chars from {sol_file.name}")

    # ── Automated test ────────────────────────────────────────────────────────
    test_result = run_node_test(solution_code, task["test_code"], task_id)
    status = "✅ PASS" if test_result["passed"] else "❌ FAIL"
    print(f"  Test:     {status}")
    if not test_result["passed"] and test_result["error"]:
        print(f"  Error:    {test_result['error'][:200]}")

    # ── LLM judge ─────────────────────────────────────────────────────────────
    judge_scores = None
    if judge_client:
        print("  Judge:    running...", end="", flush=True)
        judge_scores = judge_solution(judge_client, task, solution_code)
        print(f" {judge_scores.get('overall', '?')}/5")

    return {
        "task_id": task_id,
        "category": task["category"],
        "title": task["title"],
        "difficulty": task["difficulty"],
        "solution_file": str(sol_file),
        "solution_code": solution_code,
        "missing": False,
        "test_passed": test_result["passed"],
        "test_output": test_result["output"],
        "test_error": test_result["error"],
        "judge_scores": judge_scores,
    }


# ─── Summary ──────────────────────────────────────────────────────────────────

def summarize(results: list[dict]) -> dict:
    total   = len(results)
    passed  = sum(1 for r in results if r["test_passed"])
    missing = sum(1 for r in results if r.get("missing"))
    failed  = total - passed - missing

    by_cat: dict = {}
    for r in results:
        c = r["category"]
        by_cat.setdefault(c, {"total": 0, "passed": 0})
        by_cat[c]["total"] += 1
        if r["test_passed"]:
            by_cat[c]["passed"] += 1

    judge_scores = [
        r["judge_scores"]["overall"]
        for r in results
        if r["judge_scores"] and r["judge_scores"].get("overall", 0) > 0
    ]
    avg_judge = round(sum(judge_scores) / len(judge_scores), 2) if judge_scores else None

    return {
        "total_tasks": total,
        "passed": passed,
        "failed": failed,
        "missing": missing,
        "pass_rate": f"{round(passed / total * 100)}%",
        "avg_judge_score": avg_judge,
        "by_category": by_cat,
    }


def print_summary(summary: dict, results: list[dict]):
    print(f"\n{'═'*60}")
    print("  GRADE RESULTS")
    print(f"{'═'*60}")
    print(f"  Tasks   : {summary['total_tasks']}")
    print(f"  Passed  : {summary['passed']}  ✅")
    print(f"  Failed  : {summary['failed']}  ❌")
    if summary["missing"]:
        print(f"  Missing : {summary['missing']}  ⚠️")
    print(f"  Pass rate: {summary['pass_rate']}")
    if summary["avg_judge_score"]:
        print(f"  Avg judge score: {summary['avg_judge_score']}/5")

    print(f"\n  By category:")
    for cat, stats in summary["by_category"].items():
        pct = round(stats["passed"] / stats["total"] * 100)
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        print(f"    {cat:<22} {bar} {pct:>3}%  ({stats['passed']}/{stats['total']})")

    if summary["avg_judge_score"]:
        print(f"\n  Judge dimensions:")
        for dim in ["correctness", "code_quality", "completeness", "explanation"]:
            scores = [
                r["judge_scores"][dim]
                for r in results
                if r["judge_scores"] and r["judge_scores"].get(dim, 0) > 0
            ]
            if scores:
                avg = round(sum(scores) / len(scores), 1)
                bar = "█" * int(avg) + "░" * (5 - int(avg))
                print(f"    {dim:<16} {bar}  {avg}/5")

    print(f"{'═'*60}\n")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Grade qwencoder solutions from Claude Code")
    parser.add_argument("--judge-key", default=os.getenv("ANTHROPIC_API_KEY"),
                        help="Anthropic API key for LLM judge (or set ANTHROPIC_API_KEY)")
    parser.add_argument("--tasks", help="Comma-separated task IDs (default: all)")
    parser.add_argument("--no-judge", action="store_true", help="Skip LLM judge, run tests only")
    args = parser.parse_args()

    tasks = json.loads(TASKS_FILE.read_text())
    if args.tasks:
        ids = {t.strip() for t in args.tasks.split(",")}
        tasks = [t for t in tasks if t["id"] in ids]

    print(f"\n{'═'*60}")
    print(f"  QWENCODER EVAL — GRADE PHASE")
    print(f"  {len(tasks)} tasks  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Reading solutions from: results/solutions/")

    # Init judge
    judge_client = None
    if not args.no_judge:
        if args.judge_key:
            import anthropic
            judge_client = anthropic.Anthropic(api_key=args.judge_key)
            print(f"  Judge: {JUDGE_MODEL}")
        else:
            print("  Judge: disabled  (pass --judge-key or set ANTHROPIC_API_KEY)")
    else:
        print("  Judge: disabled  (--no-judge)")
    print(f"{'═'*60}")

    results = [grade_task(task, judge_client) for task in tasks]
    summary = summarize(results)
    print_summary(summary, results)

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"eval_{ts}.json"
    out.write_text(json.dumps({"summary": summary, "model": "qwen/qwen3-coder-next",
                                "timestamp": ts, "results": results}, indent=2))
    print(f"  Results saved → results/eval_{ts}.json")
    print(f"  Generate report: python scripts/generate_report.py\n")


if __name__ == "__main__":
    main()
