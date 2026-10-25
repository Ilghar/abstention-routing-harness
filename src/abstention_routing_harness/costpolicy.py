"""Cost/risk-aware multi-route policy with threshold calibration.

Layered on top of policy.decide(): every hard safety gate (scope, budget,
permitted input, malformed proposals) still forces the human route. Only cases
the base policy admits are re-scored here.

Support for a route = weighted share of proposals naming it (weight = the
proposal's optional "confidence" in [0,1], default 1.0). Expected cost of
answering on route r = (1 - support_r) * error_cost[r]; abstaining costs
abstain_cost. The policy answers on the cheapest route only when its support
reaches min_support and its expected cost is below abstain_cost.

calibrate() sweeps min_support over a labelled set and picks the value with
the lowest total realised cost. It is in-sample: report it as a fit, not as
held-out performance. Advisory only; never moves documents.
"""
import math
from .policy import decide, ROUTES

DEFAULT_COSTS = {"error_cost": {"spreadsheet": 1.0, "conversation": 1.0}, "abstain_cost": 0.3}
GRID = [round(i / 20, 2) for i in range(21)]

def _check_costs(costs):
    ec, ac = costs.get("error_cost"), costs.get("abstain_cost")
    if not isinstance(ec, dict) or set(ec) != ROUTES: raise ValueError("error_cost must cover exactly %s" % sorted(ROUTES))
    for v in list(ec.values()) + [ac]:
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
            raise ValueError("costs must be finite, non-negative numbers")

def support(proposals):
    tot, per = 0.0, {r: 0.0 for r in ROUTES}
    for p in proposals:
        c = p.get("confidence", 1.0)
        if isinstance(c, bool) or not isinstance(c, (int, float)) or not math.isfinite(c) or not 0 <= c <= 1:
            return None
        per[p["route"]] += c; tot += 1.0
    return {r: (v / tot if tot else 0.0) for r, v in per.items()}

def decide_cost(case, costs=None, min_support=0.5, rubric="rubric-v1"):
    costs = costs or DEFAULT_COSTS
    _check_costs(costs)
    if not (0 <= min_support <= 1): raise ValueError("min_support must be in [0,1]")
    # Base gates, but allow conflicting proposals through to scoring.
    base = decide(case, rubric)
    if base["route"] == "human" and base["reason_code"] != "PROPOSALS_CONFLICT":
        return dict(base, expected_cost=costs["abstain_cost"], support=None)
    s = support(case["proposals"])
    if s is None:
        return dict(base, route="human", abstained=True, reason_code="CONFIDENCE_INVALID", expected_cost=costs["abstain_cost"], support=None)
    exp = {r: (1 - s[r]) * costs["error_cost"][r] for r in ROUTES}
    best = min(sorted(ROUTES), key=lambda r: exp[r])
    if s[best] < min_support: code, route = "SUPPORT_BELOW_THRESHOLD", "human"
    elif exp[best] >= costs["abstain_cost"]: code, route = "RISK_ABOVE_ABSTAIN_COST", "human"
    else: code, route = "ADMITTED_COST", best
    return dict(base, route=route, abstained=route == "human", reason_code=code,
                expected_cost=round(exp[best] if route != "human" else costs["abstain_cost"], 6),
                support={k: round(v, 6) for k, v in s.items()})

def realised_cost(route, expected_route, costs):
    if route == "human": return 0.0 if expected_route == "human" else costs["abstain_cost"]
    return 0.0 if route == expected_route else costs["error_cost"][route]

def calibrate(cases, costs=None, grid=GRID):
    costs = costs or DEFAULT_COSTS
    _check_costs(costs)
    rows = []
    for t in grid:
        tot = sum(realised_cost(decide_cost(c, costs, t)["route"], c.get("expected_route"), costs) for c in cases)
        rows.append({"min_support": t, "total_cost": round(tot, 6)})
    best = min(rows, key=lambda r: (r["total_cost"], -r["min_support"]))  # ties -> stricter threshold
    return {"best_min_support": best["min_support"], "best_total_cost": best["total_cost"], "sweep": rows,
            "n_cases": len(cases), "in_sample": True, "costs": costs}
