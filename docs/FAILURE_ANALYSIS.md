# M07 failure analysis (Bot-authored, not independently reviewed)

Reproduce: `PYTHONPATH=src python3 -m abstention_routing_harness failure . --out out/m07` (receipt `tests/receipts/m07_failure.json`).

## 1. Adversarial / malformed inputs against `decide()`
34 deterministic cases in `src/abstention_routing_harness/failure.py` (`ADVERSARIAL`), each probing one precondition; every output is also validated against `schemas/decision.schema.json`.

| Policy version | Passed | Failures |
|---|---|---|
| M06 (commit 4d6c36e) | 24/34 | invisible-only text admitted (ZWSP/ZWNJ, bidi overrides, control chars); lone surrogate **crashed** (`UnicodeEncodeError` in identity hash); non-string / malformed `id` admitted; 9 agreeing proposals admitted (no cap); non-string `model_id` admitted |
| M07 | 34/34 | — |

Fixes: visible-character check (Unicode categories Z*/C* do not count), UTF-8 encodability check + `surrogatepass` in identity, `id` must match the schema pattern (new reason `CASE_INVALID`, added to decision schema), `MAX_PROPOSALS = 8` (schema `maxItems`), proposal `model_id`/`revision` must be strings. Regression tests: `tests/test_m07.py`. M06 baseline numbers are unchanged by the fixes (verified by diff).

## 2. Disagreement handling
Any conflict between proposals, or any `unknown` among agreeing proposals, abstains to human (`PROPOSALS_CONFLICT` / `PROPOSAL_ABSTAINED`); covered by adversarial rows `conflict_2`, `unknown_among_agree` and a dedicated test. No second real proposer exists yet, so agreement-based gains are **not** measured.

## 3. Held-out error analysis (keyword rule, test split n=24)
11 errors: 6 over-abstentions (vocabulary shift; no lexicon keyword — safe failure) and 5 false acceptances (H17, H18, H19, H23, H24), each triggered by a domain keyword inside an out-of-scope request (`cell`, `sheet`, `chat`, `tabelle`, `message`). Diagnosis: keyword presence ≠ intent.

Not fixed on purpose: patching the lexicon against these probes would tune on held-out data. The proposed fix is architectural (require an independent proposer to agree) and needs a new blind probe set to evaluate.
