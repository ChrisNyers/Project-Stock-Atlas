# Market-Data Identity Join Contract

Status: **binding for Phase 4A.5.2** (market-data benchmark). Established in
Phase 4A.5.1B. This is not a Security Master redesign and not an instrument-master
system — it is only the join rule the market-data benchmark must obey.

## The rule

1. **A market price observation attaches to a `security_key`, never to a bare
   issuer CIK.**
   `security_key` has the form `SEC-CIK:{cik}:{SEC_TICKER}` and is produced by
   `identity_resolver.resolve_security()`.

2. **A provider ticker is a lookup identifier only.** Before any price row is
   stored or compared it must be resolved:
   `ticker → resolve_security(ticker) → security_key`.
   Use `identity_resolver.market_price_join_key(ticker)` — it fails closed
   (`IdentityJoinError`) if the ticker does not resolve to a `security_key`.

3. **Fundamental (SEC/XBRL) evidence** stays on the existing evidence model:
   issuer-level facts on the issuer, security-level facts on the security, as
   today. Phase 4A.5.1B does not change fundamental evidence association.

4. **Issuer vs security stay two levels.**
   - `issuer_key` = `SEC-CIK:{cik}` — shared by every share class / series of one
     filer.
   - `security_key` = `SEC-CIK:{cik}:{SEC_TICKER}` — one per listed line.

## BRK.A / BRK.B (the control)

| | BRK.A | BRK.B |
|---|---|---|
| issuer CIK | `0001067983` | `0001067983` |
| `issuer_key` | `SEC-CIK:0001067983` | `SEC-CIK:0001067983` |
| `security_key` | `SEC-CIK:0001067983:BRK-A` | `SEC-CIK:0001067983:BRK-B` |
| provider ticker | `BRK-A` (SEC) / `BRK.A` (dotted) | `BRK-B` / `BRK.B` |
| share class | `A` | `B` |

- **May** share one issuer CIK — they do.
- **Must** have distinct `security_key`s — they do.
- **Must never** silently share one market-price series. A price row for `BRK.A`
  binds to `SEC-CIK:0001067983:BRK-A`; a price row for `BRK.B` binds to
  `SEC-CIK:0001067983:BRK-B`. They are different rows, different series.

`assert_distinct_price_series("BRK.A", "BRK.B")` returns the two distinct
`security_key`s and confirms `shares_issuer = true`.

## ORM mapping (no schema change)

`MarketStateORM.security_id` (already a FK to `security_identity.security_id`)
MUST be set to the resolved `security_key`. `ResolvedSecurity.to_orm_kwargs()`
maps `security_id = security_key`, `issuer_id = issuer_key`, `share_class`
preserved — so two share classes persist as two `SecurityIdentityORM` rows under
one `issuer_id`, and each carries its own `MarketStateORM` rows.

## Explicitly out of scope for Phase 4A.5.1B

- FIGI / OpenFIGI (not added).
- Any general instrument-master or cross-vendor symbology system.
- Security Master redesign.
- Actual market-data provider integration (Phase 4A.5.2).
