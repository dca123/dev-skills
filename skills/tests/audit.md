# Audit tests

Improve the scoped proof using the guide's section 8. Make ordinary task-scoped corrections without asking for redundant permission. Discussion-only requests authorize findings, not edits. Frozen contracts and owner approvals remain binding.

## Scope and baseline

Load the current [guide.md](guide.md) in full on entry to this audit, even if write or another phase already read it. Selected sections and redirected output do not load the rulebook into context.

Use named or proposed tests first; otherwise inspect the active VCS diff, untracked files, changed implementation, and related tests. Include phase-contracted tests during implementation self-review. Read the active workflow's approval policy when one exists.

If no test or contracted behaviour is in scope, return `NO TEST SURFACE` with what you inspected. If neither a named target nor changed behaviour identifies a scope, ask for a target rather than inventing coverage.

Discover commands in project scripts and configuration. Run focused existing tests before quality rewrites. Proposed tests have no execution result; use the relevant current suite as baseline. A failed baseline stops unrelated cleanup. Report an unavailable runner and obtain acceptance before making static-only changes.

## Judge and resolve

Inspect the production behaviour, public contract, and actual dependency proof. Apply section 8, starting with G12. Delete a catching test after use rather than polishing it into a permanent test. Preserve owner-approved cases and values while asking the owner about any conflict.

Use this vocabulary for actionable findings. Each needs a location, G-ID or explicit gap, concrete observable risk, evidence, remedy, and disposition.

| Action | Disposition |
| --- | --- |
| `DROP` | Identify replacement protection or why the test has no supported contract. |
| `REWRITE` | Repair proof, setup, or naming for a valuable contract. |
| `ADD MISSING TEST` | Identify the authority and supported changed risk before writing. |
| `PUSH LEFT / API DESIGN` | Show the earlier enforcement; retain runtime proof until it actually exists. |
| `GUIDE GAP` | Identify a generalizable decision no current rule addresses. |
| `GUIDE CHALLENGE` | Show a concrete counterexample to a correctly applied rule. |
| `AMBIGUOUS / ASK USER` | Finish the investigation and identify the unresolved owner decision. |

For a consequential finding, give the strongest reason for the cited rule, then try to defeat the recommendation using the inspected code. Distinguish an existing exception from a real gap. Label hypothetical regressions as hypothetical; a description of a mutation is not execution evidence.

Apply supported in-scope corrections, then re-audit the edits. Ask before crossing scope, changing product policy, or altering an owner-approved contract. Audit does not start an implementation workflow or run mutation testing.

## Verify and report

Run focused tests and relevant type checks after edits. Expand validation for changed integration boundaries. Record unavailable checks and already-green additions honestly. Completion requires a known result, section 8 satisfied or a disclosed exception, and each finding fixed, justified, or blocked on an owner decision.

Give a concise receipt with scope, baseline, actionable findings, changes, verification, and blockers. Summarize acceptable tests together instead of listing them all.

Then finish the parent task's remaining authorized actions, including a commit when the user requested one. An audit receipt alone does not complete implementation or replace the user's requested deliverable.

## Evidenced disagreement only

For a gap or challenge, quote the affected rule, steelman its purpose, show the supported contract and discriminating regression, and state the proposal's limits. A bounded local exception may preserve authorized behaviour; disclose it. Product or frozen-contract conflicts still need the owner.

If the user supplies a personal learning ledger or contribution process, consult it only for a matching candidate or provenance question. Record evidence only within authorized artifact scope. Routine fixes are not learnings. Changing this rulebook or promoting a candidate requires explicit user authorization.
