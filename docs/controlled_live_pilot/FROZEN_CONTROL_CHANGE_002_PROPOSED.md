# Frozen-control change record 002 — PROPOSED (pre-change; NOT implemented; awaiting human disposition)

| | |
|---|---|
| Date | 2026-10-28 |
| Status | **PROPOSED — no frozen-control file has been modified for this record** |
| Trigger | Backend Completion Package, Workstream A: "If a reproducible Critical/Material failure remains, stop and request only a narrowly described safety change with pre-change record; no further scope until disposition." |
| Baseline | HEAD `11bd220` (includes `af6f61f` proposal, `3466a03` implementation of change 001) |
| Classification | Targeted completion of change 001's own safeguard; not an architecture change |

## 1. The reproduced failure (my own change 001 is incomplete)

`CapitalDecisionFacade._verify_funded_freshness` measures run age, the latest completed XNYS session and the Treasury window against the
**caller-supplied `created_at`**. A direct caller that states a `created_at` close to the Stage 7 run, together with evidence copied from that
run, passes every check. Reproduced at `11bd220` (`atlas_ui/evidence/probe_backdated_created_at.py`, output
`EVIDENCE_BACKDATED_CREATED_AT_at_11bd220.txt`): an **8-day-old eligible run was ACCEPTED by the facade, one funded ledger row written**.
Strict-xfail regression: `tests/test_funded_freshness_boundaries.py::test_a_direct_caller_cannot_backdate_created_at_to_defeat_the_staleness_safeguard`.
The UI path is not affected (its own gate uses the real clock and the Gate B bind), which is why the existing UI tests did not show it.
Everything else in change 001 reproduced as designed: omitted/wrong-typed evidence, $100→$130, changed provider/instrument/currency/key,
Treasury mismatch, old-format and tampered artifacts all reject with a byte-identical ledger; calendar boundaries behave correctly
(one second before the next close accepted, at the close rejected); HOLD CASH / DO NOTHING unaffected.

## 2. Proposed change (smallest that closes it)

`capital_decision_facade.py` only:
1. `CapitalDecisionFacade.__init__(..., clock: Callable[[], datetime] | None = None)`; default is the system UTC clock. The clock is not a
   per-call argument, so a caller cannot choose "now".
2. In `_verify_funded_freshness`, "now" is `self._clock()` for the age check, the session authority and the Treasury window (instead of
   `created_at`).
3. For INITIATE/ADD, additionally require `|created_at − self._clock()| ≤ 5 minutes`, so the ledger timestamp of a funded record is
   truthful. Non-actions are untouched.

Nothing else: no change to `stock_atlas/`, `controls.py`, `decision_store.py`, `pipeline.py`, models, methodology, Stage 7 eligibility or
Human Stage 8 authority; no new provider, FX, agent, optimizer or scoring.

## 3. Impact

- Production behaviour: a funded decision recorded more than 96 h after its run, or after a newer XNYS session has completed, is refused
  **regardless of what the caller passes**. A caller that copies the frozen evidence can no longer defeat staleness; the residual trust
  boundary shrinks to same-session price corrections, which only the Gate B bind can detect.
- Tests: facades built in fixture tests that record funded decisions at fixed fixture times (`NOW = 2026-09-02T21:00Z`) must be constructed with
  `clock=lambda: NOW`; UI tests pass the clock the UI already uses. The strict-xfail test above becomes a normal passing test.
- Operational: the UI constructs the facade with the default clock; no user-visible change.

## 4. Residual after the change (stated)

Host clock integrity is trusted; a fabricated "fresh" snapshot identical to a still-current frozen one passes (same session, same price — nothing to
detect); appending directly to `DecisionStore` remains an unsanctioned path (repo scan test unchanged).

## 5. Disposition requested

Approve, amend, or reject Section 2. Until then no further backend-completion workstream (research adapter, assessment view, cohort comparison, outcome
linkage) is started, per the work order.

---

## 6. Disposition (2026-10-28, recorded BEFORE implementation; sections 1–5 are unchanged)

**APPROVED WITH AMENDMENTS** by the human. The amendments below govern; where they differ from Section 2, they supersede it.

1. **Trusted backend UTC clock.** The canonical facade uses a trusted backend UTC clock for *all* funded-decision freshness checks: Stage 7 run age, XNYS
   session currency and Treasury reference freshness. A caller-supplied `created_at` must never establish the time used for any of them.
2. **`created_at` tolerance.** The five-minute tolerance is approved **only** as an operational timestamp-consistency check: for INITIATE/ADD, a `created_at`
   more than five minutes away from the trusted clock **in either direction** is rejected. It is not a freshness input.
3. **Clock injection cannot become a production bypass.** *Clarification of Section 2.1:* there is **no public clock parameter** — not on `__init__`, not on
   `record_final_decision`. The clock is a private method (`_now()`) returning the system UTC time. Deterministic tests substitute it by patching that method
   from the test side; nothing in production code offers a way to choose "now". As a defence in depth, the funded check **fails closed if `_now` has been replaced
   (on the class, a subclass, or the instance) in any process where the pytest test runner is not loaded**, so an ordinary production caller cannot supply a clock
   by overriding or monkeypatching it.

Everything else in Sections 2–5 stands: `capital_decision_facade.py` only; no other frozen-control change; HOLD CASH / DO NOTHING untouched; Human Stage 8
authority unchanged; Cycle 0 Correction 002 and the MCD/RPM revisit restrictions preserved.

Acceptance required by the human: the strict-xfail reproduction becomes a passing regression test; an eight-day-old funded decision with a backdated timestamp is
rejected with zero ledger writes; legitimate fresh decisions and non-actions still work.
