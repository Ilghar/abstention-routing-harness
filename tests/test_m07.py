import json, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from abstention_routing_harness import failure, collection
from abstention_routing_harness.policy import decide
B = failure.BASE
class M07(unittest.TestCase):
    def test_adversarial_suite_all_pass_and_schema_valid(self):
        r = failure.run_adversarial(); self.assertEqual(r["passed"], r["n"], [x for x in r["rows"] if not x["pass"]])
    def test_regressions_fixed_in_m07(self):
        for mut, code in [({"text": "\u200b\u200c"}, "TEXT_INVALID"), ({"text": "\u202e"}, "TEXT_INVALID"), ({"text": "\ud800x"}, "TEXT_INVALID"),
                          ({"id": {"a": 1}}, "CASE_INVALID"), ({"id": "lower"}, "CASE_INVALID"), ({"proposals": failure.P(*["spreadsheet"] * 9)}, "PROPOSAL_MALFORMED")]:
            with self.subTest(mut=str(mut)[:30]): self.assertEqual(decide(dict(B, **mut))["reason_code"], code)
    def test_disagreement_always_abstains(self):
        for props in (failure.P("spreadsheet", "conversation"), failure.P("conversation", "spreadsheet", "conversation"), failure.P("spreadsheet", "unknown")):
            self.assertTrue(decide(dict(B, proposals=props))["abstained"])
    def test_heldout_error_analysis_counts_match_m06(self):
        a = failure.analyze(collection.split_cases(ROOT, "test"))
        self.assertEqual(a["by_kind"].get("false_acceptance"), 5)  # same 5/12 as docs/RESULTS.md
        self.assertTrue(all(e["keyword_hits"] for e in a["errors"] if e["kind"] == "false_acceptance"))
if __name__ == "__main__": unittest.main()
