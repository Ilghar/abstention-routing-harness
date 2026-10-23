# ADR 0001 — Scope and boundaries
Status: accepted (Bot self-review, 2026-10-23); independent review pending.

## Context
Historical reference policy works but has known edge-case bugs (S06) and couples to a specific model/transport. Two historical fixtures measure different tasks.

## Decision
- Write a new vendor-neutral, pure-stdlib core; do not copy or modify the reference code.
- Proposals come only from recorded/mock JSON in this phase; no model import, no Jev transport, no network.
- Every non-admitted path routes to human; decisions are advisory with immutable `can_move_documents: false`.
- False acceptance on `expected_route: human` is the primary metric; accuracy is selective and secondary.
- Never present S03 vs S04 as a comparison.

## Consequences
Real model quality stays unmeasured until a separately approved local run. The harness is reusable for any proposer that can emit recorded JSON.
