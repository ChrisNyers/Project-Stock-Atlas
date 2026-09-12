# PILOT 3 — NHP PRIMARY-EVIDENCE TRIAGE 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> First Batch 003 candidate to receive primary-evidence triage. First
> record governed by the two Batch 003 narrow fixes
> (`pilot3/PILOT3_BATCH_003_CHARTER.md`): `PILOT3_HOOK_RECONSTRUCTION_AT_TRIAGE`
> and `PILOT3_PRICED_IN_ONE_LINER`, both applied below.

| | |
|---|---|
| Date | September 12, 2026 |
| Batch | `PILOT3_BATCH_003_REGISTRATION.md` |
| Candidate | NHP — National Healthcare Properties, Inc. |
| Source | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY`, as-of 2026-09-12 |
| Prior state | `SURFACE_FOR_TRIAGE` |

---

## 1. Canonical identity — verified, no ambiguity found

- **Issuer legal name:** National Healthcare Properties, Inc.
- **CIK:** `0001561032`
- **Ticker:** **NHP** (common stock). Related, distinct securities on the
  same CIK: **NHPAP** (7.375% Series A Cumulative Redeemable Perpetual
  Preferred Stock), **NHPBP** (7.125% Series B Cumulative Redeemable
  Perpetual Preferred Stock) — both are being fully redeemed (§4 below),
  not the common stock this record triages.
- **Exchange / MIC:** Nasdaq Global Market, **MIC `XNMS`** — confirmed
  directly from the provider (`symbol_search`/`quote`), not assumed; this
  is a different Nasdaq tier than `XNGS` (Global Select) used elsewhere
  in this pilot, and Gate B's supported-calendar list required the
  correct tier to bind (an ambiguous/wrong MIC fails closed by design).
- **Security type:** REIT common stock (SIC 6798).
- **Former names, primary source (10-K):** "Healthcare Trust, Inc."
  (2015–2024) and, before that, "American Realty Capital Healthcare
  Trust II, Inc." (2012–2015) — a non-traded REIT sponsored by AR Global
  that renamed and uplisted to Nasdaq in September 2024. This confirms
  the Scout-claimed "neglected / lower-attention" discovery theme is at
  least plausible on its face (recently relisted, small-cap, complex
  legacy naming) — **this record does not treat that theme claim as
  established fact merely because it is asserted.**

**No ambiguity found for NHP itself.** (TCS's identity is registered
separately in the Batch 003 registration document with its own explicit
collision warning, per instruction; it is not researched here.)

---

## 2. Source provenance and ranking discipline

Source: `GROK_SCOUT_UNDER_SURFACE_DISCOVERY`, as-of `2026-09-12`. Per
instruction, **Scout's own characterization of NHP as the "best
research-use-of-time candidate" is explicitly disregarded as a ranking
input** — this record's disposition rests solely on primary evidence
gathered below, not on Scout's stated confidence. Preserve provenance,
remove privilege — same governing principle as Batch 001/002.

---

## 3. Scout's discovery hypothesis — restated, treated as tentative

> The outpatient-medical portfolio sale may represent more than a simple
> asset disposition because proceeds are reducing debt beyond the
> collateral attached to the sold properties while preferred equity is
> also being redeemed, potentially improving the capital stack for
> common shareholders.

**Per instruction, this record does not assume deleveraging is
accretive** — that assumption is the specific thing tested below, and
(§7) it does not survive the test.

---

## 4. Primary evidence reviewed

- **8-K filed 2026-09-10** (accession `0001561032-26-000058`,
  `hct-20260910.htm`) — completion of the first tranche of the OMF
  portfolio disposition.
- **8-K filed 2026-08-05** (accession `0001561032-26-000052`,
  `hct-20260803.htm`, with exhibit `amendedandrestatedcreditag.htm` and
  earnings-release exhibit `q22026earningspressrelease.htm`) — Series A/B
  preferred redemption, new $1.2B credit facility, Q2 2026 earnings, and
  a board addition.
- **10-Q for the quarter ended June 30, 2026** (accession
  `0001561032-26-000055`, `hct-20260630.htm`) — debt footnote, preferred
  stock footnote, subsequent-events footnote, equity footnote.
- **10-K for FY2025** (accession `0001561032-26-000009`) — used for
  former-name history and as a cross-check.
- **Earnings-release exhibits for Q3 2025, Q4/FY2025, and Q1 2026**
  (accessions `0001561032-25-000033`, `0001561032-26-000010`,
  `0001561032-26-000027`) — used specifically for the Fix 1
  hook-reconstruction table below.
- **SEC XBRL company facts** (CIK `0001561032`) — used to independently
  verify secured-debt balances, common-share counts, and equity-issuance
  proceeds against the narrative in the filings above.
- **Equity price series** (TwelveData), 2026-07-31 through 2026-09-11 —
  checked directly per this pilot's standing discipline.

Secondary sources were **not used** for this record — primary sources
were sufficient and are not supplemented here.

---

## 5. Transaction facts, confirmed

**OMF portfolio sale (Item 2.01, first-tranche 8-K + 10-Q subsequent
event):**

- **Full portfolio:** 86 outpatient medical facilities (OMFs), agreed in
  May 2026, for **~$528.2 million** total consideration (before
  transaction expenses/prorations), **including ~$278.0 million of
  secured debt to be defeased or assumed by the purchaser.**
- **First tranche, closed September 10, 2026:** **30 of the 86
  properties**; **~$79 million net cash proceeds**; **~$119 million of
  secured indebtedness repaid**, of which **~$60 million encumbered
  other OMFs not part of this tranche** (i.e., cross-collateralized debt
  cleanup, not solely debt on the properties actually sold — this is the
  specific fact Scout's hook points to). Buyer: an unaffiliated third
  party, not named.
- **Remaining exposure:** ~56 properties and, by arithmetic, roughly
  **~$159 million of the total ~$278M debt figure** still to be
  defeased/assumed in subsequent tranches, **conditional on lender
  approvals** for debt assumption — a real, disclosed execution
  contingency on the rest of the deal.
- **Named debt tranches** ("Term Loan 1"/"Term Loan 3" per the work
  order): the 10-Q's debt footnote names **Secured Term Loan 1 due 2028**
  ($85.8M, 4.60% fixed) and **Secured Term Loan 3 due 2031** ($33.1M,
  2.93% fixed) among the company's mortgage-note tranches (alongside a
  Term Loan 4 due 2033 and several single/multi-property mortgages and
  Fannie Mae facilities). **Evidence gap, disclosed:** no source reviewed
  states by name which specific tranche(s) the ~$119M first-tranche
  repayment actually retired — the 8-K describes only an aggregate
  dollar figure.
- **New credit facility (Item 2.03, Aug 5 8-K):** Wells Fargo-led,
  **$1.2 billion total** ($750M revolver to Aug 2030, $300M term loan to
  Aug 2029, $150M delayed-draw term loan to Aug 2029), up to $1.0B further
  expansion capacity, replacing a prior $550M facility.
- **Preferred redemption (Item 8.01, Aug 5 8-K):** **Full redemption of
  both remaining preferred series** — Series A (3,289,061 shares,
  7.375%, redeemed **Sept 4, 2026**, ~$82.2M) and Series B (2,850,427
  shares, 7.125%, redeemed **Oct 6, 2026**, ~$72.6M) — confirmed to be
  the **entire** June 30, 2026 outstanding balance of each series (10-Q:
  "3,289 and 3,846" Series A, "2,850 and 3,417" Series B shares
  outstanding at June 30 and Dec 31, 2025 respectively) — this is a
  **complete retirement** of the preferred stack, not a partial buyback.

---

## 6. Narrow Fix 1 — hook reconstruction (last 5 reporting periods)

The hook depends materially on **margin/leverage change** and **FCF/
per-share improvement** (Normalized FFO per share is the correct,
REIT-standard per-common-share proxy for "capital stack improvement" —
GAAP EPS is not, for a depreciation-heavy REIT). Reconstructed directly
from each quarter's own earnings-release exhibit:

| Period | FFO / diluted share | Normalized FFO / diluted share | Net Leverage (Net Debt / Ann. Adj. EBITDA) | SHOP same-store cash NOI (YoY) | OMF same-store cash NOI (YoY) |
|---|---|---|---|---|---|
| Q2 2025 | — | $0.22 | 9.2x (as of Jun 2025... *see note*) | — | — |
| Q3 2025 | $0.23 | not separately disclosed | 8.9x | +27.2% | +4.7% |
| Q4 2025 | $0.07 | $0.20 | 9.2x | +26.5% | +1.9% |
| Q1 2026 | **$0.31** | **$0.26** | 8.6x | +24.0% | +5.5% |
| Q2 2026 | $0.19 | **$0.18** | **4.9x** | ~20.1% | **−0.4%** |

*Note: the Q2 2026 release states net leverage "improved 4.3x to 4.9x...
from 9.2x as of June 30, 2025" — the 9.2x figure in that specific
year-over-year comparison is the company's own stated Jun-2025 value;
the Mar-2025 comparison in the Q1 2026 release separately states 9.6x.
Both are quoted as given, without reconciling the two into one series,
since this record does not build a historical-data engine.*

**What the reconstruction shows, plainly:**

1. **Net leverage was roughly flat-to-choppy in the 8.6x–9.6x range for
   a full year** (Mar 2025 through Mar 2026) and then **dropped sharply
   to 4.9x in a single quarter (Q2 2026)** — before the OMF portfolio
   sale had closed a single property (first tranche closed Sept 10,
   three months after the June 30 balance-sheet date) and before either
   preferred series had been redeemed (Sept 4 / Oct 6, also after June
   30). **The leverage improvement Scout's hook implicitly credits to
   the asset sale and preferred redemption had already happened before
   either event occurred.**
2. **FFO and Normalized FFO per diluted share peaked in Q1 2026 ($0.31 /
   $0.26) — the strongest quarter in this reconstruction — then fell
   sharply in Q2 2026 ($0.19 / $0.18), an 18.2% YoY decline and a much
   larger sequential decline**, even as SHOP operating performance
   remained strong (+20–24% same-store NOI) and OMF only turned mildly
   negative (−0.4%). **Operating performance does not explain a decline
   of this size.**
3. **SHOP same-store NOI growth is decelerating each quarter measured**
   (27.2% → 26.5% → 24.0% → 20.1%) even as full-year guidance was raised
   — still strong, but the trend line points down, not up.
4. **OMF same-store NOI growth reversed to negative in the exact
   quarter the portfolio sale process was underway** (+4.7% → +1.9% →
   +5.5% → **−0.4%**) — plausibly a held-for-sale/deferred-capex
   accounting effect given the pending disposition, but **no cause is
   disclosed** in sources reviewed; treated as an evidence gap, not
   assumed favorable or unfavorable.

**Per Fix 1's rule, this is a hook whose own load-bearing per-share
metric has already reversed** (declined 18.2% YoY, and more sharply
sequentially) in the exact window the hook claims improvement is
occurring. The reconstruction requires asking whether an independent
source of edge remains before writing a full bullish variant — see §7.

---

## 7. What actually drove the leverage improvement — the reconstruction's key finding

**Independently verified via SEC XBRL** (not merely inferred from the
press release): National Healthcare Properties **raised approximately
$531.3 million gross ($499.4 million net) of new common equity in a
single public offering that closed April 23, 2026** — issuing
**44,275,000 shares of Class A common stock** against a pre-offering
base of **~28.4 million shares outstanding** — **more than doubling
the share count (+156%)**. The Class A shares convert automatically into
ordinary common shares on **October 18, 2026**. This offering:

- **Fully explains the revolving-credit-facility paydown to $0** (from
  $186M at Dec 31, 2025) that shows up in the Q2 2026 10-Q — the revolver
  was paid down with new equity, not with asset-sale proceeds (which did
  not yet exist) or preferred-redemption proceeds (a use of cash, not a
  source).
- **Is the dominant, primary-sourced explanation for the Q2 2026 net
  leverage collapse** from 8.6x (Q1 2026) to 4.9x (Q2 2026) — a much
  larger single-quarter move than anything in the preceding
  twelve months, coincident with, not caused by, the OMF sale or
  preferred redemption.
- **Is the most probable explanation for the Normalized FFO/share
  decline** — weighted-average diluted shares outstanding jumped from
  28.3M (Q1 2026) to a Q2 2026 figure reflecting the mid-quarter
  issuance (45.1M / 61.6M under different XBRL dimensions) — a
  mechanical per-share dilution effect large enough to swamp flat-to-
  growing aggregate FFO dollars, without requiring any deterioration in
  underlying operations.

**This is precisely the "another independent source of edge" test Fix 1
requires, run in reverse: the record actively looked for a reason the
FFO/share reversal might not matter, and found instead a bigger,
countervailing fact — a large, dilutive equity raise — that the
discovery hook never mentioned and that directly explains why the
capital stack has not obviously improved for common shareholders on a
per-share basis.** No source reviewed discloses the stated use of the
$499M in offering proceeds beyond what is inferable from the facts
above (revolver paydown, upcoming preferred redemptions, stated FY2026
acquisition guidance of $375–425M) — **this allocation is not
confirmed and is not asserted as fact.**

---

## 8. Narrow Fix 2 — priced-in one-liner

> For this to be mispriced **positively** for common shareholders, the
> market would have to be underestimating how quickly the ~$531.3
> million raised in the April 2026 equity offering gets deployed into
> per-share-accretive uses (debt reduction already executed, the
> upcoming preferred redemptions, and up to $375–425M of guided FY2026
> acquisitions) — fast enough to outrun the ~156% increase in share
> count.

**This sentence can be stated credibly — there is a real, quantifiable
number to test (share count, redemption savings, acquisition guidance)
— so Fix 2 does not veto this record for vagueness.** But stating it
credibly is not the same as it being supported: **Normalized FFO per
share already fell 18.2% year-over-year in the very quarter the capital
was raised**, and the record finds no disclosed evidence (§9) that this
reverses in the next reported quarter. The one-liner is stateable, but
the evidence gathered points against it, not for it.

---

## 9. Market reaction — checked directly, not assumed

| Date | Close | Note |
|---|---|---|
| 2026-08-03 | $15.24 | Before the Aug 5 announcement bundle |
| 2026-08-05 | $16.03 | Q2 earnings + full preferred redemption + new $1.2B facility announced |
| 2026-08-06 | $16.83 | +4.99% |
| 2026-08-07 | $16.95 | Peak of the post-announcement move — **+11.2% over 4 sessions** |
| 2026-08-20 | $17.08 | 52-week-high territory ($17.46) |
| 2026-08-28 | $16.06 | Giving back most of the August gain |
| 2026-09-09 | $16.25 | Day before tranche-1 closing |
| 2026-09-10 | $16.04 | **First-tranche OMF sale closing date** — down, not up |
| 2026-09-11 | **$15.74** | **−1.87%**, second consecutive decline |

**Two findings, both direct from completed-session data:**

1. **The market already reacted, materially and positively, to the
   preferred-redemption/new-facility/leverage-improvement news bundle
   on August 5–7** (+11.2%) — over five weeks before Scout's discovery
   date. Whatever informational value that bundle carried has already
   been substantially priced.
2. **The actual closing of the first OMF-sale tranche on September 10 —
   the specific event Scout's hook centers on — was met with a decline,
   not a rally**, continuing into a further decline the next session.
   **This is a direct, completed-session contradiction of "the market
   hasn't recognized this as more than a simple disposition."**

---

## 10. Candidate variant — tested against primary evidence, not corroborated

> The outpatient-medical portfolio sale may represent more than a simple
> asset disposition because proceeds are reducing debt beyond the
> collateral attached to the sold properties while preferred equity is
> also being redeemed, potentially improving the capital stack for
> common shareholders.

**Not corroborated.** The specific mechanism (debt paydown +
preferred redemption → improved capital stack for common) is real as a
narrow fact pattern (§5) but is **not the dominant driver** of this
year's capital-structure change — a ~156%-dilutive common equity raise
is (§7) — and the per-common-share metric that would actually show the
claimed improvement (Normalized FFO/share) **moved in the opposite
direction** in the same quarter (§6). The one completed-session market
reaction most directly tied to the hook (the Sept 10 tranche closing)
was negative (§9), not a sign of an under-recognized positive.

---

## 11. Market-could-be-right case

- Aggregate leverage genuinely improved (9.6x→4.9x over four quarters,
  most of it in one quarter) — a real balance-sheet positive the market
  has already rewarded once (Aug 5–7).
- SHOP segment fundamentals remain genuinely strong (20–27% same-store
  NOI growth every quarter measured) even as the growth rate decelerates
  — a real, separate positive not dependent on the capital-stack hook.
- The preferred redemptions and remaining OMF tranches are not yet fully
  executed — some further, real (if modest — §5's ~$9M/year of
  as-yet-unrealized incremental preferred-dividend savings beyond the
  ~$2M already captured through H1 2026 open-market buybacks) benefit to
  common may still be forthcoming and not yet reflected in any reported
  quarter.
- The market's mild negative reaction on Sept 10–11 could reflect
  broader market conditions unrelated to NHP specifically — this record
  does not control for market-wide moves on those two sessions, an
  evidence gap.

**This case does not require inventing anything — it is built entirely
from this record's own findings** — but it does not overcome the direct
per-share evidence in §6–§7.

---

## 12. Fresh-price bind (Gate B)

```
security_key: SEC-CIK:0001561032:NHP
price: $15.74
currency: USD
session_date: 2026-09-11
freshness_status: FRESH
freshness_basis: derived from independent exchange calendar (XNYS
                  calendar, XNMS venue), not provider self-report
