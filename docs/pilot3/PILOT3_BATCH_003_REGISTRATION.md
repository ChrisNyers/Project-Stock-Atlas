# PILOT 3 — BATCH 003 REGISTRATION

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Registers five Scout-surfaced candidates under the rules chartered in
> `PILOT3_BATCH_003_CHARTER.md`. **All five candidates (NHP, UCB, NNBR,
> SAIA, TCS) have now received full primary-evidence triage** in their
> own dedicated records (cross-referenced below); NNBR additionally
> received deep underwriting. Batch 003 discovery/triage is complete.

| | |
|---|---|
| Date registered | September 12, 2026 |
| Pilot | Pilot 3 — Opportunity Discovery Shadow Test |
| Batch | 003 |
| Governing rules | `PILOT3_HOOK_RECONSTRUCTION_AT_TRIAGE`, `PILOT3_PRICED_IN_ONE_LINER` (both effective as of this batch) |

---

## Source provenance

**Source:** `GROK_SCOUT_UNDER_SURFACE_DISCOVERY`
**As-of:** `2026-09-12`

**Discovery themes represented** (per the Batch 003 charter's categories
A–D): capital allocation / balance-sheet change (NHP); neglected /
lower-attention security (all five, to varying degrees per Scout);
competitor / industry read-through; quiet structural / balance-sheet
change.

**Governing principle, unchanged:** **Preserve provenance. Remove
privilege.** Scout candidates receive no underwriting advantage over any
other source. **Scout's own characterization of NHP as the "best
research-use-of-time candidate" is explicitly disregarded as a ranking
input** — Atlas determines progression from primary evidence alone, not
from the discovery source's own confidence claim.

---

## Batch 003 — frozen registration

| Candidate | Legal name | CIK / canonical identifier | Ticker | Exchange / MIC | Initial state |
|---|---|---|---|---|---|
| NHP | National Healthcare Properties, Inc. | SEC CIK `0001561032` | NHP | Nasdaq Global Market, MIC `XNMS` | `NO_DEMONSTRATED_EDGE` (see triage record) |
| UCB | United Community Banks, Inc. | SEC CIK `0000857855` | UCB | NYSE, MIC `XNYS` | `NO_DEMONSTRATED_EDGE` (see triage record) |
| NNBR | NN, Inc. | SEC CIK `0000918541` | NNBR | Nasdaq Global Select, MIC `XNGS` | `BLOCKED_BY_MATERIAL_UNCERTAINTY` — deep underwriting closed (see `PILOT3_NNBR_DEEP_UNDERWRITING_001.md`) |
| SAIA | Saia, Inc. | SEC CIK `0001177702` | SAIA | Nasdaq Global Select, MIC `XNGS` | `NO_DEMONSTRATED_EDGE` — see `PILOT3_SAIA_PRIMARY_EVIDENCE_TRIAGE_001.md` |
| TCS | Tecsys Inc. | Canadian issuer — no SEC EDGAR CIK identified | TCS | Toronto Stock Exchange, MIC `XTSE` (also cross-listed NEO, MIC `NEOE`) | `NO_DEMONSTRATED_EDGE` — see `PILOT3_TCS_PRIMARY_EVIDENCE_TRIAGE_001.md` |

**Only NHP receives primary-evidence triage in this record.** UCB, NNBR,
SAIA, and TCS are registered with canonical identity only — no
underwriting, no evidence review, no discovery-hook detail, no
disposition beyond `SURFACE_FOR_TRIAGE`, pending a future work order.

---

## Canonical identity checks — fail-closed on ambiguity, per instruction

**NHP:** verified without ambiguity. Full identity check, including
former-name history (Healthcare Trust, Inc. / American Realty Capital
Healthcare Trust II, Inc.) and MIC confirmation (`XNMS`, not the more
common `XNGS`), is recorded in
`PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md` §1.

**UCB — a real collision exists and is resolved here:** "UCB" is *also*
the ticker for **UCB SA**, a large Belgian pharmaceutical company listed
on Euronext Brussels (MIC `XBRU`) — an entirely unrelated company. **The
candidate registered here is United Community Banks, Inc., NYSE, MIC
`XNYS`, SEC CIK `0000857855`**, confirmed directly against SEC EDGAR's
own company-submissions record (ticker `UCB`, exchange `NYSE`). A second,
stale artifact was found in provider data (ticker `UCBI` on Nasdaq,
MIC `XNGS`, also mapped to "United Community Banks, Inc.") — this
reflects United Community Banks' **former** ticker before it moved to
NYSE under `UCB`; the current, SEC-confirmed identity is `UCB` / NYSE /
`XNYS`, not `UCBI` / Nasdaq. **This record fails closed by explicitly
naming and resolving both collisions rather than assuming either.**

