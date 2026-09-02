# Gate B — Live Data Binding

**Starting freeze:** `8dba996` (Final Code Red Team ACCEPTED)
**Scope:** production-data binding only. No architecture change.
**Capital status:** **NO REAL PORTFOLIO ACTION**

Gate B proves that real upstream observations can enter the accepted
capital-decision path with correct identity, freshness, currency and evidence
retention — and that the system still fails closed when those inputs are wrong,
stale or missing.

---

## Design rule that governs everything here

> **A provider may never be the authority on whether its own observation is fresh.**

Red Team C-02 is the reason. A provider that self-asserts freshness can assert
that a stale session is current, and nothing downstream can tell. So session
truth is derived from an **independent exchange calendar**, and the provider's
`is_market_open` / exchange-state response is captured as *evidence only*:

```
decision timestamp
      -> XNYS calendar (exchange_calendars==4.13.2)
      -> latest completed session
      -> known_latest_session_date
      -> existing Stock Atlas freshness validation   [unchanged]
```

`live_session_calendar.py` performs no network I/O, holds no credential, and
makes no decision. If it cannot resolve the applicable exchange or session, it
raises `SessionCalendarError` and the binding fails closed.

---

## What was added

| File | Role |
|---|---|
| `live_session_calendar.py` | B3. Independent session truth + `SessionAttestation` provenance. |
| `live_price_binding.py` | B1/B2/B4. Binds a live observation to the frozen `PriceSnapshot` / `FXSnapshot` contracts; refuses anything incomplete or misidentified. |
| `tests/test_gate_b_live_binding.py` | 31 tests proving B1–B5. |
| `requirements.txt` | pins `exchange_calendars==4.13.2`. |
| `pytest.ini` | registers the `live` marker. |

**No control-layer file was modified.** All 10 v0.2 files remain byte-identical
to the verified archive. `capital_decision_facade.py` is unchanged.

---

## B1 — real-provider price binding

Live TwelveData observation bound into the existing `PriceSnapshot`:

```
security_key                  SEC-CIK:0001067983:BRK-B
quoted_security_key           SEC-CIK:0001067983:BRK-B
quoted_instrument             Berkshire Hathaway Inc. Class B (XNYS)
ticker                        BRK.B
price                         505.23999
currency                      USD
provider                      twelvedata
price_as_of                   2026-09-02T19:59:00+00:00
price_session_date            2026-09-02
latest_completed_session_date 2026-09-02      <- from calendar, not provider
market_session_status         COMPLETED
adjusted                      false           <- recorded honestly
price_mode                    COMPLETED_SESSION
freshness_status              FRESH
freshness_basis               derived from independent exchange calendar
```

`adjusted=false` is deliberate: TwelveData's `/quote` returns an unadjusted last
price. Recording it honestly is preferable to asserting an adjustment that was
not applied.

Blocked cases proven: missing currency, wrong expected currency, venue/MIC
mismatch against the attested calendar, non-positive price, unresolvable symbol.

## B2 — security / class identity binding

BRK.A and BRK.B share issuer CIK `0001067983` and are **distinct securities**:

| | BRK.B | BRK.A |
|---|---|---|
| security key | `SEC-CIK:0001067983:BRK-B` | `SEC-CIK:0001067983:BRK-A` |
| live price | 505.24 | 758,500.00 |

A 1,501× price difference makes the consequence of collapsing them explicit.
The issuer segment alone is asserted **not** to be an identity.

Proven: BRK.A observation cannot satisfy BRK.B; BRK.B cannot satisfy BRK.A
(symmetric); the correctly bound class still passes; and if the binder were
bypassed entirely, `validate_price_snapshot` independently rejects the swap.

## B3 — authoritative latest-session / calendar binding

| Case | Decision time | Attested session |
|---|---|---|
| normal, after close | 2026-09-02 21:00Z | 2026-09-02 |
| **before today's close** | 2026-09-02 15:00Z | **2026-09-01** |
| Saturday | 2026-08-29 12:00Z | 2026-08-28 |
| Sunday | 2026-08-30 12:00Z | 2026-08-28 |
| Labor Day holiday | 2026-09-07 12:00Z | 2026-09-04 |

An incomplete session is never treated as a completed-session close.

**Stale-consistent block (C-02, live form):** a session dated 2026-08-12,
internally consistent and self-labelled `FRESH`, is rejected against the
attested session with *"Completed-session price is not bound to the attested
latest trading session."*

**Provider contradiction:** with the provider explicitly reporting
`is_market_open=True`, the attestation is unchanged, records
`provider_agrees_with_calendar: false`, and reports
`authority: independent exchange calendar`. The provider does not control
session truth.

Fail-closed: unmapped MIC (`XNAS`), blank exchange, naive timestamp, and
out-of-bounds decision time all raise.

