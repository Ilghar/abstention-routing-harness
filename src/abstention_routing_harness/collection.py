"""M05: versioned case collection with manifest (hashes, splits, provenance, class counts) and schema validation."""
import hashlib, json, pathlib
from collections import Counter
from .pipeline import ingest
from .schema import load_schema, validate
FILES = {"dev_queue.json": {"split": "dev", "provenance": "synthetic (Drive input S05, cleared)", "format": "pairs"},
         "dev_probes.json": {"split": "dev", "provenance": "synthetic, Bot-written M04", "format": "cases"},
         "heldout_probes.json": {"split": "test", "provenance": "synthetic, Bot-written after rule (not blind)", "format": "cases"}}
HISTORICAL = ["inputs/narrow_fixture_historical.json", "inputs/expanded_fixture_historical.json"]
def load_cases(cdir, name):
    d = json.loads((cdir / name).read_text(encoding="utf-8"))
    if FILES[name]["format"] == "pairs": return ingest(d, prefix="Q")
    return [{k: v for k, v in c.items() if k != "known_limitation"} for c in d["cases"]]
def build(root):
    root = pathlib.Path(root); cdir = root / "data/collection_v1"; schema = load_schema(root, "case.schema.json")
    man = {"collection": "abstention-routing-cases", "version": "1.0.0", "empirical_items": 0,
           "note": "All items synthetic. Historical fixture summaries are listed separately as historical_not_rerun and are not part of any split.",
           "files": {}, "historical_not_rerun": {h: hashlib.sha256((root / h).read_bytes()).hexdigest() for h in HISTORICAL}, "errors": []}
    ids = Counter()
    for name, meta in FILES.items():
        cases = load_cases(cdir, name); ids.update(c["id"] for c in cases)
        for c in cases:
            stub = dict(c, proposals=c.get("proposals", []))
            man["errors"] += [f"{name}:{c['id']}: {e}" for e in validate(stub, schema)]
        man["files"][name] = {**meta, "sha256": hashlib.sha256((cdir / name).read_bytes()).hexdigest(), "n": len(cases),
                              "classes": dict(sorted(Counter(c["case_class"] for c in cases).items())),
                              "expected_routes": dict(sorted(Counter(c["expected_route"] for c in cases).items()))}
    man["errors"] += [f"duplicate id {i}" for i, n in ids.items() if n > 1]
    texts = Counter(c["text"].strip().lower() for n in FILES for c in load_cases(cdir, n))
    man["errors"] += [f"duplicate text across collection: {t!r}" for t, n in texts.items() if n > 1]
    return man
def split_cases(root, split):
    cdir = pathlib.Path(root) / "data/collection_v1"
    return [c for n, m in FILES.items() if m["split"] == split for c in load_cases(cdir, n)]
