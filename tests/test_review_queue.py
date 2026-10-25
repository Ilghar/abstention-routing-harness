import json, pathlib, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from abstention_routing_harness.review_queue import build_queue, render_md, main, EXPLAIN
from abstention_routing_harness.policy import decide
class ReviewQueue(unittest.TestCase):
    def test_only_abstentions_are_queued_and_sorted_by_priority(self):
        d = [{"case_id": "a", "abstained": False, "reason_code": "ADMITTED_ADVISORY"},
             {"case_id": "b", "abstained": True, "reason_code": "BUDGET_EXCEEDED"},
             {"case_id": "c", "abstained": True, "reason_code": "SCOPE_UNVERIFIED"},
             {"case_id": "d", "abstained": True, "reason_code": "SOMETHING_NEW"}]
        q = build_queue(d)
        self.assertEqual([i["case_id"] for i in q["items"]], ["c", "b", "d"]); self.assertEqual(q["n_queued"], 3)
        self.assertIn("inspect manually", q["items"][-1]["why"])
    def test_every_policy_reason_has_an_explanation(self):
        src = (ROOT / "src/abstention_routing_harness/policy.py").read_text()
        import re
        codes = set(re.findall(r'"([A-Z][A-Z_]+)"', src)) - {"ADMITTED_ADVISORY", "ZC"}
        self.assertEqual(codes - set(EXPLAIN), set())
    def test_markdown_escapes_pipes_and_cli_writes_files(self):
        q = build_queue([{"case_id": "x|y", "abstained": True, "reason_code": "NO_PROPOSAL"}], [{"id": "x|y", "text": "a|b"}])
        self.assertIn("x\\|y", render_md(q))
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / "d.json"; p.write_text(json.dumps([{"case_id": "z", "abstained": True, "reason_code": "PROPOSALS_CONFLICT"}]))
            self.assertEqual(main([str(p), "--out", str(pathlib.Path(t) / "q.md")]), 0)
            self.assertTrue((pathlib.Path(t) / "q.json").exists())
    def test_on_m03_fixture(self):
        data = json.loads((ROOT / "fixtures/synthetic_cases_m03.json").read_text())
        decs = [decide(c, "rubric-v1") for c in data["cases"]]; q = build_queue(decs, data["cases"])
        self.assertEqual(q["n_queued"], sum(1 for x in decs if x["abstained"]))
if __name__ == "__main__": unittest.main()