**NNBR:** no material collision found — NN, Inc., Nasdaq, MIC `XNGS`,
confirmed via SEC EDGAR.

**SAIA:** no material collision found on the primary U.S. listing — Saia
Inc., Nasdaq, MIC `XNGS`, confirmed via SEC EDGAR. (A distinct ticker
"SQR" is used for Saia on several German trading venues — not a "SAIA"
collision, noted only for completeness.)

**TCS — the collision the work order specifically flagged, resolved
without researching the company:** "TCS" maps to at least three
unrelated real issuers depending on venue: **Tata Consultancy Services
Ltd.** (NSE/BSE, India — a large, well-known IT-services company),
**Tecsys Inc.** (TSX, Canada — the actual Batch 003 candidate, also
cross-listed on NEO), and a German-venue listing that resolves to
**Axon Enterprise, Inc.** under the same three-letter code on certain
European exchanges. **The candidate registered here is Tecsys Inc.,
Toronto Stock Exchange, ticker TCS, MIC `XTSE`.** Tecsys does not appear
to be SEC EDGAR-registered (no CIK identified in a ticker-resolution
check) — consistent with a Canadian-domiciled issuer that files with
Canadian regulators rather than the SEC; this is recorded as the
canonical-identifier gap it is, not resolved by inference. **No
fundamental or economic research on Tecsys was performed, per explicit
instruction** ("do not research TCS yet").

---

## NHP — full primary-evidence triage

Recorded separately in `PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md`.
Disposition: **`NO_DEMONSTRATED_EDGE`**. Scout's hook (OMF-portfolio-sale
proceeds paying down debt beyond the sold properties' own collateral,
plus a full preferred-stock redemption, improving the capital stack for
common shareholders) is real as a narrow fact pattern but is directly
contradicted by the mandatory hook reconstruction (Fix 1): a ~156%-
dilutive common equity raise ($531.3M gross, closed April 23, 2026, more
than doubling share count), not the asset sale or preferred redemption,
is the primary-sourced driver of this year's leverage improvement, and
Normalized FFO per diluted share fell 18.2% year-over-year in the same
quarter. The one completed-session price reaction most directly tied to
the hook (the September 10 first-tranche closing) was negative, not
positive. Treated as a successful discovery-system outcome — the new
narrow fixes killed a plausible-sounding hook cheaply, on primary
evidence, before a full variant was written around it.

---

## UCB — full primary-evidence triage

Recorded separately in `PILOT3_UCB_PRIMARY_EVIDENCE_TRIAGE_001.md`.
Disposition: **`NO_DEMONSTRATED_EDGE`**. Scout's hook (Navitas exit +
HTM-to-AFS securities repositioning + debt paydown + expanded buyback
collectively improving earnings quality and risk profile more than the
market credits) was tested via the mandatory hook reconstruction and
restructuring bridge: management's own EPS walkforward shows the
Navitas-exit (−$0.07/quarter) and securities-reset reinvestment
(+$0.06/quarter) pieces net to roughly zero, with the touted overall
EPS improvement driven instead by an unrelated small acquisition (Peach
State, +$0.02) and unguided future "core bank growth" (+$0.02–0.04) —
neither named in the hook. The credit-risk-reduction half of the hook
(Navitas responsible for ~50% of total net charge-offs) was well
corroborated, but the market's own reaction to the September 8
announcement was flat-to-mildly-negative, not a sign of an
under-recognized positive, and post-restructuring valuation (~1.5–1.65x
tangible book, ~11–12x P/E, ~13% ROTCE) is unremarkable for a
well-capitalized regional bank. Closed `NO_DEMONSTRATED_EDGE`.

## NNBR — full primary-evidence triage, then Series D resolution, then deep underwriting

