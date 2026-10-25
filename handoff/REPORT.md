# Handoff report — Abstention and routing evaluation harness

Owner: ilghar.studio coordinator
UTC timestamp: 2026-10-23T08:50:00Z
Repository: https://github.com/Ilghar/abstention-routing-harness (private), branch main; commit SHA recorded in portfolio/STATUS.json of repo01
Source inventory and rights: docs/SOURCES.md, inputs/source_register.jsonl
Accepted milestones: M01-M07 (internal review only)
Actual fraction: 7/10
Commands/tests: `PYTHONPATH=src python3 -m unittest discover -s tests -v`; receipt tests/receipts/m07_run.json
Implemented vs mocked vs planned: Cleared queue fixture (20 EN/DE) + 7 OOD/mixed probes -> local keyword proposer -> abstention policy -> decisions + report. Result 21/27 admitted, 20/21 correct, false acceptance 1/7 (P07). Rule tuned on same fixture: not held-out.
Known failures/blockers: Library search unavailable; no independent review yet
Budget: week1 3% used at 11:09 Berlin (user reading); pool vs Expert unknown
Drive mirror: see portfolio/HANDOFF.md
Next three actions: handoff/NEXT.md
Pending review/publication: license choice, public visibility (not requested)

## Review pass (2026-10-25)
Internal self-review (separate pass, not a human review). See `docs/REVIEW_M01_M07.md` for findings and fixes. Tests: `tests/receipts/review_run.json`. Milestone count unchanged (7/10).

## M08 (2026-10-25): blocked on CI
- Done and tested locally: a `pyproject.toml` with an in-tree stdlib build backend (no runtime or build dependencies), an offline `pip install --no-index .`, a byte-reproducible wheel, `docs/DEPENDENCIES.md`, and `examples/run.sh`, which checks outputs against `examples/expected.sha256` on CPython 3.11.17 and 3.13.5. Receipt: `tests/receipts/m08_run.json`.
- Blocked: focused CI. Actions billing (payment method, budget) could not be verified read-only, so the workflow is committed inactive under `docs/ci-proposed/`. No billing settings were touched.
- Milestones accepted: 7/10 (M08 `blocked`).
