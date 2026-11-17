---
name: tests
description: Tests. For tasks to write or change tests, including TDD and integration tests, load write. After any test change, during implementation self-review, or for test-quality review, always load audit. Load design only when the user asks for test design; load mutation only when the user asks for mutation testing.
---

# Tests

Finish with useful contract proof inside the user's authorized scope. [guide.md](guide.md) is the single testing rulebook. Explicit user instructions and owner-approved contracts govern authorization; a guide heuristic cannot authorize changing a protected expectation.

Read the guide fully before writing or judging tests. Read applicable repository testing conventions separately for commands, fixtures, and runner mechanics. Resolve paths below relative to this skill's directory.

For a task to add or change tests or use TDD, first read [write.md](write.md) and [guide.md](guide.md), even when seam approval is pending. Investigation that ends at the approval gate still uses the write phase.

## Route by the current task

| Trigger | Read and follow |
| --- | --- |
| Before writing or changing a test, including integration tests or selected TDD work | [write.md](write.md) |
| After every test-change batch, at implementation self-review, or for a test-quality review | [audit.md](audit.md) |
| The user explicitly asks to design tests together or agree a test slate | [design.md](design.md) |
| The user explicitly asks for mutation testing or a mutation tool | [mutation.md](mutation.md) |

The post-change audit is an exit condition, including after write, design-authorized implementation, or mutation-approved edits. Read the audit phase and current guide at that boundary even if an earlier phase ran. Re-audit further edits until the guide's section 8 is satisfied; do not recursively invoke a new workflow.

An integration-test request selects write, not collaborative design or TDD by implication. Use test-first order only when requested or required by the active workflow or repository. Design and mutation are opt-in. A thorough audit does not authorize mutation tooling; clarify an ambiguous request for a heavyweight audit.

Keep diagnosis-only and discussion-only requests within their scope. A failing test alone is not permission for quality cleanup. During self-review with no test changes or contracted tests, audit may return `NO TEST SURFACE`.

Personal learning and contribution records are optional references only when the user supplies them for an evidenced disagreement. Do not require a personal directory or installed sibling skill to use this package.
