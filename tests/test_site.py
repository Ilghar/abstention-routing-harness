import json, pathlib, subprocess, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "tools"))
import export_site
class Site(unittest.TestCase):
    def test_project_json_valid_and_html_escapes(self):
        p = json.loads((ROOT / "site/project.json").read_text()); s = json.loads((ROOT / "site/schema.json").read_text())
        self.assertEqual(export_site.validate(p, s), [])
        h = export_site.render(dict(p, title="<script>x</script>")); self.assertNotIn("<script>", h); self.assertIn("<script>", h)
        self.assertIn("prefers-reduced-motion", h); self.assertNotIn("http", h.split("<main>")[0].replace("http://www.w3.org", ""))
    def test_svg_diagram_matches_project_architecture(self):
        svg = (ROOT / "docs/architecture.svg").read_text(); p = json.loads((ROOT / "site/project.json").read_text())
        self.assertTrue(all(__import__("html").escape(a) in svg for a in p["architecture"])); self.assertIn("<desc", svg)
    def test_generated_pages_in_sync_with_project_json(self):
        p = json.loads((ROOT / "site/project.json").read_text(encoding="utf-8"))
        self.assertEqual((ROOT / "site/index.html").read_text(encoding="utf-8"), export_site.render(p))
        self.assertEqual((ROOT / "docs/CASE_PAGE.md").read_text(encoding="utf-8"), export_site.render_md(p))
if __name__ == "__main__": unittest.main()
