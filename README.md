
# Cage Code-Runner

A minimal code-runner with guardrails that operates inside a safe "cage" environment.

## Six Core Pieces

1. **Room** - The safe place it runs (paths, startup)
2. **Referee** - The rule-keeper that enforces constraints
3. **Logbook** - Append-only JSONL record of all operations
4. **Workbench** - Controlled file IO under `./workspace`
5. **Rulebook** - Your preferences and corrections (JSON)
6. **Voice** - Consistent "Maxim + Threadline" response format

## Key Rules

- **Plan-then-Act**: No edits unless a PLAN was recorded this run
- **Diff-only**: Never write whole files; generate and apply diffs/patches
- **Append-only log**: `trail.log` is JSONL; only append, never edit/remove
- **Rehydrate-before-act**: Read rulebook + relevant past corrections before planning/acting
- **Workspace-only**: Only paths under `./workspace` are writable
- **Publish gate**: Moving files from `workspace/` → `artifacts/` requires explicit approval

## Directory Structure

```
cage/
  run.py                 # CLI entrypoint
  cagecore/
    room.py             # paths, startup
    referee.py          # rule checks
    logbook.py          # append-only JSONL log
    workbench.py        # controlled file IO under ./workspace
    rulebook.py         # preferences + corrections (JSON)
    voice.py            # "Maxim + Threadline" responses
    planner.py          # makes a PLAN object (no editing)
    executor.py         # applies diffs only
    diffs.py            # make/apply unified diffs
    rehydrator.py       # loads past corrections + prefs
    arc.py              # Adaptive Retrieval Controller (context amount)
    tests.py            # smoke/guard checks
  workspace/            # only writable area for content
  artifacts/            # publish target (requires approval)
  rulebook.json         # created on init if missing
  trail.log             # append-only JSONL
```

## CLI Commands

### Initialize the cage
```bash
python run.py init
```

### Create a plan
```bash
python run.py plan "Update greeting" --file sample.txt --replace "Hello" --with "Hey"
```

### Show the latest plan
```bash
python run.py show-plan
```

### Apply the latest plan
```bash
python run.py apply
```

### Publish a file to artifacts
```bash
python run.py publish --file sample.txt
```

### Show recent log entries
```bash
python run.py show-log
```

### Add a correction rule
```bash
python run.py add-correction --from "Hello" --to "Hey" --note "Prefer casual tone"
```

## Example Workflow

1. Initialize: `python run.py init`
2. Plan a change: `python run.py plan "Fix greeting" --file sample.txt --replace "Hello" --with "Hi"`
3. Apply the change: `python run.py apply`
4. Publish if tests pass: `python run.py publish --file sample.txt`

## Rule Violations

If any rule is violated, you'll see this exact message:
> `Not allowed. Diff-only and append-only per the rules.`

The violation will also be logged to `trail.log`.

## License

MIT License - see LICENSE file for details.
