# PILOT 3 — TCS (TECSYS INC.) PRIMARY-EVIDENCE TRIAGE 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Fifth and final Batch 003 candidate to receive primary-evidence
> triage. All figures in **CAD** unless a source explicitly states
> otherwise, per instruction.

| | |
|---|---|
| Date | September 14, 2026 |
| Batch | `PILOT3_BATCH_003_REGISTRATION.md` |
| Candidate | TCS — Tecsys Inc. |
| Discovery type | `NEGLECTED / INSTALLED_BASE_EXPANSION` |
| Source | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY` |
| Prior state | `SURFACE_FOR_TRIAGE` (identity-only) |

---

## 1. Canonical identity — preserved, no new ambiguity introduced

- **Issuer:** Tecsys Inc., **Toronto Stock Exchange**, ticker **TCS**,
  **MIC `XTSE`** — re-confirmed this record via a fresh TwelveData
  `symbol_search`, which returns exactly the same collision set the
  Batch 003 registration already resolved: **Tata Consultancy Services
  Ltd.** (NSE `XNSE`/BSE `XBOM`, India, INR), **Axon Enterprise, Inc.**
  (several German venues, EUR), **TCS Group Holding PLC** (`XSTU`,
  Germany, EUR), and **Tecsys Inc.** itself dual-listed on TSX (`XTSE`)
  and NEO (`NEOE`), both CAD. **The candidate registered and triaged
  here is Tecsys Inc., TSX, MIC `XTSE`, CAD-denominated.**
- **Security type:** common stock; Canadian issuer (incorporated under
  the Canada Business Corporations Act), reporting in CAD under IFRS.
- **No SEC EDGAR CIK** — consistent with a Canadian-domiciled issuer
  filing under Canadian securities law rather than with the SEC. This
  record uses issuer-published primary documents directly rather than
  SEDAR+ search tooling, which is not available to this record.
- **No new fail-closed condition triggered.**

---

## 2. Discovery hook — restated, treated as tentative

> Existing large U.S. healthcare customers may be expanding Tecsys
> Elite from warehouse/pharmacy deployments into hospital point-of-use
> workflows, creating higher installed-base SaaS penetration, RPO
> growth, and recurring revenue without relying primarily on new-logo
> acquisition.

Per instruction, this record does **not** assume RPO automatically
becomes ARR, that named customer expansion automatically means new
recurring revenue, or that SaaS growth automatically creates attractive
shareholder economics — each is tested separately below.

---

## 3. Primary evidence reviewed

- **Q1 FY2027 earnings release** (Tecsys investor-relations site,
  dated September 10, 2026): press release text plus embedded guidance
  table image (`00_FY26Guidance.png`, retrieved and read directly as an
  image since it is not machine-readable text).
- **Q1 FY2027 Interim Report** (financial statements + MD&A,
  `Tecsys Q1 FY27 Interim Report.pdf`), extracted to text via
  `pdftotext` after the initial fetch returned only binary/compressed
  content — condensed interim consolidated financial statements, notes
  (including Note 7, Remaining Performance Obligation), and the full
  MD&A (KPI definitions, 8-quarter selected financial data, liquidity,
  NCIB, subsequent events, outstanding share data).
- **Q1 FY2027 Investor Presentation** (`Investor Presentation Q1
  FY2027.pdf`), same extraction method — corporate overview, TAM/market-
  opportunity slides, Elite SaaS ARR net-retention-rate chart, brokerage
  coverage list, self-disclosed valuation comparison.
- **No issuer-hosted earnings-call transcript was found published** on
  the investor-relations site as of the evidence date — a disclosed
  evidence gap; this record does not use a secondary transcript digest
  to fill it, per instruction that secondary sources may only supplement
  facts unobtainable from primary sources, and treats management
  commentary beyond what is in the MD&A/press release/deck as
  unavailable rather than inferred.
- **NCIB disclosures**: Note (d) to the Q1 FY2027 financial statements
  (share-capital note), and the MD&A's "Outstanding Share Data" section.
- **Secondary/contextual only, clearly labeled as such below**: current
  and recent daily closing prices and volumes (Google Finance,
  stockanalysis.com) — used only because **Gate B could not be attempted
  for this security at all** (§15).

---

## 4. Scout's facts — verified against primary sources, not assumed

| Scout's figure | Primary-sourced actual | Verified? |
|---|---|---|
| Total revenue ≈$50.0M | **$50.048M** (Q1 FY2027) | ✅ Exact |
| SaaS revenue ≈$22.7M | **$22.652M** | ✅ Exact |
| Total SaaS growth ≈+18% | **+18%** YoY (+17% constant currency) | ✅ Exact |
| Elite SaaS growth ≈+24% | **+24%** YoY (+23% constant currency) | ✅ Exact |
| ARR ≈$93.7M | **$93.744M** total SaaS ARR (Elite SaaS ARR alone is $89.636M, +24%) | ✅ Exact — Scout used the correct (total) denominator |
| RPO ≈$259.2M | **$259.154M** SaaS RPO | ✅ Exact |
| Adjusted EBITDA ≈$6.9M | **$6.858M** | ✅ Exact |
| FY2027 Elite SaaS growth guidance raised to 21-23% | **Confirmed exactly** — raised from a **prior 18-20%** range, per the earnings-release guidance table | ✅ Exact |
| NCIB shares repurchased | **17,400 shares**, average price **$33.07**, total cost **$575K (~$0.6M)** | ✅ Confirmed |
| Dividend $0.09 | **$0.09/share**, paid Aug 4, 2026; a further $0.09/share declared Sept 10, 2026, payable Oct 2, 2026 | ✅ Confirmed |

**Every headline fact Scout cited checks out precisely against primary
sources.** This is a materially different starting point than NHP, UCB,
or SAIA, where at least one headline figure required significant
reframing. **This record does not, however, treat factual accuracy
alone as evidence of edge** — the remaining sections test whether these
accurate facts add up to a genuine, unpriced expectations gap.

---

## 5. Narrow Fix 1 — hook reconstruction (8 quarters available, exceeding the 4-period minimum)

**Source: the MD&A's own "Quarterly Selected Financial Data" table
(8 most recently completed quarters).**

| (CAD 000s) | FY27 Q1 | FY26 Q4 | FY26 Q3 | FY26 Q2 | FY26 Q1 | FY25 Q4 | FY25 Q3 | FY25 Q2 |
|---|---|---|---|---|---|---|---|---|
| SaaS revenue | 22,652 | 21,488 | 20,131 | 19,654 | 19,139 | 18,375 | 17,252 | 16,130 |
| Total revenue | 50,048 | 50,045 | 48,496 | 48,641 | 45,960 | 46,555 | 45,181 | 42,442 |
| Adjusted EBITDA | 6,858 | 6,731 | 5,046 | 5,040 | 3,214 | 4,305 | 3,535 | 2,942 |
| **Adj. EBITDA margin (this record's calc)** | **13.7%** | 13.4% | 10.4% | 10.4% | 7.0% | 9.2% | 7.8% | 6.9% |
| Diluted EPS | $0.21 | $(0.02) | $0.12 | $0.12 | $0.05 | $0.11 | $0.08 | $0.05 |

**SaaS revenue YoY growth (this record's calc, same-quarter-prior-year):**
FY26 Q2 **+21.8%** → FY26 Q3 **+16.7%** → FY26 Q4 **+16.9%** → FY27 Q1
**+18.4%** — **roughly stable in a 16.7%-21.8% band, not a clean,
monotonic acceleration** at the total-SaaS-revenue level.

**Adjusted EBITDA margin, however, shows a real, largely monotonic
expansion** over the trailing five quarters (6.9%→7.8%→9.2%→7.0%
[seasonal Q1 dip]→10.4%→10.4%→13.4%→13.7%), and the **same-quarter YoY
comparison is dramatic**: FY26 Q1's 7.0% margin roughly **doubled** to
FY27 Q1's 13.7% — consistent with the company's own "+113%" Adjusted
EBITDA YoY figure.

**Professional services revenue is flat, not growing**: $16.099M (Q1
FY27) vs. $16.039M (Q1 FY26), **+0% YoY (-1% on a constant-currency
basis)** — and **Professional Services Backlog fell 37% YoY (38%
constant currency)**, from $43.694M (Q1 FY26) / $31.906M (Q4 FY26) to
**$27.338M (Q1 FY27)** — **the single most negative, load-bearing data
point this record found**, and one management itself flags directly:
**"the lower professional services backlog level at quarter-end is
expected to have a near-term impact on revenue conversion, resulting in
a slight sequential decline in professional services revenue in Q2
Fiscal 2027."**

**Hardware revenue is up sharply but is a small, disclosed-as-volatile
line** ($3.803M vs. $2.836M, +34% YoY) — management itself states
"hardware revenue tends to be uneven."

**Separating the SaaS headline into its Elite and non-Elite
components (the reconstruction the hook specifically depends on):**
Elite SaaS ARR grew from $72.434M (Q1 FY26) to $89.636M (Q1 FY27), **+24%
YoY** — while **total** SaaS ARR grew only **+18%** over the same window
($79.314M → $93.744M). The MD&A explains the gap directly: **"attrition,
which was proportionately higher within the non-Elite™ SaaS
platform."** **This is the key reconstruction finding**: Elite — the
specific product Scout's hook is about — is growing faster than, and
accelerating relative to, the blended total-SaaS figure (Elite ARR YoY
growth itself accelerated from **+18.6%** at FY26 Q4 to **+24%** at FY27
Q1), while a shrinking non-Elite legacy SaaS book mutes the consolidated
number. **The hook's core growth claim is not flattened or peaked under
reconstruction — it strengthens once Elite is isolated from the blended
total**, a materially different outcome than NHP, UCB, or SAIA.

---

## 6. RPO → ARR → revenue bridge — load-bearing, answered with the primary note

**Source: Note 7 to the financial statements ("Remaining performance
obligation"), which discloses RPO by future recognition period —
evidence this record specifically sought out rather than treating the
$259.2M headline as self-explanatory.**

| Period | SaaS RPO (CAD 000s) | % of total |
|---|---|---|
| Remainder of Fiscal 2027 (~9 months) | $63,794 | 24.6% |
| Fiscal 2028 | $66,665 | 25.7% |
| Fiscal 2029 and thereafter | $128,695 | **49.7%** |
| **Total** | **$259,154** | 100% |

**RPO is, by the note's own definition, SaaS-only** (explicitly
excludes maintenance/support and one-year-or-shorter contracts) — so
unlike some SaaS disclosures, this RPO figure is not conflated with
services backlog (which Tecsys reports and discloses separately, as
"Professional Services Backlog," §5). **This is a genuine positive**:
RPO growth (+14%, +13% constant currency) at least measures the right
thing.

**However, per instruction, RPO is not treated as revenue dollar-for-
dollar**: **nearly half (49.7%) of the RPO balance is not expected to
convert to revenue until Fiscal 2029 or later** — a real, multi-year
recognition tail consistent with the company's disclosed three-to-five-
year SaaS contract terms, but a genuine caution against reading the
$259.2M figure as near-term revenue.

**A finding this record flags but does not force a conclusion on:** SaaS
RPO growth (**+14%**, +13% cc) is running **below** both total SaaS ARR
growth (+18%) and, more notably, Elite SaaS ARR growth (+24%). One
plausible, evidence-consistent explanation is that newer bookings carry
shorter average contract durations than the existing book (which would
grow the one-year-forward ARR metric faster than the multi-year
cumulative RPO metric even at equal booking dollar value) — but **no
source reviewed discloses average contract-term trends directly**, so
this record states the divergence as an observed fact and an open
question, not a resolved finding in either direction.

**Renewals/cancellations:** not separately quantified in dollar terms in
sources reviewed, **but the Elite SaaS ARR net-retention-rate disclosure
(§7) is the closest primary-sourced proxy available**, and is used there
instead of being inferred here.

**Answering the work order's core question directly: rising RPO
represents genuine, contracted future SaaS revenue (not conflated with
services), but its long average duration (half not converting until
FY2029+) makes the headline number, on its own, a weak indicator of
near-term revenue — the RPO growth rate itself is a more useful, if
still imperfect, signal, and it is the slowest-growing of the three
headline recurring-revenue metrics (RPO +14% vs. ARR +18% vs. Elite ARR
+24%).**

---

## 7. Installed-base expansion economics — verified where possible, gap named plainly where not

**Scout's specifically named accounts — Prisma Health, UT Southwestern,
and "another cancer-center/healthcare-system deployment" — were sought
directly in every primary source reviewed (earnings release, full
MD&A text, investor presentation) and were not found in any of
them.** This record's search located no reference to these
institutions by name anywhere in Tecsys's Q1 FY2027 primary disclosure
set. **This is stated plainly, per instruction, rather than assumed away
or silently dropped**: the specific, named-customer color in Scout's
hook is **not corroborated by primary evidence available to this
record**, and no dollar figure for any single named expansion is
disclosed anywhere reviewed.

**What primary evidence does confirm, at the aggregate level, is a
genuine, quantified land-and-expand mechanism:**

- **Elite SaaS ARR net retention rate: 111% (LTM, Q1 FY2027)** —
  explicitly defined by the company as **"(Existing customer expansion
  less churn) divided by Beginning period Elite SaaS ARR"** — i.e., a
  rate above 100% means existing customers are, in aggregate, adding
  more Elite SaaS value than is lost to churn. **The company's own
  trend chart shows this climbing**, from roughly 102% several quarters
  ago to **111% most recently**, with intervening readings around
  106%-113%.
- **83% of SaaS annual recurring revenue is Healthcare**, versus 17%
  General distribution (investor presentation) — consistent with a
  healthcare-concentrated expansion story.
- **Market-sizing evidence, self-disclosed, treated as company framing
  rather than independently verified**: "409 target health systems,"
  a claimed **14%** current market-share penetration of a **$1.6B** U.S./
  Canada health-systems-and-providers ARR opportunity, and a **$153M**
  ARR opportunity "with current base" — i.e., the company's own claim
  that its **existing** installed base alone represents roughly **$153M**
  of addressable ARR, against **$89.6M** of Elite SaaS ARR actually
  captured today (≈59% penetrated of the *existing-base* opportunity
  alone, by this record's own division, **not a company-stated
  percentage**) — **leaving real, quantified room for expansion within
  the current customer base specifically**, independent of new-logo
  acquisition, which is the precise mechanism Scout's hook describes.

**Answering the work order's question directly: this record can
confirm, from aggregate, quantified primary evidence (111% net
retention, a company-claimed $153M-vs-$89.6M in-base opportunity), that
a repeatable, installed-base expansion mechanism with real recurring
economics is plausible and directionally supported.** It **cannot**
confirm the specific named-customer anecdotes Scout cited, or quantify
any single expansion's dollar contribution — **this is a genuine,
disclosed evidence gap**, not filled by inference, and it weakens
confidence in the hook's specific narrative even though the aggregate
mechanism it describes is independently, if more generally, evidenced.

---

## 8. Healthcare concentration / market structure

- **Healthcare share of SaaS ARR: 83%** (investor presentation) — a
  real, disclosed, heavy concentration.
- **U.S. vs. Canada mix**: **74% of Q1 FY2027 revenue was generated in
  U.S. dollars** (72% in Q1 FY2026) — the business is majority
  U.S.-dollar-denominated while costs are predominantly Canadian-dollar,
  creating a real, disclosed FX sensitivity (Q1 FY2027 net favorable FX
  revenue impact of $0.4 million; the U.S. dollar averaged $1.3957 vs.
  $1.3743 a year prior).
- **Hospital/health-system concentration**: "409 target health systems"
  cited as the addressable base; the number of *currently signed*
  customers, and concentration among the largest few, are **not
  disclosed** in sources reviewed — a genuine gap.
- **Competitive position / implementation cycle / switching friction**:
  qualitatively described (healthcare supply chains as "stressed," "point
  of use breakdowns," "fragmented standardization") but **not
  quantified** (no disclosed average implementation timeline, win rate,
  or competitive-displacement data) in sources reviewed.

**Answering the work order's question directly: healthcare
specialization plausibly creates durable expansion economics (the
111% net-retention figure is real, quantified evidence of this), but
this record cannot independently confirm the extent to which
concentration (83% of ARR in one vertical, majority U.S.-dollar
revenue against CAD costs) creates offsetting risk, beyond noting both
factors are real and disclosed — this is presented as a genuine
two-sided finding, not resolved in either direction.**

---

## 9. Services / implementation burden

- **Professional services revenue: flat** ($16.099M vs. $16.039M, +0%
  YoY; -1% constant currency) — **not growing alongside SaaS**, a
  genuine divergence from the "SaaS growth requiring substantial
  services effort" risk the work order asks about; if anything, the
  data shows the opposite risk (§5, §6): **services backlog
  contracting**, with management explicitly guiding to a near-term
  professional-services revenue decline.
- **Gross margin by revenue type, disclosed precisely**: "SaaS,
  maintenance, support and professional services" blended gross margin
  **56%** (Q1 FY27) vs. **53%** (Q1 FY26) — a real, quantified 300bps
  expansion, **attributed by management specifically to "SaaS margin
  expansion,"** not to services efficiency. **"License and hardware"**
  gross margin **23%** (Q1 FY27) vs. **24%** (Q1 FY26), a modest decline
  **"due to a higher mix of lower-margin hardware revenue."**
- **Elite SaaS product margins are disclosed by the company, in the
  investor deck, as "running at over 75%"** on its "latest
  infrastructure" — a high, real, if company-self-reported, figure.
- **Implementation utilization and per-project cost/margin detail: not
  disclosed** in sources reviewed — a genuine gap.

**Answering the work order's question directly: on the evidence
gathered, incremental SaaS growth is improving, not being offset by,
consolidated economics** — gross margin expanded, driven specifically by
SaaS mix, while services revenue and backlog are actually
**contracting**, not consuming disproportionate implementation effort.
**The risk this section anticipated (services burden suppressing
margin) is not what this record found; the more relevant, disclosed
risk is the opposite one — a shrinking services backlog creating a
near-term revenue headwind (§5).**

---

## 10. Capital efficiency / cash conversion

- **Operating cash flow: $5.037 million** (Q1 FY2027) vs. **−$4.657
  million** (Q1 FY2026) — a **$9.7 million** favorable swing, attributed
  by the company to "lower net cash outflows from changes in working
  capital as well as higher profitability."
- **Investing activities used $0.553 million** (Q1 FY2027) vs. $3.039
  million (Q1 FY2026) — primarily deferred development costs
  (capitalized software) and property/equipment; **this record's own,
  labeled estimate of quarterly free cash flow: OCF $5.037M − investing
  outflow $0.553M ≈ $4.48 million** for the quarter (a coarse proxy, not
  a company-reported FCF figure — Tecsys does not itself report a
  distinct "free cash flow" line in sources reviewed).
- **Capitalized development costs, net of tax credits: $0.5 million**
  (both Q1 FY2027 and Q1 FY2026) — small, stable, not a growing drag.
- **Stock-based compensation: $850K** (Q1 FY27) vs. $784K (Q1 FY26) —
  modest, gradually rising, not disclosed as materially dilutive on its
  own (679,471 options excluded from diluted EPS as anti-dilutive,
  against ~14.4M shares outstanding).
- **Working capital**: current assets $82.7M vs. current liabilities
  $73.7M (July 31, 2026) — both declined modestly quarter-over-quarter
  (lower AR/WIP; lower deferred revenue), a normal, not alarming,
  pattern.
- **Dividends**: $0.09/share quarterly ($1.298M total per quarter, per
  the financial statements), a real, funded, recurring cash commitment.
- **NCIB repurchases**: $575K (17,400 shares) in the quarter — small
  relative to the ~$4.48M of estimated quarterly FCF.
- **Net cash position: ~$35.0 million** (cash + short-term investments,
  July 31, 2026), **no funded long-term debt or credit-facility
  borrowings disclosed** in sources reviewed.

**Answering the work order's question directly: yes, on the most
recent quarter's evidence, recurring growth is translating into
materially improved cash economics** — a $9.7M favorable OCF swing,
real (if modest) FCF generation covering both the dividend and the
NCIB comfortably, and a debt-free balance sheet. **This record does not
have a full trailing-twelve-month cash-flow reconstruction** (the
MD&A's quarterly table does not include OCF/FCF by quarter, only
revenue/profit/EBITDA/EPS) — a disclosed limitation; the one-quarter
YoY comparison is treated as a real, positive data point, **not yet a
multi-quarter-confirmed trend**, consistent with how this pilot has
treated single strong quarters elsewhere (e.g., NNBR).

---

## 11. NCIB / dividend economics — checked for materiality, not assumed

- **Authorization**: renewed September 17, 2025 (12-month term to
  September 19, 2026), originally up to **500,000 shares (3.4%** of the
  ~14.81M then-outstanding), **amended March 17, 2026 to up to 900,000
  shares** (≈6.2% of shares outstanding).
- **Actual activity, Q1 FY2027: 17,400 shares repurchased and
  cancelled**, average price **$33.07**, total cost **$575K** — **only
  ≈1.9% of the current 900,000-share authorization used in the quarter**,
  and **≈0.12% of shares outstanding**.
- **Dividend: $0.09/quarter ($0.36/year)** — per the investor
  presentation, this equates to roughly a **1.1%-1.2%** yield at recent
  prices (§15).

**Answering the work order's question directly: capital return here is
routine, not economically material as a standalone thesis driver** — the
NCIB pace is far below its own authorization ceiling, and the dividend,
while real and funded, is a modest yield. **This record does not treat
either as a meaningful, independent source of edge**, consistent with
instruction.

---

## 12. Cheapest falsification test — run first, as instructed

> Are installed-base expansions producing incremental recurring SaaS
> economics that are not already fully captured in RPO/guidance, and do
> they improve consolidated margin/cash conversion?

**Split answer, genuinely mixed, not a clean yes or no:**

- **On margin/cash conversion: yes, clearly** — Adjusted EBITDA margin
  roughly doubled YoY for the same quarter (7.0%→13.7%), gross margin
  expanded 300bps specifically on SaaS mix, and OCF swung $9.7M
  favorably. This half of the test is well-supported.
- **On "not already fully captured in RPO/guidance": weak, leaning
  no.** The very Q1 FY2027 results Scout's hook is built on are the
  **same results the company itself used to raise FY2027 guidance**
  (Elite SaaS growth 18-20%→21-23%; total SaaS 13-15%→16-18%; total
  revenue 2-4%→5-8%; Adjusted EBITDA margin 11-13%→11-14%), announced
  the **same day** (September 10, 2026). **By construction, management
  has already incorporated the installed-base-expansion evidence into
  its own forward guidance** — the specific, credible incremental edge
  a discovery hook would need to demonstrate is not "is Tecsys growing
  well" (already reflected, already guided), but "is Tecsys's
  installed-base expansion likely to run meaningfully **ahead of** the
  just-raised guidance" — and **this record found no primary evidence
  (the unconfirmed named customers being the one place such evidence
  might have lived) to support that specific, forward, above-guidance
  claim.**

**Per instruction, this result weakens the discovery hook materially,
without killing it outright** — this record continues through the
remaining sections, consistent with the instruction's "if no" branch
calling for material weakening rather than an automatic stop, and
because the margin/cash-conversion half of the test is genuinely
strong evidence in the hook's favor even as the "unpriced information"
half is not.

---

## 13. Narrow Fix 2 — priced-in one-liner

> For Tecsys to be mispriced positively, the market must currently be
> assuming that Elite SaaS growth and net retention will merely hold
> near their current, already-strong levels (21-23% guided growth, 111%
> net retention) rather than the installed-base expansion mechanism
> continuing to accelerate beyond what management itself just
> guided — i.e., that the freshly-raised FY2027 guidance is itself
> conservative relative to the true trajectory of existing-customer
> expansion.

**This sentence can be stated, but this record finds it only weakly
supported by the evidence gathered.** Guidance was raised the same day
as the hook's underlying data became public; six sell-side analysts
cover the name and would ordinarily update models on the same
information; and the specific evidence that might most credibly support
"guidance is still conservative" — the named large-account expansions
Scout cited — **could not be located in any primary source reviewed**
(§7). **Per instruction, since the expectations gap cannot be credibly
articulated with the evidence available, this record does not promote
on this basis.**

---

## 14. Neglect / attention test

- **Analyst coverage: six sell-side firms** — ATB Cormark Capital
  Markets, Canaccord Genuity Corp, National Bank Financial, Raymond
  James, Stifel, and TD Cowen (investor presentation, "Brokerage
  coverage" slide). **This is not a genuinely uncovered name** by
  conventional analyst-coverage standards — six covering brokers is
  meaningful institutional attention for a company of this size.
- **Trading liquidity: genuinely, severely thin.** Daily closing volumes
  reconstructed for the two weeks surrounding the Q1 FY2027 release
  (secondary source, stockanalysis.com, clearly labeled as such — see
  §15's disclosure on why a certified source was unavailable): **371
  to 4,385 shares/day on non-event days** (Sept 2, 4, 8, 9, 10), spiking
  to **110,192 shares on September 11** (the session after the earnings
  release) before falling back toward more normal levels (5,546 shares,
  September 14). **This is a real, quantified, primary-adjacent
  mechanism by which important operating information could remain
  under-synthesized in the price** — even with six analysts nominally
  covering the name, a market this thin limits how much capital can
  practically act on new information without moving the price
  substantially, and limits the depth of continuous price discovery
  between event days.
- **Institutional ownership**: not reliably found in primary sources
  reviewed; **insider ownership is disclosed at 16%** (investor
  presentation) — a real, if partial, data point on ownership structure,
  not the same as institutional-ownership breadth.
- **Frequency of investor communication**: quarterly earnings releases
  with a full MD&A and investor presentation, consistent with standard
  Canadian issuer practice — **no issuer-hosted call transcript was
  found published**, a modest, disclosed gap relative to larger-cap
  peers that typically post full transcripts.

**Answering the work order's question directly: yes, there is a
credible mechanism — not from a lack of analyst coverage, but from
genuinely thin trading liquidity, which limits how efficiently new
information gets reflected in price even when analysts are nominally
watching.** Per instruction, **this is treated as context, not proof of
edge** — thin liquidity cuts both ways: it can mean information is
under-synthesized, or it can simply mean any single day's price move
(including the September 11 spike, §16) carries less informational
weight than it would in a liquid name.

---

## 15. Valuation checkpoint — coarse, explicitly not falsely precise, and with an honest data-availability limitation stated up front

**Gate B could not be attempted for this security at all — a genuine,
disclosed limitation, not a workaround.** Two independent reasons: (1)
`XTSE` is **not** a MIC supported by this project's live session
calendar (`live_session_calendar.SUPPORTED_MICS` covers only `XNYS`/
`NYSE`, `XNGS`, `XNMS`, and `ARCX`); (2) the configured TwelveData plan
returned `"This symbol is available starting with the Grow or Venture
plan"` when queried directly for `TCS` on the TSX. **Per this project's
standing discipline, this record does not manufacture a certified fresh
price where none can be obtained — it uses the most recent reliable
data available and labels it plainly as uncertified.**

