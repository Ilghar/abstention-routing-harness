# Notes for Grok chat (Expert) and Grok Imagine

Searched Drive copies of inputs/, docs/, assets/, site/, common/ (2026-10-23). No standalone Expert prompt file exists in this project folder; `common/GROK_CAPABILITIES.md` mentions "both prompts", which were not supplied here.

Applies to Expert (recorded, not executed by Bot):
- EXECUTION_CONTRACT: Expert must see `handoff/STATE.json` lease `released` (or an explicit release report) before writing. **Lease is currently active (Grok Bot).**
- Expert cannot use Bot tools/memory; continue from repo files + Drive `outputs/current/MANIFEST_*.json` only.
- If pools are shared, Expert is a continuation interface, not extra budget (pool relationship unknown).
- Useful Expert tasks: independent review of M01–M06; writing a blind held-out probe/case set; native Persian review (P03).

Applies to Grok Imagine:
- `assets/IMAGE_PROMPT.md`: one editorial 3:2 image, at most one targeted correction, no tiny text/claimed results; native labels authoritative; record provenance + alt text in `assets/ASSETS.json`. **Not executed** pending user decision.
