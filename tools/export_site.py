"""Export site/project.json -> site/index.html (static, no JS, no network, escaped text, reduced-motion safe) and
validate project.json against site/schema.json with the repo's stdlib validator. Accessibility is NOT claimed tested."""
import html, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
PKG = [p.name for p in (ROOT / "src").iterdir() if p.is_dir() and not p.name.startswith("_")][0]
validate = __import__(f"{PKG}.schema", fromlist=["validate"]).validate
CSS = """:root{color-scheme:light;--ink:#222;--muted:#666;--accent:#7a5c3e;--bg:#fbfaf7}
body{margin:0;background:var(--bg);color:var(--ink);font:1.05rem/1.6 Georgia,'Noto Naskh Arabic',serif}
main{max-width:46rem;margin:0 auto;padding:3rem 1.25rem}h1{font-size:2rem;line-height:1.2}h2{margin-top:2.5rem;color:var(--accent);font-size:1.15rem;text-transform:uppercase;letter-spacing:.06em}
.lede{font-size:1.2rem;color:var(--muted)}ol.flow{padding-left:1.25rem}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:.4rem;text-align:left;vertical-align:top}
.badge{display:inline-block;border:1px solid var(--accent);padding:0 .5rem;border-radius:1rem;font-size:.85rem}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}"""
def render(p):
    e = lambda s: html.escape(str(s), quote=True)
    rows = "".join(f"<tr><td>{e(r['metric'])}</td><td>{e(r['value'])}</td><td>{e(r['denominator'])}</td><td>{e(r['kind'])}</td><td>{e(r.get('caveat',''))}</td></tr>" for r in p["results"])
    flow = "".join(f"<li>{e(s)}</li>" for s in p["architecture"])
    lim = "".join(f"<li>{e(s)}</li>" for s in p.get("limitations", []))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(p['title'])}</title><style>{CSS}</style></head><body><main>
<p><span class="badge">{e(p['status'])}</span> <span class="badge">{e(p['evidence_level'])}</span></p>
<h1>{e(p['title'])}</h1><p class="lede">{e(p['summary'])}</p>
<h2>Workflow</h2><figure><ol class="flow">{flow}</ol><figcaption>Text equivalent of docs/architecture.mmd (authoritative diagram).</figcaption></figure>
<h2>Measured results</h2>{('<table><thead><tr><th scope=col>Metric</th><th scope=col>Value</th><th scope=col>Denominator</th><th scope=col>Kind</th><th scope=col>Caveat</th></tr></thead><tbody>' + rows + '</tbody></table>') if rows else '<p>No measured results yet.</p>'}
<h2>Limitations</h2><ul>{lim}</ul><h2>Contribution</h2><p>{e(p['contribution'])}</p>
</main></body></html>
"""
if __name__ == "__main__":
    p = json.loads((ROOT / "site/project.json").read_text(encoding="utf-8")); s = json.loads((ROOT / "site/schema.json").read_text(encoding="utf-8"))
    errs = validate(p, s)
    if errs: print(json.dumps({"valid": False, "errors": errs})); sys.exit(1)
    (ROOT / "site/index.html").write_text(render(p), encoding="utf-8"); print(json.dumps({"valid": True, "wrote": "site/index.html"}))
