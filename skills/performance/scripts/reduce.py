#!/usr/bin/env python3
"""Rank where time went in a CPU or React profile, inside the measured flow window.

    reduce.py TRACE... --out OUT.sqlite (--window START_MS END_MS | --whole) [--map BUNDLE.map] [--top 20] [--compare BEFORE.sqlite]

Inputs:
  - CPU: a Hermes/Chrome `.cpuprofile`, or a Chrome trace JSON with Profile/ProfileChunk events
    (React Native DevTools > Performance > Save profile).
  - React: a React DevTools Profiler export (Profiler > Save profile).
  - `.gz` files are read directly.

Window: milliseconds from the start of each trace. A file `<trace>.flow.json` containing
{"window_ms": [start, end]} sets that trace's window instead. `--whole` ranks the entire trace;
use it only when the trace was recorded around the flow and nothing else.

`--map` is the flat v3 source map of the exact bundle that ran, so bundle frames resolve to
source file and line. Frames that cannot be mapped stay marked unmapped (mapped = 0).

CPU frames from the executing bundle (`.bundle`, `.jsbundle`, `.hbc`, or the map's `file`) are
mapped through `--map`; other frames with a URL and line keep those coordinates.

Prints JSON with the ranked rows (self and inclusive milliseconds, share of the trace kind's
total) and, with `--compare`, the per-frame self-time delta against an earlier output. React
inclusive time is the profiler's actual duration. The SQLite file keeps traces, frames, costs,
samples and stack_samples for further queries. It replaces OUT only when reduction succeeds.
Python 3.9+ standard library only.
"""

import argparse
import bisect
import os
import gzip
import json
import math
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlsplit


def load(path):
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as stream:
        return json.load(stream)


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Expected a finite number")
    return value


def vlq(segment):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    value = shift = 0
    for char in segment:
        digit = alphabet.index(char)
        value += (digit & 31) << shift
        if digit & 32:
            shift += 5
        else:
            yield -(value >> 1) if value & 1 else value >> 1
            value = shift = 0
    if shift:
        raise ValueError("Truncated source-map VLQ")


class SourceMap:
    def __init__(self, file):
        data = load(file)
        if data.get("version") != 3 or "sections" in data:
            raise ValueError("Expected a flat v3 source map; flatten indexed maps first")
        self.sources = data["sources"]
        self.root = data.get("sourceRoot", "")
        self.file = Path(data["file"]).name if data.get("file") else None
        self.lines = []
        source = line = column = 0
        for encoded in data["mappings"].split(";"):
            generated = 0
            entries = []
            for segment in encoded.split(","):
                if not segment:
                    continue
                parts = list(vlq(segment))
                generated += parts[0]
                if len(parts) == 1:
                    entries.append((generated, None))
                    continue
                if len(parts) not in (4, 5):
                    raise ValueError("Invalid source-map segment")
                source += parts[1]
                line += parts[2]
                column += parts[3]
                name = self.sources[source]
                path = name if (not self.root or name.startswith("/") or urlsplit(name).scheme) \
                    else self.root.rstrip("/") + "/" + name
                entries.append((generated, (path, line + 1, column + 1)))
            self.lines.append(([g for g, _ in entries], [m for _, m in entries]))

    def lookup(self, line, column):
        """The mapping of the last segment at or before the generated column."""
        if line < 0 or line >= len(self.lines):
            return None
        columns, mappings = self.lines[line]
        index = bisect.bisect_right(columns, column) - 1
        return mappings[index] if index >= 0 else None


def cpu_profile(data):
    """One sampled CPU profile, with `offset_ms` from the trace's first timestamp to its start."""
    if "nodes" in data:
        return {**data, "offset_ms": 0}
    events = data.get("traceEvents", [])
    starts = {}
    profiles = {}
    for event in data.get("traceEvents", []):
        args = event.get("args", {}).get("data", {})
        if event.get("name") == "CpuProfile" and "cpuProfile" in args:
            key = (event.get("pid"), event.get("tid"), event.get("id", "standalone"))
            profiles[key] = args["cpuProfile"]
            starts[key] = args["cpuProfile"].get("startTime", event.get("ts"))
        if event.get("name") not in ("Profile", "ProfileChunk"):
            continue
        key = (event.get("pid"), event.get("tid"), event.get("id", event.get("id2", {}).get("local", "default")))
        profile = profiles.setdefault(key, {"nodes": [], "samples": [], "timeDeltas": []})
        if event.get("name") == "Profile":
            starts[key] = args.get("startTime", event.get("ts"))
        chunk = args.get("cpuProfile", {})
        profile["nodes"].extend(chunk.get("nodes", []))
        profile["samples"].extend(chunk.get("samples", []))
        profile["timeDeltas"].extend(args.get("timeDeltas", chunk.get("timeDeltas", [])))
    sampled = [key for key, p in profiles.items() if p["samples"]]
    if len(sampled) != 1:
        raise ValueError("Trace must contain exactly one sampled CPU profile; split it by target/thread first")
    key = sampled[0]
    start = starts.get(key)
    clocks = [e["ts"] for e in events if isinstance(e.get("ts"), (int, float))] + [t for t in starts.values() if t is not None]
    offset_ms = (start - min(clocks)) / 1000 if start is not None else 0
    merged = {}
    for node in profiles[key]["nodes"]:
        old = merged.get(node["id"], {})
        merged[node["id"]] = {**old, **node, "children": list(set(old.get("children", []) + node.get("children", [])))}
    return {**profiles[key], "nodes": list(merged.values()), "offset_ms": offset_ms}