- **Most recent primary (company-disclosed) reference point**: the Q1
  FY2027 investor presentation states **market capitalization of
  $482 million** and **14,416,937 shares outstanding**, both **as of
  July 31, 2026** — implying a per-share price of **≈$33.44**, closely
  consistent with the Q1 FY2027 NCIB average repurchase price of
  **$33.07** (same quarter).
- **Secondary, uncertified, context-only price data** (Google Finance;
  stockanalysis.com), gathered because no certified source exists:
  closing prices around **$28.25-$29.40** in the days immediately
  before the September 10, 2026 release, rising to **≈$31.36-$31.44**
  by September 14, 2026, with a **52-week range of $22.51-$38.00**.
- **Using the more recent, though uncertified, ≈$31.40 reference
  price** and **14,416,937 shares**: **market capitalization ≈$452.7
  million.** **No funded debt was found disclosed** (§10) — **enterprise
  value, this record's own coarse estimate: ≈$452.7M − $35.0M
  cash/short-term investments ≈ $417.7 million.**
- **EV/Revenue (TTM $197.230M, per the investor presentation's own
  TTM column): ≈2.1x** — closely consistent with the company's own
  self-disclosed **"2.2x NTM EV/Sales"** figure (a forward, not
  trailing, basis, so the near-match is a reasonable cross-check, not
  an exact reconciliation).
