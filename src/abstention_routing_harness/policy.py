"""Pure, deterministic abstention policy. Advisory only; never moves documents."""
import hashlib, json, math, re, unicodedata
ROUTES = {"spreadsheet", "conversation"}
PERMITTED = {"synthetic", "approved-existing-text"}
MAX_PROPOSALS = 8  # M07: unbounded proposal lists rejected (schema maxItems)
ID_RX = re.compile(r"^[A-Z0-9_-]{1,32}$")

def _visible(t):
    """M07 fix: text made only of whitespace/format/control chars (ZWSP, ZWNJ, bidi overrides) is not content."""
    return any(unicodedata.category(ch)[0] not in "ZC" for ch in t)

def _utf8(t):
    try: t.encode("utf-8"); return True
    except UnicodeEncodeError: return False  # lone surrogates

def identity(text, model_id, revision, rubric):
    return hashlib.sha256(json.dumps([text, model_id, revision, rubric], ensure_ascii=False, separators=(",", ":")).encode("utf-8", "surrogatepass")).hexdigest()

def _out(case, route, code, rubric):
    props = case.get("proposals") or [{}] if isinstance(case, dict) else [{}]
    p0 = props[0] if isinstance(props, list) and props and isinstance(props[0], dict) else {}
    text = case.get("text") if isinstance(case, dict) and isinstance(case.get("text"), str) else ""
    return {"case_id": case["id"] if isinstance(case, dict) and isinstance(case.get("id"), str) and ID_RX.match(case["id"]) else "", "route": route,
            "abstained": route == "human", "reason_code": code,
            "identity": identity(text, str(p0.get("model_id", "")), str(p0.get("revision", "")), rubric),
            "advisory_only": True, "can_move_documents": False, "external_requests_allowed_now": 0}

def decide(case, rubric="rubric-v1"):
    h = lambda code: _out(case, "human", code, rubric)
    if not isinstance(case, dict): return h("TEXT_INVALID")
    if not isinstance(case.get("id"), str) or not ID_RX.match(case["id"]): return h("CASE_INVALID")
    t = case.get("text")
    if not isinstance(t, str) or len(t) > 2000 or not _utf8(t) or not _visible(t): return h("TEXT_INVALID")
    if case.get("scope_verified") is not True: return h("SCOPE_UNVERIFIED")
    if case.get("fixture_kind") not in PERMITTED: return h("INPUT_NOT_PERMITTED")
    u = case.get("requests_used")
    if isinstance(u, bool) or not isinstance(u, int) or u < 0:  # floats (incl. 1.0, NaN, inf) rejected: schema requires integer
        return h("BUDGET_INVALID")
    if u > 1: return h("BUDGET_EXCEEDED")
    props = case.get("proposals")
    if not isinstance(props, list) or not props: return h("NO_PROPOSAL")
    if len(props) > MAX_PROPOSALS: return h("PROPOSAL_MALFORMED")
    routes = []
    for p in props:
        r = p.get("route") if isinstance(p, dict) else None
        if r == "unknown": return h("PROPOSAL_ABSTAINED")
        if not isinstance(r, str) or r not in ROUTES: return h("PROPOSAL_MALFORMED")
        if not isinstance(p.get("model_id", ""), str) or not isinstance(p.get("revision", ""), str): return h("PROPOSAL_MALFORMED")
        routes.append(r)
    if len(set(routes)) > 1: return h("PROPOSALS_CONFLICT")
    return _out(case, routes[0], "ADMITTED_ADVISORY", rubric)
