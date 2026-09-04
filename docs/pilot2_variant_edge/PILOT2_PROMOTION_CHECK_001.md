# PILOT 2 — PRIMARY EVIDENCE PROMOTION CHECK 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Narrow promotion-confirmation step only. No valuation/return underwriting
> performed. No capital allocated. No ranking. No sizing.

| | |
|---|---|
| Date | September 4, 2026 |
| Scope | FIS, MELI, JD (tentatively advanced) · GLNG (evidence-gap resolution) |
| Out of scope | FISV, ADBE, SNOW, WCC, NTR, CVS — not reopened |
| Predecessor record | `PILOT2_INITIAL_TRIAGE_001.md` (commit `cb4feea`) |

---

## Method

Every claim below is checked against **authoritative primary sources**:
SEC EDGAR filer/identity data pulled through Atlas's own `sec_adapter.py`
(`resolve_cik`, `get_company_submissions`, `get_recent_filings`), and the
actual SEC-filed exhibit text (8-K/6-K press-release exhibits) fetched
directly from `sec.gov`. Filing classification was **not** assumed from
memory. Where earnings-call commentary (not written into the filed exhibit
text) is used, that distinction is stated explicitly. Analyst-consensus
framing is cited only as evidence a market narrative exists, never as the
thesis itself.

---

## 1. Identity / filing classification — confirmed via SEC EDGAR

| Ticker | Issuer (SEC) | CIK | Filer category | Filing regime | Reporting currency | Most relevant current primary documents |
|---|---|---|---|---|---|---|
| **FIS** | Fidelity National Information Services, Inc. | 0001136893 | Large accelerated filer | Domestic — 10-Q / 8-K | USD | 8-K filed 2026-01-12 (acc. 0001136893-26-000003→**0001193125-26-009759**, Item 2.01, transaction closing); 8-K filed 2026-02-24 (acc. 0001136893-26-000009, Item 2.02, FY26 guidance introduced); 8-K filed 2026-08-04 (acc. 0001136893-26-000046, Item 2.02, Q2 2026 results/updated guidance); 10-Q filed 2026-08-04 (acc. 0001136893-26-000050) |
| **MELI** | MercadoLibre, Inc. | 0001099590 | Large accelerated filer | Domestic — 10-Q / 8-K (not a 20-F filer, despite LatAm operations) | USD | 8-K filed 2026-08-05 (acc. 0001099590-26-000021, exhibit 99.1, Q2 2026 results); 10-Q filed 2026-08-06 (acc. 0001099590-26-000023) |
| **JD** | JD.com, Inc. | 0001549802 | Large accelerated filer | **Foreign private issuer — 20-F (annual) / 6-K (interim)** | RMB (primary), with USD convenience references in commentary | 6-K filed 2026-08-13 (acc. 0001193125-26-347753, exhibit 99.1, Q2 2026 results); 20-F filed 2026-04-16 (acc. 0001193125-26-157870, FY2025 annual report) |
| **GLNG** | Golar LNG Limited | 0001207179 | Large accelerated filer | **Foreign private issuer — 20-F (annual) / 6-K (interim)**, Bermuda domicile | USD | 6-K filed 2026-08-19 (acc. 0001628280-26-057847, H1 2026 interim report); 20-F filed 2026-03-26 (acc. 0001628280-26-021198, FY2025 annual report) |

Correction to the initial triage record: FIS's most consequential 8-K for the
Worldpay/Issuer Solutions transaction is the **January 12, 2026** filing
(Item 2.01, completion), not the January 22 filing (which is an unrelated
director-appointment 8-K, Item 5.02) — both were pulled and distinguished
directly from EDGAR rather than assumed.

---

## 2. FIS

### What primary evidence confirms