BUNDLE_SUFFIXES = (".bundle", ".jsbundle", ".hbc")


def cpu_rows(data, source_map):
    data = cpu_profile(data)
    nodes = {n["id"]: n for n in data["nodes"]}
    parents = {child: node["id"] for node in nodes.values() for child in node.get("children", [])}
    parents.update({n["id"]: n["parent"] for n in nodes.values() if n.get("parent") is not None})
    samples, deltas = data["samples"], data.get("timeDeltas", [])
    if len(samples) != len(deltas):
        raise ValueError("CPU samples need one timeDelta per sample")
    bundles = BUNDLE_SUFFIXES + ((source_map.file,) if source_map and source_map.file else ())
    elapsed = data["offset_ms"]
    for node_id, delta in zip(samples, deltas):
        duration = finite(delta) / 1000
        if duration < 0:
            raise ValueError("Negative CPU sample duration")
        stack, seen, current = [], set(), node_id
        while current is not None:
            if current in seen:
                raise ValueError("Cycle in CPU stack")
            seen.add(current)
            frame = nodes[current]["callFrame"]
            mapping = None
            url = urlsplit(frame.get("url", "")).path
            in_bundle = url.endswith(bundles)
            if source_map and in_bundle:
                mapping = source_map.lookup(frame.get("lineNumber", -1), frame.get("columnNumber", -1))
            elif frame.get("url") and frame.get("lineNumber", -1) >= 0 and not in_bundle:
                mapping = (frame["url"], frame["lineNumber"] + 1, frame.get("columnNumber", 0) + 1)
            stack.append((frame.get("functionName") or "(anonymous)", mapping))
            current = parents.get(current)
        yield elapsed, duration, stack
        elapsed += duration


def react_rows(data):
    """Per commit and fiber: (timestamp, self ms, actual ms, frame). Actual time includes children."""
    for root in data["dataForRoots"]:
        names = {key: value.get("displayName") or f"fiber-{key}" for key, value in root.get("snapshots", [])}
        sources = dict(root.get("sourceLocations", []))
        for commit in root["commitData"]:
            own = {key: finite(ms) for key, ms in commit["fiberSelfDurations"]}
            actual = {key: finite(ms) for key, ms in commit.get("fiberActualDurations", [])}
            for key in dict.fromkeys([*own, *actual]):
                source = sources.get(key)
                mapping = (source["file"], source["line"], source.get("column", 1)) if source else None
                self_ms = own.get(key, 0)
                yield commit["timestamp"], self_ms, actual.get(key, self_ms), (names.get(key, f"fiber-{key}"), mapping)


def ranked(db, top):
    db.row_factory = sqlite3.Row
    return [dict(row) for row in db.execute("""
        WITH totals AS (SELECT t.kind, SUM(c.self_ms) total FROM costs c JOIN traces t ON c.trace_id=t.id GROUP BY t.kind)
        SELECT t.kind, f.name, f.file, f.line, f.col, f.mapped,
          SUM(c.self_ms) self_ms, SUM(c.inclusive_ms) inclusive_ms, SUM(c.self_ms)/NULLIF(totals.total, 0) share
        FROM costs c JOIN traces t ON t.id=c.trace_id JOIN frames f ON f.id=c.frame_id JOIN totals ON totals.kind=t.kind
        GROUP BY t.kind, f.id ORDER BY self_ms DESC, inclusive_ms DESC LIMIT ?
    """, (top,))]


def window_for(trace, window):
    if window == "whole":
        return 0, math.inf
    if window is not None:
        return window
    sidecar = Path(str(trace) + ".flow.json")
    if not sidecar.is_file():
        raise ValueError(f"No window for {trace}: pass --window START END, add {sidecar.name}, or pass --whole")
    return tuple(load(sidecar)["window_ms"])


