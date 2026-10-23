# Abstention and routing evaluation harness

**Status: work in progress (private). 3/10 milestones; minimal stdlib tool on synthetic/mock fixtures only — no measured model results.**

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
