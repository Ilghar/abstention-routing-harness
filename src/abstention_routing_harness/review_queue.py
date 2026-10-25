"""Human review queue: turn decisions.json into a readable, prioritised worklist for a person.

The harness never moves documents. Every abstention lands here with a plain-language reason,
so a reviewer can see *why* the system held back instead of a bare route label.
Usage: python -m abstention_routing_harness.review_queue decisions.json [--cases fixture.json] --out queue.md
"""
import argparse, json, pathlib, sys

EXPLAIN = {
    "SCOPE_UNVERIFIED": (1, "Nobody independently confirmed what kind of item this is, so no proposal may be trusted."),
    "INPUT_NOT_PERMITTED": (1, "The text asks to change permissions, authority or actions; that is never routed automatically."),
    "PROPOSALS_CONFLICT": (2, "The readers disagree. Disagreement is treated as evidence of ambiguity, not averaged away."),
    "PROPOSAL_ABSTAINED": (2, "The reader itself said it does not know (mixed, unclear or out of domain)."),
    "PROPOSAL_MALFORMED": (3, "The proposal was not valid structured output, so it was discarded rather than guessed at."),
    "NO_PROPOSAL": (3, "No reader produced a proposal for this item."),
    "TEXT_INVALID": (3, "The text is empty, invisible-only or otherwise unreadable."),
    "CASE_INVALID": (3, "The record itself failed validation."),
    "BUDGET_INVALID": (4, "The request budget was not a finite, non-negative integer."),
    "BUDGET_EXCEEDED": (4, "The request budget was used up; the harness stops instead of spending more."),
}
UNKNOWN = (5, "Unrecognised reason code; inspect manually.")

def build_queue(decisions, cases=None):
    text = {c.get("id"): c.get("text", "") for c in (cases or []) if isinstance(c, dict)}
    items = []
    for d in decisions:
        if not d.get("abstained"):
            continue
        prio, why = EXPLAIN.get(d.get("reason_code"), UNKNOWN)
        items.append({"case_id": d.get("case_id"), "reason_code": d.get("reason_code"), "priority": prio,
                      "why": why, "excerpt": (text.get(d.get("case_id")) or "")[:120]})
    items.sort(key=lambda i: (i["priority"], str(i["case_id"])))
    by_reason = {}
    for i in items:
        by_reason[i["reason_code"]] = by_reason.get(i["reason_code"], 0) + 1
    return {"n_decisions": len(decisions), "n_queued": len(items), "by_reason": dict(sorted(by_reason.items())), "items": items}

def render_md(q):
    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
    rows = "\n".join(f"| {i['priority']} | {esc(i['case_id'])} | `{i['reason_code']}` | {esc(i['why'])} | {esc(i['excerpt'])} |" for i in q["items"])
    return (f"# Human review queue\n\n{q['n_queued']} of {q['n_decisions']} items were held back for a person.\n\n"
            "| Priority | Case | Reason | Why it was held back | Excerpt |\n|---|---|---|---|---|\n" + rows + "\n")

def main(argv=None):
    ap = argparse.ArgumentParser(prog="abstention_routing_harness.review_queue")
    ap.add_argument("decisions"); ap.add_argument("--cases"); ap.add_argument("--out", required=True); a = ap.parse_args(argv)
    decs = json.loads(pathlib.Path(a.decisions).read_text(encoding="utf-8"))
    raw = json.loads(pathlib.Path(a.cases).read_text(encoding="utf-8")) if a.cases else None
    cases = raw.get("cases", []) if isinstance(raw, dict) else raw
    q = build_queue(decs, cases); out = pathlib.Path(a.out)
    out.write_text(render_md(q), encoding="utf-8"); out.with_suffix(".json").write_text(json.dumps(q, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"queued": q["n_queued"], "of": q["n_decisions"], "by_reason": q["by_reason"]})); return 0

if __name__ == "__main__":
    sys.exit(main())
