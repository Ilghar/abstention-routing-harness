# Review of M01–M07

**Type: internal self-review (separate pass, not a human review), 2026-10-25. This is not an independent expert review.** The same team that built M01–M07 wrote this review, so it cannot replace a human reviewer.

## Method
- Fresh copy of `main` rebuilt from the GitHub tree, with every listed blob SHA-1 matching the local tree. The tree listing was truncated at 20 kB, so a few `tools/` files were not compared.
- Full test suite rerun under `PYTHONHASHSEED` = 0, 1 and 12345 with `-W error`, on Python 3.13.5 and, via uv, CPython 3.11.17.
- Every README command rerun. Outputs compared with the committed receipts, and reruns compared with each other to check determinism.
- Every `schemas/*.json` checked with `unsupported_keywords`. Fixtures, inputs and outputs validated against their schemas.
- Grep for leaked emails, tokens, box paths and identifiers. Checked whether blind packets expose item IDs. License notes re-read.

## Common findings
| ID | Severity | Finding | Fix |
|---|---|---|---|
| R-01 | medium | `docs/CASE_PAGE.md` was hand-written and stale against the M06/M07 results. `site/project.json` evidence text was stale too. | `tools/export_site.py` now generates CASE_PAGE.md and index.html from project.json. `tests/test_site.py` fails if either drifts. |
| R-00 | info | README says "Python >= 3.11", which was previously unverified. | Verified: the suite passes on CPython 3.11.17 and 3.13.5. |
| — | ok | The README numbers reproduce exactly. Slice outputs are byte-identical across reruns. No leaked emails, tokens or IDs. Blind packets carry no item IDs. All schemas use only supported keywords. | — |

## Project-specific findings
| ID | Severity | Finding | Fix |
|---|---|---|---|
| R-04 | low | Probe files (`ood_probes_m04`, `collection_v1/*_probes`) carried `known_limitation`, which `case.schema.json` did not allow (`additionalProperties: false`). Probes were therefore never schema-valid cases. | Added an optional `known_limitation` string to the schema. `tests/test_review.py` validates every probe once proposals are attached. |
| — | info | Three M03 fixture cases (B05, B06, B10) fail the schema on purpose as malformed-input cases. | none needed |
| — | info | Historical receipts (M03/M04) still match the current outputs exactly. | — |

## Not covered
No human listening, expert annotation or blind probe authoring took place. Milestone acceptance stays "internal review only".
