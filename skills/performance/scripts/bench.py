#!/usr/bin/env python3
"""Compare two sets of benchmark runs and give a verdict.

    bench.py BEFORE.json AFTER.json --direction lower|higher --noise-floor N --limiter "TEXT"

Each file describes one side:

    {
      "environment": {"device": "...", "native_build": "...", "flow": "...", "metric": "...", "workload": "..."},
      "runs": [{"value": 812.4, "error_count": 0, "work_count": 1, "proof": "what showed the work completed"}]
    }

`value` is the metric in its unit (for example milliseconds). `work_count` is how much work the
run did (rows saved, screens shown); every run on both sides must do the same positive amount.
`proof` names the evidence that the work happened, read inside the timed region.
`--limiter` names the measured resource or source path that bounds the result; an empty limiter
makes the verdict inconclusive.

The five fields above are required. Any other environment field (for example cache_policy) is
compared too. Refuses to compare when any environment field differs. Verdicts:
  faster / slower             the median gap exceeds the noise (the larger of --noise-floor and
                              each side's full range)
  no measurable difference    the gap is within the noise
  inconclusive                fewer than 5 runs a side, any errors, unequal or missing work,
                              missing proof, or no limiter
Prints JSON. Python 3.9+ standard library only.
"""

import argparse
import json
import math
import sys
from statistics import median

ENVIRONMENT = ("device", "native_build", "flow", "metric", "workload")


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Expected a finite number")
    return value


def summarize(runs):
    values = [finite(r["value"]) for r in runs]
    if not values:
        raise ValueError("No measured runs")
    if any(v < 0 for v in values) or any(finite(r["error_count"]) < 0 or finite(r["work_count"]) < 0 for r in runs):
        raise ValueError("Values, error counts and work counts cannot be negative")
    return {"median": median(values), "range": [min(values), max(values)], "count": len(values),
            "error_count": sum(r["error_count"] for r in runs), "work_count": sum(r["work_count"] for r in runs)}


def same_environment(before, after):
    for key in ENVIRONMENT:
        if before.get(key) is None or after.get(key) is None:
            raise ValueError(f"Comparison refused: {key} is missing")
    differing = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    if differing:
        raise ValueError("Comparison refused: " + ", ".join(
            f"{k} differs: {before.get(k)!r} vs {after.get(k)!r}" for k in differing))


def compare(before, after, direction, floor, limiter):
    if floor < 0 or direction not in ("lower", "higher"):
        raise ValueError("Need --direction lower|higher and a nonnegative --noise-floor")
    same_environment(before["environment"], after["environment"])
    runs_a, runs_b = before["runs"], after["runs"]
    a, b = summarize(runs_a), summarize(runs_b)
    noise = max(finite(floor), a["range"][1] - a["range"][0], b["range"][1] - b["range"][0])
    delta = b["median"] - a["median"]
    invalid = (len(runs_a) < 5 or len(runs_b) < 5 or a["error_count"] or b["error_count"]
               or any(r["work_count"] <= 0 or not r.get("proof") for r in runs_a + runs_b)
               or len({r["work_count"] for r in runs_a + runs_b}) != 1 or not limiter)
    if invalid:
        verdict = "inconclusive"
    elif abs(delta) > noise:
        verdict = "faster" if (delta < 0 if direction == "lower" else delta > 0) else "slower"
    else:
        verdict = "no measurable difference"
    return {"environment": before["environment"], "before": a, "after": b, "delta": delta,
            "noise": noise, "verdict": verdict, "limiter": limiter,
            "reason": "Needs >=5 runs a side, equal positive work with proof, no errors, and a limiter"
                      if invalid else "Median gap compared with the larger of the noise floor and each side's range"}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--direction", required=True, choices=("lower", "higher"))
    parser.add_argument("--noise-floor", required=True, type=float)
    parser.add_argument("--limiter", required=True)
    args = parser.parse_args()
    try:
        with open(args.before) as a, open(args.after) as b:
            result = compare(json.load(a), json.load(b), args.direction, args.noise_floor, args.limiter)
    except (ValueError, KeyError) as error:
        sys.exit(f"bench.py: {error}")
    json.dump(result, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
