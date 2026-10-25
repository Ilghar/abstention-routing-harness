# Original vision: what this project was meant to be

Sources read on 2026-10-25: the project package in Google Drive (the 2026-10-23 portfolio package folder `01_abstention-routing-harness`, `PROJECT_INDEX.json`, the text export `chat_exports/PROJECT_01.txt`) and the historical reference code it contains (`bounded_routing.py`, four mocked tests). Paraphrased, not copied.

## The original system
- An archive of mixed material had to be sent to **two technical review queues**: spreadsheets and conversations. Anything else (unrelated, ambiguous, mixed, or a request to change authority or permissions) had to become **unknown → human**.
- Two readers were planned: a **local multilingual reader** (laya-multilingual) proposing a queue, and a **second, independent reader** asked the same question. `reconcile()` admitted a route only when the scope was verified and both readers agreed; otherwise it went to a parent/human review.
- A stable **identity/cache contract**: the same text, model and rubric revision give the same identity; changing the model or rubric invalidates it.
- Strict **request budgets**, with zero external requests allowed by default, and the reader loaded only on explicit opt-in.
- The motivating evidence: on a broader 20-item historical fixture the local reader **failed 12/20, with one false winner on an unknown item**.

## The ambitious parts that were cut (and where they stand)
| Ambition | Status now |
|---|---|
| Real two-reader reconciliation (local reader + second reader) | Policy supports multiple proposals and abstains on any conflict; no real reader is run (offline, no inference). |
| Re-run the historical 20-item fixture with the local reader | Not done; summaries only. |
| Per-class confusion, coverage and false-acceptance reporting | Implemented. |
| Human review queue as the final stage | Implemented as `review_queue` (2026-10-25). |
| Calibration study before confidence is trusted | Not started; no calibration claim made. |
| Transport to the second reader | Deliberately not implemented in this phase. |
| Hardened budget handling (string, NaN, missing adapter crashes found in review) | Fixed and tested. |

## What must stay true
Advisory only; never moves documents. Text is data, not instructions. Mock and rule results are labelled. No metric without a denominator.
