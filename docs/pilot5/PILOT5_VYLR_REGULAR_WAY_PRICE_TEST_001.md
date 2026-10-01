# PILOT 5 — VYLR OCTOBER 1 REGULAR-WAY PRICE & DISLOCATION TEST 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Price test only. No capital decision. No Stage 7. No position size,
> allocation score, conviction score, sizing formula, optimizer, or price
> target.

| | |
|---|---|
| Date | October 1, 2026 (evidence gathered after the close, ~6:50 PM EDT) |
| Prior state | `READY_FOR_WI_PRICE_TEST` (frozen, `PILOT5_VYLR_PRE_WI_FUNDAMENTAL_UNDERWRITING_001.md`); active trigger `WAIT_FOR_VYLOR_REGULAR_WAY_PRICE_TEST` |
| Question | Does VYLR's first completed regular-way session show an investable dislocation against the frozen pre-trading underwriting? |

---

## 1. Event confirmation

| Item | Finding | Source class |
|---|---|---|
| Distribution completed | Yes. Vylor press release (Oct 1): separation completed, NYSE trading under `VYLR` beginning Oct 1. Pro rata dividend, record date Sept 24, **one Vylor share per Corteva share**, expected prior to 9:30 a.m. ET Oct 1. | Issuer press release; Corteva 8-K (`d23835d8k.htm`) |
| Identity | Vylor Inc., CIK `0002128626`, NYSE (`XNYS`), ticker `VYLR`, USD. **Ticker and exchange now confirmed in issuer primary text** (the underwriting had it secondary-sourced). CUSIP `US92892R1086` appears only in a secondary aggregator. | Issuer / aggregator |
| Shares outstanding | **Not stated in any primary document I could read.** 1:1 distribution against ≈667.2M Corteva shares gives ≈667M. Yahoo's market cap ÷ price (45.543B ÷ 68.26) implies ≈667.2M, which agrees but is not independent evidence. Treated as **derived, not confirmed**. | Derived |
| Change in separation terms | The Corteva 8-K records that the board **waived the "Legal Restraints Condition"** as of Sept 30, 2026. No change to the 1:1 ratio, record date, or distribution date was found. | Corteva 8-K |
| Trading plan change | Superseding event already recorded (commit `c77dd86`): no WI market, no Corteva ex-distribution market. Reconfirmed by an issuer-notice summary (Cultivar). **Contradiction noted:** one secondary article (Pomegra) says WI trading ran Sept 25–30, and MarketScreener labels a Sept 25–30 "VYLR.WI" series at ≈$77–79. Those prices equal Corteva's cum-distribution tape (CTVA prior close $77.65 = the "VYLR.WI" Sept 30 close), **not VYLR trades**. The issuer account governs. | Cross-check |
| Debt exchange | Offers expired 5:00 p.m. Sept 30. Tendered: 2.300% 2030 $434.8M (86.97%); 5.125% 2032 $476.2M (95.24%); 4.800% 2033 $527.6M (87.93%); **total ≈ $1,438.6M** (as of the Sept 29 announcement). The pre-spin filing assumed $1,280M of Vylor Notes, so exchanged notes may run ≈$159M higher. **Final settlement results and a post-close capitalization table were not found.** | Corteva/Vylor 8-K exhibits |
| Newly disclosed standalone costs or liabilities | **None found.** No stranded-cost or dis-synergy quantification, equity-award treatment, or TSA fee figure surfaced. | — |

New facts that bear on the thesis (see §4): **Vylor was added to the S&P 500
on Oct 1, replacing Corteva**; Corteva moves to the S&P MidCap 400 effective
before the open Oct 6 (replacing Olin); Vylor's GICS sector changes to
Consumer Staples effective Oct 6 (S&P Dow Jones Indices release).

---

## 2. Price evidence and certification

**Certification status: `UNCERTIFIED — GATE B BLOCKED FOR VYLR`.**

- `TWELVEDATA_API_KEY` is absent from the environment, as are the Alpaca and
  Tiingo keys; `.env` holds SEC-only configuration. The existing
  `live_price_binding` path therefore cannot produce a bound `PriceSnapshot`
  for VYLR. VYLR also has no registered security key in Atlas.
- No attempt was made to bypass this. Public aggregator figures below are
  **uncertified research evidence** and are not presented as certified.
- Only price-control-governed data may support Stage 7. None exists.

Completed-session figures (Oct 1, 2026, NYSE `VYLR`), after the close at
~6:50 PM EDT:

| Field | Yahoo Finance | MarketScreener | Other (Pomegra and a search summary) |
|---|---|---|---|
| Open | 66.00 | 66.00 | ≈66 |
| High | 74.95 | 75.00 | ≈70 (intraday, stale) |
| Low | 65.00 | 65.00 | — |
| Close | **68.26** (4:04 PM) | **68.26** | ≈69 (+4.5%) |
| Volume | 14,991,996 | 14,988,861 | 7,740,459 (apparently a partial-session snapshot) |
| After hours | 70.70 (6:30 PM) | — | — |

