---
name: xray-clean
description: >-
  Remove all x-ray instrumentation from the codebase. Strips __XRAY__ marked
  lines, cleans up runner scripts, and verifies the repo is back to its
  original state.
  TRIGGER when: user says "xray clean", "clean up xray", "remove xray",
  or asks to remove instrumentation after an x-ray session.
  DO NOT TRIGGER when: x-ray session is still actively iterating.
user-invocable: true
---
<!-- repo-types: api-service, cli-tool, library, frontend-app, full-stack, monorepo -->

# X-Ray Clean

Remove all instrumentation left by the x-ray skill. Safe, verifiable,
and complete.

---

## Workflow

### Step 1: Survey

Find all `__XRAY__` markers in the codebase:

```bash
grep -rn "__XRAY__" .
```

Present the results to the user:

```
Found __XRAY__ markers in 4 files:

  api/handlers.py       -- 3 lines
  pagination/cursor.py  -- 4 lines
  data/items.py         -- 2 lines
  xray_runner.py        -- 8 lines (runner script)

Remove all? Or keep the runner script?
```

If no markers are found, report that the codebase is already clean and stop.

### Step 2: Remove Markers

Remove every line containing `__XRAY__` from source files. Two approaches,
in order of preference:

1. **Edit tool** (preferred): For each file, use the Edit tool to remove
   the marked lines. This gives the user visibility into each change.

2. **Batch removal** (if many files): If more than 5 files are affected,
   offer to batch-remove with:
   ```bash
   sed -i '' '/__XRAY__/d' $(grep -rl "__XRAY__" . --include="*.py" --include="*.js" --include="*.ts" --include="*.java" --include="*.kt" --include="*.go" --include="*.rb" --include="*.sh")
   ```

### Step 3: Runner Script

Ask the user about the runner script (`xray_runner.*`):

| User says | Action |
|-----------|--------|
| "Delete it" | Remove the file |
| "Keep it" | Leave it, but strip any `__XRAY__` markers from it |
| (no preference) | Default to deleting it |

### Step 4: Verify

Run verification to confirm clean removal:

1. `grep -rn "__XRAY__" .` -- should return nothing
2. `grep -rn "\[XRAY\]" .` -- should return nothing (catches any log strings
   that weren't on a marked line)
3. `git diff` -- review that only x-ray lines were removed, no accidental
   changes to business logic

Present the git diff to the user for confirmation.

### Step 5: Report

```
X-ray clean complete.

  Removed: 9 instrumentation lines across 3 source files
  Runner:  deleted xray_runner.py
  Verify:  no __XRAY__ or [XRAY] markers remain
  Diff:    only x-ray lines removed, no business logic changes
```

---

## Guidelines

**Do:**
- Always survey before removing -- show the user what will be cleaned
- Verify after removal -- grep for both `__XRAY__` and `[XRAY]`
- Show the git diff so the user can confirm nothing unexpected changed
- Ask about the runner script -- the user may want to keep it

**Don't:**
- Remove lines that don't have the `__XRAY__` marker
- Modify any business logic during cleanup
- Auto-delete the runner script without asking
- Skip verification