## B4 — live FX binding

Live EUR/USD observation from the same single provider. No FX engine, no
cross-rating, no inversion.

| Case | Result |
|---|---|
| correct pair `EUR/USD`, fresh | **PASS** — binds, `FRESH`, passes `validate_fx_binding` |
| reversed pair `USD/EUR` | **BLOCK** — "pair mismatch … cannot be silently inverted" |
| wrong pair `GBP/USD` | **BLOCK** — pair mismatch |
| stale observation | **BLOCK** — `STALE`, then "FX snapshot is STALE" |
| stale-consistent, self-labelled FRESH | **BLOCK** — "FX snapshot is too old" |
| FX missing while currencies differ | **BLOCK** — "requires a bound FX snapshot" |
| currencies match (USD/USD) | no FX required — none fabricated |

B4 was exercised independently. No foreign-security portfolio decision was
invented to force FX into the B5 replay.

## B5 — integrated production-adapter replay

Real observation → canonical identity → independent calendar session → frozen
`PriceSnapshot` → `CapitalDecisionFacade.run_stage7` → retained hashed
`Stage7Run` → human Stage 8 boundary.

```
decision_time_utc : 2026-09-02T22:44:55Z
security_key      : SEC-CIK:0001067983:BRK-B | BRK.B
live price        : 505.23999 USD from twelvedata
price_as_of       : 2026-09-02T19:59:00+00:00
session (provider): 2026-09-02   market_open: False   [evidence only]
session (CALENDAR): 2026-09-02   close 2026-09-02T20:00:00Z
                    exchange_calendars==4.13.2        [AUTHORITY]
freshness         : FRESH (derived from calendar)

STAGE 7 STATUS    : WATCH / NO DECISION
   reason: missing coarse return/variant band
   reason: missing return-band basis/provenance
   reason: missing required-return band
   reason: underwriting_gate_status=UNVERIFIED does not permit new-capital comparison
constraint_state  : UNVERIFIED
header            : COMPARISON AID — NO PORTFOLIO ACTION — STAGE 8 OPEN

artifact retained : gate_b_replay_record.json (1,398 bytes)
artifact sha256   : a099662921d6ff8532f4fb7248c132d9eacb3897696aa8bc73a738896222f3e2
ledger rows       : 0   (Stage 8 boundary not crossed)
```

**The outcome was not forced.** No human underwriting exists for BRK.B, so the
replay supplies none: `return_band=None`, `underwriting_gate_status=UNVERIFIED`.
Fabricating an investment conclusion to manufacture an ELIGIBLE result would be
a methodology change and is out of scope. The **data path cleared** — identity,
price, currency, venue, session and freshness all bound successfully — and the
**underwriting gate** is what stopped advancement. That is the correct and
honest result, and the handoff explicitly permits it.

All ten B5 conditions demonstrated, including: Treasury/Cash, beta and
Do Nothing present as distinct alternatives; artifact frozen and retained;
Stage 7 emits no `PortfolioAction`; a forged direct `INITIATE` against the real
non-eligible run is refused with *"INITIATE requires Stage 7 status 'ELIGIBLE
FOR STAGE 8'"* and the ledger stays empty; and no credential appears anywhere
in retained evidence.

---

## Test-harness note (disclosed in full)

TwelveData's free tier allows 8 credits/minute and each binding spends two.
Unpaced, the adapter fails closed with `RATE_LIMITED` — correct behaviour, but
it made evidence non-reproducible. The test module therefore paces live calls
(8.5s apart) and retries **only** on provider rate limiting.

This paces the harness. It does not retry a control failure, relax a freshness
rule, or convert a refusal into a pass: a `RATE_LIMITED` result is a *missing
observation*, not a failed control. No existing test was weakened, deleted,
skipped or reclassified.

Live tests carry `@pytest.mark.live` and skip when the credential is absent —
**a skip is a BLOCKED Gate B result, never a PASS.**

---

## Residual limitations

Recorded rather than papered over:

1. **One venue.** Only `XNYS`/`NYSE` is mapped. Any other MIC — including
   `XNAS`/`XNGS` — fails closed by design rather than borrowing NYSE's holiday
   schedule. Extending coverage means adding calendars deliberately.
2. **Unadjusted prices.** `adjusted=false` is recorded truthfully. A
   split/dividend-adjusted series is a separate binding not required by B1–B5.
3. **FX freshness is age-based.** B4 uses observation age against
   `max_age_hours`, not an FX-market session calendar. FX trades ~24×5; a
   session-calendar treatment of FX was not required by B4 and was not invented.
4. **No underwriting exists for BRK.B**, so the replay cannot exercise the
   ELIGIBLE branch on live data. Closing that requires a human underwriting
   input, not more code.

**Capital status: NO REAL PORTFOLIO ACTION.**