- **EV/ARR (SaaS ARR $93.744M): ≈4.45x.**
- **EV/EBITDA (TTM Adjusted EBITDA $23.675M, per the investor
  presentation): ≈17.6x.**
- **FCF yield**: using this record's own quarterly FCF estimate (§10,
  ≈$4.48M) annualized ×4 as an **illustrative, explicitly labeled**
  run-rate (**not a true TTM figure**, since only one quarter's cash-
  flow detail was available) ≈$17.9M/year against the ≈$417.7M EV
  estimate ≈ **4.3%** — a coarse illustration only.
- **Dividend yield**: $0.36/year ÷ ≈$31.40 ≈ **1.1%.**

**The company's own self-disclosed valuation framing**: the investor
presentation states Tecsys trades at **"2.2x NTM EV/Sales, a 75%
discount to its closest comparable MANH [Manhattan Associates]"** — a
real, company-promoted data point this record notes but does **not**
independently verify (no separate Manhattan Associates valuation
reconstruction was performed) and does **not** treat as evidence of
edge on its own, per instruction not to rely on peer multiples alone.

**Answering the work order's question directly: today's valuation
(≈17.6x EV/EBITDA, ≈4.45x EV/ARR) is a full, growth-company multiple,
not a distressed or obviously cheap one** — it already appears to
require continued mid-teens-to-20%-plus SaaS growth and continued
margin expansion roughly in line with the just-raised guidance, **not**
a material beat above it. This is consistent with, not contradictory
to, this record's §12/§13 findings.

