# Architecture and experiment plan (M02)

Diagram: `docs/architecture.mmd`. Decision record: `docs/adr/0001-scope-and-boundaries.md`.

## Modules (`src/abstention_routing_harness/`, planned M03)
| Module | Responsibility | Side effects |
|---|---|---|
| `schema.py` | Load + validate cases (stdlib checks mirroring `schemas/*.json`) | none |
| `policy.py` | Pure `decide(case, rubric) -> Decision`; ordered gates below | none |
| `identity.py` | sha256 over canonical JSON `[text, model_id, revision, rubric]` | none |
| `adapters.py` | Read **recorded/mock** proposals from JSON only; no import of model packages | file read |
| `metrics.py` | Coverage, selective accuracy, false acceptance, confusion, disagreement | none |
| `cli.py` | `python -m abstention_routing_harness run FIXTURE --out DIR` | writes DIR |

## Decision gates (first failing gate wins → `route: human`)
1. text not str / empty / >2000 → `TEXT_INVALID`
2. `scope_verified` not exactly `True` → `SCOPE_UNVERIFIED`
3. `fixture_kind` not synthetic/approved → `INPUT_NOT_PERMITTED`
4. `requests_used` not a finite non-negative int (rejects bool, str, float, NaN) → `BUDGET_INVALID`; >1 → `BUDGET_EXCEEDED`
5. no proposals → `NO_PROPOSAL`; any route outside the enum → `PROPOSAL_MALFORMED`; any `unknown` → `PROPOSAL_ABSTAINED`
6. proposals disagree → `PROPOSALS_CONFLICT` (counted as disagreement)
7. else `ADMITTED_ADVISORY` with the agreed route; still `advisory_only`, `can_move_documents: false`.

Mixed-domain and out-of-domain cases are labelled `expected_route: human`; if a proposal routes them, that is a **false acceptance**, the headline safety metric.

## Failure cases to cover (from S06 + TEST_PLAN)
string/NaN/bool/negative budget; missing proposal; malformed route (`"delete"`, dict, `""`); unknown; conflict; unverified scope; unapproved input; overlong text; model revision change; rubric change; mixed EN/DE domain markers; out-of-domain request ("weather tomorrow"); permission-escalation text.

## Metrics (denominators always reported)
coverage = admitted/all; selective accuracy = correct admitted/admitted (null if 0); false acceptance = admitted with expected human / items with expected human; per-class confusion; disagreement count; reason-code histogram. No calibration claim.

## Deterministic test strategy
stdlib `unittest` only; fixtures are committed JSON with recorded sha256; output sorted, canonical JSON; no clock/random in outputs except receipt metadata; receipts in `tests/receipts/` record command, UTC time, Python version, exit code, fixture hash.

## Dependencies
Python ≥3.11 standard library only. No network. Optional future local-model adapter is out of scope until rights + budget review.

## License / consent plan
New code is original (not copied from S01). Fixtures: synthetic only. Repo license undecided until M10; historical summaries keep their "historical, not rerun" label.

## Review
Self-review by Grok Bot on 2026-10-23 against MILESTONES M02 and TEST_PLAN; independent (Expert/Codex) review pending.