The January 12, 2026 8-K exhibit (Item 2.01) states the transaction verbatim:
FIS acquired Global Payments' Issuer Solutions business (formerly TSYS,
"the world's largest issuing business") at an enterprise value of $13.5B / net
purchase price of $12.0B, while divesting its remaining 45% minority stake in
Worldpay. The release states **"$500 million in incremental Adjusted Free
Cash Flow in 2026"** and **"$700 million by 2028"** — described as "expected
additional" amounts, i.e., a company projection, not formal guidance. No
quantified offset for the lost Worldpay economics is disclosed in this
exhibit, and no integration-risk language appears in it.

FY2026 guidance was **introduced** February 24, 2026 (8-K, Item 2.02):
adjusted revenue growth 30–31% ($13,770–$13,850M), adjusted EPS $6.22–$6.32
(+8–10%), adjusted FCF $2.05–$2.15B (+27–33%). No segment-level guidance was
given even at introduction.

The **August 4, 2026** Q2 2026 8-K exhibit shows an **updated** FY2026 outlook:
adjusted revenue growth trimmed to 29–30%, adjusted EPS growth trimmed to
7.0–8.5%, but **adjusted FCF guidance raised by $100M to $2,150–$2,250M**. The
exhibit states Issuer Solutions integration is "ahead of plan" and contributed
193bps of margin expansion in Banking Solutions. **No mention of a Capital
Markets divestiture review appears in the written press-release exhibit
itself.**

That claim — CEO Stephanie Ferris stating Capital Markets "sales are behind
plan in the first half of the year" and that FIS is "evaluating strategic
alternatives for specific products within Capital Markets that do not align
with the core focus" — is sourced to the **August 11, 2026 earnings-call
transcript** (reported via Motley Fool and financial press), not the filed
exhibit text. This distinction is preserved rather than blurred. Capital
Markets segment revenue grew 3.2–3.5% with a modest 32bps margin contraction
attributed to "higher labor costs and timing."

**Market reaction, dated and specific:** FIS stock fell **more than 10% in
premarket trading** on the Q2 print (August 4, 2026) and was down **~32.6%
year-to-date** as of that report — a large, immediate, observable reaction.

### Promotion test

**Yes — a specific, falsifiable disagreement exists.** The same disclosure
event contained both a raise (FCF, +$100M) and a cut (revenue/EPS, modest) plus
a named, segment-specific weakness (Capital Markets) and a segment-specific
strength described as "ahead of plan" (Banking/Issuer Solutions, +193bps
margin). The >10% single-session decline and the size of the YTD decline
(32.6%) suggest the market may be pricing this as one undifferentiated
"guidance cut" event rather than two distinguishable segment stories — a
testable claim, not an adopted opinion.

### `PROMOTE_TO_DEEP_UNDERWRITING`

- **`observable_priced_in`:** Stock down ~32.6% YTD, >10% in one session on the
  Aug 4, 2026 print, following a guidance trim and disclosed Capital Markets
  strategic review.
- **`potential_atlas_variant`:** The deterioration is segment-specific
  (Capital Markets, +3.2–3.5% growth, modest margin contraction) while
  Banking/Issuer Solutions is "ahead of plan" with a raised, quantified FCF
  guide (+$100M) in the same release — the two may be getting valued as one
  undifferentiated negative event.
- **`why_gap_can_exist`:** A single mixed disclosure (one raise + one cut +
  a divestiture review, the last disclosed on the call rather than in the
  press-release text) is exactly the kind of release that can produce a
  same-day overreaction to the negative headline over the positive, harder-to-
  parse detail.
- **`variant_wrong_if`:** Capital Markets softness proves to be a leading
  indicator that later reaches Banking/Issuer Solutions (management's own
  cited causes — geopolitical tension, trade-policy caution — are
  macro, not segment-specific); or the disclosed $500–700M FCF accretion
  proves to be an unrealized projection as integration matures past its
  current "ahead of plan" early phase.

---

## 3. MELI

### What primary evidence confirms

The August 5, 2026 8-K exhibit confirms: credit portfolio $16.06B, **+75% YoY**
(credit card ~47% of mix, up from 43% a year prior); headline 15–90 day NPL
7.0% overall / 4.6% credit card, both "near historic lows." This part of the
initial triage claim is **confirmed as stated.**

