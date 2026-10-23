# Collection v1 — datasheet
- Version 1.0.0; manifest built by `python -m abstention_routing_harness collection . --out DIR` (hashes, class counts, schema errors).
- dev: `dev_queue.json` (20 cleared Drive synthetic EN/DE pairs), `dev_probes.json` (7 Bot-written OOD/mixed probes).
- test: `heldout_probes.json` (24 Bot-written probes: vocabulary shift, mixed, homograph traps like "bed sheet"/"cell phone", injection).
- Historical summaries (`inputs/*_historical.json`) are listed as `historical_not_rerun`, outside all splits.
- Synthetic vs empirical: 0 empirical items. Labels author-assigned, unreviewed.
- Edge cases: malformed/budget/conflict gates live in `fixtures/synthetic_cases_m03.json` (unit level, deliberately schema-violating).
- Review: Bot only. Needed: a blind probe set written by Ilghar or Expert without seeing `pipeline.LEX`.
