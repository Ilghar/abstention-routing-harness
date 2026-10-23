from collections import Counter
def frac(n, d): return None if d == 0 else round(n / d, 6)
def evaluate(cases, decisions):
    exp = {c["id"]: c["expected_route"] for c in cases}
    adm = [d for d in decisions if not d["abstained"]]
    correct = sum(1 for d in adm if exp[d["case_id"]] == d["route"])
    human = [c["id"] for c in cases if c["expected_route"] == "human"]
    fa = sum(1 for d in adm if exp[d["case_id"]] == "human")
    conf = Counter(f'{exp[d["case_id"]]}->{d["route"]}' for d in decisions)
    return {"n_items": len(cases),
            "coverage": {"admitted": len(adm), "denominator": len(cases), "value": frac(len(adm), len(cases))},
            "selective_accuracy": {"correct": correct, "denominator": len(adm), "value": frac(correct, len(adm))},
            "false_acceptance": {"count": fa, "denominator": len(human), "value": frac(fa, len(human))},
            "confusion": dict(sorted(conf.items())),
            "disagreements": sum(1 for d in decisions if d["reason_code"] == "PROPOSALS_CONFLICT"),
            "reason_counts": dict(sorted(Counter(d["reason_code"] for d in decisions).items()))}
