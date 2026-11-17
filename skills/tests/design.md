# Design tests with the user

Agree a minimal contract slate, one seam at a time. This phase produces decisions and a plan, not test or production edits. Seam agreement alone does not authorize implementation.

Read the guide, relevant domain documents, architecture decisions, existing approvals, and nearby tests. Map natural seams in dependency order using G03's ownership table. Include the preserved behaviour at risk, natural observation, dependency proof, outside authority under G12, and unresolved product policy. State the total seam count and how many remain as each is discussed.

Resolve the active seam's caller-facing interface first. Apply section 8 to candidates, then propose exact test titles and authority-backed expectations. Name the G12 persistence disposition for each case; a useful catching check is not automatically part of the committed slate. Record keep, fold, drop, and defer decisions with the replacement proof or reason. Follow G08 rather than importing local naming or table rules as universal policy.

Research authoritative behaviour when systems disagree. Technical possibility alone is not a business invariant. Present the evidence and ask the owner to choose the target policy.

When the user questions a test, give its strongest defense, a plausible regression, and the exact assertion that catches it. Label an unexecuted mutation hypothetical. Recommend keep, rewrite, fold, or drop, then let the user rule. Withdraw the argument if the assertion cannot catch the example.

## Consolidated authorization

After locking all seams, consolidate the plan with exact titles, authorities and expected values, existing tests to update, dependency order, validation commands, exclusions, deferred decisions, and implementation ownership. State the selected test mode. A TDD plan follows G11; design does not silently select it for all work.

Summarize the final slate, additions versus updates, replacements for dropped tests, intentionally untested behaviour, and compatibility limits. Ask:

> Do you approve this exact test plan and authorize implementation?

Wait for explicit approval of the consolidated plan and authorization to execute before code edits or an implementation handoff. If contract decisions change, update the plan and repeat this gate.

After authorization, hand off to [write.md](write.md) with the approved plan, first case, selected mode, protected expectations, exclusions, deferred decisions, commands, and completion requirements. New seams, expectations, error policy, or public interfaces return to the owner.