Beyond it, the exhibit discloses figures the initial triage did not have:
**provisions for doubtful accounts grew 85% YoY** ($690M → $1,276M in Q2),
**outpacing the 75% portfolio growth rate.** Allowance for credit losses rose
from $3,057M (Dec 31, 2025) to $4,251M (Jun 30, 2026). **NIMAL** (net interest
margin after losses — the loss-adjusted profitability metric) fell 2ppts YoY
to 20.7%; **credit-card NIMAL specifically moved from breakeven to −2.5%
YoY.** Management attributes this to "new cohort dilution" that "matures" per
historical pattern (2.6M new cards issued in Q2'26 vs. 1.6M in Q2'25), stating
explicitly this is not a sign of "deterioration in asset quality."

### Promotion test

**Yes — more specific than "credit is growing rapidly but losses might rise."**
The falsifiable claim: the widely cited headline NPL figure (near historic
lows) is the metric most visible in coverage, but the loss-adjusted
profitability metric (NIMAL) and the provisioning growth rate (85% vs. 75%
portfolio growth) tell a less favorable story that the headline NPL framing
does not surface. Management has offered a specific, testable explanation
(temporary cohort dilution); whether NIMAL recovers over the next several
quarters is directly observable and falsifiable.

### `PROMOTE_TO_DEEP_UNDERWRITING`

- **`observable_priced_in`:** Headline 15–90 day NPL (7.0% / 4.6%), cited by
  the company and consensus as "near historic lows," is the dominant credit-
  quality reference point.
- **`potential_atlas_variant`:** Provisions grew faster (85%) than the
  portfolio (75%), and credit-card NIMAL moved from breakeven to −2.5% YoY —
  a loss-adjusted deterioration the headline NPL metric does not capture.
- **`why_gap_can_exist`:** NPL is the simplest, most-cited credit metric;
  NIMAL and the provisioning growth-rate delta require reading further into
  the earnings materials than the headline figure.
- **`variant_wrong_if`:** Credit-card NIMAL recovers toward breakeven or
  positive over the next 2–3 quarters as new cohorts mature, without further
  acceleration in provisioning intensity relative to portfolio growth — this
  would validate management's own explanation and the "credit quality is
  fine" framing.

---

## 4. JD

### What primary evidence confirms

The August 13, 2026 6-K exhibit provides segment detail the initial triage
did not have. Consolidated revenue: RMB346.4B, **−2.9% YoY**, which management
attributes to "a high base effect" from Q2 2025. New Businesses (incl. food
delivery): revenue RMB7.3B, **−47.6% YoY**; operating loss narrowed from
RMB14.8B to RMB9.9B, a ~RMB4.9B improvement, driven by deliberately narrowing
investment. Non-GAAP net income +21% YoY to RMB8.9B — **confirms** the initial
triage's profit/loss-shrinkage framing.

What the initial triage **did not surface**: **JD Retail — the core
segment, excluding New Businesses entirely — also declined, −4.7% YoY**
(RMB295.4B vs. RMB310.1B), even as its margin held (4.6% vs. 4.5%). Within
that, product revenue fell 5.4%, and **electronics/home appliances — JD's
historical flagship category — fell 11.8%.** Service revenue (marketplace +
logistics) grew 6.8%, partially offsetting. R&D spending rose 37.7% YoY
despite the revenue decline.

### Promotion test

**Yes — more specific than "margins may improve if loss-making businesses
lose less money."** That exact reduced thesis is explicitly what the
governing question warns against, and the segment data shows the real
question is sharper and arguably more consequential: **the core JD Retail
segment itself contracted, led by an 11.8% decline in JD's traditional
flagship electronics/appliance category** — not merely a New Businesses
consolidation effect. Management's "high base effect" explanation is a
specific, dated, falsifiable claim: if correct, JD Retail growth should
reaccelerate once the comparison laps in coming quarters.