def reduce_traces(traces, out, window=None, source_map=None, top=20, compare_to=None):
    out = Path(out)
    temp = out.with_name(f".{out.name}.{os.getpid()}.tmp")
    temp.unlink(missing_ok=True)
    db = sqlite3.connect(temp)
    try:
        db.executescript("""
            CREATE TABLE traces(id INTEGER PRIMARY KEY, path TEXT, kind TEXT, start_ms REAL, end_ms REAL);
            CREATE TABLE frames(id INTEGER PRIMARY KEY, name TEXT, file TEXT, line INTEGER, col INTEGER, mapped INTEGER);
            CREATE TABLE costs(trace_id INTEGER, frame_id INTEGER, start_ms REAL, self_ms REAL, inclusive_ms REAL);
            CREATE TABLE samples(trace_id INTEGER, start_ms REAL, duration_ms REAL, leaf INTEGER);
            CREATE TABLE stack_samples(sample_id INTEGER, frame_id INTEGER, depth INTEGER);
            CREATE INDEX stack_frame ON stack_samples(frame_id);
        """)
        mapper = SourceMap(source_map) if source_map else None
        frames = {}

        def frame_id(name, mapping):
            key = (name, mapping)
            if key not in frames:
                file, line, col = mapping if mapping else (None, None, None)
                frames[key] = db.execute("INSERT INTO frames(name,file,line,col,mapped) VALUES(?,?,?,?,?)",
                                         (name, file, line, col, int(mapping is not None))).lastrowid
            return frames[key]

        for index, trace in enumerate(traces, 1):
            path = Path(trace).resolve(strict=True)
            data = load(path)
            kind = "react" if "dataForRoots" in data else "cpu"
            low, high = window_for(path, window)
            if finite(low) < 0 or not high > low:
                raise ValueError("Window must have ordered, nonnegative millisecond boundaries")
            db.execute("INSERT INTO traces VALUES(?,?,?,?,?)",
                       (index, str(path), kind, low, None if math.isinf(high) else high))
            if kind == "react":
                for start, self_ms, actual_ms, (name, mapping) in react_rows(data):
                    if not low <= start < high or (self_ms <= 0 and actual_ms <= 0):
                        continue
                    frame = frame_id(name, mapping)
                    db.execute("INSERT INTO costs VALUES(?,?,?,?,?)", (index, frame, start, self_ms, actual_ms))
                    if self_ms > 0:
                        sample = db.execute("INSERT INTO samples VALUES(?,?,?,?)", (index, start, self_ms, frame)).lastrowid
                        db.execute("INSERT INTO stack_samples VALUES(?,?,?)", (sample, frame, 0))
                continue
            for start, duration, stack in cpu_rows(data, mapper):
                weight = max(0, min(start + duration, high) - max(start, low))
                if weight <= 0:
                    continue
                ids = list(dict.fromkeys(frame_id(name, mapping) for name, mapping in stack))
                sample = db.execute("INSERT INTO samples VALUES(?,?,?,?)", (index, start, weight, ids[0])).lastrowid
                db.executemany("INSERT INTO stack_samples VALUES(?,?,?)",
                               [(sample, frame, depth) for depth, frame in enumerate(ids)])
                db.executemany("INSERT INTO costs VALUES(?,?,?,?,?)",
                               [(index, frame, start, weight if depth == 0 else 0, weight) for depth, frame in enumerate(ids)])
        db.commit()
        ranking = ranked(db, top)
        if not ranking:
            raise ValueError("No measured work inside the selected window")
        diff = []
        if compare_to:
            def identity(row):
                return row["kind"], row["name"], row["file"], row["line"], row["col"]
            with sqlite3.connect(f"file:{Path(compare_to).resolve()}?mode=ro", uri=True) as previous:
                before = {identity(r): r for r in ranked(previous, 10**6)}
            after = {identity(r): r for r in ranked(db, 10**6)}
            for key in before.keys() | after.keys():
                a, b = before.get(key, {}), after.get(key, {})
                diff.append({"kind": key[0], "name": key[1], "file": key[2], "line": key[3], "col": key[4],
                             "before_ms": a.get("self_ms", 0), "after_ms": b.get("self_ms", 0),
                             "delta_ms": b.get("self_ms", 0) - a.get("self_ms", 0)})
            diff.sort(key=lambda row: abs(row["delta_ms"]), reverse=True)
        db.close()
        os.replace(temp, out)
        return {"sqlite": str(out), "ranked": ranking, "diff": diff[:top],
                "note": "unmapped frames (mapped = 0) are hypotheses, not source diagnoses"}
    except BaseException:
        db.close()
        temp.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("traces", nargs="+")
    parser.add_argument("--out", required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--window", nargs=2, type=float, metavar=("START_MS", "END_MS"))
    group.add_argument("--whole", action="store_true")
    parser.add_argument("--map")
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--compare")
    args = parser.parse_args()
    window = "whole" if args.whole else (tuple(args.window) if args.window else None)
    try:
        result = reduce_traces(args.traces, args.out, window, args.map, args.top, args.compare)
    except (ValueError, KeyError, FileNotFoundError) as error:
        sys.exit(f"reduce.py: {error}")
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
