"""M06: measured baselines with denominators and Wilson 95% intervals. All runs local and deterministic."""
import math
from .policy import decide
from .metrics import evaluate
from .pipeline import propose
def wilson(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]
PROPOSERS = {"always_abstain": lambda t: "unknown", "majority_spreadsheet": lambda t: "spreadsheet", "keyword_rule": lambda t: propose(t)["route"]}
def run_baselines(cases, rubric="rubric-v1"):
    out = {}
    for name, f in PROPOSERS.items():
        cs = [dict(c, proposals=[{"source": "rule", "model_id": name, "revision": "m06", "route": f(c["text"])}]) for c in cases]
        m = evaluate(cs, [decide(c, rubric) for c in cs])
        for k, num in (("coverage", "admitted"), ("selective_accuracy", "correct"), ("false_acceptance", "count")):
            m[k]["wilson95"] = wilson(m[k][num], m[k]["denominator"])
        out[name] = m
    return out
