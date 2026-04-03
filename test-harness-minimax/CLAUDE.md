# MiniMax Coding Eval — CLAUDE.md

This file is picked up automatically by Claude Code.

## What you are doing

You are being evaluated on software engineering tasks. Your job is to solve each
task and write the solution to the correct file. Nothing else.

## How to run the eval

### Step 1 — See what tasks need solving

```bash
python scripts/solve_tasks.py --list
```

### Step 2 — Print all task prompts

```bash
python scripts/solve_tasks.py
```

Read each task prompt carefully, solve it, and write the solution to
`results/solutions/<TASK_ID>.ts` — for example `results/solutions/BUG_001.ts`.

### Step 3 — Write solutions

For each task:
- Read the prompt carefully
- Write the complete solution to `results/solutions/<TASK_ID>.ts`
- The file should contain only the solution code — no test harness, no `main()`, no imports unless they are part of the solution

## Code style

- TypeScript unless the task says otherwise
- Prefer `async/await` over callbacks or raw Promises
- No TODO comments — solutions must be complete
- No unnecessary dependencies

## File naming

| Task ID | Output file |
|---|---|
| BUG_001 | results/solutions/BUG_001.ts |
| BUG_002 | results/solutions/BUG_002.ts |
| REFACTOR_001 | results/solutions/REFACTOR_001.ts |
| ... | ... |
