Adds five agent skills that Claude Code and pi load automatically in this repo. They hold the standards most review comments come back to, so an agent applies them while writing the change instead of a reviewer raising them afterwards.

```text
.agents/skills/
├── tests/                         # which tests to write, and which to commit
├── smells/                        # structural code smells and their fixes
├── principle-fix-root-causes/     # fix the cause, and choose a local or structural fix
├── principle-separate-before-serializing-shared-state/
└── principle-make-operations-idempotent/
.claude/skills → ../.agents/skills (Claude Code reads the same files)
```

## What each skill does

**`tests`** loads when an agent writes or changes tests. Tests written while coding are temporary checks and get deleted. Only a test that protects an agreed decision gets committed. After any test change, the agent audits the tests against `tests/guide.md` before finishing.

**`smells`** loads when an agent reviews a diff or self-reviews its own change. It lists 29 patterns that usually mean a state or decision is carried by the wrong code: an optional field nothing ever leaves empty, a `??` default covering a state that can't happen, a `useEffect` copying props into state, two places deciding the same rule. Each smell names the structural fix and the legitimate uses that are not a problem.

**`principle-fix-root-causes`** loads when debugging. The agent traces a bug to the first wrong decision and fixes it there. If the same kind of bug can recur elsewhere, or the quick fix is a guard, lock or retry that hides the cause, the agent changes the structure so that kind of bug can't happen. The two other principles describe two of those structures: giving concurrent writers separate state instead of a lock, and making an operation safe to run twice.

## Using them

Nothing to install. A Claude Code or pi session in this repo picks these up. To use one directly, type its name, for example `/tests` in Claude Code.

## Maintenance

These files are generated from [dca123/dev-skills](https://github.com/dca123/dev-skills). Each skill folder records its source commit in `.dev-skills.json`. A future sync PR overwrites edits made here, so propose changes in dev-skills instead.

Docs only: no application code changes.