---

## 16. Market reaction — reconstructed from the best available (uncertified) evidence, with the data-availability limitation restated

| Date | Close (CAD) | Volume | Note |
|---|---|---|---|
| 2026-09-02 | $29.40 | 371 | Pre-release, extremely thin |
| 2026-09-04 | $29.20 | 1,276 | Pre-release |
| 2026-09-08 | $28.44 | 2,312 | Pre-release |
| 2026-09-09 | $28.25 | 1,945 | Day before release |
| **2026-09-10** | **$28.55** | **4,385** | **Release day — muted same-day reaction, only +1.1%, on still-thin volume** |
| **2026-09-11** | **$30.42** | **110,192** | **T+1 — the real reaction: +6.5% on ~25-50x normal volume** |
| 2026-09-14 | $31.36-$31.44 | ~5,546 | Continued drift upward, volume normalizing |

**The reaction was materially delayed, not same-day** — the release
itself (September 10) produced almost no price or volume response;
the substantial move came on **September 11**, coincident with a huge
relative volume spike, plausibly consistent with sell-side analyst notes
following the six-broker coverage list (§14) reaching investors a day
after the release, though this record does not have direct evidence of
that specific mechanism and does not assert it as fact.

**Cumulative reaction, pre-release ($28.25, Sept 9) to most recent
(≈$31.40, Sept 14): approximately +11%** — a real, meaningful positive
market reaction to the Q1 FY2027 results and the raised guidance.