mic: XNMS (Nasdaq Global Market — confirmed, not XNGS/XNAS)
52-week range (raw observation, context only): $11.25 - $17.46
```

No intraday price was used.

---

## 13. Evidence gaps, disclosed

- Which named debt tranche(s) the Sept 10 ~$119M first-tranche repayment
  actually retired is not stated by name in any source reviewed.
- The stated use of the $499.4M net equity-offering proceeds is not
  disclosed in any source reviewed — the debt-paydown/preferred-
  redemption/acquisition-guidance connection drawn in §7 is this
  record's own inference, not a company disclosure, and is labeled as
  such.
- The cause of OMF same-store NOI turning negative (−0.4%) in Q2 2026 is
  not disclosed.
- Q1 2026's own market reaction (around the April 23 offering and May 13
  earnings release) was not gathered — this record's price-reaction
  check (§9) covers only the window most directly relevant to Scout's
  September hook.
- Whether NHP pays a common dividend, and any change to it, was not
  investigated — tangential to the specific hook tested.

---

## 14. Final triage disposition

> ## `NO_DEMONSTRATED_EDGE`

Scout's specific mechanism — debt paydown beyond the sold properties'
own collateral, plus preferred redemption, improving the capital stack
for common shareholders — is real as a narrow fact pattern but is
**directly contradicted, not merely unresolved, by the load-bearing
per-share evidence this record's mandatory hook reconstruction (Fix 1)
surfaced**: a ~156%-dilutive common equity raise, not the asset sale or
the preferred redemption, is the primary-sourced explanation for both
this year's leverage improvement and its Normalized FFO/share decline,
and the one completed-session reaction most directly tied to the hook
(the Sept 10 tranche closing) was negative. This is treated, per this
pilot's standing framing, as a **successful discovery-system outcome**,
not a failure: the new Fix 1/Fix 2 discipline did exactly what it was
adopted to do — killed a plausible-sounding hook cheaply, using primary
evidence gathered specifically to test it, before a full deep-
underwriting variant was written around it.

**No deep underwriting of NHP follows from this record.**

---

## 15. Confirmation — other Batch 003 candidates and all prior states unchanged

UCB, NNBR, SAIA, and TCS remain registered only
(`PILOT3_BATCH_003_REGISTRATION.md`) — **not triaged by this record**,
per instruction. All Batch 001/002 states are unchanged: PATH, MDB, XOM,
PCG `NO_DEMONSTRATED_EDGE`; DOCU, SPXC, SOLS `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`; AAPL `EVIDENCE_GAP`; JPM
`CALENDAR_HOLD` (not advanced); SMH `REFERENCE_PEER_TAPE`; NVDA
`REFERENCE_ONLY`.

---

## What this record does not do

No deep underwriting of NHP. No triage of UCB, NNBR, SAIA, or TCS. No
research of TCS. No Stage 7 or Stage 8. No capital allocated. No scoring,
ranking, or new engine. No advance of JPM or AAPL.

**Capital status: NO REAL PORTFOLIO ACTION.**
