# Abstention and routing evaluation harness

**Status: work in progress (private). 6/10 milestones (Bot-reviewed); synthetic data only.**

- Product contract: `docs/PRODUCT_CONTRACT.md`
- Sources/evidence vs plans: `docs/SOURCES.md`
- Architecture/experiment plan: `docs/ARCHITECTURE.md`, ADR `docs/adr/0001-scope-and-boundaries.md`
- Handoff: `handoff/`

Contribution: Ilghar — problem framing, requirements, evaluation direction. Implementation AI-assisted (Grok Bot). License: not yet chosen.

## Quickstart (fresh environment)
Requires Python >= 3.11, no dependencies, no network.
```
git clone <this repo> && cd abstention-routing-harness
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m abstention_routing_harness run fixtures/synthetic_cases_m03.json --out out/
```
Modules: policy.py, metrics.py, cli.py. Fixture: 16 synthetic cases with hand-written mock proposals: coverage 6/16, selective accuracy 4/6, false acceptance 1/4 (mock data, not a model result). Receipts: `tests/receipts/`.

## Vertical slice (M04)
```
PYTHONPATH=src python3 -m abstention_routing_harness slice inputs/synthetic_queue_fixture.json --probes fixtures/ood_probes_m04.json --out out/m04
```
Cleared queue fixture (20 EN/DE) + 7 OOD/mixed probes -> local keyword proposer -> abstention policy -> decisions + report. Result 21/27 admitted, 20/21 correct, false acceptance 1/7 (P07). Rule tuned on same fixture: not held-out.
Review: `docs/REVIEW_M01_M03.md`.

## Collection and results
- Datasheet: `data/collection_v1/DATASHEET.md`
- Results: `docs/RESULTS.md`
- Case page: `docs/CASE_PAGE.md`; static page: `site/index.html` (`python3 tools/export_site.py`); diagram `docs/architecture.mmd` + `docs/architecture.svg`
- Schema validation in code: `src/abstention_routing_harness/schema.py` (stdlib subset)
