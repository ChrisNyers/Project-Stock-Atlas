# PILOT 3 — BATCH 003 REGISTRATION

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Registers five Scout-surfaced candidates under the rules chartered in
> `PILOT3_BATCH_003_CHARTER.md`. Only NHP receives primary-evidence
> triage in this record (`PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md`).
> UCB, NNBR, SAIA, and TCS are registered only — not triaged, not
> researched beyond canonical identity.

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
| NNBR | NN, Inc. | SEC CIK `0000918541` | NNBR | Nasdaq Global Select, MIC `XNGS` | `SURFACE_FOR_TRIAGE` — registered only |
| SAIA | Saia, Inc. | SEC CIK `0001177702` | SAIA | Nasdaq Global Select, MIC `XNGS` | `SURFACE_FOR_TRIAGE` — registered only |
| TCS | Tecsys Inc. | Canadian issuer — no SEC EDGAR CIK identified; not researched further per instruction | TCS | Toronto Stock Exchange, MIC `XTSE` (also cross-listed NEO, MIC `NEOE`) | `SURFACE_FOR_TRIAGE` — registered only, **identity only, not researched** |

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

## NNBR, SAIA, TCS — remain registered, not triaged

No discovery-hook detail, economic rationale, hook reconstruction,
priced-in one-liner, candidate variant, market-could-be-right
alternative, cheapest-falsification test, or evidence-gap assessment is
recorded for these three candidates in this record — no work order
governing this registration has yet provided discovery-hook detail for
them, and two successive work orders have explicitly instructed that
they not be triaged. **Initial disposition for all three:
`SURFACE_FOR_TRIAGE`**, pending a future work order that provides the
discovery-hook detail needed to apply the required Batch 003
discovery-record template (§7 of the charter).

---

## TCS — registered, not triaged, not researched

Same as above, with the additional, explicit instruction that TCS not be
researched at all beyond the canonical-identity collision resolution
above. **Initial disposition: `SURFACE_FOR_TRIAGE`**, pending a future
work order.

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
| NNBR | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` | `SURFACE_FOR_TRIAGE` | not yet triaged | — |
| SAIA | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` | `SURFACE_FOR_TRIAGE` | not yet triaged | — |
| TCS | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` | `SURFACE_FOR_TRIAGE` | not yet triaged (not researched) | — |

No discovery score. This log records outcomes only.

---

## What this record does not do

No deep underwriting of NHP. No triage of UCB, NNBR, SAIA, or TCS. No
research of TCS. No Stage 7 or Stage 8. No capital allocated. No
architecture change. No scoring, ranking, or new engine. Batch 001 and
Batch 002 are untouched. No advance of JPM or AAPL.

**Capital status: NO REAL PORTFOLIO ACTION.**