**Deep underwriting closed** `BLOCKED_BY_MATERIAL_UNCERTAINTY`
(`PILOT3_NNBR_DEEP_UNDERWRITING_001.md`). Three separately-guided growth
programs (Data Center & Electric Grid, Defense & Electronics, Medical
Products — combined ~$155M TTM, ~30% of revenue) and a ~5x segment
operating-margin gap (Power Solutions 15.1% vs. Mobile Solutions 3.0%,
FY2025) confirmed the mix shift as economically, not merely
descriptively, significant, and the resolved Series D trade was found
to be a credible, non-cheap de-risking. The disposition is blocked on
one specific, named gap: capex has not approached the guided $35-40M
annual run-rate in any of the eight quarters reconstructed, and free
cash flow (this record's own calculation) was positive in only one of
the last nine quarters — the load-bearing precondition for converting
the win pipeline into the ~$32.7M of incremental Adjusted EBITDA needed
merely to restore pre-dilution per-share economics is not yet evidenced.

## NNBR — full primary-evidence triage, then Series D resolution (superseded summary retained below)

Triage recorded separately in `PILOT3_NNBR_PRIMARY_EVIDENCE_TRIAGE_001.md`
— **`PROMOTE_TO_DEEP_UNDERWRITING`**. Unlike NHP and UCB, the mandatory
hook reconstruction did not kill or neutralize Scout's operating thesis:
revenue growth accelerated for three consecutive quarters, EBITDA margin
expanded in the most recent quarter, new-business-wins guidance was
raised at every update for a year, Data Center & Electric Grid revenue
(~$80M TTM) was confirmed as fact, and the auto/non-auto sales mix shift
(65%/35% in 2023 to 40%/60% by Q2 2026) is real and substantially already
executed. A thesis-blocking capital-structure question was named:
whether the "9,850 shares of Series D Preferred exchanged" figure
represented the bulk of the preferred cleanup or left most of it intact.

**Resolved via an addendum to the same record**, after locating the
actual Series D Exchange Agreement (a 10-Q exhibit) and cross-checking
against NN's special-meeting proxy's share-count disclosure. The
reconciliation is now clean: of 65,000 pre-transaction shares, 9,850 were
exchanged for stock and a **separate 36,750-share cash redemption** (not
previously located) retired an additional tranche — **71.7% of the
Series D balance eliminated in total**, leaving 18,400 shares (~28.3%,
~$34.6M) outstanding at a temporarily reduced 10.0% rate through August
2027, with a confirmed $5.0 million discount incentive to fully redeem
by December 31, 2026. Common-share dilution from the private placement
and exchange combined is confirmed at ~57.1%; the exchange ratio itself
retired preferred at roughly fair-to-premium value, not a discount — a
genuine de-risking trade, not a cheap one. Uncertainty classification
updated to **`RESOLVED_SUPPORTS_THESIS`**; progression decision
**`PROCEED_TO_DEEP_UNDERWRITING`**. Deep underwriting has since been
performed and closed `BLOCKED_BY_MATERIAL_UNCERTAINTY` — see the
dedicated section above.

## SAIA — full primary-evidence triage (read-through discovery type)

Recorded separately in `PILOT3_SAIA_PRIMARY_EVIDENCE_TRIAGE_001.md`.
Disposition: **`NO_DEMONSTRATED_EDGE`**. Scout's hook (ODFL's August 2026
LTL pricing data suggesting industry pricing is firmer than feared,
softening SAIA's guided Q3 operating-ratio pressure) failed the
mandatory cheapest-falsification test on four grounds: SAIA's own Q3
guidance (100bps sequential OR degradation, already better than the
150-200bps historical norm) was public more than a month before the
hook; SAIA discloses its own monthly shipment/tonnage data via SEC
filing, filed the same calendar day as ODFL's release; ODFL's cited
ex-fuel pricing metric was not new information (it sat inside a stable,
year-long range); and the cost items most likely to drive SAIA's actual
Q3 outcome (new-terminal drag, stacked wage increases, purchased-
transportation inflation +47.3% YoY) are SAIA-specific and unrelated to
ODFL's pricing environment. Direct market-reaction evidence (SAIA rose
on the Sept 3 release day; ODFL did not) confirmed the market's own
repricing is better explained by SAIA's own data than by the read-
through. Classified `READ_THROUGH_PARTIAL` as a Pilot 3 learning
observation — a genuine industry pricing-discipline signal exists but
does not transfer with the specificity Scout's hook required.

## TCS — full primary-evidence triage

