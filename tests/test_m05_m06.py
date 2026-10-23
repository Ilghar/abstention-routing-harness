import json, pathlib, subprocess, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from abstention_routing_harness.schema import validate, load_schema, unsupported_keywords
from abstention_routing_harness.collection import build
from abstention_routing_harness.baselines import wilson
from abstention_routing_harness.policy import decide
class Schema(unittest.TestCase):
    def test_schema_catches_intended_malformed_fixture_items(self):
        s = load_schema(ROOT, "case.schema.json"); self.assertEqual(unsupported_keywords(s), set())
        bad = {c["id"]: validate(c, s) for c in json.loads((ROOT / "fixtures/synthetic_cases_m03.json").read_text())["cases"]}
        self.assertEqual(sorted(k for k, v in bad.items() if v), ["B05", "B06", "B10"])
        self.assertTrue(validate({"id": "x"}, s)); self.assertIn("unexpected property 'zz'", " ".join(validate(dict(bad and json.loads((ROOT / "fixtures/synthetic_cases_m03.json").read_text())["cases"][0], zz=1), s)))
    def test_decisions_and_reports_conform(self):
        c = json.loads((ROOT / "fixtures/synthetic_cases_m03.json").read_text())["cases"]
        ds = load_schema(ROOT, "decision.schema.json")
        self.assertEqual([e for x in c for e in validate(decide(x), ds)], [])
class Collection(unittest.TestCase):
    def test_manifest_clean_and_synthetic_only(self):
        m = build(ROOT); self.assertEqual(m["errors"], []); self.assertEqual(m["empirical_items"], 0)
        self.assertEqual({k: v["n"] for k, v in m["files"].items()}, {"dev_queue.json": 20, "dev_probes.json": 7, "heldout_probes.json": 24})
        self.assertEqual(m["files"]["heldout_probes.json"]["split"], "test"); self.assertEqual(len(m["historical_not_rerun"]), 2)
class Baselines(unittest.TestCase):
    def test_wilson(self):
        self.assertIsNone(wilson(0, 0)); self.assertEqual(wilson(5, 12), [0.1933, 0.6805])
    def test_measured_baselines_regression(self):
        with tempfile.TemporaryDirectory() as t:
            subprocess.run([sys.executable, "-m", "abstention_routing_harness", "baselines", ".", "--out", t], check=True, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")}, capture_output=True)
            r = json.loads((pathlib.Path(t) / "baselines.json").read_text())
        kw = r["splits"]["test"]["keyword_rule"]
        self.assertEqual((kw["coverage"]["admitted"], kw["selective_accuracy"]["correct"], kw["false_acceptance"]["count"], kw["false_acceptance"]["denominator"]), (11, 6, 5, 12))
        self.assertEqual(r["splits"]["test"]["always_abstain"]["false_acceptance"]["count"], 0)
        self.assertEqual(r["splits"]["test"]["majority_spreadsheet"]["false_acceptance"]["value"], 1.0)
        self.assertTrue(any("not blind" in l for l in r["limitations"]))
if __name__ == "__main__": unittest.main()
