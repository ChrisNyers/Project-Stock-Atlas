# PILOT 3 — UCB PRIMARY-EVIDENCE TRIAGE 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Second Batch 003 candidate to receive primary-evidence triage, and the
> second record governed by the two narrow fixes
> (`pilot3/PILOT3_BATCH_003_CHARTER.md`).

| | |
|---|---|
| Date | September 14, 2026 |
| Batch | `PILOT3_BATCH_003_REGISTRATION.md` |
| Candidate | UCB — United Community Banks, Inc. |
| Source | `GROK_SCOUT_UNDER_SURFACE_DISCOVERY`, as-of 2026-09-12 |
| Prior state | `SURFACE_FOR_TRIAGE` |

---

## 1. Canonical identity — re-confirmed, no ambiguity reappeared

- **Issuer:** United Community Banks, Inc., **NYSE**, ticker **UCB**, **MIC
  `XNYS`**, SEC CIK `0000857855` — re-verified directly against SEC EDGAR
  company submissions (unchanged from the Batch 003 registration record).
- **Collision check re-run:** the prior resolution against **UCB SA**
  (Belgian pharmaceutical, Euronext Brussels, MIC `XBRU`) and the stale
  **UCBI** (Nasdaq) legacy-ticker artifact still holds — no new ambiguity
  appeared in this record's own identity/price lookups. **Fails closed
  correctly:** this record's Gate B bind (§18) used the CIK-qualified
  `expected_security_key` and `expected_mic=XNYS` exactly as before.

---

## 2. Discovery hook — restated, treated as tentative

> The Navitas exit, HTM-to-AFS securities repositioning, realization of
> low-yield securities losses, debt paydown, and expanded buyback may
> collectively improve UCB's future earnings quality and risk profile
> more than the market is crediting.

Per instruction, **this record does not assume balance-sheet
restructuring creates value merely because duration declines** — that is
the specific thing tested below (§8), and it does not survive intact.

---

## 3. Primary evidence reviewed

- **8-K filed 2026-09-08, 11:30 UTC** (accession `0001104659-26-105666`,
  exhibits `tm2624931d1_ex99-1.htm` press release and
  `tm2624931d1_ex99-2.htm` investor presentation) — securities
  repositioning, debt paydown, expanded buyback authorization.
- **8-K filed 2026-09-08, 18:42 UTC** (accession `0001104659-26-105855`,
  exhibit `tm2624990d1_ex99-1.htm`) — Navitas sale, quoting CEO Lynn
  Harton and CFO Jefferson Harralson directly (a special-call transcript
  excerpt embedded in the release).
- **10-Q for Q2 2026** (accession `0000857855-26-000076`) — used for
  balance-sheet cross-checks (equity, shares outstanding, goodwill).
- **Q2 2026, Q1 2026, Q4/FY2025, and Q3 2025 earnings-release exhibits**
  (accessions `0001104659-26-085229`, `0001104659-26-045714`,
  `0001104659-26-003548`, `0001104659-25-101399`) — used specifically for
  the Fix 1 4-period hook reconstruction (§7).
- **8-K filed 2026-08-03** (accession `0000857855-26-000069`, exhibit
  `exhibit991-pressreleaseann.htm`) — Peach State Bancshares acquisition
  closing.
- **SEC XBRL company facts** (CIK `0000857855`) — diluted EPS, dividends
  declared, stockholders' equity, shares outstanding, goodwill/intangibles
  — used to independently cross-check the press-release figures.
- **Equity price series** (TwelveData), 2026-08-24 through 2026-09-14 —
  checked directly.

Secondary sources were not used for economics; none were needed given
the depth of primary disclosure (an unusually well-documented pair of
8-Ks, including transcript-style management remarks).

---

## 4. Navitas exit — economics reconstructed

- **Sale consideration:** **$2.0 billion cash**, at a **7% premium**
  (per CEO Lynn Harton, on the record).
- **Pretax gain:** **$68 million**, to be recognized in **Q3 2026**.
- **Book value of assets disposed:** **not disclosed** in any source
  reviewed — an evidence gap; only the $2.0B proceeds and $68M gain are
  given, from which a book value of roughly $1.93B can be inferred
  (proceeds minus gain, before transaction costs/taxes), but this is
  **this record's own arithmetic, not a company-disclosed figure**, and
  is labeled as such.
