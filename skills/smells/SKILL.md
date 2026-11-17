---
name: smells
description: Structural code smells and their fixes. Use when reviewing a diff or pull request, or self-reviewing your own change before handing it off.
---

# Smells

A smell is a pattern that usually means the code is carrying a state or decision its owner should have settled. It is a reason to investigate, not a finding by itself.

[smells.md](smells.md) lists each smell with its rule, its structural fix and its keep list. Read it in full before reviewing.

## Using it

1. **Match, then investigate.** For each match in the changed code, trace the real producer and callers before calling it anything. Check the keep list; a pattern on the keep list is not a finding.
2. **Report what the trace found:** the pattern, the producer and callers, the invariant it breaks, the owning boundary, the consequence, and the structural fix. A syntax match alone is not a finding.
3. **One owner defect, one finding.** Several smells caused by the same missing owner are reported once, at the owner.
4. **Choose the kind of fix** with [fix root causes](../principle-fix-root-causes/SKILL.md): a local fix, or a structural fix that removes the class.

Apply the React section only to React code, and the TypeScript-specific smells only to typed code. Test smells point into the `tests` skill's guide, which holds the full rules.

When reviewing someone else's change, raise smells as questions with the line and the reason. When reviewing your own, fix them.
