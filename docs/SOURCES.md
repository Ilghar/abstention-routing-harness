# Source and access register (M01)

Machine-readable register: `inputs/source_register.jsonl`. This page separates **existing evidence** from **plans**.

## Existing evidence (historical, not re-run in this repository)
| ID | What | Status |
|---|---|---|
| S01/S02 | Reference policy `bounded_routing.py` + 4 mocked unittest tests (sha256 recorded) | Kept outside this repo; rights not reviewed. Reference only. |
| S03 | Narrow two-queue routing fixture, laya-multilingual @1720e3e: 19/20 (gate ≥18) | Historical summary only. |
| S04 | Broader version-ranking fixture, same model: **12/20, failed**, 1 false winner on unknown | Historical summary only. **Different task from S03.** |
| S05 | 20 synthetic EN/DE single-domain queue cases | Copied; synthetic. |
| S06 | Offline review: string `requests_used` → TypeError; NaN bypasses budget check; missing adapter import raises outside handler | Paraphrased; drives new validation requirements. |
| S07 | HF model locator | Reference, not ownership; not downloaded. |

**No controlled accuracy comparison exists.** S03 and S04 are different tasks, fixtures and gates; this repository must never present 19/20 vs 12/20 as an improvement, regression or model ranking.

## Access actually used (2026-10-23, Europe/Berlin)
- Google Drive handoff folder (project 01) read via connector: all listed files downloaded except `.DS_Store`.
- GitHub account `Ilghar` verified via connector; this repo created private.
- Grok Library / Projects / native chat search: **not available** on the executing surface (S08).
- No network inference, no model download, no Jev transport.

## Plans (not evidence)
Everything in `docs/PRODUCT_CONTRACT.md` acceptance criteria and `docs/ARCHITECTURE.md` is planned until code + test receipts exist.