Yahoo and MarketScreener agree on open, low, close and volume (within 0.02%).
They may share one upstream feed, so agreement is **not** independent
confirmation. The high differs by $0.05. The "previous close 66.00" shown by
Yahoo is a reference price for a new listing, not a trade. MarketScreener's
"−12.09%" change is an artifact of comparing to the Corteva cum-distribution
series and **carries no information about VYLR**.

Working figures used below: **close $68.26; volume ≈15.0M; shares ≈667.2M
(derived)**. Provenance and timestamps are as shown; no tick or intraday-bar
data was obtained.

Context: CTVA was reported at **$12.75 (−83.6%) as of a 9:57 AM snapshot**,
not a close; I did not verify a CTVA close. Prior CTVA close (cum-distribution)
was $77.65. Illustrative combined value: $12.75 + $68.26 = $81.01, +4.3%
versus $77.65. This mixes a morning snapshot with a close and is **context
only**. No sector or industry comparator (peer seed names, XLB/staples) was
retrieved, and none is claimed.

---

## 3. Price against the frozen pre-trading underwriting

Frozen inputs (§16 of the underwriting) are used exactly as committed; no
assumption was rebuilt from today's price.

| Measure | Value | Basis |
|---|---|---|
| Market capitalization | **≈ $45.5B** | $68.26 × ≈667.2M (shares derived) |
| EV, frozen "structural" net debt ($2.436B LT debt − $1.1B cash = $1.336B) | **≈ $46.9B** | frozen convention |
| EV, full pro forma borrowings ($5.579B − $1.1B = $4.479B) | **≈ $50.0B** | seasonal borrowings included |
| EV/EBITDA on FY2025 Seed EBITDA $2,636M | **≈ 17.8x** (structural) / **≈ 19.0x** (full) | frozen EBITDA base |
| Same EV on the "strong execution" EBITDA (+15% = $3,031M) | ≈ 15.5x (structural) | vs frozen strong band 13–15x |

Position against the frozen sensitivity map ($/share, illustrative):

| Frozen scenario | Band | Close $68.26 vs band | Implied move from $68.26 to band midpoint |
|---|---|---|---|
| Downside economics | ≈ $25–28 | **≈ 2.4–2.7x** the band | ≈ −61% |
| Reasonable/base | ≈ $36–43 | ≈ +58% to +90% above the band | ≈ −42% |
| Strong execution | ≈ $57–65 | **≈ 5% above the top of the band** | ≈ −11% (−4.8% to the top) |

- **§17 threshold test.** The underwriting said VYLR would warrant further
  capital comparison only if traded value fell "meaningfully below" the
  downside band (~$25–28). The first-session **low was $65.00**, so the
  threshold was never approached.
- **Remaining upside under the original assumptions: none.** VYLR traded at
  or above the top of the frozen strong-execution band for the entire
  session. This is the §18 **Scenario B** ("valuation remains rich"), not
  Scenario C.
- **Unavailable inputs, disclosed.** (a) Confirmed shares outstanding.
  (b) Post-close debt and cash (exchange settlement, revolver draws, the cash
  paid to New Corteva). (c) Fully diluted shares (equity-award treatment
  not located). (d) Standalone-cost and dis-synergy figures. (e) Any
  post-spin earnings. (f) Net debt is the frozen pro forma, not a Oct 1
  balance sheet; the ≈$159M of extra exchanged notes would move EV ≈0.3%
  and change no conclusion.
- Management's 2029 targets (net sales $11.2–11.9B; operating EBITDA
  $3.3–3.7B) were stated at launch. They are **issuer claims, not Atlas
  facts**, and are not used in valuation. For context only, EV ≈ $46.9B is
  ≈13.4x the $3.5B midpoint of a target four years out.

---

## 4. Forced-flow test

The hypothesis was not demonstrated at entry and is not demonstrated now.

**Observed**
- **The central mechanism did not occur.** The triage rested on S&P 500
  index-related selling of a spun entity held by CTVA's index holders.
  Vylor was **added to the S&P 500 on Oct 1 as Corteva's replacement**. S&P
  500 index funds keep exposure through VYLR and have no required sale from
  that index. The mechanism the triage treated as credible and "unresolved"
  is resolved against it for the S&P 500 holder base.
- **Volume was modest.** ≈15.0M shares ≈ **2.2% of ≈667M outstanding**.
  Even if every share traded were a forced seller (impossible), that is only
  ≈11–23% of the preserved exploratory 65–135M figure.
- **Price path.** Opened 66.00, low 65.00, high ≈74.95–75.00, close 68.26,
  after-hours 70.70. Opening supply was absorbed and price recovered above
  the open. That pattern is *consistent* with absorbing opening supply, but
  it is equally consistent with ordinary first-day price discovery.
  Without intraday bars, I cannot say when the low and high occurred.

