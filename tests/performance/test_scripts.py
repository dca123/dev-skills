"""Authority: Chrome DevTools SamplesHandler and MetaHandler, the Chrome/Hermes CPU profile
and React DevTools export formats, the v3 source-map spec, and Dev's benchmark rules
(>=5 runs a side, same device and build, equal positive work, no errors, a named limiter).
Run: python3 -m unittest discover -s tests -t .
"""

import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills/performance/scripts"))
from bench import compare  # noqa: E402
from reduce import reduce_traces  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


class TraceReduction(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)

    def test_cpu_time_is_clipped_to_the_flow_window_and_mapped_or_marked_unmapped(self):
        result = reduce_traces([FIXTURES / "cpu.cpuprofile"], self.out / "cpu.sqlite", source_map=FIXTURES / "bundle.map")
        save = next(r for r in result["ranked"] if r["name"] == "save")
        self.assertEqual({k: save[k] for k in ("file", "line", "col", "self_ms", "share", "mapped")},
                         {"file": "src/save.ts", "line": 10, "col": 3, "self_ms": 6, "share": 0.75, "mapped": 1})
        unknown = next(r for r in result["ranked"] if r["name"] == "unknown")
        self.assertEqual((unknown["file"], unknown["mapped"], unknown["self_ms"]), (None, 0, 2))
        with sqlite3.connect(result["sqlite"]) as db:
            self.assertEqual(db.execute("SELECT SUM(duration_ms) FROM samples").fetchone()[0], 8)

    def test_react_self_time_counts_only_commits_inside_the_window_and_compares_runs(self):
        result = reduce_traces([FIXTURES / "react.json"], self.out / "react.sqlite")
        self.assertEqual([(r["name"], r["self_ms"], r["mapped"]) for r in result["ranked"]],
                         [("SaveForm", 5, 1), ("LegWorksheet", 2, 0)])
        later = reduce_traces([FIXTURES / "react.json"], self.out / "after.sqlite", (0, 30), compare_to=result["sqlite"])
        self.assertEqual(later["diff"][0]["delta_ms"], 2)

    def test_a_trace_without_a_window_is_refused_rather_than_ranked_whole(self):
        trace = self.out / "bare.cpuprofile"
        trace.write_text((FIXTURES / "cpu.cpuprofile").read_text())
        with self.assertRaisesRegex(ValueError, "No window"):
            reduce_traces([trace], self.out / "bad.sqlite")
        whole = reduce_traces([trace], self.out / "whole.sqlite", "whole")
        self.assertEqual(sum(r["self_ms"] for r in whole["ranked"] if r["name"] != "(root)"), 10)

    def test_chrome_trace_chunks_keep_sample_deltas_and_source_attribution(self):
        trace = {"traceEvents": [
            {"name": "Profile", "pid": 1, "tid": 1, "id": "a", "args": {"data": {"startTime": 100000}}},
            {"name": "ProfileChunk", "pid": 1, "tid": 1, "id": "a", "args": {"data": {
                "cpuProfile": {"nodes": [{"id": 1, "callFrame": {"functionName": "save", "url": "index.bundle",
                                                                 "lineNumber": 0, "columnNumber": 0}}],
                               "samples": [1, 1]}, "timeDeltas": [2000, 3000]}}}]}
        file = self.out / "chrome.json"
        file.write_text(json.dumps(trace))
        result = reduce_traces([file], self.out / "chrome.sqlite", (0, 5), FIXTURES / "bundle.map")
        self.assertEqual((result["ranked"][0]["self_ms"], result["ranked"][0]["file"]), (5, "src/save.ts"))

    def test_a_cpu_profile_that_starts_after_the_trace_is_windowed_on_the_trace_clock(self):
        trace = {"traceEvents": [
            {"name": "TracingStartedInBrowser", "ph": "I", "pid": 1, "tid": 1, "ts": 0},
            {"name": "Profile", "pid": 1, "tid": 1, "id": "a", "ts": 1000000, "args": {"data": {"startTime": 1000000}}},
            {"name": "ProfileChunk", "pid": 1, "tid": 1, "id": "a", "args": {"data": {
                "cpuProfile": {"nodes": [{"id": 1, "callFrame": {"functionName": "save", "url": "index.bundle",
                                                                 "lineNumber": 0, "columnNumber": 0}}],
                               "samples": [1, 1]}, "timeDeltas": [1000, 1000]}}}]}
        file = self.out / "late.json"
        file.write_text(json.dumps(trace))
        result = reduce_traces([file], self.out / "late.sqlite", (1000, 1002))
        self.assertEqual(result["ranked"][0]["self_ms"], 2)

    def chrome_sample_time(self, events, profile_ts, payload_start, window):
        trace = {"traceEvents": [*events,
            {"name": "Profile", "ph": "P", "pid": 1, "tid": 1, "id": "a", "ts": profile_ts,
             "args": {"data": {"startTime": payload_start}}},
            {"name": "ProfileChunk", "ph": "P", "pid": 1, "tid": 1, "id": "a", "ts": profile_ts + 2000,
             "args": {"data": {"cpuProfile": {"nodes": [{"id": 1, "callFrame": {"functionName": "save"}}],
                                              "samples": [1]}, "timeDeltas": [2000]}}}]}
        file = self.out / "clock.json"
        file.write_text(json.dumps(trace))
        rows = reduce_traces([file], self.out / "clock.sqlite", window)["ranked"]
        return [(r["name"], r["self_ms"]) for r in rows]

    def test_a_profile_starts_at_its_event_timestamp_not_its_payload_clock(self):
        events = [{"name": "work", "ph": "I", "pid": 1, "tid": 1, "ts": 5000000}]
        self.assertEqual(self.chrome_sample_time(events, 5004000, 2000000, (4, 6)), [("save", 2)])

    def test_metadata_timestamps_do_not_set_the_recording_origin(self):
        timed = {"name": "work", "ph": "I", "pid": 1, "tid": 1, "ts": 5000000}
        for origin, window in (([timed], (4, 6)), ([], (0, 2))):
            with self.subTest(timed_event=bool(origin)):
                events = [{"name": "process_name", "ph": "M", "pid": 1, "tid": 0, "ts": 0},
                          {"name": "thread_name", "ph": "M", "pid": 1, "tid": 1, "ts": 1000}, *origin]
                self.assertEqual(self.chrome_sample_time(events, 5004000, 5004000, window), [("save", 2)])

    def test_ios_jsbundle_frames_are_mapped_through_the_source_map(self):
        profile = json.loads((FIXTURES / "cpu.cpuprofile").read_text())
        for node in profile["nodes"]:
            node["callFrame"]["url"] = node["callFrame"]["url"].replace("index.bundle", "main.jsbundle")
        file = self.out / "ios.cpuprofile"
        file.write_text(json.dumps(profile))
        save = next(r for r in reduce_traces([file], self.out / "ios.sqlite", (1, 9), FIXTURES / "bundle.map")["ranked"]
                    if r["name"] == "save")
        self.assertEqual((save["file"], save["line"], save["mapped"]), ("src/save.ts", 10, 1))

    def test_a_react_parent_with_no_self_time_keeps_its_inclusive_render_time(self):
        export = {"version": 5, "dataForRoots": [{"rootID": 1,
            "snapshots": [[1, {"displayName": "Screen"}], [2, {"displayName": "Row"}]],
            "commitData": [{"timestamp": 2, "duration": 5,
                            "fiberSelfDurations": [[1, 0], [2, 5]], "fiberActualDurations": [[1, 5], [2, 5]]}]}]}
        file = self.out / "nested.json"
        file.write_text(json.dumps(export))
        rows = {r["name"]: (r["self_ms"], r["inclusive_ms"]) for r in reduce_traces([file], self.out / "n.sqlite", (0, 10))["ranked"]}
        self.assertEqual(rows, {"Row": (5, 5), "Screen": (0, 5)})

    def test_a_comparison_keeps_two_frames_on_the_same_line_apart(self):
        def trace(name, first, second):
            profile = {"nodes": [{"id": 1, "callFrame": {"functionName": "(root)", "url": "", "lineNumber": -1, "columnNumber": -1},
                                  "children": [2, 3]},
                                 {"id": 2, "callFrame": {"functionName": "(anonymous)", "url": "src/a.ts", "lineNumber": 4, "columnNumber": 0}},
                                 {"id": 3, "callFrame": {"functionName": "(anonymous)", "url": "src/a.ts", "lineNumber": 4, "columnNumber": 9}}],
                       "samples": [2, 3], "timeDeltas": [first * 1000, second * 1000]}
            file = self.out / name
            file.write_text(json.dumps(profile))
            return file
        before = reduce_traces([trace("before.cpuprofile", 10, 20)], self.out / "b.sqlite", "whole")
        after = reduce_traces([trace("after.cpuprofile", 10, 30)], self.out / "a.sqlite", "whole", compare_to=before["sqlite"])
        changed = [(d["location"][2], d["delta_ms"]) for d in after["diff"] if d["delta_ms"]]
        self.assertEqual(changed, [(10, 10)])

    def test_a_comparison_sums_renamed_bundle_frames_at_the_same_source_location(self):
        source_map = self.out / "renamed.map"
        source_map.write_text(json.dumps({"version": 3, "sources": ["src/work.ts"], "names": [], "mappings": "AAAA"}))

        def reduction(label, frames, baseline=None):
            nodes = [{"id": n, "callFrame": {"functionName": name, "url": "index.bundle",
                                            "lineNumber": 0, "columnNumber": n}}
                     for n, (name, _) in enumerate(frames, 1)]
            path = self.out / f"{label}.cpuprofile"
            path.write_text(json.dumps({"nodes": nodes, "samples": [node["id"] for node in nodes],
                                        "timeDeltas": [ms * 1000 for _, ms in frames]}))
            return reduce_traces([path], self.out / f"{label}.sqlite", "whole", source_map, compare_to=baseline)

        before = reduction("before", [("a", 20), ("b", 30)])
        after = reduction("after", [("c", 50)], before["sqlite"])
        self.assertEqual([(row["location"], row["before_ms"], row["after_ms"], row["delta_ms"])
                          for row in after["diff"]], [(["src/work.ts", 1, 1], 50, 50, 0)])

    def test_unmapped_frames_with_one_name_stay_apart_by_generated_location(self):
        profile = {"nodes": [{"id": 1, "callFrame": {"functionName": "(root)", "url": "", "lineNumber": -1, "columnNumber": -1},
                              "children": [2, 3]},
                             {"id": 2, "callFrame": {"functionName": "(anonymous)", "url": "index.bundle", "lineNumber": 0, "columnNumber": 5}},
                             {"id": 3, "callFrame": {"functionName": "(anonymous)", "url": "index.bundle", "lineNumber": 0, "columnNumber": 90}}],
                   "samples": [2, 3], "timeDeltas": [1000, 9000]}
        file = self.out / "unmapped.cpuprofile"
        file.write_text(json.dumps(profile))
        rows = [(r["self_ms"], r["mapped"], r["generated_col"]) for r in reduce_traces([file], self.out / "u.sqlite", "whole")["ranked"]
                if r["name"] == "(anonymous)"]
        self.assertEqual(rows, [(9, 0, 90), (1, 0, 5)])

    def test_an_output_that_is_also_the_comparison_baseline_is_refused(self):
        baseline = reduce_traces([FIXTURES / "react.json"], self.out / "base.sqlite")["sqlite"]
        with self.assertRaisesRegex(ValueError, "same file"):
            reduce_traces([FIXTURES / "react.json"], baseline, compare_to=baseline)
        with sqlite3.connect(baseline) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM traces").fetchone()[0], 1)

    def test_a_failed_reduction_leaves_the_previous_output_in_place(self):
        out = self.out / "keep.sqlite"
        reduce_traces([FIXTURES / "react.json"], out)
        bare = self.out / "bare.cpuprofile"
        bare.write_text((FIXTURES / "cpu.cpuprofile").read_text())
        with self.assertRaises(ValueError):
            reduce_traces([bare], out)
        with sqlite3.connect(out) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM traces").fetchone()[0], 1)


