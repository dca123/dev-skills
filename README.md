# dev-skills

Portable engineering standards for coding agents, as [Agent Skills](https://agentskills.io): what makes a test worth keeping, when a comment earns its place, and how to keep data shapes honest.

These skills hold rules only. Project-specific conventions and worked examples stay in each project's own skills, keyed to the rule they illustrate.

## Skills

| Skill | Use |
|---|---|
| `tests` | Write, audit, design and mutation-test tests against one guide. Only contract tests are committed. |
| `smells` | Structural code smells, each with its fix and the legitimate uses that are not findings. |
| `error-message-review` | Write and review validation messages, warnings, and application failures in context. |
| `principle-fix-root-causes` | Debugging: fix where the system first went wrong, and choose a local or structural fix. |
| `principle-separate-before-serializing-shared-state` | Concurrent writers: separate the state before reaching for a lock. |
| `principle-make-operations-idempotent` | Operations that converge however often they run and wherever they stopped. |
| `performance` | Find why a flow is slow and prove an improvement. Ships `scripts/reduce.py` (profile → ranked, source-mapped SQLite) and `scripts/bench.py` (benchmark verdict). |

The three principles and `performance` are adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT). Each of those skill folders carries `LICENSE-pstack`, so the notice travels with every copy.

## Install

**pi**

```sh
pi install git:github.com/dca123/dev-skills
```

**Claude Code**

```sh
git clone https://github.com/dca123/dev-skills ~/.dev-skills
for s in ~/.dev-skills/skills/*/; do ln -s "$s" ~/.claude/skills/; done
```

Install these globally, not into a project. Pi keeps the first skill it finds with a given name and Claude Code prefers personal skills over project ones, so a copy inside a project would collide. Projects name their own conventions skills differently and point to these.
