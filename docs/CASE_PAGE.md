# Abstention and routing evaluation harness

> How can a routing system abstain reliably on mixed, malformed, conflicting or out-of-domain requests without mistaking model confidence for authority?

**Status:** Measured rule baselines on synthetic cases; no model results. Private work in progress.

## Problem
How can a routing system abstain reliably on mixed, malformed, conflicting or out-of-domain requests without mistaking model confidence for authority?

## Existing contribution
Ilghar Dadgostari: problem framing, requirements and evaluation direction. Implementation AI-assisted (Grok Bot), reviewed only by Grok Bot so far.

## Architecture
See `architecture.mmd` (authoritative) and `architecture.svg` (fallback). Stages: Input record + independent scope label → Pure validation and advisory policy → Recorded or mocked model proposal adapter → Abstention + disagreement decision → Per-class confusion/coverage/error report → Human review queue

## Example
See README *Vertical slice* and `tests/receipts/`.

## Measured results
- keyword rule false acceptance (test): 5/12 = 0.417 (Wilson 95% 0.193–0.681) (measured, synthetic; test probes written by rule author; not blind)
- keyword rule selective accuracy (test): 6/11 = 0.545 (measured, synthetic; small n)
- keyword rule coverage (test): 11/24 = 0.458 (measured, synthetic; )
- keyword rule false acceptance (dev): 1/7 = 0.143 (measured, synthetic; rule developed on dev)
- majority-class false acceptance (test): 12/12 = 1.0 (measured baseline; )

## Limitations
- All items synthetic; no model was run.
- Test probes written by the same author after the rule existed (not blind).
- Historical laya-multilingual fixtures are summaries, not rerun, and measure different tasks.

## Next step
See `handoff/NEXT.md`.
