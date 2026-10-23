"""Pure, deterministic abstention policy. Advisory only; never moves documents."""
import hashlib, json, math
ROUTES = {"spreadsheet", "conversation"}
PERMITTED = {"synthetic", "approved-existing-text"}

def identity(text, model_id, revision, rubric):
    return hashlib.sha256(json.dumps([text, model_id, revision, rubric], ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()

def _out(case, route, code, rubric):
    props = case.get("proposals") or [{}] if isinstance(case, dict) else [{}]
    p0 = props[0] if isinstance(props, list) and props and isinstance(props[0], dict) else {}
    text = case.get("text") if isinstance(case, dict) and isinstance(case.get("text"), str) else ""
    return {"case_id": str(case.get("id", "")) if isinstance(case, dict) else "", "route": route,
            "abstained": route == "human", "reason_code": code,
            "identity": identity(text, str(p0.get("model_id", "")), str(p0.get("revision", "")), rubric),
            "advisory_only": True, "can_move_documents": False, "external_requests_allowed_now": 0}

def decide(case, rubric="rubric-v1"):
    h = lambda code: _out(case, "human", code, rubric)
    if not isinstance(case, dict): return h("TEXT_INVALID")
    t = case.get("text")
    if not isinstance(t, str) or not t.strip() or len(t) > 2000: return h("TEXT_INVALID")
    if case.get("scope_verified") is not True: return h("SCOPE_UNVERIFIED")
    if case.get("fixture_kind") not in PERMITTED: return h("INPUT_NOT_PERMITTED")
    u = case.get("requests_used")
    if isinstance(u, bool) or not isinstance(u, (int, float)) or (isinstance(u, float) and (math.isnan(u) or math.isinf(u) or u != int(u))) or u < 0:
        return h("BUDGET_INVALID")
    if u > 1: return h("BUDGET_EXCEEDED")
    props = case.get("proposals")
    if not isinstance(props, list) or not props: return h("NO_PROPOSAL")
    routes = []
    for p in props:
        r = p.get("route") if isinstance(p, dict) else None
        if r == "unknown": return h("PROPOSAL_ABSTAINED")
        if not isinstance(r, str) or r not in ROUTES: return h("PROPOSAL_MALFORMED")
        routes.append(r)
    if len(set(routes)) > 1: return h("PROPOSALS_CONFLICT")
    return _out(case, routes[0], "ADMITTED_ADVISORY", rubric)
