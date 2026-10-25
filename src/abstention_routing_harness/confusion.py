"""Confusion report (expected vs decided route) and a static HTML report.

Labels: spreadsheet, conversation, human (= abstain). Counts are computed from
actual decisions on the given cases; no figure is invented. Cases without an
expected_route are counted as unlabelled and left out of the matrix.
"""
import html, json
LABELS = ["spreadsheet", "conversation", "human"]

def confusion(cases, decide_fn):
    m = {e: {d: 0 for d in LABELS} for e in LABELS}
    rows, unlabelled = [], 0
    for c in cases:
        d = decide_fn(c); exp = c.get("expected_route") if isinstance(c, dict) else None
        rows.append({"case_id": d["case_id"], "expected": exp, "decided": d["route"], "reason_code": d["reason_code"]})
        if exp not in LABELS: unlabelled += 1; continue
        m[exp][d["route"]] += 1
    n = sum(sum(r.values()) for r in m.values())
    correct = sum(m[l][l] for l in LABELS)
    per = {}
    for l in LABELS:
        tp = m[l][l]; pp = sum(m[e][l] for e in LABELS); ap = sum(m[l].values())
        per[l] = {"precision": round(tp / pp, 4) if pp else None, "recall": round(tp / ap, 4) if ap else None, "support": ap}
    wrong_answer = sum(m[e][d] for e in LABELS for d in LABELS[:2] if e != d)
    return {"labels": LABELS, "matrix": m, "n_labelled": n, "unlabelled": unlabelled,
            "accuracy": round(correct / n, 4) if n else None, "per_label": per,
            "wrong_answers": wrong_answer, "missed_abstentions": sum(m["human"][d] for d in LABELS[:2]),
            "over_abstentions": sum(m[e]["human"] for e in LABELS[:2]), "rows": rows}

CSS = ("body{font-family:Jost,system-ui,sans-serif;margin:3rem auto;max-width:60rem;color:#2b1d2f;background:#faf6f1}"
       "h1{font-weight:500;letter-spacing:-.01em}table{border-collapse:collapse;margin:1rem 0}"
       "td,th{border:1px solid #d9cfc5;padding:.4rem .7rem;text-align:right}th{background:#efe6dc}"
       "td.hit{background:#e3efe2}td.miss{background:#f6e0de}.note{color:#6b5b6e;font-size:.9rem}footer{margin-top:3rem;font-size:.85rem}")

def to_html(title, sections):
    """sections: list of (heading, confusion_dict). Returns a self-contained HTML page."""
    e = html.escape
    out = ["<!doctype html><html lang=en><meta charset=utf-8><title>%s</title><style>%s</style><h1>%s</h1>" % (e(title), CSS, e(title)),
           "<p class=note>Rows = expected route, columns = decided route. human = abstain / hand to a person. "
           "Computed from the deterministic policy on the listed fixtures; synthetic data, no gold human labels.</p>"]
    for head, c in sections:
        out.append("<h2>%s</h2><table><tr><th>expected \\ decided</th>%s</tr>" % (e(head), "".join("<th>%s</th>" % l for l in c["labels"])))
        for ex in c["labels"]:
            out.append("<tr><th>%s</th>%s</tr>" % (ex, "".join('<td class="%s">%d</td>' % ("hit" if ex == d else ("miss" if c["matrix"][ex][d] else ""), c["matrix"][ex][d]) for d in c["labels"])))
        out.append("</table><p>labelled %d · accuracy %s · wrong answers %d · missed abstentions %d · over-abstentions %d · unlabelled %d</p>"
                   % (c["n_labelled"], c["accuracy"], c["wrong_answers"], c["missed_abstentions"], c["over_abstentions"], c["unlabelled"]))
        out.append("<details><summary>per-case decisions</summary><table><tr><th>case</th><th>expected</th><th>decided</th><th>reason</th></tr>%s</table></details>"
                   % "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(e(str(r[k])) for k in ("case_id", "expected", "decided", "reason_code")) for r in c["rows"]))
    out.append("<footer>ilghar.studio</footer></html>")
    return "\n".join(out)