**Answering the work order's question directly: yes, the market has
already reacted substantially, on the same facts Scout's hook and this
record's own reconstruction rely on** — an ≈11% move in under a week is
not a sign the installed-base-expansion story remains hidden or
unrecognized following the September 10 disclosure. **Per instruction,
this record does not treat the small-cap price move as proof of edge on
its own** — the extreme thinness of pre-event volume (a few hundred to
a few thousand shares/day) means this record places only modest
confidence in reading the September 11 spike as a fully efficient,
complete repricing, but it is nonetheless the best available evidence
that the market has begun to, not failed to, incorporate this
information.

---

## 17. Market-could-be-right case

- **The specific named-customer evidence Scout's hook depends on for
  color and scale (Prisma Health, UT Southwestern, a cancer center)
  could not be corroborated in any primary source** — a reasonable
  investor could discount the "point-of-use expansion" narrative
  specifically, even while crediting the aggregate net-retention data.
- **RPO growth (+14%) trails both SaaS ARR growth (+18%) and Elite ARR
  growth (+24%)** — a reasonable investor could read this as a sign that
  new bookings carry shorter contract durations or smaller multi-year
  commitments than the existing book, i.e., a quality dilution not
  visible in the headline ARR growth figures.
- **Professional Services Backlog fell 37-38% YoY, and management
  itself guided to a Q2 FY2027 professional-services revenue decline**
  — a reasonable investor could see this as an early signal of slowing
  new-deployment momentum, not merely a services-mix curiosity.
