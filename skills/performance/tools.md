# Profiling with stock tools and the bundled scripts

If both the `profile_session_start` tool and the `profiling-tools` skill are available, read that skill and use its tools for builds, captures, trace reduction and benchmarks. Otherwise, follow the rest of this file.

Use the project's own profiling setup first when it has one: a project skill, scripts, or agent tools. Its build, deploy and device commands replace the generic ones below. The evidence requirements in [SKILL.md](SKILL.md) apply whichever tools you use.

## Builds

Use separate builds of the same commit for benchmark timings and attribution:

- **Benchmark:** Use Release with no profilers attached for all baseline and comparison numbers. Development mode adds checks and disables optimizations.
- **Profile:** For stock React Native, use the iOS scheme's `Debug` configuration or the Android `debug` variant with Hermes and Metro in development mode. Open DevTools from the Dev Menu and confirm the Performance and React Profiler panels connect before recording. React Native [disables DevTools in Release](https://reactnative.dev/docs/0.85/debugging); use these captures to locate work, not to time a speedup. In CompleteFlight, use the project toolkit's `Profile` mode for attribution and `Benchmark` mode for Release timings.

Record the native build identity (version and build number, or binary hash) and the JS bundle identity (commit plus bundle hash) for every run. After a JS-only change, prove the app runs the new bundle: a reload that returns success, or a listening dev server, proves neither.

## Capturing

- **CPU stacks:** React Native DevTools, Performance panel. Record around the flow and save the profile. The export is Chrome trace JSON or a `.cpuprofile`.
- **React components:** React DevTools Profiler. Record the same flow and save the profile JSON. Component render time is not wall time.
- **Source map:** keep the source map of the exact bundle that ran (for Hermes, the composed map the build produces). Without it, bundle frames cannot be mapped to source.
- **Flow window:** note where the flow starts and ends in each trace, in milliseconds from the trace start. A marker the app emits at those points is the most reliable source; otherwise use the profiler's timeline. Save it beside the trace as `<trace>.flow.json` containing `{"window_ms": [start, end]}`.
- **Driving the flow:** use the project's device automation (for example Maestro or Detox flows) so every run does the same work. Each run records proof that the work completed, such as the stored row or the shown screen.

## Reducing traces: `scripts/reduce.py`

```sh
python3 scripts/reduce.py trace.json --map index.map --out run.sqlite
python3 scripts/reduce.py react-profile.json --window 1200 4800 --out react.sqlite
python3 scripts/reduce.py after.json --map index.map --out after.sqlite --compare run.sqlite
```

It ranks self time, inclusive time and share inside the flow window, maps bundle frames to source file and line, and marks frames it cannot map (`mapped = 0`). The SQLite file keeps `traces`, `frames`, `costs`, `samples` and `stack_samples` for further queries. React inclusive time is the profiler's actual render duration, which includes children. A trace with no window is refused; `--whole` ranks the entire trace when the recording covered only the flow. An unmapped frame is a hypothesis, not a diagnosis: resolve it with the right source map or report it as unresolved.

React names come from the initial snapshots. Components mounted during the recording can appear as `fiber-<id>` because the reducer does not decode commit operations. Do not match these IDs across recordings. To name them, inspect the commit in React DevTools, or start another attribution capture after the component has mounted.

## Comparing benchmarks: `scripts/bench.py`

```sh
python3 scripts/bench.py before.json after.json --direction lower --noise-floor 20 --limiter "SQLite write on the JS thread"
```

Each side's file holds the environment (device, native build, flow, metric, workload) and every measured run with its value, error count, work count and proof; `--help` shows the format. It refuses to compare different environments. It returns faster, slower, no measurable difference, or inconclusive. Fewer than five runs a side, any errors, missing or unequal work counts, missing proof or no limiter make the verdict inconclusive. Warmups stay out of the files. Alternate the two sides when collecting runs.

Both scripts need only Python 3.9+ and its standard library.
