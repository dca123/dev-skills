# Profiling tools

`pi-profiling` wraps local build, service, inspector and device commands. Its fixture file selects the project-specific deployment registry, flow files, and collectors. It does not guess a device or a timing metric. Check `provenance` in every result. Replay results test the tools, not an app's speed.

## Setup and manual recording

Call `profile_session_start` with `project`, `mode`, an explicit `device` with `kind` and `selector`, a fixture JSON path, `goal`, and an optional `idle_timeout_minutes` number or `off`. Defaults are cwd, Profile, and 120 idle minutes. Each call renews idle time. Active captures and benchmarks cannot idle out. Stop the session when done; `off` still requires a live owner and explicit cleanup.

Inspect device kind/model/OS, native build, bundle fingerprint and app acknowledgement. A Profile session may return `awaiting-performance-ui`. Use its `preview_open` invocation for the current JS Performance target. Retain the returned tab ID. The React Profiler is the toolkit's standalone Electron window, revealed separately. Its main-process inspector is not the app's Performance frontend. There is no supported second `preview_open` URL for that window in this toolkit.

For live Profile readiness, follow the deployment result's `runtimeReadExpression` and `finish` proof contract. Save the current Performance snapshot's URL, title, accessibility tree, owned tab ID and inspected runtime observation to `state_dir/performance-proof.json`, then call `profile_session_status`. Only `ready_to_record: true` means readiness passed. Keep both profilers idle for the user to record. Re-establish this evidence after each `profile_push`.

Use `profile_session_status` for current services and evidence paths. Use `profile_session_stop` to stop owned services. Traces and results remain even with `keep_evidence: false`. Close only preview tabs this task opened. Device claims and another worker's services remain theirs.

## Loop capture

`profile_push` exports this checkout, uses the registered compatible native mode, serves frozen bytes, relaunches, and requires fresh executing-JS acknowledgement. It fails when the app does not acknowledge the selected deployment. An HTTP 200 reload or completed transfer alone is insufficient.

`profile_capture` takes `session`, `kinds` containing `react`, `cpu`, or both, a named `flow`, and a `label`. Flow files contain bounded agent-device steps, start/end marker names, and a project collector that proves completed work. Validate selectors, the collector, and clock alignment before marking a flow verified. The Save-to-visible example is deliberately unverified. Keep incomplete capture evidence; do not turn a failed export into a valid sample.

## Reduction

`profile_trace_reduce` takes `traces` as path descriptors with optional `source_map` and `flow` sidecar paths. The default window is `flow`; each trace needs a sidecar containing `window_ms` in that trace's clock. An explicit two-number millisecond range is also supported. `top` defaults to 20. `compare_to` is a previous reduction's SQLite path.

Query the returned SQLite file for samples, stacks, frames and windows. Inspect ranked self time, inclusive time and share. Unmapped components and frames stay marked unmapped. Do not infer a source location from a component name alone.

## Benchmark

`profile_benchmark` requires a ready Benchmark session, `flow`, and `metric`. Defaults are seven measured runs and one warmup. `compare` takes `before` and `after` deployment-reference JSON paths, not numbers copied from a report. It activates the frozen sides alternately without rebuilding them. Both sides must use the same device, native build and fixture. Different JS commits and bundle fingerprints are expected.

Read every run, median, range, error count, work count, noise floor, and verdict. The comparison conservatively uses the larger full within-side range or configured floor. A baseline without a comparison is inconclusive about improvement. A replay verdict is only a fixture result. Keep limiter evidence with the number and apply the method's production and correctness checks even when the tool returns faster.