class BenchmarkVerdict(unittest.TestCase):
    ENV = {"device": "iPad (A16) 26.1 physical", "native_build": "1.0.2 (12)", "flow": "save",
           "metric": "visible ms", "workload": "50 legs"}

    def side(self, values, errors=0, work=1, env=None):
        return {"environment": env or self.ENV,
                "runs": [{"value": v, "error_count": errors, "work_count": work, "proof": "row persisted"} for v in values]}

    def test_a_gap_past_the_noise_is_faster(self):
        result = compare(self.side([99, 100, 101, 100, 100]), self.side([79, 80, 81, 80, 80]), "lower", 1, "query CPU")
        self.assertEqual((result["before"]["median"], result["after"]["median"], result["noise"], result["verdict"]),
                         (100, 80, 2, "faster"))

    def test_missing_work_count_makes_the_verdict_inconclusive(self):
        before = self.side([100] * 5)
        after = self.side([50] * 5)
        del after["runs"][0]["work_count"]
        result = compare(before, after, "lower", 1, "CPU")
        self.assertEqual((result["verdict"], result["after"]["work_count"]), ("inconclusive", None))

    def test_supplied_work_counts_must_be_nonnegative_and_finite_even_when_one_is_missing(self):
        before = self.side([100] * 5)
        for work, message in ((-1, "cannot be negative"), (float("inf"), "finite number")):
            with self.subTest(work=work), self.assertRaisesRegex(ValueError, message):
                after = self.side([50] * 5)
                del after["runs"][0]["work_count"]
                after["runs"][1]["work_count"] = work
                compare(before, after, "lower", 1, "CPU")

    def test_noise_errors_skipped_work_too_few_runs_or_no_limiter_are_not_wins(self):
        baseline = self.side([90, 100, 110, 100, 100])
        self.assertEqual(compare(baseline, self.side([95] * 5), "lower", 1, "CPU")["verdict"], "no measurable difference")
        for candidate, limiter in [(self.side([50] * 5, errors=1), "CPU"), (self.side([50] * 5, work=0), "CPU"),
                                   (self.side([50] * 4), "CPU"), (self.side([50] * 5), "")]:
            with self.subTest(limiter=limiter):
                self.assertEqual(compare(baseline, candidate, "lower", 1, limiter)["verdict"], "inconclusive")
        self.assertEqual(compare(self.side([10] * 5), self.side([20] * 5), "lower", 1, "CPU")["verdict"], "slower")

    def test_any_differing_environment_field_is_refused(self):
        with self.assertRaisesRegex(ValueError, "cache_policy"):
            compare(self.side([1] * 5, env={**self.ENV, "cache_policy": "warm"}),
                    self.side([1] * 5, env={**self.ENV, "cache_policy": "cold"}), "lower", 0, "CPU")

    def test_a_field_present_on_one_side_only_is_refused(self):
        with self.assertRaisesRegex(ValueError, "cache_policy"):
            compare(self.side([1] * 5, env={**self.ENV, "cache_policy": None}), self.side([1] * 5), "lower", 0, "CPU")

    def test_a_different_device_or_native_build_is_refused(self):
        for key in ("device", "native_build"):
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, key):
                compare(self.side([1] * 5), self.side([1] * 5, env={**self.ENV, key: "other"}), "lower", 0, "CPU")


if __name__ == "__main__":
    unittest.main()
