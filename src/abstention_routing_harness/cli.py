import argparse, hashlib, json, pathlib, sys
from .policy import decide
from .metrics import evaluate
def main(argv=None):
    ap = argparse.ArgumentParser(prog="abstention_routing_harness")
    ap.add_argument("cmd", choices=["run","slice","collection","baselines"]); ap.add_argument("fixture", nargs="?", default="."); ap.add_argument("--out", required=True)
    ap.add_argument("--rubric", default="rubric-v1"); ap.add_argument("--probes"); a = ap.parse_args(argv)
    if a.cmd in ("collection", "baselines"):
        from .collection import build, split_cases
        from .baselines import run_baselines
        out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True); man = build(a.fixture)
        if a.cmd == "collection":
            (out / "manifest.json").write_text(json.dumps(man, indent=1, sort_keys=True, ensure_ascii=False) + "\n"); print(json.dumps({"errors": len(man["errors"]), "files": {k: v["n"] for k, v in man["files"].items()}})); return 1 if man["errors"] else 0
        rep = {"collection_version": man["version"], "file_sha256": {k: v["sha256"] for k, v in man["files"].items()},
               "splits": {s: run_baselines(split_cases(a.fixture, s), a.rubric) for s in ("dev", "test")},
               "limitations": ["all items synthetic; n is small (dev 27, test 24) so intervals are wide",
                               "keyword rule was developed on dev; test probes were written by the same author after the rule existed (not blind)",
                               "labels are author-assigned and unreviewed", "no model was run; these are rule baselines only"]}
        (out / "baselines.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
        print(json.dumps({s: {b: [v["coverage"]["value"], v["selective_accuracy"]["value"], v["false_acceptance"]["value"]] for b, v in r.items()} for s, r in rep["splits"].items()})); return 0
    raw = pathlib.Path(a.fixture).read_bytes(); data = json.loads(raw)
    if a.cmd == "slice":
        from .pipeline import run, RULE_ID, RULE_REV
        probes = json.loads(pathlib.Path(a.probes).read_text())["cases"] if a.probes else []
        cases, decs, m = run(data, probes, a.rubric)
        rep = {"fixture_sha256": hashlib.sha256(raw).hexdigest(), "rubric_id": a.rubric, "run_kind": "rule", "proposer": f"{RULE_ID}@{RULE_REV}",
               "caveat": "keyword rule tuned on this same fixture; not held-out, not a model result", **m}
    else:
        cases = data["cases"]; decs = [decide(c, a.rubric) for c in cases]
        rep = {"fixture_sha256": hashlib.sha256(raw).hexdigest(), "rubric_id": a.rubric, "run_kind": data.get("run_kind", "mock"), **evaluate(cases, decs)}
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "decisions.json").write_text(json.dumps(decs, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    (out / "report.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: rep[k] for k in ("coverage", "selective_accuracy", "false_acceptance")}, sort_keys=True)); return 0
if __name__ == "__main__": sys.exit(main())
