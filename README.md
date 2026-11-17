# dev-skills

Portable engineering standards for coding agents, as [Agent Skills](https://agentskills.io): what makes a test worth keeping, when a comment earns its place, and how to keep data shapes honest.

These skills hold rules only. Project-specific conventions and worked examples stay in each project's own skills, keyed to the rule they illustrate.

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