- **Revenue/earnings contribution lost:** management states selling
  Navitas and reinvesting the proceeds **"takes about $0.07 of quarterly
  earnings"** — i.e., this figure is already stated net of a
  reinvestment assumption, not gross Navitas earnings alone; the
  reinvestment offset is disclosed separately (§5) rather than netted
  invisibly.
- **Credit-risk contribution surrendered:** **material and disclosed**
  (§13) — Navitas is confirmed to account for roughly half of total
  net charge-offs company-wide despite being a minority of the loan
  book.
- **Capital released:** **+145 basis points of CET1** (Navitas-specific,
  per CFO Jefferson Harralson) — driven predominantly by risk-weighted-
  asset reduction (removing higher-risk-weight equipment-finance
  receivables from the balance sheet), not primarily by the gain itself.
- **Reserve release:** **~$38 million ALLL release in Q2 2026** tied to
  the pending Navitas sale (held-for-sale reclassification).
- **Timing:** closed **September 1, 2026**.
- **Taxes / transaction costs:** **not disclosed** in any source
  reviewed — an evidence gap.

**Answering the work order's question directly:** UCB surrendered a
loan/lease platform that was disproportionately responsible for the
company's credit losses, in exchange for $2.0B of cash, a one-time $68M
gain, and 145bps of capital — a genuine, quantified de-risking trade,
**not** primarily an earnings-generating trade (the earnings given up
are real and stated plainly by management, not hidden).

---

## 5. Securities restructuring — reconciled, not accepted at face value

- **Reclassified HTM→AFS:** **$2.2 billion.**
- **Actually sold:** **~$2.6 billion book value** of lower-yielding
  securities (a larger figure than the reclassified amount — meaning
  some AFS securities beyond the newly-reclassified HTM pool were also
  sold, or the reclassified pool itself was larger than what was
  ultimately sold and retained in part; **this record does not resolve
  the precise overlap** between the $2.2B reclassification and the
  $2.6B sale figure from the sources reviewed — a disclosed evidence
  gap).
- **Prior yield / duration:** **2.20% weighted-average yield**, **~5.5
  year average duration**, **~6.5 year weighted average life.**
- **Replacement:** reinvested into **cash and short-duration
  securities** at **~4.5% yield**, **~2 year average duration.**
- **Realized pretax loss:** **~$300 million** — the two source exhibits
  differ slightly on whether this figure is stated gross or net of the
  Navitas gain (one framing referenced "$300 million pretax loss...net
  of $64 million gain from Navitas," a second, separately-sourced
  management quote states the Navitas gain as **$68 million**); **this
  $64M-vs-$68M discrepancy is not reconciled by this record** — treated
  as a disclosed, immaterial-to-the-conclusion inconsistency between two
  same-day disclosures, not resolved by assuming either is correct.
- **Expected annual income benefit:** management states the reinvestment
  **"adds about $0.06 of earnings per quarter"** (≈$0.24/year — the two
  figures are the same benefit stated on two timeframes, not additive).
- **Tangible book value / capital impact:** **this is the single
  largest number in the entire package** — see §9's dedicated bridge.
- **AOCI impact:** not separately quantified in sources reviewed — an
  evidence gap; realization of the loss moves it from an AOCI
  (unrealized) position into realized GAAP earnings/equity, but the
  precise pre-transaction AOCI balance was not disclosed.

**Per instruction, this record does not accept the stated "yield
improvement" without reconciling the loss required to obtain it** — see
§7's bridge, which finds the reinvestment benefit **roughly offsets, but
does not exceed, the earnings given up elsewhere in the same package.**

---

## 6. Debt paydown — verified, only partially quantified

- **Amount repaid:** **$1.0 billion** of borrowings.
- **Funding cost repaid:** **~3.80%.**
- **Annual interest savings: not explicitly quantified** in any source
  reviewed — a genuine evidence gap on a specific dollar figure,
  although a coarse, labeled estimate is possible: $1.0B at ~3.80% funding
  cost, if not replaced by any new borrowing, implies roughly **~$38
  million of gross annual interest expense avoided** — **this record's
  own arithmetic, not a company-disclosed figure**, and pretax before
  any offsetting reduction in interest income the repaid funds might
  otherwise have earned if left invested (they were not — they came from
  the Navitas/securities proceeds, which are being redeployed
  elsewhere).