- **Nearly half of RPO does not convert until FY2029 or later** — a
  reasonable investor could argue the "backlog" headline overstates
  near-term visibility.
- **Guidance was just raised on the same information this hook relies
  on** — a reasonable investor could conclude any genuine
  expectations gap has already been closed by management's own
  disclosure and the market's ≈11% reaction, leaving little room for a
  "the market hasn't noticed yet" thesis.
- **83% healthcare/majority-U.S.-dollar revenue concentration** creates
  real, disclosed FX and vertical-concentration risk a reasonable
  investor could weight heavily for a company this size.
- **Valuation (≈17.6x EV/EBITDA, ≈4.45x EV/ARR) is a full growth
  multiple**, not a discount to intrinsic value — a reasonable investor
  could argue the market already rewards the recurring-revenue
  narrative fully.
- **Extremely thin trading liquidity** is itself a risk, not only an
  opportunity — a reasonable investor could require a liquidity
  discount rather than read illiquidity as a pure source of
  informational edge.
- **NCIB is economically immaterial** (§11) — not a meaningful offset to
  any of the above.

**This case is credible, built entirely from this record's own
findings, and is not a strawman.**

---

## 18. Tentative variant — refined, not rejected outright, but not promotable as framed

> Tecsys may be benefiting from a repeatable installed-base expansion
> model in U.S. healthcare, where existing customers add higher-value
> Elite modules across facilities, driving recurring SaaS economics
> faster and more durably than the market currently expects.

