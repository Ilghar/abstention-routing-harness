"""Export site/project.json -> site/index.html and docs/CASE_PAGE.md.

Static, no JS, no network, every value escaped, CSS scoped under .ilg-case so the page can be embedded
in the ilghar.studio React site without leaking styles. Tokens mirror the studio's styles.css
(see site/DESIGN_TOKENS.json). Reduced motion honoured. Accessibility is NOT claimed tested."""
import html, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
PKG = [p.name for p in (ROOT / "src").iterdir() if p.is_dir() and not p.name.startswith("_")][0]
validate = __import__(f"{PKG}.schema", fromlist=["validate"]).validate
CSS = """.ilg-case{--canvas:#f3f1f6;--surface:#fffcfe;--ink:#4a3a5c;--muted:#7a688c;--subtle:#a394ae;--accent:#c97a98;--accent-fg:#fffafc;--line:#e4dde8;
--shadow-frame:inset 0 1px 0 rgba(255,255,255,.98),inset 0 -1px 0 rgba(74,58,92,.05),0 2px 3px rgba(74,58,92,.06),0 10px 18px rgba(74,58,92,.1),0 28px 44px -8px rgba(74,58,92,.22);
--shadow-plate:0 1px 0 rgba(255,255,255,.7),0 6px 18px rgba(74,58,92,.1);--ease-out:cubic-bezier(.22,1,.36,1);
font-family:"Jost","Avenir Next","Avenir","Helvetica Neue",Helvetica,Arial,"Vazirmatn","Noto Naskh Arabic",sans-serif;font-weight:400;color:var(--ink);background:var(--canvas);
-webkit-font-smoothing:antialiased;line-height:1.6;font-size:1.0625rem}
@media (prefers-color-scheme:dark){.ilg-case{--canvas:#4a434c;--surface:#5a535c;--ink:#f4eef3;--muted:#cbbdce;--subtle:#9a8a9c;--accent:#e8a8bc;--accent-fg:#2c262f;--line:#4a424c;
--shadow-frame:inset 0 1px 0 rgba(255,255,255,.1),0 2px 4px rgba(0,0,0,.25),0 16px 32px -8px rgba(0,0,0,.45);--shadow-plate:0 1px 0 rgba(255,255,255,.08),0 8px 20px rgba(0,0,0,.28)}}
body{margin:0;background:#f3f1f6}.ilg-case *{box-sizing:border-box}
.ilg-case main{max-width:72rem;margin:0 auto;padding:clamp(1.5rem,4vw,4rem) clamp(1rem,4vw,3rem);display:grid;grid-template-columns:repeat(12,minmax(0,1fr));column-gap:1.5rem}
.ilg-case main>*{grid-column:1/-1}.ilg-case .col{grid-column:1/-1}@media (min-width:60rem){.ilg-case .col{grid-column:3/11}}
.ilg-case h1,.ilg-case h2,.ilg-case h3{font-family:"Nunito Sans","Jost","Avenir Next",sans-serif;font-weight:700;text-wrap:balance;letter-spacing:-.01em;margin:0}
.ilg-case h1{font-size:clamp(2.2rem,5vw,3.6rem);line-height:1.05;margin:.5rem 0 1rem}
.ilg-case h2{font-size:.8rem;text-transform:uppercase;letter-spacing:.14em;color:var(--accent);margin:4rem 0 1rem}
.ilg-case h3{font-size:1.15rem;margin:0 0 .35rem}.ilg-case p{text-wrap:pretty;margin:.5rem 0}
.ilg-case .kicker{font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.ilg-case .pitch{font-size:clamp(1.2rem,2.2vw,1.5rem);font-weight:300;color:var(--ink);max-width:40rem}
.ilg-case .meta{color:var(--muted);font-size:.95rem}
.ilg-case .badge{display:inline-block;border:1px solid var(--accent);color:var(--ink);padding:.05rem .65rem;border-radius:1rem;font-size:.8rem;margin:0 .35rem .35rem 0}
.ilg-case figure{margin:2rem 0}.ilg-case figure img{width:100%;height:auto;display:block;border-radius:14px;box-shadow:var(--shadow-frame);background:var(--surface)}
.ilg-case figcaption{font-size:.85rem;color:var(--muted);margin-top:.75rem}
.ilg-case .cards{display:grid;gap:1.25rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr))}
.ilg-case .card{background:var(--surface);border-radius:14px;padding:1.25rem 1.35rem;box-shadow:var(--shadow-plate)}
.ilg-case .step{counter-increment:s}.ilg-case .steps{counter-reset:s}.ilg-case .step h3::before{content:counter(s,decimal-leading-zero) "  ";color:var(--accent)}
.ilg-case pre{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:1rem;overflow:auto;font:.85rem/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;word-break:break-word}
.ilg-case code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.9em}
.ilg-case table{border-collapse:collapse;width:100%;font-size:.95rem}.ilg-case td,.ilg-case th{border-bottom:1px solid var(--line);padding:.55rem .4rem;text-align:start;vertical-align:top}
.ilg-case th{font-weight:600;color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.08em}
.ilg-case ul{padding-inline-start:1.2rem}.ilg-case li{margin:.3rem 0}.ilg-case footer{margin-top:5rem;color:var(--muted);font-size:.9rem;border-top:1px solid var(--line);padding-top:1.5rem}
.ilg-case ::selection{background:color-mix(in oklab,var(--accent) 38%,transparent)}
@media (prefers-reduced-motion:reduce){.ilg-case *{animation:none!important;transition:none!important;scroll-behavior:auto!important}}"""

