# MiniMax Coding Eval

Evaluates MiniMax M2.5 on 10 real TypeScript software engineering tasks by running it
**inside Claude Code's agentic harness**, then grading the solutions with automated
Node.js tests and an optional Claude Sonnet judge.

## The two-phase workflow

```
Phase 1 (inside claude-minimax):  MiniMax solves the tasks → writes results/solutions/*.ts
Phase 2 (your shell):             grade.py tests the solutions + runs LLM judge
```

## Tasks

| ID | Category | Title | Difficulty |
|---|---|---|---|
| BUG_001 | Bug fixing | Off-by-one in pagination | Easy |
| BUG_002 | Bug fixing | Race condition in React hook | Medium |
| BUG_003 | Bug fixing | Timezone date comparison bug | Medium |
| REFACTOR_001 | Refactoring | Extract reusable API service | Medium |
| REFACTOR_002 | Refactoring | Nested conditionals → strategy pattern | Hard |
| REFACTOR_003 | Refactoring | Callback hell → async/await | Easy |
| API_001 | API integration | Fetch with retry + exponential backoff | Medium |
| API_002 | API integration | Request deduplication | Hard |
| API_003 | API integration | Fetch all paginated pages | Easy |
| API_004 | API integration | In-memory cache with TTL | Medium |

## Step-by-step

### Prerequisites

```bash
pip install anthropic   # for the LLM judge
node --version          # needed for automated tests
```

### Phase 1 — Solve (inside claude-minimax)

```bash
cd ~/minimax-eval
claude-minimax
```

Inside Claude Code, run:

```
python scripts/solve_tasks.py
```

Claude Code (MiniMax) will read all 10 task prompts and write solutions to
`results/solutions/<TASK_ID>.ts`. Once done, exit Claude Code.

### Phase 2 — Grade (your normal shell)

```bash
# Tests only
python scripts/grade.py --no-judge

# Tests + LLM judge (recommended)
python scripts/grade.py --judge-key sk-ant-YOUR_KEY

# Or export the key and just run:
export ANTHROPIC_API_KEY=sk-ant-YOUR_KEY
python scripts/grade.py
```

### Generate HTML report

```bash
python scripts/generate_report.py
open results/eval_*.html
```

## Re-running individual tasks

```bash
# Delete a solution and re-run solve for just that task
rm results/solutions/BUG_001.ts
# Back in claude-minimax:
python scripts/solve_tasks.py --tasks BUG_001

# Re-grade specific tasks
python scripts/grade.py --tasks BUG_001,API_002
```

## Project structure

```
minimax-eval/
  tasks/
    eval_tasks.json          ← Task definitions (read-only)
  results/
    solutions/               ← MiniMax's solutions written here by Claude Code
      BUG_001.ts
      BUG_002.ts
      ...
    eval_<timestamp>.json    ← Grade output
    eval_<timestamp>.html    ← HTML report
  scripts/
    solve_tasks.py           ← Run inside claude-minimax to print tasks
    grade.py                 ← Run in your shell to test + judge solutions
    generate_report.py       ← Generates HTML dashboard from grade output
  CLAUDE.md                  ← Picked up by Claude Code automatically
  README.md
```
