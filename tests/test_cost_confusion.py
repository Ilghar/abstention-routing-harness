import json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from abstention_routing_harness.costpolicy import decide_cost, calibrate, support, DEFAULT_COSTS
from abstention_routing_harness.confusion import confusion, to_html
from abstention_routing_harness.policy import decide
from abstention_routing_harness import report
ROOT = os.path.join(os.path.dirname(__file__), "..")

def case(props, **kw):
    c = {"id": "T1", "text": "Add a row for invoice 12", "scope_verified": True, "fixture_kind": "synthetic", "requests_used": 0,
         "proposals": [dict({"model_id": "m", "revision": "r"}, **p) for p in props]}
    c.update(kw); return c

class Cost(unittest.TestCase):
    def test_unanimous_admitted(self):
        d = decide_cost(case([{"route": "spreadsheet"}]))
        self.assertEqual((d["route"], d["reason_code"]), ("spreadsheet", "ADMITTED_COST"))
    def test_conflict_resolved_by_confidence(self):
        d = decide_cost(case([{"route": "spreadsheet", "confidence": 1.0}, {"route": "conversation", "confidence": 0.1}]),
                        {"error_cost": {"spreadsheet": 0.5, "conversation": 1}, "abstain_cost": 0.3})
        self.assertEqual(d["route"], "spreadsheet")
    def test_even_conflict_abstains(self):
        d = decide_cost(case([{"route": "spreadsheet"}, {"route": "conversation"}]))
        self.assertTrue(d["abstained"]); self.assertEqual(d["reason_code"], "RISK_ABOVE_ABSTAIN_COST")
    def test_threshold(self):
        d = decide_cost(case([{"route": "spreadsheet", "confidence": 0.4}]), min_support=0.5)
        self.assertEqual(d["reason_code"], "SUPPORT_BELOW_THRESHOLD")
    def test_safety_gates_kept(self):
        for kw, code in (({"scope_verified": False}, "SCOPE_UNVERIFIED"), ({"requests_used": 2}, "BUDGET_EXCEEDED")):
            self.assertEqual(decide_cost(case([{"route": "spreadsheet"}], **kw))["reason_code"], code)
    def test_bad_confidence_and_costs(self):
        for c in (float("nan"), 1.5, True, -0.1):
            self.assertEqual(decide_cost(case([{"route": "spreadsheet", "confidence": c}]))["reason_code"], "CONFIDENCE_INVALID")
        with self.assertRaises(ValueError): decide_cost(case([{"route": "spreadsheet"}]), {"error_cost": {"spreadsheet": 1}, "abstain_cost": 0.3})
        with self.assertRaises(ValueError): decide_cost(case([{"route": "spreadsheet"}]), {"error_cost": {"spreadsheet": -1, "conversation": 1}, "abstain_cost": 0.3})
    def test_calibrate_deterministic_and_in_sample(self):
        cs = [case([{"route": "spreadsheet", "confidence": 0.8}], expected_route="spreadsheet"),
              case([{"route": "conversation", "confidence": 0.3}], expected_route="human")]
        a, b = calibrate(cs), calibrate(cs)
        self.assertEqual(a, b); self.assertTrue(a["in_sample"]); self.assertEqual(a["best_total_cost"], 0.0)
        self.assertTrue(0.3 < a["best_min_support"] <= 0.8)

class Confusion(unittest.TestCase):
    def test_matrix(self):
        cs = [case([{"route": "spreadsheet"}], expected_route="spreadsheet"),
              case([{"route": "spreadsheet"}], expected_route="human"),
              case([{"route": "spreadsheet"}], scope_verified=False, expected_route="conversation"),
              case([{"route": "spreadsheet"}])]
        c = confusion(cs, decide)
        self.assertEqual(c["matrix"]["spreadsheet"]["spreadsheet"], 1)
        self.assertEqual(c["missed_abstentions"], 1); self.assertEqual(c["over_abstentions"], 1)
        self.assertEqual(c["unlabelled"], 1); self.assertEqual(c["n_labelled"], 3)
    def test_html_escapes_and_credit(self):
        cs = [case([{"route": "spreadsheet"}], id="X<1", expected_route="human")]
        h = to_html("t<", [("s", confusion(cs, decide))])
        self.assertNotIn("<1", h.replace("&lt;1", "")); self.assertIn("ilghar.studio", h)
    def test_report_on_fixtures_matches_receipt(self):
        fx = [os.path.join(ROOT, "fixtures", f) for f in ("synthetic_cases_m03.json", "ood_probes_m04.json")]
        with tempfile.TemporaryDirectory() as d:
            r = report.build(fx, d)
            for f in ("confusion.json", "calibration.json", "index.html"): self.assertTrue(os.path.exists(os.path.join(d, f)))
            got = json.load(open(os.path.join(d, "confusion.json")))
        rec = os.path.join(ROOT, "tests", "receipts", "m08_confusion_receipt.json")
        if os.path.exists(rec):
            exp = json.load(open(rec))
            self.assertEqual(got["base_policy"]["matrix"], exp["base_matrix"])
            self.assertEqual(got["cost_policy"]["matrix"], exp["cost_matrix"])

if __name__ == "__main__": unittest.main()