Recorded separately in `PILOT3_TCS_PRIMARY_EVIDENCE_TRIAGE_001.md`.
Disposition: **`NO_DEMONSTRATED_EDGE`**. Every headline fact in Scout's
hook (revenue, SaaS revenue/growth, Elite SaaS growth, ARR, RPO,
Adjusted EBITDA, raised FY2027 guidance, NCIB, dividend) verified
precisely against primary sources, and the aggregate installed-base-
expansion mechanism (Elite SaaS ARR net retention 111% LTM, climbing;
Elite ARR accelerating to 24% YoY beneath a merely-stable blended total-
SaaS figure) strengthened under the mandatory hook reconstruction —
unlike NHP, UCB, or SAIA. Promotion failed on a different dimension:
Scout's specifically named customer expansions (Prisma Health, UT
Southwestern, a cancer center) could not be corroborated in any primary
Tecsys disclosure; FY2027 guidance was raised the same day as the
hook's underlying Q1 results, meaning the evidence is already reflected
in management's own forward guidance; and the market's own reaction
(~+11% over the following days) indicates the story has already begun
to be priced. Gate B could not be attempted at all for this security
(XTSE unsupported by the live session calendar; TwelveData's plan does
not cover TSX-listed names) — disclosed as a genuine limitation, not
worked around. Classified `NEGLECT_PARTIAL` (six analysts cover the
name, but trading liquidity is genuinely thin) as a Pilot 3 learning
observation. **Batch 003 is now fully triaged.**

---

## Shadow sentiment

No sentiment observations were recorded, sought, or used in registering
any of the five candidates or in triaging NHP. Per the Batch 003 charter,
had any been available they would be labeled `SHADOW` and kept out of
promotion/blocking/funding logic — none arose in this record.

---

## Pilot 3 discovery log — Batch 003

| Candidate | Source | Initial state | Atlas disposition | Survived primary-evidence triage? |
|---|---|---|---|---|
| NHP | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` | `SURFACE_FOR_TRIAGE` | `NO_DEMONSTRATED_EDGE` | No — the specific discovery mechanism (debt paydown + preferred redemption improving the common capital stack) was directly contradicted by a primary-sourced, dilutive equity raise the discovery layer did not surface, and by the Normalized FFO/share decline it produced |
| UCB | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` | `SURFACE_FOR_TRIAGE` | `NO_DEMONSTRATED_EDGE` | No — the earnings-quality half of the hook nets to roughly zero on management's own bridge once an unrelated acquisition and unguided future growth are excluded; the credit-risk-reduction half is real but the market's own flat-to-negative reaction does not indicate it is under-recognized |
| NNBR | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` | `SURFACE_FOR_TRIAGE` | `BLOCKED_BY_MATERIAL_UNCERTAINTY` (deep underwriting) | Yes at triage (growth acceleration, margin expansion, mix shift, data-center revenue all corroborated and strengthened) and yes on the resolved Series D reconciliation (71.7% retired, not ~15%); deep underwriting then found the win pipeline is broader than triage knew (three ~$155M-TTM growth programs, a ~5x segment margin gap) but blocked promotion on capex execution never reaching guided run-rate across 8 quarters and free cash flow durability unproven |
| SAIA | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` (`READ_THROUGH`) | `SURFACE_FOR_TRIAGE` | `NO_DEMONSTRATED_EDGE` | No — the ODFL-August-data read-through failed the cheapest-falsification test: SAIA's own Q3 guidance was already better-than-normal-seasonality a month before the hook, SAIA discloses its own monthly volume data contemporaneously with ODFL's release, ODFL's cited pricing metric was not new information, and the cost items most likely to drive SAIA's Q3 outcome are SAIA-specific and unrelated to ODFL's pricing environment. Classified `READ_THROUGH_PARTIAL` |
| TCS | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` (`NEGLECTED / INSTALLED_BASE_EXPANSION`) | `SURFACE_FOR_TRIAGE` | `NO_DEMONSTRATED_EDGE` | Facts verified exactly; the aggregate installed-base-expansion mechanism (111% Elite SaaS net retention, Elite ARR accelerating to 24% YoY) strengthened under reconstruction — but Scout's named customer expansions (Prisma Health, UT Southwestern) could not be corroborated in any primary source, FY2027 guidance was raised the same day on the same results, and the market had already reacted ~+11% by the evidence date, leaving no demonstrated unpriced edge |

No discovery score. This log records outcomes only.

---

## What this record does not do

No deep underwriting of TCS or any Batch 003 candidate beyond NNBR's
already-recorded deep underwriting. No Stage 7 or Stage 8. No capital
allocated. No architecture change. No scoring, ranking, or new engine.
Batch 001 and Batch 002 are untouched. No advance of JPM or AAPL. No
Batch 004.

**Capital status: NO REAL PORTFOLIO ACTION.**
