"""M07: failure analysis + deterministic adversarial suite. Findings are about this rule/policy only."""
import json, re
from .policy import decide, MAX_PROPOSALS
from .pipeline import propose, LEX
from .schema import validate, load_schema
BASE = {"id": "ADV", "text": "Fix the formula in cell B2", "scope_verified": True, "fixture_kind": "synthetic", "requests_used": 0,
        "proposals": [{"source": "rule", "model_id": "m", "revision": "r", "route": "spreadsheet"}]}
P = lambda *rs: [{"source": "rule", "model_id": "m", "revision": "r", "route": r} for r in rs]
# (name, mutation, must_abstain). Each was written to probe one precondition of decide().
ADVERSARIAL = [
    ("clean_control", {}, False), ("zwsp_only_text", {"text": "\u200b\u200c"}, True), ("bidi_override_only", {"text": "\u202e\u2066\u2069"}, True),
    ("nbsp_only", {"text": "\u00a0\u3000"}, True), ("control_only", {"text": "\x00\x07"}, True), ("lone_surrogate", {"text": "\ud800 cell"}, True),
    ("text_2000_ok", {"text": "cell " + "a" * 1995}, False), ("text_2001", {"text": "a" * 2001}, True), ("text_bytes", {"text": b"cell"}, True),
    ("id_dict", {"id": {"a": 1}}, True), ("id_lowercase", {"id": "x1"}, True), ("id_33", {"id": "A" * 33}, True), ("id_missing", {"id": None}, True),
    ("scope_string_true", {"scope_verified": "true"}, True), ("scope_int_1", {"scope_verified": 1}, True), ("fixture_unapproved", {"fixture_kind": "unapproved"}, True),
    ("used_bool", {"requests_used": True}, True), ("used_float", {"requests_used": 0.0}, True), ("used_nan", {"requests_used": float("nan")}, True),
    ("used_neg", {"requests_used": -1}, True), ("used_2", {"requests_used": 2}, True), ("used_huge", {"requests_used": 10 ** 30}, True),
    ("props_tuple", {"proposals": ("x",)}, True), ("props_none_item", {"proposals": [None]}, True), ("props_dict", {"proposals": {"route": "spreadsheet"}}, True),
    ("props_9_agree", {"proposals": P(*["spreadsheet"] * (MAX_PROPOSALS + 1))}, True), ("props_8_agree", {"proposals": P(*["spreadsheet"] * MAX_PROPOSALS)}, False),
    ("route_case", {"proposals": P("Spreadsheet")}, True), ("route_space", {"proposals": P("spreadsheet ")}, True), ("route_human_direct", {"proposals": P("human")}, True),
    ("model_id_obj", {"proposals": [{"source": "rule", "model_id": {"x": 1}, "revision": "r", "route": "spreadsheet"}]}, True),
    ("conflict_2", {"proposals": P("spreadsheet", "conversation")}, True), ("unknown_among_agree", {"proposals": P("spreadsheet", "unknown", "spreadsheet")}, True),
    ("not_a_dict", None, True)]
def run_adversarial():
    sch = load_schema(__import__("pathlib").Path(__file__).resolve().parents[2], "decision.schema.json"); rows = []
    for name, mut, must in ADVERSARIAL:
        case = None if mut is None else dict(BASE, **mut)
        try: d = decide(case); err = None
        except Exception as e: d, err = None, f"{type(e).__name__}: {e}"
        ok = d is not None and d["abstained"] == must and not validate(d, sch)
        rows.append({"name": name, "must_abstain": must, "reason_code": d and d["reason_code"], "exception": err, "pass": ok})
    return {"n": len(rows), "passed": sum(r["pass"] for r in rows), "rows": rows}
def _kw(text): return {k: re.findall(rx, text.lower()) for k, rx in LEX.items()}
def analyze(cases):
    """Categorize every keyword-rule error on the given cases (no tuning: the rule is unchanged)."""
    errs = []
    for c in cases:
        p = propose(c["text"]); d = decide(dict(c, proposals=[p])); exp = c["expected_route"]
        if d["route"] == exp: continue
        kind = "false_acceptance" if exp == "human" else ("misroute" if not d["abstained"] else "over_abstention")
        errs.append({"id": c["id"], "case_class": c.get("case_class"), "expected": exp, "got": d["route"], "kind": kind, "keyword_hits": {k: v for k, v in _kw(c["text"]).items() if v}})
    by = {}
    for e in errs: by[e["kind"]] = by.get(e["kind"], 0) + 1
    return {"n_cases": len(cases), "n_errors": len(errs), "by_kind": by, "errors": errs,
            "diagnosis": "Over-abstentions are vocabulary shift (no lexicon keyword; safe failure). False acceptances share one pattern: a domain keyword appears in a request whose intent is out of scope (keyword presence != intent). Fixing this inside the keyword rule would tune on held-out data, so it is NOT done; the fix is architectural (require an independent second proposer to agree)."}
