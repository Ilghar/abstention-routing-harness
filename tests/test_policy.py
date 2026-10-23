import json, math, pathlib, subprocess, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from abstention_routing_harness.policy import decide
BASE = {"id": "T", "text": "Fix sheet", "scope_verified": True, "fixture_kind": "synthetic", "requests_used": 0,
        "proposals": [{"model_id": "m", "revision": "r", "route": "spreadsheet"}]}
def mk(**kw): d = dict(BASE); d.update(kw); return d
class Gates(unittest.TestCase):
    def test_admits_only_clean_agreement(self):
        d = decide(mk()); self.assertEqual((d["route"], d["reason_code"]), ("spreadsheet", "ADMITTED_ADVISORY"))
        self.assertFalse(d["can_move_documents"]); self.assertTrue(d["advisory_only"])
    def test_budget_edge_cases_route_human_without_raising(self):
        for u, code in [("1", "BUDGET_INVALID"), (math.nan, "BUDGET_INVALID"), (True, "BUDGET_INVALID"), (-1, "BUDGET_INVALID"), (math.inf, "BUDGET_INVALID"), (1.0, "BUDGET_INVALID"), (2, "BUDGET_EXCEEDED")]:
            with self.subTest(u=u): self.assertEqual(decide(mk(requests_used=u))["reason_code"], code)
    def test_proposal_failures(self):
        P = lambda *r: [{"model_id": "m", "revision": "r", "route": x} for x in r]
        for props, code in [([], "NO_PROPOSAL"), (P("unknown"), "PROPOSAL_ABSTAINED"), (P("delete"), "PROPOSAL_MALFORMED"), (P(None), "PROPOSAL_MALFORMED"), (["x"], "PROPOSAL_MALFORMED"), (P("spreadsheet", "conversation"), "PROPOSALS_CONFLICT")]:
            with self.subTest(code=code): d = decide(mk(proposals=props)); self.assertEqual((d["route"], d["reason_code"]), ("human", code))
    def test_scope_permission_text(self):
        self.assertEqual(decide(mk(scope_verified="true"))["reason_code"], "SCOPE_UNVERIFIED")
        self.assertEqual(decide(mk(fixture_kind="unapproved"))["reason_code"], "INPUT_NOT_PERMITTED")
        self.assertEqual(decide(mk(text="x" * 2001))["reason_code"], "TEXT_INVALID")
        self.assertEqual(decide("not a dict")["route"], "human")
    def test_identity_changes_with_revision_and_rubric(self):
        a = decide(mk())["identity"]; self.assertEqual(a, decide(mk())["identity"])
        self.assertNotEqual(a, decide(mk(), rubric="rubric-v2")["identity"])
        self.assertNotEqual(a, decide(mk(proposals=[{"model_id": "m", "revision": "r2", "route": "spreadsheet"}]))["identity"])
class CLI(unittest.TestCase):
    def test_fixture_report_counts(self):
        with tempfile.TemporaryDirectory() as t:
            subprocess.run([sys.executable, "-m", "abstention_routing_harness", "run", str(ROOT / "fixtures/synthetic_cases_m03.json"), "--out", t], check=True, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")}, capture_output=True)
            r = json.loads((pathlib.Path(t) / "report.json").read_text())
        self.assertEqual(r["n_items"], 16)
        self.assertEqual(r["coverage"], {"admitted": 6, "denominator": 16, "value": 0.375})
        self.assertEqual(r["selective_accuracy"]["correct"], 4)  # A05 wrong, B01 false acceptance
        self.assertEqual(r["false_acceptance"], {"count": 1, "denominator": 4, "value": 0.25})
        self.assertEqual(r["disagreements"], 1)
if __name__ == "__main__": unittest.main()