**Inferred, not observed**
- Some selling by holders mismatched on sector (Corteva was GICS Materials;
  Vylor moves to Consumer Staples on Oct 6) or on other benchmarks (Russell,
  MSCI, style and sector funds, non-US index) cannot be ruled out. I did
  not verify treatment under any of those. I read none of the Solactive
  notice.
- Constrained supply **cannot be meaningfully bounded** from available
  evidence. The 65–135M figure remains `EXPLORATORY_CONTEXT_ONLY`.

**Conclusion:** no evidence of ownership-dislocation selling that drove
price below a defensible value. A price decline would not have proven forced
selling, and here there was no decline against the frozen map. The price
*rose* over the first-session open.

---

## 5. Fundamental separation

Nothing in the first session separates the five explanations by pricing,
because price is **above** the frozen strong-execution band; there is no weakness to explain.

| Candidate explanation | Assessment |
|---|---|
| Actual forced flow | Not observed. S&P 500 retention; low turnover. |
| New capital structure | Not testable; post-close capitalization not located. |
| Seed-industry fundamentals | No new data. |
| Dis-synergies | Still unquantified (the cheapest falsification fact in §20 of the underwriting remains unresolved). |
| Ordinary price discovery | Best fit: the market priced the stub at a premium to the frozen map. |

**Strongest market-could-be-right case.** The market may be capitalizing
what the frozen map under-weighted: a ≈$500M+ gross licensing stream
targeted for 2027, a #1 U.S. seed franchise with three years of expanding
margins, and the possibility that seed genetics deserve a scarcity multiple
well above the 10–12x Atlas used as base. The frozen multiples were "this
record's own judgment calibration" with no peer study, so the gap
(≈17.8x versus 10–12x) may measure the calibration's weakness, not the
market's error. Either way, **a price 5% above the frozen strong case
cannot be called a dislocation in Atlas's favor.**

---

## 6. Capital opportunity question

> Is VYLR trading at a sufficiently attractive valuation, relative to the
> original independent underwriting, to justify Stage 7 comparison?

**No.** On the frozen map VYLR traded at or above the strong-execution case
all session; the §17 entry condition was missed by more than 2x.

> Does VYLR remain the cleanest expression of the opportunity?

**No evidence that it is.** The S&P 500 index event is now known to run
*through* Corteva: Corteva (down ~84% on the distribution) moves from the
S&P 500 to the MidCap 400 effective Oct 6, which implies a mechanical sale
by S&P 500 holders and a purchase by MidCap holders. That is a forced-flow
mechanism of a different kind, on a different security. **It is recorded as
an observation only. It was not researched and is not a candidate.** No
candidate is created; any examination needs an explicit new work order.

---

## 7. Final disposition

> ## `NO_DEMONSTRATED_INVESTABLE_DISLOCATION`

Why not `BLOCKED_BY_MATERIAL_UNCERTAINTY`: the price is uncertified, but the
conclusion does not depend on certification. The Oct 1 low ($65.00) is
2.3x the §17 threshold; a certified price would need to differ from the
public figures by more than 50% to change the answer. **Certification would
be required before any Stage 7 step, so the blocker is preserved, not waived.**
Why not `CONTINUE_REGULAR_WAY_OBSERVATION_FOR_SPECIFIC_EVIDENCE`: no specific
pending evidence would reverse a price above the strong case. The one open
item (dis-synergy costs) can only lower value from here, not create a
discount.

This disposition applies to Vylor at the first-session price. It is not a view
that the business is poor: the frozen `SOLID_CYCLICAL_BUSINESS` finding stands.

---

## 8. What Atlas learned by underwriting before trading

- The pre-trading work paid off in **speed and discipline**: the frozen map
  and the §17 threshold gave a pass/fail answer within hours of the first
  close, with no anchoring on the opening price.
- It also showed what pre-trading work **cannot** do. The forced-flow premise
  rested on an index outcome that was still unknown at underwriting. The
  result went against it (S&P 500 retention). Pre-trading work did not
  produce an edge; it produced a fast, honest falsification.
- Early relative to trading was not early relative to market recognition, as
  the Red Team checkpoint warned. The market priced the stub above Atlas's
  strongest case.
- The frozen multiples (10–12x base) were uncalibrated judgment with no peer
  study. A further calibration is a Red Team question, not a license to
  reshape the frozen map after seeing the price.
- Data hygiene: aggregator tapes can mislabel (the "VYLR.WI" series is
  Corteva's tape; one site's volume is a partial snapshot). Certified-price
  controls exist for this reason.

---

## 9. Isolation and scope

Unchanged: Vylor triage and underwriting records, Crasus
(`NO_DEMONSTRATED_FORCED_FLOW_EDGE`), MSG Rangers
(`NO_DEMONSTRATED_FORCED_FLOW_EDGE`), Pilot 4 records, the frozen control
layer, the facade. No code, test, or configuration changed. No Scan 002
started. No new candidate. No new data provider. No capital decision.

**Capital status: NO REAL PORTFOLIO ACTION.**
