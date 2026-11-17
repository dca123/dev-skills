---
name: principle-fix-root-causes
description: "Apply when debugging. Trace each symptom back to the first place the system went wrong and fix it there. A guard is a fix only when the state it handles is legitimate."
disable-model-invocation: true
---

# Fix Root Causes

When debugging, fix the fault, not the place where it surfaced. The symptom is where a wrong state became visible. The root cause is the first place the system did something it should not do, or failed to handle a state it should handle.

**Why:** A symptom fix hides the evidence and leaves the fault free to surface somewhere else. Each one makes the system harder to reason about, because the code now carries a workaround for a bug that nobody named.

**Pattern:**
- Reproduce first.
- Ask "why" at each step until the answer is a wrong decision in the code, not a consequence of an earlier one.
- When stuck, instrument. Read the actual error and the actual state. Do not guess.
- Ask whether the state that triggered the symptom is legitimate. If the system may be in that state, the code that broke on it is the root cause, and handling the state there is the fix. If the state should never exist, a check where it broke hides the bug. Find what produced the state. Guards, retries, swallowed errors, clamped values, and discarded state are the usual ways to hide a bug.
- When something fails only after a restart, suspect persisted state first: config files, caches, lock files, serialized state.
- Check for the pattern, not just the instance. Find every place with the same fault and fix them all.
- If a workaround needs a paragraph-long comment to justify it, the code is wrong. Fix the code, not the comment.
- If the deciding fact took a deep dig to find, propose the cheap, always-on signal that would have shown it at first look.

## Local or structural fix

Once the root cause is known, decide which kind of fix it needs, and say which in the report.

- **Local:** one site, one wrong decision. Fix it there.
- **Structural:** the same class of bug can recur at other sites, or the obvious fix is a guard, lock, retry or default that hides the cause. Change the structure so the class cannot exist:
  - concurrent writers: give each its own state, or one writer ([separate before serializing shared state](../principle-separate-before-serializing-shared-state/SKILL.md));
  - repeats, restarts and partial runs: make the operation converge ([make operations idempotent](../principle-make-operations-idempotent/SKILL.md));
  - states that should never exist: a type, discriminated union or state machine that cannot represent them.

A legitimate state can still need a structural fix: concurrent saves are legitimate, and handling them belongs in the structure, not in a lock around one call site. When no test seam can reproduce the bug at its real call pattern, that is evidence for the structural kind.

When the structural fix is out of scope, ship the local fix and record a follow-up that names the class of bug. Never ship the guard instead.

When a classifier model is available (Pi's `models.classify` with `typesafe/jev-latest`), it can label the fix kind for each finding, one call per finding, run in parallel. Act on the probability of the kind you would apply, not on the answer's confidence: accept clear answers (for example above 0.75 or below 0.25) and decide the middle band with written reasoning.