- **Loan-to-deposit ratio, pro forma:** **~75%** (management-disclosed).
- **Deposit mix:** not separately reconciled pre/post in sources
  reviewed.

**Answering the work order's question directly:** the evidence supports
**structurally better funding, not merely relief of temporary pressure**
— the $1.0B was wholesale/borrowed funding at a real, disclosed cost
(~3.80%), repaid with permanent proceeds (asset-sale cash), not rolled
into new short-term debt; the pro forma ~75% loan-to-deposit ratio is a
conservative, not stretched, level for a regional bank of this size.

---

## 7. Narrow Fix 1 — hook reconstruction (4 reporting periods) and the restructuring bridge

| Metric | Q3 2025 | Q4 2025 | Q1 2026 | Q2 2026 |
|---|---|---|---|---|
| NIM (FTE) | 3.58% | 3.62% | 3.65% | **3.68%** |
| Loan yield | 6.21% | 6.05% | 5.99% | 6.03% |
| Deposit cost (interest-bearing) | 2.68% | 2.39% | 2.27% | 2.27% |
| CET1 (preliminary) | 13.4% | 13.4% | 13.4% | **13.5%** |
| Tangible book value / share | $21.59 | $22.24 | $22.56 | **$23.31** |
| Diluted operating EPS | $0.75 | $0.71 | $0.70 | $0.71 |
| Operating ROA | 1.33% | 1.22% | 1.22% | 1.22% |
| Operating ROTCE | 13.56% | 13.31% | 13.05% | **13.0%** |

**What the reconstruction shows, before layering on the September
actions:**

1. **NIM has been improving every single quarter for a full year**
   (3.58%→3.68%), driven by deposit costs falling faster (2.68%→2.27%)
   than loan yields (6.21%→6.03%) — a real, already-in-progress positive
   trend that **predates** and is **independent of** the September
   restructuring.
2. **CET1 has been stable and strong (13.4–13.5%) for four straight
   quarters** — the restructuring is being executed from a position of
   genuine capital strength, not distress.
3. **Tangible book value per share has been growing every quarter**
   (+8.0% over the year, $21.59→$23.31) — this is the trend the
   September restructuring interrupts (§9).
4. **Diluted operating EPS has been flat, not trending up**, for a full
   year ($0.75→$0.71→$0.70→$0.71) — there is no pre-existing earnings
   growth trend for the restructuring to build on; it starts from a
   flat base.
5. **Operating ROTCE has been quietly declining every quarter**
   (13.56%→13.0%) even as NIM improved — a real, disclosed, mildly
   negative trend this record does not paper over; likely reflects
   equity growing faster than net income, but the specific cause is not
   disclosed in sources reviewed (evidence gap).

**The restructuring bridge, from the company's own investor-presentation
walkforward (page 7, "EPS & TBV Impacts"):**

| Component | Quarterly EPS impact |
|---|---|
| Baseline operating EPS | $0.74 |
| Navitas sale | **($0.07)** |
| Portfolio restructure (reinvestment) | **+$0.06** |
| Peach State acquisition | +$0.02 |
| Core bank growth | +$0.02 to +$0.04 |
| **Updated baseline operating EPS** | **$0.78** |

**This bridge is the single most important primary-evidence finding in
this record:** the Navitas sale (−$0.07) and the portfolio-restructure
reinvestment benefit (+$0.06) — **the two pieces that are actually
Scout's hook** — net to **−$0.01 per quarter, essentially a wash,
slightly negative.** The entire **net increase** in the updated baseline
($0.74→$0.78, +$0.04) comes from **two sources unrelated to the
Navitas/securities-reset pairing**: the Peach State acquisition (+$0.02,
which the work order explicitly instructs not to let "contaminate" this
thesis) and "core bank growth" (+$0.02–0.04, an explicitly
**management-dependent, not contractual**, future assumption per §10).

**Per Fix 1's rule ("stop if the advertised earnings improvement
disappears after this bridge"): it does disappear.** The specific
earnings-quality claim in Scout's hook — that the Navitas exit and
securities reset together improve earnings — is not corroborated by
management's own numbers once Peach State and unguided future growth are
excluded. **A different, narrower claim — that the transaction improves
risk/funding profile at roughly no net earnings cost — remains
standing** and is tested on its own terms below (§13).

---