def render(p):
    e = lambda s: html.escape(str(s), quote=True)
    fig = lambda a: f'<figure><img src="{e(a["src"])}" alt="{e(a["alt"])}" width="{e(a.get("width",1280))}" height="{e(a.get("height",720))}" loading="lazy"><figcaption>{e(a.get("caption",""))}</figcaption></figure>' if a else ""
    hero = p.get("hero"); figs = {f["id"]: f for f in p.get("figures", [])}
    paras = lambda xs: "".join(f"<p>{e(x)}</p>" for x in xs)
    rows = "".join(f"<tr><td>{e(r['metric'])}</td><td>{e(r['value'])}</td><td>{e(r['denominator'])}</td><td>{e(r['kind'])}</td><td>{e(r.get('caveat',''))}</td></tr>" for r in p["results"])
    flow = "".join(f"<li>{e(s)}</li>" for s in p["architecture"])
    steps = "".join(f'<div class="card step"><h3>{e(s["title"])}</h3><p>{e(s["body"])}</p></div>' for s in p.get("how", []))
    who = "".join(f'<div class="card"><h3>{e(a["who"])}</h3><p>{e(a["why"])}</p></div>' for a in p.get("audience", []))
    cmds = "".join(f'<h3><code>{e(c["cmd"])}</code></h3><p>{e(c["what"])}</p><pre>{e(c["output"])}</pre>' for c in p.get("commands", []))
    sch = "".join(f"<tr><td><code>{e(s['path'])}</code></td><td>{e(s['what'])}</td></tr>" for s in p.get("schemas", []))
    road = "".join(f"<tr><td>{e(r['item'])}</td><td>{e(r['status'])}</td><td>{e(r['origin'])}</td></tr>" for r in p.get("roadmap", []))
    lim = "".join(f"<li>{e(s)}</li>" for s in p.get("limitations", []))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(p['title'])} · ilghar.studio</title><style>{CSS}</style></head><body><div class="ilg-case"><main>
