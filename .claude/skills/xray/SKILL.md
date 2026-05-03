---
name: xray
description: >-
  Instrument code paths with targeted logging to understand execution flow
  end-to-end. Like a debugger using print statements -- zero setup, works
  anywhere, produces a readable narrative of what actually happens.
  TRIGGER when: user wants to understand how unfamiliar code works, see
  what actually happens at runtime, or build a mental model of code they
  did not write.
  DO NOT TRIGGER when: debugging a specific known bug (use systematic-debugging),
  or reviewing code for quality (use code-review).
user-invocable: true
---

# X-Ray

Instrument unfamiliar code with targeted logging to make execution flow
visible. Like a debugger but using print statements -- zero setup, works
in any environment, and produces a readable narrative of what actually
happens when code runs.

---

## Philosophy

Understanding comes from seeing concrete values flow through real code.
Reading source and generating reference docs produces shallow, unverified
knowledge. This skill makes the implicit explicit: add temporary logging
at key points, run the code, read what actually happened.

The x-ray output serves both the user (learning) and the AI (validation).
Making something obvious enough for an AI to get right is the same work
as making it obvious enough for a human to understand.

---

## When to Use

| Scenario | Use This |
|----------|----------|
| Unfamiliar framework or library code | Yes |
| "Which code path actually runs?" questions | Yes |
| Implicit behavior (defaults, DI, config-driven) | Yes -- especially |
| Understanding code an AI wrote | Yes |
| End-to-end request/response flow | Yes |
| Known bug with a stack trace | No -- use systematic-debugging |
| Code review for quality | No -- use code-review |

---

## Marker Convention

Every line added by this skill ends with a language-appropriate marker:

| Language | Marker |
|----------|--------|
| Python | `# __XRAY__` |
| JavaScript/TypeScript | `// __XRAY__` |
| Java/Kotlin/Go | `// __XRAY__` |
| Ruby | `# __XRAY__` |
| Shell | `# __XRAY__` |

This makes all instrumentation greppable and removable in one command.

### Log Output Format

```
[XRAY] <depth> <location> | <event> | <key=value, ...>
```

- **depth**: arrows showing call depth (`>`, `>>`, `>>>`, etc.)
- **location**: `Class.method` or `module.function`
- **event**: one of `entry`, `exit`, `branch`, `value`, `query`, `response`, `default`
- **key=value**: the specific runtime values that matter at this point

Example output:
```
[XRAY] > PaginationHandler.handle | entry | endpoint=/api/items, page_token=None
[XRAY] >> CursorFactory.create | branch | no token provided, using default
[XRAY] >> CursorFactory.create | default | cursor_type=OffsetCursor, page_size=20
[XRAY] >> CursorFactory.create | exit | cursor=OffsetCursor(offset=0, limit=20)
[XRAY] >> ItemRepository.query | query | sql=SELECT * FROM items LIMIT 20 OFFSET 0
[XRAY] >> ItemRepository.query | response | row_count=20, has_more=True
[XRAY] > PaginationHandler.handle | exit | next_token=eyJvZmZzZXQiOjIwfQ==
```

---

## Workflow

### Phase 1: Target

Ask the user (or extract from their prompt):

1. **What operation?** -- e.g., "paginated list request with default cursor"
2. **What entry point?** -- e.g., endpoint, function, CLI command, test
3. **What is confusing?** -- e.g., "I don't know which cursor type gets used
   when no cursor is specified"

If any of these are unclear, ask before proceeding. A vague target produces
useless instrumentation.

### Phase 2: Map

Use available search/exploration tools or sub-agents to find the code paths
involved. Prefer fast local search tools such as `rg` and file listing when
available. Search for:

- Entry point(s) for the operation
- Key functions in the call chain (follow the calls, don't guess)
- Decision points: conditionals, factory methods, DI resolution, config lookups
- Data transformations (serialization, encoding, mapping)
- External calls: DB queries, API calls, cache reads/writes
- Return path back to the caller

**Output to user:** An ordered list of code locations with one-line descriptions.
Present this as the proposed instrumentation plan. Example:

```
X-ray plan for: paginated list request with default cursor

1. PaginationHandler.handle (api/handlers.py:45) -- entry point, receives request
2. CursorFactory.create (pagination/cursor.py:12) -- decides cursor type
3. CursorFactory._default_cursor (pagination/cursor.py:67) -- builds default
4. ItemRepository.list_items (data/items.py:89) -- executes DB query
5. PaginationSerializer.encode (pagination/serializer.py:30) -- encodes next cursor
6. PaginationHandler.handle (api/handlers.py:62) -- builds response

Instrument these locations? Or adjust first?
```

Wait for user confirmation or adjustment before proceeding.

### Phase 3: Instrument

Add logging at the confirmed locations. Rules:

- **Start light.** Instrument the confirmed locations only. Do not blanket
  the codebase. 3-8 log statements is a good first pass.
- **Every added line gets the `__XRAY__` marker** so cleanup is trivial.
- **Log concrete values**, not descriptions. `cursor_type=OffsetCursor` not
  `"using default cursor type"`.
- **Log at decision points**, not just entry/exit. The branch taken is often
  the thing the user needs to see.
- **Use the language's native print/log.** Python: `print(f"...")`. JS:
  `console.log(...)`. Java: `System.out.println(...)`. No external dependencies.
- **Do not modify business logic.** Only add print/log lines. Never change
  control flow, variable assignments, or return values.

Example instrumentation (Python):
```python
def create(self, page_token=None):
    print(f"[XRAY] >> CursorFactory.create | entry | page_token={page_token}")  # __XRAY__
    if page_token is None:
        print(f"[XRAY] >> CursorFactory.create | branch | no token, using default")  # __XRAY__
        cursor = self._default_cursor()
        print(f"[XRAY] >> CursorFactory.create | exit | cursor={cursor}")  # __XRAY__
        return cursor
```

### Phase 4: Script

Generate a runner script that exercises the instrumented code path. Save it
to the project root as `xray_runner.py` (or appropriate name/extension).

The script must:
- **Be self-contained** -- handle imports, setup, config
- **Use concrete inputs** -- real or realistic values, not placeholders
- **Be re-runnable** -- no side effects that prevent a second run, or
  include cleanup/reset logic
- **Print a header** so x-ray output is easy to find in noisy logs:
  ```
  print("=" * 60)  # __XRAY__
  print("[XRAY] === Starting x-ray: <description> ===")  # __XRAY__
  print("=" * 60)  # __XRAY__
  ```
- **Include comments** explaining what it exercises and what to look for

If the code path requires infrastructure (DB, external service) that is not
available, note this and help the user set up the minimum needed, or suggest
mocking just the external boundary.

### Phase 5: Run

Execute the runner script. Capture the output and present it to the user with
brief annotations:

```
X-ray output for: paginated list request with default cursor
============================================================

[XRAY] > PaginationHandler.handle | entry | endpoint=/api/items, page_token=None
  ^ Request comes in with no cursor

[XRAY] >> CursorFactory.create | branch | no token, using default
  ^ This is the answer to your question -- default path is taken

[XRAY] >> CursorFactory.create | default | cursor_type=OffsetCursor, page_size=20
  ^ Default is OffsetCursor with page_size=20 (configured in settings.py:14)

...
```

If the script cannot run (missing deps, env issues), help the user resolve
the blocker. Do not skip this phase -- the x-ray output IS the deliverable.

### Phase 6: Iterate

After presenting output, ask the user what they want to do:

| User says | Action |
|-----------|--------|
| "Deeper into X" | Add more logging in that area, re-run |
| "What's this value?" | Add a specific log for that variable, re-run |
| "That's clear, what about Y?" | Shift instrumentation to new area |
| "Add the DB query" | Instrument the data layer, re-run |
| "Good, I get it" | Move to Phase 7 |
| "Clean up" | Move to Phase 7 |

Each iteration re-runs the script so the user sees updated output.
The instrumentation grows incrementally -- only add, don't remove, unless the user
says an area is clear.

### Phase 7: Clean

Invoke the **xray-clean** skill to remove all instrumentation. It handles marker
removal, runner script cleanup, and verification.

---

## Guidelines

**Do:**
- Start light -- 3-8 log statements on the first pass
- Log values, not descriptions
- Wait for user confirmation of the trace plan before instrumenting
- Make the runner script trivially re-runnable
- Annotate the x-ray output so the user can follow the narrative

**Don't:**
- Blanket the codebase with logging -- targeted beats exhaustive
- Modify any business logic, even "temporarily"
- Skip the run phase -- unexecuted instrumentation is just more code to read
- Add logging to test files (instrument source, exercise via script)
- Leave `__XRAY__` markers after the session ends

---

## REPL Alternative

If the user prefers interactive exploration over a script:

1. Provide a series of REPL commands instead of a runner script
2. Each command exercises one step of the flow
3. The user can inspect intermediate values between steps
4. Instrumentation still uses `__XRAY__` markers for cleanup

The REPL approach works best when:
- The user wants to poke at individual functions
- The full end-to-end flow is hard to trigger from a script
- The user wants to try different inputs interactively

The script approach works best when:
- The flow is end-to-end (API request to DB and back)
- The user wants to re-run after adding more instrumentation
- The trace output tells a sequential story

---

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| systematic-debugging | X-ray helps during Phase 1 (investigation) when the call chain is unclear |
| dispatch | X-ray Phase 2 (Map) can use dispatch-style parallel exploration where available |
| code-review | A completed x-ray can inform a code review by revealing actual behavior |