**Refined, not rejected.** The **general mechanism** — existing
customers expanding Elite SaaS faster than they churn, evidenced by a
111% net-retention rate that has itself been climbing — is **real and
well-corroborated** by aggregate primary evidence. **What is not
supported is the "faster and more durably than the market currently
expects" clause specifically** — the market's own information set (the
same Q1 FY2027 results), the company's own freshly-raised guidance, and
the market's own ≈11% reaction all point toward this mechanism being
**recognized, not overlooked**, as of the evidence date. The **named,
specific** customer-expansion color that might have supported a
still-larger, still-underappreciated opportunity **could not be
verified**. **The variant survives in a narrowed, more modest form**
(the mechanism is real) but **fails the specific "underappreciated"
claim** the discovery hook requires for promotion.

---

## 19. What Atlas added beyond the original Scout hook

- **Verified every one of Scout's headline figures precisely against
  primary sources** — a distinct, useful confirmation given this
  pilot's prior experience of hooks whose headline facts did not survive
  scrutiny (NHP, UCB).
- **Found that Scout's specifically named customer expansions (Prisma
  Health, UT Southwestern, a cancer center) are not corroborated in any
  primary Tecsys disclosure reviewed** — a material specificity gap the
  original hook's framing did not flag.
- **Located and quantified the Elite-vs-total-SaaS growth divergence**
  (Elite ARR accelerating 18.6%→24% while blended total SaaS ARR held
  roughly flat at 18%, due to shrinking non-Elite attrition) — a more
  precise, and more favorable to the hook, characterization than
  Scout's headline SaaS-growth figure alone conveyed.
- **Found and quantified the Elite SaaS ARR net-retention rate (111%
  LTM, climbing from ~102%)** — direct, aggregate, primary evidence for
  the "installed-base expansion" mechanism, not present in Scout's hook.
