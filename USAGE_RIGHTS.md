# Market-Data Usage Rights — Phase 4A.5.2A

Free-plan licensing / storage rights are a **hard** benchmark dimension for Stock
Atlas, which keeps **persistent decision and audit records with provenance** and
is used privately by **two people** (not a single individual).

Verdict scale (no interpretation beyond each provider's written terms; where the
terms are silent the verdict is `UNCLEAR_REQUIRES_CONFIRMATION`):

| verdict | meaning |
|---|---|
| `ELIGIBLE` | free plan clearly permits the Atlas use (persistent internal storage, ≥2 private users) |
| `ELIGIBLE_WITH_LIMITATIONS` | permitted but with a constraint Atlas must respect (bounded retention, per-user accounts, no display) |
| `INCOMPATIBLE_WITH_ATLAS_USE` | a written term directly conflicts with the Atlas architecture |
| `UNCLEAR_REQUIRES_CONFIRMATION` | terms do not address the question — confirm with the provider before relying on it |

All terms fetched **2026-08-30**.

---

## Matrix

| provider | free personal/internal use | persistent storage allowed? | two-person private use permitted? | redistribution / display | audit-store compatible? | verdict |
|---|---|---|---|---|---|---|
| **Massive** | Individuals ToS: "solely for your own personal, non-commercial, and non-business purposes"; NYSE non-professional "personal, non-business use" | **Unclear** — Market Data Terms require deleting all data on termination (§8); no explicit retention limit *during* an active subscription; personal archival vs prohibited "copying" not spelled out | **No, not on one account** — Individuals ToS explicitly prohibits "sharing an account or API keys with others" → two people need two separate free accounts | Prohibited: no copying/republishing/redistribution/public display; no business/commercial use | Unclear — needs written confirmation | `UNCLEAR_REQUIRES_CONFIRMATION` |
| **Twelve Data** | Terms 2.1: "Internal Use" only | **Limited** — 2.3(g) no "store or cache Data beyond permitted timeframes specified in the Documentation"; 16.1 retain only for subscription duration / regulatory compliance; delete ≤30 days after termination. Documentation gives no explicit free-plan window → a *bounded* personal cache is defensible; an *indefinite* audit store is not clearly permitted | Not addressed; Internal Use by a 2-person household is not obviously prohibited but is not spelled out → confirm | Prohibited without a Redistribution Rights Add-On (2.2(e)) | Partial — bounded cache yes; permanent retention unclear. **Free-tier commercial use explicitly prohibited (2.3(l))** | `ELIGIBLE_WITH_LIMITATIONS` |
| **Alpaca** | IEX Non-Professional Subscriber Agreement: Market Data "solely for personal, non-business use" / managing own assets | **Yes for derived/EOD records** under personal non-business use; the binding constraint is the IEX agreement, not an Alpaca storage ban | Each person receiving real-time IEX data must be a subscriber → two people need two free accounts; one shared account not clearly permitted | "Subscriber shall not furnish Market Data to any other person or entity" — no redistribution / external display | Yes for EOD/derived personal records; real-time redistribution/display is not | `ELIGIBLE_WITH_LIMITATIONS` |
| **Tiingo** | Starter: internal / personal use only | **No** — "you may not write, save, archive, back up, or otherwise retain Tiingo Data in any persistent or durable storage"; "process … only transiently in volatile memory or in a temporary, non-persistent cache"; "permanently remove … immediately after the calculation or operation is completed". Applies to databases, object stores, file systems, logs, backups | **No** — "you may only use the data for your own personal use and you may not display or share the data with another person or organization" | Prohibited on the free plan; requires a paid Power / redistribution license | **No** — explicit persistent-storage prohibition directly conflicts with Stock Atlas provenance/audit records | `INCOMPATIBLE_WITH_ATLAS_USE` |

---

## Consequences for the source stack

1. **Tiingo Starter is out** — regardless of its (excellent) technical data quality,
   its free terms forbid the persistent storage Stock Atlas is built on, and forbid
   a second user. It would only be usable under a paid Power plan, which is out of
   scope for this phase.

2. **Massive, Twelve Data, Alpaca** are all `ELIGIBLE`-class only with caveats:
   - **Two people ⇒ two free accounts each.** None of the three clearly permits two
     people on one account; Massive explicitly forbids account/key sharing.
   - **No redistribution or external display** on any free plan — Stock Atlas must
     treat provider data as internal-only (fine: it is a private tool).
   - **Twelve Data free tier: no commercial use.** A private two-person investment
     tool is arguably non-commercial, but if either user's use is a business, the
     free tier does not cover it → confirm or use a paid plan.
   - **Retention window** for Massive and Twelve Data is not written down for the
     free plan → before Atlas persists provider data indefinitely for audit, get
     written confirmation, or keep only Atlas-derived values (not raw vendor data)
     in the durable store.

3. **EOD-only is acceptable.** Stock Atlas's use case is investment decisions, not
   trading, so a reliable EOD/consolidated close plus corporate actions is
   sufficient; real-time is not required. That keeps Massive (EOD Basic) fully in
   contention and means Alpaca's IEX-only real-time limitation is not disqualifying.
