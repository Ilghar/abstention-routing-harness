# Product contract (M01)

## User
An evaluator or maintainer of a small document-review routing step (e.g. "spreadsheet" vs "conversation" review queue) who needs to measure *when the system should refuse to route* — not only how often it routes correctly.

## Problem
Routing proposals (from a local model, a rule, or a recorded run) look authoritative. Mixed, malformed, conflicting, out-of-scope or budget-violating inputs must end in **abstention → human review**, and the evaluation must report coverage and false acceptance, not just accuracy.

## Bounded scope (this repository)
- Offline, deterministic Python CLI + library.
- Inputs: synthetic or approved-existing text records with an *independent* scope label, plus zero or more **recorded or mocked** proposals.
- Outputs: machine-readable decisions (JSONL) and a metrics report (JSON + Markdown).
- Stable identity hash over (text, model id/revision, rubric/question) so a model or rubric change invalidates cached decisions.

## Non-goals
- No external inference, no model download/loading in default paths, no Jev transport.
- No automatic document moves; decisions are advisory (`can_move_documents: false` always).
- No production decision authority; no calibration claim without a separate study.
- No claim comparing the historical narrow (19/20) and broader (12/20) fixtures.

## Acceptance criteria for the finished tool (planned)
1. Unknown, mixed-domain and out-of-scope items always abstain (0 false acceptances on those classes in the fixture).
2. Missing/malformed proposals and malformed budgets (string, NaN, negative, bool, >limit) → human review, never exceptions.
3. Unverified scope prevents admission.
4. Conflicting proposals abstain and are counted as disagreements.
5. Identity changes when model revision or rubric changes; unchanged otherwise.
6. Report contains coverage, selective accuracy (null if none admitted), false-acceptance count/rate with denominators, per-class confusion and disagreement counts.
7. Runs with no network; test receipts saved under `tests/receipts/`.

## Data rights and gaps
- Only synthetic fixtures (S05 and new cases written for this repo) enter the repository; historical run summaries are allowlisted summaries.
- Reference code (S01/S02) stays outside the repo until a rights decision; the new core is written independently.
- No license chosen yet (do not assume MIT/Apache); decided at M10 review.
- Gap: S05 has no unknown/mixed/malformed cases — new synthetic cases required (M03/M05).

## Contribution
Ilghar: problem framing, safety requirements, evaluation direction, historical fixtures. Implementation in this repo: AI-assisted (Grok Bot), attributed per commit.