- **Discovered the RPO maturity schedule** (nearly half not converting
  until FY2029+) via the financial-statement note, directly testing and
  substantially qualifying the "RPO growth" half of the hook.
- **Found and flagged the 37-38% YoY collapse in Professional Services
  Backlog**, and management's own explicit guidance to a near-term
  professional-services revenue decline — a real, negative,
  forward-looking data point absent from Scout's hook.
- **Established that FY2027 guidance was raised the same day as the
  hook's underlying data**, directly informing the cheapest-
  falsification and priced-in-one-liner findings that this record's
  central conclusion rests on.
- **Reconstructed the actual (delayed, T+1, volume-spike-driven) market
  reaction** and quantified the ≈11% cumulative move, using the best
  available (uncertified) data after confirming Gate B could not be
  attempted for this security at all — a limitation this record
  disclosed rather than papered over.

---

## 20. Neglected-name learning classification

> **`NEGLECT_PARTIAL`**

Six sell-side analysts cover Tecsys, so the "neglected" label does not
hold in the conventional coverage sense — but genuinely thin trading
liquidity (a few hundred to a few thousand shares on non-event days) is
a real, quantified, disclosed mechanism by which price discovery could
still lag available information even with nominal coverage. **This is
a Pilot 3 learning observation only, not a permanent scoring field.**

---

## 21. Uncertainty classification

> **`POTENTIAL_SOURCE_OF_EDGE`**

Whether the installed-base expansion mechanism (111% net retention,
climbing) continues to accelerate beyond the just-raised FY2027
guidance — the one question this record could not resolve because the
specific named-customer evidence needed to test it is not available in
primary sources — is classified as a potential source of edge, not
thesis-blocking, because the aggregate mechanism is real and improving,
not deteriorating or contradicted; this record simply lacks the
specific forward evidence needed to state confidently that it exceeds
what management itself has already guided. **This is a Pilot 3 learning
observation about this record, not a permanent architecture field or a
score.**

---

## 22. Final disposition

> ## `NO_DEMONSTRATED_EDGE`

Every headline fact in Scout's hook is verified, and the aggregate
installed-base-expansion mechanism (111% Elite SaaS net retention,
climbing; Elite ARR accelerating to 24% YoY even as the blended total
SaaS figure looks merely stable) is real, primary-sourced, and — unlike
NHP, UCB, or SAIA — **strengthens, not weakens, under the mandatory
hook reconstruction.** What this record cannot demonstrate is a
**still-open, unpriced expectations gap**: the specific named-customer
evidence that might have supported "the market hasn't caught up yet"
could not be corroborated in any primary source; FY2027 guidance was
raised on the **same** Q1 results this hook relies on; and the market's
own reaction (≈+11% over the following days, mostly concentrated in one
high-volume session) indicates the story has already begun to be
priced, not ignored. The cheapest-falsification test (§12) and the
priced-in one-liner (§13) both come back weak on the "not already
captured in guidance" dimension specifically, which is the dimension
that determines whether a real business (which this evidently is)
also represents a demonstrated Atlas edge (which this record does not
find). **This is not a finding that Tecsys is a weak company** — cash
conversion, margin expansion, and net retention are all genuinely
strong and improving — but **this specific discovery hook does not
survive the test of showing the market has not already recognized
what it describes.**

**No deep underwriting of TCS is performed by this record.**

---

## 23. Preserve other Batch 003 candidates and all prior states — unchanged

NHP remains `NO_DEMONSTRATED_EDGE`
(`PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md`). UCB remains
`NO_DEMONSTRATED_EDGE`
(`PILOT3_UCB_PRIMARY_EVIDENCE_TRIAGE_001.md`). NNBR remains
`BLOCKED_BY_MATERIAL_UNCERTAINTY`
(`PILOT3_NNBR_DEEP_UNDERWRITING_001.md`). SAIA remains
`NO_DEMONSTRATED_EDGE`
(`PILOT3_SAIA_PRIMARY_EVIDENCE_TRIAGE_001.md`). **No prior candidate is
advanced by this record.** All other Pilot 3 states are unchanged: PATH,
MDB, XOM, PCG `NO_DEMONSTRATED_EDGE`; DOCU, SPXC, SOLS
`BLOCKED_BY_MATERIAL_UNCERTAINTY`; AVGO `BLOCKED_BY_MATERIAL_UNCERTAINTY`;
AAPL `EVIDENCE_GAP`; JPM `CALENDAR_HOLD`; SMH `REFERENCE_PEER_TAPE`;
NVDA `REFERENCE_ONLY`. **Batch 003 is now fully triaged — all five
registered candidates (NHP, UCB, NNBR, SAIA, TCS) have received
primary-evidence triage.**

---

## 24. Shadow sentiment

No sentiment observations were encountered or used in this record. Had
any arisen, they would have been labeled `SHADOW` and excluded from the
disposition, per the Batch 003 charter.

---

## What this record does not do

No deep underwriting of TCS. No Stage 7 or Stage 8. No capital
allocated. No scoring, ranking, or new engine. No advance of any prior
Batch 003 candidate, JPM, or AAPL. No Batch 004.

**Capital status: NO REAL PORTFOLIO ACTION.**
