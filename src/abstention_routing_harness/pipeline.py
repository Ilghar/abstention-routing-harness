"""M04 vertical slice: cleared queue fixture -> cases -> local rule proposer -> abstention policy -> report.
The rule proposer is a transparent keyword baseline written while looking at this fixture: NOT a held-out or model result."""
import hashlib, json, re
from .policy import decide
from .metrics import evaluate
LEX = {"spreadsheet": r"spreadsheet|workbook|formula|sheet|excel|cell|tabelle|formel|arbeitsmappe|tabellenbl",
       "conversation": r"conversation|chat|message|reply|thread|nachricht|antwort|gespr"}
RULE_ID, RULE_REV = "keyword-rule", hashlib.sha256(json.dumps(LEX, sort_keys=True).encode()).hexdigest()[:12]
def propose(text):
    hits = {k for k, rx in LEX.items() if re.search(rx, text.lower())}
    route = hits.pop() if len(hits) == 1 else "unknown"   # none or both domains -> abstain
    return {"source": "rule", "model_id": RULE_ID, "revision": RULE_REV, "route": route}
def ingest(pairs, prefix="Q"):
    cases = []
    for i, p in enumerate(pairs, 1):
        text, label = (p if isinstance(p, list) and len(p) == 2 else (None, "human"))
        cases.append({"id": f"{prefix}{i:02}", "text": text, "scope_verified": True, "fixture_kind": "synthetic",
                      "case_class": "in_scope" if label in ("spreadsheet", "conversation") else "out_of_domain",
                      "expected_route": label if label in ("spreadsheet", "conversation") else "human", "requests_used": 0})
    return cases
def run(pairs, probes=(), rubric="rubric-v1"):
    cases = ingest(pairs) + [dict(c) for c in probes]
    for c in cases: c["proposals"] = [propose(c["text"])] if isinstance(c.get("text"), str) else []
    decs = [decide(c, rubric) for c in cases]
    return cases, decs, evaluate(cases, decs)