<header class="col"><p class="kicker">ilghar.studio · case study</p><h1>{e(p['title'])}</h1><p class="pitch">{e(p.get('pitch', p['summary']))}</p>
<p><span class="badge">{e(p['status'])}</span><span class="badge">{e(p['evidence_level'])}</span></p></header>
{fig(hero)}
<section class="col"><h2>The question</h2><p class="pitch">{e(p['summary'])}</p>{paras(p.get('problem', []))}</section>
{('<section><h2>Who it is for</h2><div class="cards">' + who + '</div></section>') if who else ''}
<section><h2>How it works</h2><div class="cards steps">{steps}</div>
<figure><ol>{flow}</ol><figcaption>Text equivalent of docs/architecture.mmd (authoritative diagram).</figcaption></figure></section>
{fig(figs.get('second'))}
{('<section class="col"><h2>Commands, with real output</h2>' + cmds + '</section>') if cmds else ''}
<section class="col"><h2>Measured results</h2>{('<table><thead><tr><th scope=col>Metric</th><th scope=col>Value</th><th scope=col>n</th><th scope=col>Kind</th><th scope=col>Caveat</th></tr></thead><tbody>' + rows + '</tbody></table>') if rows else '<p>No measured results yet.</p>'}</section>
{('<section class="col"><h2>Schemas</h2><table><tbody>' + sch + '</tbody></table></section>') if sch else ''}
<section class="col"><h2>Limitations</h2><ul>{lim}</ul></section>
{('<section class="col"><h2>Roadmap: the original ambition</h2><table><thead><tr><th scope=col>Next</th><th scope=col>Status</th><th scope=col>Where it comes from</th></tr></thead><tbody>' + road + '</tbody></table></section>') if road else ''}
<footer class="col">{e(p['contribution'])}</footer>
</main></div></body></html>
"""

def render_md(p):
    """docs/CASE_PAGE.md is generated from the same project.json so the page, HTML and README claims cannot drift."""
    res = "\n".join(f"| {r['metric']} | {r['value']} | {r['kind']} | {r.get('caveat','')} |" for r in p["results"])
    lim = "\n".join(f"- {s}" for s in p.get("limitations", []))
    hero = p.get("hero"); figs = {f["id"]: f for f in p.get("figures", [])}
    img = lambda a: f"![{a['alt']}]({a['src']})\n\n*{a.get('caption','')}*\n\n" if a else ""
    how = "\n".join(f"{i}. **{s['title']}.** {s['body']}" for i, s in enumerate(p.get("how", []), 1))
    who = "\n".join(f"- **{a['who']}:** {a['why']}" for a in p.get("audience", []))
    cmds = "\n\n".join(f"### `{c['cmd']}`\n{c['what']}\n\n```\n{c['output']}\n```" for c in p.get("commands", []))
    road = "\n".join(f"| {r['item']} | {r['status']} | {r['origin']} |" for r in p.get("roadmap", []))
    return (f"# {p['title']}\n\n**{p.get('pitch', p['summary'])}**\n\n{img(hero)}"
            f"## The question\n> {p['summary']}\n\n" + "\n\n".join(p.get("problem", [])) + "\n\n"
            + (f"## Who it is for\n{who}\n\n" if who else "")
            + f"## How it works\n{how}\n\nStages (see `architecture.mmd`, authoritative, and `architecture.svg`): {' → '.join(p['architecture'])}\n\n"
            + img(figs.get("second"))
            + (f"## Commands, with real output\n{cmds}\n\n" if cmds else "")
            + f"## Measured results\n| Metric | Value | Kind | Caveat |\n|---|---|---|---|\n{res}\n\n**Status:** {p['evidence_level']}. Private work in progress.\n\n"
            + f"## Limitations\n{lim}\n\n"
            + (f"## Roadmap: the original ambition\n| Next | Status | Where it comes from |\n|---|---|---|\n{road}\n\n" if road else "")
            + f"## Credit\n{p['contribution']}\n\n"
            "_Generated by `tools/export_site.py` from `site/project.json`; do not edit by hand._\n")

if __name__ == "__main__":
    p = json.loads((ROOT / "site/project.json").read_text(encoding="utf-8")); s = json.loads((ROOT / "site/schema.json").read_text(encoding="utf-8"))
    errs = validate(p, s)
    if errs: print(json.dumps({"valid": False, "errors": errs})); sys.exit(1)
    (ROOT / "site/index.html").write_text(render(p), encoding="utf-8"); (ROOT / "docs/CASE_PAGE.md").write_text(render_md(p), encoding="utf-8")
    print(json.dumps({"valid": True, "wrote": ["site/index.html", "docs/CASE_PAGE.md"]}))
