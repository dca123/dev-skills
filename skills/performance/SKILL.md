---
name: performance
description: "Performance work: find why part of an app is slow and prove an improvement. Use when a flow is slow, when asked to profile, or to improve a timing metric."
---

# Performance

Finish with a source-attributed explanation and a repeatable before/after result for the flow the user waits on. Preserve correctness and workload. A faster rejection, skipped write, or different device is not an improvement. The user's instructions set the scope, mode, and authority to change code or run a device.

## Agree the claim

Before measuring, agree with the user on the claim to ship, the flow, the metric and its measurement boundary, the workload, the device, the noise floor, and a stop rule with both a target and a minimum number of attempts. Reuse an existing agreement rather than asking again. State whether the endpoint is a JS callback, a native frame, or a visible usable screen. These are different metrics.

Choose a workload that reproduces the complaint. Record data size, account/tenant, cache state, concurrency, and preparation. Check the measurement script for what it times, counts, and omits. Prove its sensitivity with contrasting realistic workloads before freezing it. If it cannot distinguish them or reproduce the complaint, repair the measurement before optimizing.

Use the `profile_*` tools when available. Read [tools.md](tools.md) before setup, captures, or comparisons. Without those tools, use the app's build/deploy commands, its device automation, stock React and runtime CPU profilers, a SQLite importer, and a repeatable benchmark script with the same evidence requirements. Do not replace end-to-end timing with tool-call duration.

## Baseline

Record the exact device kind, model, OS, native build, commit and executing bundle identity. Use the same environment for every side. Keep simulator and physical results separate. Reuse a compatible installed native build for JS-only changes; native dependencies, configuration, or capabilities need a verified compatible native artifact.

Collect a clean Release/benchmark baseline without attached profilers. Report at least five measured runs, their median and range, errors, and work counts. Keep warmups separate. Check host load, device thermal state when available, and other workers before attributing variation to code. Save the raw runs and run the correctness gate before editing.

## Attribute

In a separate Profile run, capture React components and CPU stacks around the same flow. Confirm start/end markers and that the intended work completed. After a push, re-prove bundle execution and both profilers' current readiness before recording. A successful reload response, listening port, or previous capture proves neither.

Import traces into queryable SQLite before analyzing them. Rank self and inclusive cost within the flow window. Map hot frames to source file and line with the executing artifact's source map. React totals are not wall time, inclusive stacks overlap, and profiler overhead is not a benchmark. A frame without a source mapping remains a hypothesis. Resolve it or state the missing evidence.

## Improve

Order source-grounded hypotheses by the performance mantras, cheapest first:

1. Don't do it. Remove work whose result nobody uses.
2. Do it, but don't do it again.
3. Do it less.
4. Do it later.
5. Do it when they're not looking.
6. Do it concurrently.
7. Do it cheaper.

Manual mode: set up the verified build and both profilers, then let the user record. Do not start, stop, reload, or replace a recording they own. Reduce their exports, propose one source-grounded change, and repeat with their next recording.

Loop mode: make one change, measure it with the frozen benchmark, run the correctness gate, then keep or revert that change. Never stack unmeasured candidates. Keep an external `decision.tsv` with attempt, hypothesis, change, before/after, delta, tests, verdict, and evidence paths. Read it before each attempt. Commit accepted changes separately and preserve unrelated edits.

Push past the first plateau. After repeated rejects, change hypothesis category, inspect a fresh trace, or revisit workload assumptions. Stop when the agreed target and attempt floor hold, or when genuinely blocked. Do not lower the target or end an authorized loop at a child-task handoff. Explain a blocker with the evidence and remaining ideas.

## Prove

Return to the clean benchmark build. Alternate at least five runs per side, A, B, A, B, with equal work and independent warmups. Preserve the same device, native build, workload, flags, versions, and cache policy. Check errors and durable/output proof inside the timed region on every run. A failed or uncertain Save is not retried blindly.

Compare the gap with the noise floor and within-side variation. Report faster, slower, no measurable difference, or inconclusive. Missing work/error evidence, untuned builds, or an unexplained limiter make the verdict inconclusive. Ask "why not double?" and name the limiting resource or source path from a separate profile or counters. Check the arithmetic against the measured share of the whole; a helper that costs 1% cannot explain a 30% end-to-end gain.

Report the claim, baseline and candidate medians with units and ranges, all run counts, errors/work, device/build/commit/bundle, limiter, correctness gate, and artifact paths. Distinguish measured, read, and inferred findings. Include what remains unverified.

## After release

If the user wants ongoing tracking, confirm the same metric and workload in production telemetry such as PostHog. Agree release/cohort boundaries, sample count, and privacy before adding telemetry. Local benchmarks do not prove a production gain. Ask whether temporary timing instrumentation should stay in the code, then remove or retain it according to that decision.

Method adapted from pstack's performance, hillclimb, trace-forensics, benchmark-checklist, and explain-the-number guidance. See the repository's `LICENSE-pstack`.