### `PROMOTE_TO_DEEP_UNDERWRITING`

- **`observable_priced_in`:** Consolidated non-GAAP profit "inflection"
  (+21% YoY), attributed in coverage to disciplined capital allocation as
  food-delivery losses shrink.
- **`potential_atlas_variant`:** JD Retail (core, ex–New Businesses) itself
  declined 4.7% YoY, led by an 11.8% drop in electronics/appliances — the
  segment JD's franchise was built on — which a "profit improved because
  losses shrank" framing does not address.
- **`why_gap_can_exist`:** A single consolidated non-GAAP profit headline is
  simpler and more attention-grabbing than the underlying segment math; "high
  base effect" is management's own explanation and has not been independently
  checked against category-level competitive data.
- **`variant_wrong_if`:** JD Retail revenue reaccelerates once the cited
  high-base-effect comparison laps in coming quarters, without further
  deterioration specifically in electronics/appliances — supporting
  management's timing explanation over a structural share-loss variant.

---

## 5. GLNG

### What primary evidence confirms — and adds

The August 19, 2026 6-K (H1 2026 interim report) confirms the two operating,
already-contracted assets are real and long-dated: **FLNG Gimi** — 20-year
Lease and Operate Agreement with **bp**, achieved COD mid-June 2025, H1 2026
revenue of $261.1M across liquefaction/lease/management-fee components.
**FLNG Hilli** — new 20-year charter with **Southern Energy S.A. (SESA)** in
Argentina commencing 2027, following expiry of its prior Cameroon contract.

What the initial triage **did not find**, because it relied on earnings-call
coverage rather than the interim-report risk-factor and liquidity language:
**FLNG Esperanza** (the "MKII" unit) has a signed 20-year SESA charter and a
~$2.45B EPC, partially funded by a **$600M senior secured RCF closed August
2026 — an 18-month facility**, with longer-term asset-level financing still
being pursued. The **fourth FLNG unit** (EPC with CIMC Raffles, ~$2.45B, FID
executed August 12, 2026) has **no signed end-user contract disclosed** and is
explicitly described as a speculative build. The filing states directly:
absent a successful capital raise, **management "may need to pause the FLNG
Esperanza conversion project and terminate the EPC contract for the fourth
FLNG unit,"** with that determination disclosed as due **before the end of
Q3 2026** — a deadline concurrent with the date of this record. Net debt is
~$1.77B ($2.68B total debt against $908.5M cash/deposits), with a $50M minimum
consolidated-cash covenant.

Financial press coverage of the same period is uniformly framing this as
unambiguous growth confirmation ("Golar LNG Greenlights Fourth FLNG as Q2 2026
Earnings Surge," "A New Era of Growth," "Golar presses ahead with fourth FLNG
unit") — a search for any subsequent resolution of the capital raise (through
early September 2026) found no confirmation either way; as of this record,
the outcome is genuinely not yet publicly known.

### Promotion test

**Yes — the contract/financing structure produces a specific, testable
mispricing thesis, and the prior evidence gap is resolved into a sharper
one.** This is not "the structure is too complex to assess" (the original
finding); it is a specific, dated, binary, disclosed contingency: does the
capital raise needed to avoid terminating the fourth FLNG EPC succeed before
the Q3 2026 deadline management itself named? Growth-story press coverage
does not foreground this; the primary filing states it plainly.

### `PROMOTE_TO_DEEP_UNDERWRITING`

- **`observable_priced_in`:** Press coverage of the Q2 2026 print and the
  4th-unit EPC signing is uniformly framed as confirmed growth (implicitly
  assuming the ~$800M 2028 run-rate EBITDA target, which itself depends on
  both newbuilds completing).
- **`potential_atlas_variant`:** The fourth unit has no end-user contract and
  is explicitly disclosed as contingent on a capital raise that, absent
  success, leads management to state it may terminate the EPC — with a
  Q3 2026 determination window essentially concurrent with today.
