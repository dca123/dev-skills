# Profiling with stock tools and the bundled scripts

If the `profile_*` agent tools are loaded, read the `profiling-tools` skill and use those tools for builds, captures, trace reduction and benchmarks. The rest of this file is the path without them.

Use the project's own profiling setup first when it has one: a project skill, scripts, or agent tools. Its build, deploy and device commands replace the generic ones below. The evidence requirements in [SKILL.md](SKILL.md) apply whichever tools you use.

## Builds

Measure on a Release build, never a development (Metro dev) build: dev mode adds checks and disables optimizations, so its timings mislead. Keep two builds of the same commit when the platform allows:

- **Benchmark:** Release, no profilers attached. Used for baselines and the final proof.
- **Profile:** Release with profiling enabled. Used to attribute time. Its numbers are not benchmark numbers.

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

It ranks self time, inclusive time and share inside the flow window, maps bundle frames to source file and line, and marks frames it cannot map (`mapped = 0`). The SQLite file keeps `traces`, `frames`, `samples` and `stack_samples` for further queries. A trace with no window is refused; `--whole` ranks the entire trace when the recording covered only the flow. An unmapped frame is a hypothesis, not a diagnosis: resolve it with the right source map or report it as unresolved.

## Comparing benchmarks: `scripts/bench.py`

```sh
python3 scripts/bench.py before.json after.json --direction lower --noise-floor 20 --limiter "SQLite write on the JS thread"
```

Each side's file holds the environment (device, native build, flow, metric, workload) and every measured run with its value, error count, work count and proof; `--help` shows the format. It refuses to compare different environments. It returns faster, slower, no measurable difference, or inconclusive. Fewer than five runs a side, any errors, unequal work, missing proof or no limiter make the verdict inconclusive. Warmups stay out of the files. Alternate the two sides when collecting runs.

Both scripts need only Python 3.9+ and its standard library.
