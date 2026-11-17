# Mutation testing

Run diagnostics only on the user's explicit mutation-testing request. Use the guide to judge findings, not a target score. This phase requires discussion and approval before code changes, even though ordinary audit can fix in-scope findings autonomously.

## Establish the diagnostic

Read the guide fully. Discover named scope or the active VCS changes, related tests, runner, mutation configuration, and available commands. Use the project's language and runner rather than assuming file extensions or a particular tool.

Prefer existing tooling. For temporary setup, use the project's package manager and a compatible mutation runner in an external task artifact directory. Discover actual tool options and configuration before executing. Ask before adding permanent dependencies, scripts, or configuration. If the language or runner lacks a supported setup, report that limitation rather than claiming a diagnostic ran.

Run the normal focused test baseline first. A failed baseline stops the diagnostic. For slow runs, use the environment's supported asynchronous completion mechanism. If using a watch tool, read its eligibility rules first; managed children already delivering completion messages need no second watcher.

Run one narrowly scoped start diagnostic. Keep its command, configuration, tool versions, scope, raw report, and exit result for the end comparison. While it runs, inspect the scoped tests and production code using section 8. Reuse audit's finding vocabulary, not its autonomous edit authorization. Temporary tooling and reports do not authorize application edits.

## Triage and obtain approval

Classify each relevant survivor by actionability and remedy:

| Actionability | Meaning |
| --- | --- |
| 0 | Equivalent, irrelevant, or tool too strict. |
| 1 | Real survivor for which the guide declines a permanent test. |
| 2 | Weak or ambiguous signal; ask if consequential. |
| 3 | Missing supported contract proof. |
| 4 | Existing tests give false confidence. |
| 5 | Evidence of a guide gap or challenge. |

Remedies are `test`, `rewrite`, `delete`, `push-left-types`, `push-left-api`, `ignore`, `guide-learning`, or `ask-user`. Include the mutant location, G-ID or gap, observed evidence, observable risk, and proposed change. Explain ignored survivors; adding no tests is a valid outcome. G07 requires actual earlier enforcement, not merely the possibility of redesign.

Merge static findings and triage into one discussion report. Ask for approval on flagged changes only. Do not change code until the user approves those items. An ambiguous or protected contract returns for an owner ruling.

## Apply and compare

Implement only approved changes through [write.md](write.md), then read [audit.md](audit.md) and the guide after test changes. Validate normally. Run an end diagnostic with the same configuration and scope where possible; explain any mismatch.

Compare the specific survivors that justified action, new risks, and acceptable remaining survivors. Scores alone do not justify more tests or a guide change. For actionability 5, use audit's evidenced-disagreement branch; personal history is optional and promotion still requires authorization.

Completion requires known diagnostic outcomes, a qualitative start/end comparison or an explicit reason no code phase occurred, normal validation, dispositions for relevant findings, and cleanup of task-owned processes and temporary sandboxes. Keep diagnostic evidence outside the repository; remove owned sandboxes before normal test discovery can include them.
