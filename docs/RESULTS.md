# Results (M06) — measured, synthetic only
Command: `PYTHONPATH=src python3 -m abstention_routing_harness baselines . --out out/m06` (receipt `tests/receipts/m06_baselines.json`).

| Split | Proposer | Coverage | Selective acc. | False acceptance |
|---|---|---|---|---|
| dev (27) | always_abstain | 0/27 | n/a | 0/7 |
| dev | majority_spreadsheet | 27/27 | 10/27 | 7/7 |
| dev | keyword_rule | 21/27 | 20/21 | 1/7 |
| test (24) | always_abstain | 0/24 | n/a | 0/12 |
| test | majority_spreadsheet | 24/24 | 6/24 | 12/12 |
| test | keyword_rule | 11/24 | 6/11 | 5/12 |

Reading: the rule's dev numbers do not transfer; on the vocabulary-shifted test set it abstains on most in-scope items and accepts 5 of 12 traps (bed *sheet*, *cell* phone, *Chat* GPT, *Tabelle* translation, film *message*). No gain over abstention is claimed; the harness exposes the failure. Wilson 95% intervals are in the receipt.
