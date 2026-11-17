# Write tests

Validate the authorized change, then leave only G12 contract tests. Every test written while coding is a catching test unless it qualifies under G12. Use catching tests freely, delete them after validation, and commit only contract tests.

## Before a test edit

Read the guide, applicable repository conventions, relevant domain documents and architecture decisions, the real producer and caller, and nearby tests. Existing tests supply vocabulary and mechanics, not automatic authority for their expectations.

Record the public seams and check active approvals under G11. An already-approved seam proceeds without another design ceremony. For an unconfirmed seam, finish the read-only investigation, name the proposed boundary, and ask the user to confirm it before writing any test. Quote this G11 gate and link to this file when it pauses work. An explicit bounded experiment stays within its authorized seam and scope.

A new public interface, protected expected value, or product decision needs its owner's ruling. Fixture trouble does not authorize changing a production contract. For language-specific type or interface changes, consult the repository's language guidance if available. In TypeScript, investigate the producer and owning boundary before adding absence or a union member; apply G07 even when no separate language skill is installed.

## Validate one case

Use the selected test mode. For TDD, follow G11 one approved case at a time and record the actual red and green commands and outcomes. For a later already-green case, report coverage honestly and apply G12. Refactor while green, preserving approved behaviour.

For each test, track its seam, authority, and disposition. A useful literal or an implementer's worked example is not outside authority by itself. Catching tests can use any double that speeds validation. Contract tests follow G05 and G06.

Validate ordinary test work with the normal runner. Running an existing mutation script as a "bug check" is still mutation testing and requires an explicit user request.

Before a commit or handoff, delete the catching tests and verify the remaining contract tests. Preserve owner-approved cases and values; a suspected G12 conflict in a frozen contract goes to the owner rather than silent deletion. Include catching-test removal in the validation record, so a clean final tree does not hide the checks used during work.

## Finish

The exit gate is a post-edit read of [audit.md](audit.md) and [guide.md](guide.md), both in full into the current context. Read both after the implementation batch, including catching-test removal. Earlier reads, selected sections, headings, or redirected output do not satisfy this gate. Apply section 8 and fix task-scoped findings, re-auditing those fixes without starting a recursive workflow.

Report the commands and observed results, tests deleted after use, contract tests retained with their authorities, and unresolved owner decisions. Completion requires that audit, not a promise to do it later.
