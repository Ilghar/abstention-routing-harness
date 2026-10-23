import json, pathlib, subprocess, sys, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from abstention_routing_harness.pipeline import propose, ingest
class Slice(unittest.TestCase):
    def test_rule_abstains_on_none_or_both_domains(self):
        self.assertEqual(propose("Prüfe die Formel")["route"], "spreadsheet")
        self.assertEqual(propose("Copy chat into the sheet")["route"], "unknown")
        self.assertEqual(propose("Book a train")["route"], "unknown")
    def test_ingest_malformed_rows_go_human(self):
        c = ingest([["ok sheet", "spreadsheet"], ["x"], ["text", "weird"]])
        self.assertEqual([x["expected_route"] for x in c], ["spreadsheet", "human", "human"])
    def test_end_to_end_regression_on_cleared_fixture(self):
        with tempfile.TemporaryDirectory() as t:
            subprocess.run([sys.executable, "-m", "abstention_routing_harness", "slice", "inputs/synthetic_queue_fixture.json", "--probes", "fixtures/ood_probes_m04.json", "--out", t], check=True, cwd=ROOT, env={"PYTHONPATH": str(ROOT / "src")}, capture_output=True)
            r = json.loads((pathlib.Path(t) / "report.json").read_text()); d = json.loads((pathlib.Path(t) / "decisions.json").read_text())
        self.assertEqual(r["n_items"], 27); self.assertEqual(r["coverage"]["admitted"], 21)
        self.assertEqual(r["selective_accuracy"], {"correct": 20, "denominator": 21, "value": 0.952381})
        self.assertEqual(r["false_acceptance"], {"count": 1, "denominator": 7, "value": 0.142857})  # P07 'sheet music'
        self.assertTrue(all(x["can_move_documents"] is False for x in d)); self.assertIn("not held-out", r["caveat"])
if __name__ == "__main__": unittest.main()
