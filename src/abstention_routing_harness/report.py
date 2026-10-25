"""Build reports/confusion.json, reports/calibration.json and reports/index.html.

Usage: python -m abstention_routing_harness.report [--out reports] FIXTURE.json ...
"""
import argparse, json, os
from .policy import decide
from .costpolicy import decide_cost, calibrate, DEFAULT_COSTS
from .confusion import confusion, to_html

def _load(p):
    d = json.load(open(p, encoding="utf-8"))
    return d["cases"] if isinstance(d, dict) else d

def build(paths, out):
    cases = [c for p in paths for c in _load(p)]
    cal = calibrate(cases)
    t = cal["best_min_support"]
    base = confusion(cases, decide)
    cost = confusion(cases, lambda c: decide_cost(c, DEFAULT_COSTS, t))
    os.makedirs(out, exist_ok=True)
    src = [os.path.basename(p) for p in paths]
    w = lambda n, o: open(os.path.join(out, n), "w", encoding="utf-8").write(json.dumps(o, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    w("confusion.json", {"sources": src, "base_policy": base, "cost_policy": cost, "cost_policy_min_support": t})
    w("calibration.json", dict(cal, sources=src))
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(
        to_html("Abstention & routing — confusion report", [("Base policy", base), ("Cost/risk policy (min_support=%s, in-sample)" % t, cost)]))
    return {"base": base, "cost": cost, "calibration": cal}

def main(argv=None):
    ap = argparse.ArgumentParser(prog="abstention_routing_harness.report")
    ap.add_argument("fixtures", nargs="+"); ap.add_argument("--out", default="reports")
    a = ap.parse_args(argv); r = build(a.fixtures, a.out)
    print(json.dumps({"base_accuracy": r["base"]["accuracy"], "cost_accuracy": r["cost"]["accuracy"],
                      "best_min_support": r["calibration"]["best_min_support"], "n": r["base"]["n_labelled"]}))

if __name__ == "__main__": main()
