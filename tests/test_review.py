"""Regression tests for findings in docs/REVIEW_M01_M07.md (AI self-review)."""
import json, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from abstention_routing_harness.schema import validate
class Review(unittest.TestCase):
    def test_probe_files_are_cases_once_proposals_attached(self):
        s = json.loads((ROOT / "schemas/case.schema.json").read_text(encoding="utf-8"))
        for f in ("fixtures/ood_probes_m04.json", "data/collection_v1/dev_probes.json", "data/collection_v1/heldout_probes.json"):
            for c in json.loads((ROOT / f).read_text(encoding="utf-8"))["cases"]:
                self.assertEqual(validate(dict(c, proposals=c.get("proposals", [])), s, s), [], (f, c.get("id")))
if __name__ == "__main__": unittest.main()