- **`why_gap_can_exist`:** The financing contingency sits in interim-report
  liquidity/risk-factor language, not the growth-story headlines that
  dominate general coverage of the order itself.
- **`variant_wrong_if`:** Golar completes the referenced long-term
  asset-level/corporate financing before the disclosed Q3 2026 window — a
  fact that should become publicly verifiable very soon via a subsequent
  6-K or press release, making this an unusually near-term-resolvable test.

---

## 6. Output table

| Ticker | Primary evidence reviewed | Triage claim confirmed? | Observable priced-in evidence | Potential variant | Main uncertainty | Final promotion state | Reason |
|---|---|---|---|---|---|---|---|
| **FIS** | 8-K (2026-01-12, Item 2.01); 8-K (2026-02-24, Item 2.02); 8-K (2026-08-04, Item 2.02); Q2 earnings-call commentary | **Confirmed and sharpened** — FCF figures verified verbatim; the "Capital Markets divestiture" element traced to call commentary, not the press-release exhibit text | Stock ≈−32.6% YTD, >10% single-session decline on the Aug 4 print | FCF-accretion vs. headline optics tension is segment-specific (Capital Markets weak, Banking/Issuer Solutions "ahead of plan") | Whether Capital Markets softness is contained or a leading macro indicator | **`PROMOTE_TO_DEEP_UNDERWRITING`** | Specific, quantified, same-release tension between a raise and a cut, with a large dated market reaction |
| **MELI** | 8-K (2026-08-05, exhibit 99.1) | **Confirmed as stated, and sharpened** — NPL figures verified; deeper NIMAL/provisioning data adds a more specific angle | Headline 15–90 day NPL "near historic lows" is the dominant cited metric | NIMAL/provisioning growth outpaces portfolio growth; headline NPL doesn't capture it | Whether cohort-dilution explanation holds as cohorts mature | **`PROMOTE_TO_DEEP_UNDERWRITING`** | Cleared the "more specific than credit-growing-losses-might-rise" bar via a distinct, falsifiable metric (NIMAL) |
| **JD** | 6-K (2026-08-13, exhibit 99.1) | **Confirmed, and materially reframed** — original triage undersold the finding; core JD Retail itself declined, not just a New Businesses mix effect | Consolidated non-GAAP profit "inflection" (+21% YoY) narrative | JD Retail (core) revenue −4.7% YoY, electronics/appliances −11.8% | Whether "high base effect" (management's claim) or structural share loss explains the core decline | **`PROMOTE_TO_DEEP_UNDERWRITING`** | Cleared the explicit "losses lose less money" exclusion via a specific, segment-level, core-franchise finding |
| **GLNG** | 6-K (2026-08-19, H1 2026 interim report) | **Evidence gap resolved into a sharper, dated finding**, not a "clean growth story" | Press coverage frames the 4th-unit order as unambiguous growth confirmation | 4th FLNG unit has no signed contract and a disclosed Q3 2026 termination contingency absent a completed capital raise | Whether the capital raise completes before the disclosed deadline — not yet publicly known | **`PROMOTE_TO_DEEP_UNDERWRITING`** | Primary filing produces a specific, dated, binary, testable mispricing thesis the original "too complex" framing could not |

---

## Promote to deep underwriting

**FIS, MELI, JD, GLNG** (unranked).

## Do not advance

None in this scope.

## Evidence gap remains

None in this scope — GLNG's prior evidence gap is resolved into a specific,
dated, near-term-resolvable question (see above), not converted into
`NO_DEMONSTRATED_EDGE` and not left as an open gap.

---

## What this record does not do

No valuation, return band, or return target was produced. No capital was
allocated. No promoted name is ranked against another. FISV, ADBE, SNOW, WCC,
NTR and CVS were not reopened. No architecture, code, basket, venue control,
Stage 7/8 process, or sentiment disposition was touched.

**Next step, not taken here:** full valuation/return underwriting of FIS,
MELI, JD and GLNG.

**Capital status: NO REAL PORTFOLIO ACTION.**
