"""Light/dark theme: WCAG AA contrast for every text/background token pair in both themes, and the
generated pages carry both themes, the system fallback and an accessible, persisted toggle."""
import pathlib, re, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "tools"))
from abstention_routing_harness import theme
import export_site

class Theme(unittest.TestCase):
    def test_text_pairs_meet_wcag_aa_in_both_themes(self):
        for mode in ("light", "dark"):
            for fg, bg in theme.TEXT_PAIRS:
                r = theme.contrast(theme.TOKENS[mode][fg], theme.TOKENS[mode][bg])
                self.assertGreaterEqual(r, 4.5, f"{mode}: {fg} on {bg} = {r:.2f}")
    def test_decorative_exceptions_documented_and_never_text(self):
        # rose/mauve are decoration only: documented, ratios recorded but not enforced, and never used as text colour
        self.assertTrue({"accent", "muted", "subtle", "line"} <= set(theme.DECORATIVE_EXCEPTIONS))
        pages = [ROOT / "site/index.html"] + sorted((ROOT / "reports").rglob("index.html"))
        for pg in pages:
            css = re.search(r"<style>(.*?)</style>", pg.read_text(encoding="utf-8"), re.S).group(1)
            for tok in theme.DECORATIVE_EXCEPTIONS:
                self.assertNotRegex(css, r"(?<![-\w])color:var\(--%s\)" % tok, f"{pg.name}: --{tok} used as text colour")
    def test_palette_is_exactly_the_studio_palette(self):
        studio = {"#f3f1f6", "#fffcfe", "#473448", "#7d5a7c", "#a6a1a7", "#856a8e", "#fffafc", "#e4dde8",
                  "#473448", "#5a535c", "#f4eef3", "#cbbdce", "#a6a1a7", "#e8a8bc", "#2c262f", "#4a424c"}
        used = {v for m in theme.TOKENS.values() for v in m.values()} | set(theme.FIGURE_BG.values())
        self.assertEqual(used - studio, set())
    def test_contrast_formula_reference_values(self):
        self.assertAlmostEqual(theme.contrast("#000000", "#ffffff"), 21.0, places=2)
        self.assertAlmostEqual(theme.contrast("#777777", "#ffffff"), 4.48, places=2)
    def test_studio_tokens_unchanged(self):
        self.assertEqual(theme.TOKENS["dark"]["canvas"], "#473448"); self.assertEqual(theme.TOKENS["dark"]["ink"], "#f4eef3")
        self.assertEqual(theme.TOKENS["light"]["canvas"], "#f3f1f6"); self.assertEqual(theme.TOKENS["light"]["accent"], "#856a8e")
    def test_generated_page_has_both_themes_and_toggle(self):
        h = (ROOT / "site/index.html").read_text(encoding="utf-8")
        self.assertIn("prefers-color-scheme:dark", h); self.assertIn(".ilg-case[data-theme=dark]", h)
        self.assertIn(":not([data-theme=light])", h)
        self.assertIn('<button type="button" class="ilg-theme-toggle" aria-pressed="false" hidden>', h)
        self.assertIn("localStorage", h); self.assertNotIn("http", h.split("<main>")[0].replace("http://www.w3.org", ""))
        css = re.search(r"<style>(.*?)</style>", h, re.S).group(1); rest = css[len(theme.css(".ilg-case")):]
        self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,6}\b", rest), [], "page colours must come from theme tokens")



class Readme(unittest.TestCase):
    def test_readme_commands_block_in_sync(self):
        import json
        p = json.loads((ROOT / "site/project.json").read_text(encoding="utf-8")); t = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(export_site.render_readme_block(p), t)

class ReportPages(unittest.TestCase):
    def test_mock_report_has_visible_banner_and_real_report_does_not(self):
        m = (ROOT / "reports/mock/index.html").read_text(encoding="utf-8"); r = (ROOT / "reports/index.html").read_text(encoding="utf-8")
        self.assertIn("MOCK DATA - demonstrates the mechanism, not a result", m); self.assertNotIn("MOCK DATA", r)
        for h in (m, r): self.assertIn(".ilg-case[data-theme=dark]", h); self.assertIn("ilg-theme-toggle", h)
if __name__ == "__main__": unittest.main()
