import argparse, hashlib, json, pathlib, sys
from .policy import decide
from .metrics import evaluate
def main(argv=None):
    ap = argparse.ArgumentParser(prog="abstention_routing_harness")
    ap.add_argument("cmd", choices=["run"]); ap.add_argument("fixture"); ap.add_argument("--out", required=True)
    ap.add_argument("--rubric", default="rubric-v1"); a = ap.parse_args(argv)
    raw = pathlib.Path(a.fixture).read_bytes(); data = json.loads(raw)
    cases = data["cases"]; decs = [decide(c, a.rubric) for c in cases]
    rep = {"fixture_sha256": hashlib.sha256(raw).hexdigest(), "rubric_id": a.rubric, "run_kind": data.get("run_kind", "mock"), **evaluate(cases, decs)}
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "decisions.json").write_text(json.dumps(decs, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    (out / "report.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: rep[k] for k in ("coverage", "selective_accuracy", "false_acceptance")}, sort_keys=True)); return 0
if __name__ == "__main__": sys.exit(main())