## 8. Cheapest falsification test — run first, per instruction

> Does the expected recurring earnings benefit from securities
> reinvestment + debt paydown + capital redeployment materially
> compensate for the realized TBV loss and earnings contribution lost
> from Navitas?

**No.** On management's own bridge (§7), the securities-reinvestment
benefit (+$0.06/quarter) very nearly offsets the Navitas earnings loss
(−$0.07/quarter) but does not exceed it, and no separate dollar figure
for debt-paydown interest savings is disclosed to add to this side of
the ledger (§6's ~$38M/year is this record's own coarse estimate, not
company-guided, and is pretax, before any partially offsetting reduction
elsewhere). **Per instruction, "if not: the hook weakens materially" —
it does.** This record does not proceed to build a full bullish variant
around the earnings-improvement framing; it proceeds to test the
narrower risk/funding-based framing on its own merits (§13).

---

## 9. Tangible book value bridge — load-bearing

- **Q2 2026 ending TBV/share (actual, pre-restructuring):** **$23.31.**
- **Q3 2026E pro forma TBV/share (post-restructuring, management-
  disclosed):** **~$21.36.**
- **Decline:** **~$1.95/share, or ~8.4%** — this single transaction
  erases **roughly three full quarters** of the steady TBV growth shown
  in §7's reconstruction ($21.59 at Q3 2025 → $23.31 at Q2 2026).
- **Components not separately broken out** by management in sources
  reviewed: the realized securities loss, the Navitas gain, the tax
  effect, and any share-count effect are not individually reconciled to
  the $1.95/share total — only the before/after totals are given. This
  record does not manufacture a component breakdown that was not
  disclosed.

**Earnback estimate — explicitly coarse, no false precision:** using the
updated baseline operating EPS ($0.78/quarter) against the current
$0.25/quarter dividend, roughly **$0.53/quarter (~68%) is retained**
before any buyback use of that capital. At that retention rate, fully
"earning back" $1.95/share of TBV from **total** company earnings (not
isolating the restructuring's own slightly-negative contribution) would
take **very roughly 3.5–4 quarters, under a year** — **this is a rough,
labeled illustration using the company's total updated EPS, not proof
that the restructuring itself pays for its own TBV damage** — recall
(§7–§8) the restructuring's own two pieces net to roughly zero; the
earnback, to the extent it happens, is being funded by the **whole
company's** earnings (including Peach State and core growth), not by the
Navitas/securities trade in isolation.

---

## 10. Earnings replacement — tested independently, not accepted as claimed

Scout's claim (management "largely replaces Navitas earnings through
securities/funding changes") is **only about half corroborated**:

- **Navitas earnings lost:** −$0.07/quarter (management-stated, net of
  reinvestment framing already built in per their own language — see
  §4).
- **After-tax income gained from higher-yield securities:**
  +$0.06/quarter (management-stated).
- **After-tax interest saved from debt paydown:** **not separately
  quantified** by management; this record's own coarse, pretax estimate
  (§6) is ~$38M/year gross, not confirmed as incremental to the
  $0.06/quarter reinvestment figure or already embedded within it — a
  genuine, unresolved double-counting risk this record flags rather than
  resolves.
- **Incremental income from future loan growth:** the "+$0.02 to +$0.04"
  core-bank-growth component is **explicitly management-dependent, not
  contractual** — this record separates it accordingly and does not
  credit it as near-certain.

**Contractual/near-certain economics: −$0.07 (Navitas) and +$0.06
(reinvestment) — a net −$0.01/quarter.** **Management-dependent future
assumptions: +$0.02 (Peach State, a separate, already-closed but still
integration-dependent acquisition) and +$0.02–0.04 (core growth,
entirely unguided beyond the range shown).** The claim that Navitas
earnings are "largely replaced" is **true only if Peach State and
unguided core growth are counted as replacement — neither of which
Scout's own hook named.**

---

## 11. Capital and buyback

- **CET1 before (Q2 2026, preliminary):** **13.5%.**
- **CET1 pro forma (Q3 2026E, post-Navitas/securities/Peach State,
  combined):** **"above 13%"** — the individual contribution of the
  securities loss and the Peach State acquisition to this figure are
  **not separately disclosed**; only Navitas's own +145bps is broken
  out. This record does not reverse-engineer precise component figures
  from an aggregate guide.
- **Regulatory minimum/buffer context:** 13%+ CET1 is well above
  standard well-capitalized thresholds — this is a strongly, not
  marginally, capitalized bank both before and after.
- **Buyback authorization:** **$100 million increase** to the existing
  program, extended through **December 31, 2027.**
- **Shares actually repurchased:** **$87 million in 2026 year-to-date**
  (disclosed as $37M in Q1 and a further tranche later in the year;
  source exhibits' figure attribution to "Q3" for the second tranche
  appears to be a labeling artifact in the fetched text, since this
  amount was disclosed before Q3 2026 had ended — **this record does not
  correct or assume a specific quarter for that $50M figure beyond what
  is stated**, flagging the inconsistency rather than resolving it).
- **Per instruction, the $100M authorization increase is not credited
  as executed** — only the $87M YTD figure is treated as realized
  capital return.

**Answering the work order's question directly:** excess capital is
**genuinely available** — CET1 stays comfortably above 13% even after
absorbing the securities loss and the (small) Peach State deal, and the
buyback has a real, if modest, execution track record ($87M YTD) — but
capital is also **being actively used** for restructuring and
acquisition purposes concurrently, not held purely for per-share value
increase; this record treats it as **both**, not exclusively either.

---

## 12. Peach State — isolated, not allowed to contaminate the thesis

- **Deal size / consideration:** **not disclosed** in the closing press
  release reviewed — an evidence gap.
- **Peach State's scale at closing (June 30, 2026):** **$784 million
  total assets, $524 million total loans, $707 million total deposits**
  — roughly **2–3% of UCB's own balance sheet**, confirming this is a
  small, bolt-on transaction, not a scale-changing one.
- **Purchase-accounting marks (loan mark, CDI, goodwill):** **not
  disclosed** in the press release reviewed — an evidence gap.
- **Closing date:** **August 3, 2026.**
- **EPS contribution:** +$0.02/quarter, per the investor-deck bridge
  (§7) — the only quantified figure tying Peach State into this
  record's analysis, and it is **explicitly excluded** from the
  Navitas/securities-reset earnings test (§7–§10) per instruction.

---

## 13. Credit-risk quality — the strongest-corroborated half of the hook

- **Navitas's share of total net charge-offs:** **~50%**, per the
  investor presentation, despite Navitas being a **minority** of UCB's
  total loan book — a real, quantified, disproportionate credit-risk
  concentration.
- **Bank-wide NCOs excluding Navitas:** **0.10% of average loans,
  year-to-date** — a genuinely low, clean figure for the remaining loan
  book.
- **Navitas-specific NCO in the last reported quarter before sale:**
  **$3.7 million in Q2 2026** alone.
- **Reserve release tied to the sale:** **~$38 million ALLL release in
  Q2 2026.**
- **CRE concentration, criticized/classified assets, NPAs, and reserve
  coverage for the remaining book:** **not separately disclosed** in
  sources reviewed beyond the NCO figures above — a genuine evidence gap
  this record does not fill by inference.

**Answering the work order's question directly: this is a real,
quantified reduction in credit risk, not merely an earnings-repositioning
story dressed up as one.** Of everything tested in this record, the
credit-risk-concentration finding is the **most directly and cleanly
corroborated** piece of Scout's hook — considerably stronger evidence
than the earnings-improvement claim (§7–§10), which did not hold up
equally well.

---

## 14. Narrow Fix 2 — priced-in one-liner

> For UCB to be mispriced **positively**, the market must currently be
> assuming that removing a loan platform responsible for roughly half of
> total net charge-offs, and cutting securities-portfolio duration from
> 5.5 years to 2 years, is worth **less** than the ~8.4% tangible-book-
> value hit taken to achieve it — when in fact the reduced credit and
> interest-rate risk, plus "core bank growth" management has not yet
   guided with specificity, are worth more than the market is crediting.

**This sentence can be stated credibly** — there are real, quantified
figures behind both the TBV hit and the credit-risk reduction — so Fix 2
does not veto this record for vagueness. But, as written, **the
mispricing case leans on an unguided future-growth assumption (§10) to
close the gap the Navitas/securities bridge itself cannot close (§7–§8),
and the market's own reaction (§16) does not show any sign of having
mispriced this in either direction.** The one-liner is stateable, but —
as with NHP — the evidence gathered does not clearly support it.

---

## 15. Valuation checkpoint

- **Reference price:** **$35.29** (last confirmed completed session,
  2026-09-11 close — see §18 for why this record could not obtain a
  same-day Gate B `FRESH` certification).
- **P/TBV (pre-restructuring, Q2 2026 actual TBV $23.31):** **~1.51x.**
- **P/TBV (pro forma, Q3 2026E TBV ~$21.36):** **~1.65x** — mechanically
  **richer**, not cheaper, immediately after the restructuring, since
  price has not moved proportionally to the TBV cut.
- **P/E** (annualizing the updated baseline operating EPS, $0.78 ×
  4 = $3.12): **~11.3x.** (Annualizing the flat trailing run-rate,
  ~$0.71–0.75 × 4 ≈ $2.84–3.00: **~11.8x–12.4x.**)
- **Dividend yield** ($0.25/quarter = $1.00/year): **~2.8%.**
- **ROTCE context:** ~13.0% operating ROTCE (trailing, declining
  slightly per §7) against ~1.5–1.65x P/TBV is a reasonable, not
  obviously mispriced, pairing for a regional bank of this profitability
  level.
- **CET1:** 13.5% pre / "above 13%" pro forma — strongly capitalized
  either way.

**Answering the work order's question directly: current valuation does
not obviously fail to reflect the improved risk/earnings profile, nor
does it obviously already fully credit it** — the multiples shown are
unremarkable for a well-capitalized, low-double-digit-ROTCE regional
bank, neither a statistically cheap nor a stretched read. **This record
does not rely solely on bank-peer multiples** — the reverse-engineered
P/TBV-before-and-after comparison above, using the company's own
disclosed TBV figures, is the primary evidence used.

---

## 16. Market reaction — checked directly, not assumed

| Date | Close | Note |
|---|---|---|
| 2026-09-04 | $35.64 | Pre-announcement baseline |
| 2026-09-08 | $35.29 | **Announcement day** (both 8-Ks filed) — **−0.98%** |
| 2026-09-09 | $35.04 | −0.71% further |
| 2026-09-10 | $35.15 | +0.31% |
| 2026-09-11 | $35.29 | +0.40% — back to the announcement-day close |

**Net change from pre-announcement (Sept 4) to the latest completed
session reviewed (Sept 11): −0.98%, essentially flat, mildly negative.**
**This is not a rally.** Per instruction, this record does not treat a
positive price movement as proof of edge — there was none to treat as
such here. The market's reaction reads as **neutral-to-mildly-skeptical**,
not as a sign investors are already excited about an underappreciated
earnings/risk improvement, and not as a sign of panic over the TBV hit
either. **The market has not clearly rewarded this restructuring**, but
it also has not punished it — consistent with the mixed, roughly-
breakeven economics this record's own bridge found (§7–§8).

---

## 17. Market-could-be-right case

- **The Navitas/securities-reset pairing nets to roughly zero on
  earnings** (§7–§8) — a reasonable investor could conclude the entire
  "earnings quality improvement" framing is marketing gloss on a
  transaction that is, in pure earnings terms, a wash.
- **The touted EPS improvement depends on unguided "core bank growth"**
  (+$0.02–0.04/quarter) — a reasonable investor could discount this
  entirely as unproven until demonstrated.
- **The TBV hit is real and immediate (~8.4%)**, while the credit-risk
  benefit, though real, is a reduction in the *probability* of future
  losses, not a certain, dated cash benefit — a reasonable investor
  could weight the certain TBV loss more heavily than the probabilistic
  risk reduction.
- **P/TBV got mechanically more expensive, not cheaper, immediately
  after the restructuring** (1.51x→1.65x) — a reasonable investor could
  see this as the market already having priced UCB richer than its new,
  lower tangible-book base justifies, rather than as an opportunity.
- **ROTCE has been quietly declining for four straight quarters**
  (13.56%→13.0%) even before this transaction — a reasonable investor
  could see the restructuring as management response to, not a solution
  for, softening profitability trends.
- **The buyback remains modest** ($87M YTD against a bank with a ~$4.3B
  market cap at this price) — not a large, valuation-moving lever on its
  own.
- **The market's own flat-to-mildly-negative reaction is itself
  evidence** that professional investors reviewing the same disclosures
  this record reviewed did not see a clear, underappreciated positive.

**This case is built entirely from this record's own findings and is
not a strawman.**

---

## 18. Fresh-price bind (Gate B)

An attempted same-day bind on 2026-09-14 (a live trading day) correctly
returned **`STALE`**, per Gate B's design: the market was open at
decision time, so no new completed session existed to certify beyond the
prior one. **Per instruction, this record does not force an intraday
bind.** The last independently-confirmed completed-session close is used
instead, with the limitation stated plainly:

```
security_key: SEC-CIK:0000857855:UCB
price: $35.29 (last confirmed completed-session close, 2026-09-11)
currency: USD
mic: XNYS
Gate B status at this record's decision time (2026-09-14, market open):
STALE — correctly returned, not routed around.
52-week range (raw observation, context only): $28.65 - $37.18
```

---

## 19. Falsifier

**The cleanest, most direct falsifier:** UCB's actual reported diluted
operating EPS for **Q3 2026 and Q4 2026**, once the Navitas sale,
securities reset, and Peach State are all fully reflected. If operating
EPS clears and **holds above** the updated $0.78 baseline on a
**recurring**, not one-quarter, basis, that would corroborate the
"core bank growth" leg this record could not verify independently and
would materially strengthen the variant. If it instead settles back
toward the flat $0.70–0.75 trailing range shown in §7, that would confirm
this record's finding that the Navitas/securities pairing alone does not
improve earnings, and that any real gain came only from Peach State — a
small, one-time, non-repeating step change.

---

## 20. Final triage disposition

> ## `NO_DEMONSTRATED_EDGE`

Scout's specific hook — that the Navitas exit, securities reset, debt
paydown, and buyback collectively improve UCB's **earnings quality**
more than the market is crediting — is **not corroborated** by
management's own disclosed bridge: the Navitas-exit and securities-reset
pieces net to roughly zero (§7–§8), the touted overall EPS improvement
comes from two sources outside the hook (Peach State and unguided core
growth, §10), and the market's own reaction to the announcement was
flat-to-mildly-negative, not a sign of an under-recognized positive
(§16). **The credit-risk-reduction half of the hook is real and well-
corroborated** (§13) — Navitas genuinely accounted for roughly half of
total net charge-offs — but this record finds no evidence the market is
failing to price a well-capitalized (13%+ CET1), reasonably-valued
(~1.5–1.65x TBV, ~11–12x P/E, ~13% ROTCE) regional bank for taking a
sensible, well-telegraphed de-risking action at roughly break-even
near-term earnings cost. This is treated, per this pilot's standing
framing, as a **successful discovery-system outcome**: the Fix 1 bridge
and Fix 2 one-liner did their job — testing a plausible-sounding,
multi-part hook against management's own numbers and finding the
specific "earnings quality" claim does not hold, before any deep-
underwriting variant was built around it.

**No deep underwriting of UCB follows from this record.**

---

## 21. Confirmation — remaining Batch 003 candidates and all prior states unchanged

NNBR, SAIA, and TCS remain registered only
(`PILOT3_BATCH_003_REGISTRATION.md`) — **not triaged by this record**,
per instruction. NHP remains `NO_DEMONSTRATED_EDGE`
(`PILOT3_NHP_PRIMARY_EVIDENCE_TRIAGE_001.md`), unchanged. All other Pilot
3 states are unchanged: PATH, MDB, XOM, PCG `NO_DEMONSTRATED_EDGE`; DOCU,
SPXC, SOLS `BLOCKED_BY_MATERIAL_UNCERTAINTY`; AVGO
`BLOCKED_BY_MATERIAL_UNCERTAINTY`; AAPL `EVIDENCE_GAP`; JPM
`CALENDAR_HOLD` (not advanced); SMH `REFERENCE_PEER_TAPE`; NVDA
`REFERENCE_ONLY`.

---

## 22. Shadow sentiment

No sentiment observations were encountered or used in this record. Had
any arisen, they would have been labeled `SHADOW_SENTIMENT` and excluded
from the disposition, per the Batch 003 charter.

---

## What this record does not do

No deep underwriting of UCB. No triage of NNBR, SAIA, or TCS. No
research of TCS. No Stage 7 or Stage 8. No capital allocated. No scoring,
ranking, or new engine. No advance of JPM or AAPL. No Batch 004.

**Capital status: NO REAL PORTFOLIO ACTION.**
