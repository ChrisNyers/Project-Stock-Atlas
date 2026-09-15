# PILOT 5 — CRASUS CHEMICAL (646A) FORCED-FLOW TRIAGE

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Forced-flow triage of the second Discovery Scan 001 situation. No
> deep/fundamental underwriting of Crasus. No research of MSG Rangers.
> Vylor's existing records (`PILOT5_VYLR_FORCED_FLOW_TRIAGE_001.md`,
> `PILOT5_VYLR_PRE_WI_FUNDAMENTAL_UNDERWRITING_001.md`) are unchanged.

| | |
|---|---|
| Date | September 14, 2026 |
| Pilot | Pilot 5 — `FORCED_FLOW / OWNERSHIP_DISLOCATION` |
| Candidate | Crasus Chemical Inc. — TSE 646A (pending listing) |
| Parent | Resonac Holdings Corporation — TSE 4004 |
| Source | `GROK_SCOUT_FORCED_FLOW_DISCOVERY` |
| Scan | Discovery Scan 001, situation 2 of 3 |

---

## 1. Preserved Pilot 5 state

- **Vylor** → `READY_FOR_WI_PRICE_TEST` — unchanged. No further Vylor work
  performed. No new primary evidence was sought or found that would
  reopen the existing underwriting.
- **MSG Rangers (MSGR)** → `SURFACE_FOR_TRIAGE` — unchanged, untouched.
- Crasus is the only research performed in this record.

---

## 2. Canonical identity (confirmed from primary Resonac/Crasus evidence)

| Field | Value | Source |
|---|---|---|
| Legal entity | Crasus Chemical Inc. (クラサスケミカル株式会社) | Resonac news release, Jul 6, 2026 |
| Expected ticker | 646A (TSE) | Resonac/Crasus press materials, Smartkarma |
| Exchange segment | Tokyo Stock Exchange **Standard Market** | Resonac news release §1; Crasus May 15, 2026 release ("filed an application for a listing on the Tokyo Stock Exchange Standard Market") |
| MIC | Not independently confirmed by Atlas (TSE Standard Market MIC is `XTSE`) — **the same MIC already confirmed unsupported by Gate B's `SUPPORTED_MICS` list during TCS's Pilot 3 triage.** Carried forward, not re-derived. |
| Head office | 2, Nakanosu, Oita City, Oita Prefecture (Tokyo Head Office also listed) | Resonac news release §4 |
| Representative | Hirotsugu Fukuda, Representative Director and President | Resonac news release §4 |
| Capital | ¥110 million | Resonac news release §4 |
| Date of establishment | August 1, 2024 (formed ahead of the split, as a shell subsidiary) | Resonac news release §4 |
| Resonac ownership before distribution | 100% | Resonac news release §4 |
| Resonac ownership after distribution | **Less than 20%** | Resonac news release §1, §3; explanatory material p.3 |
| Shares distributed | **More than 80%** of Crasus shares, via in-kind dividend | Resonac news release §1 |
| Distribution ratio | **1 Crasus share : 1 Resonac share** | Resonac news release §1; explanatory material p.4-5 |
| New capital raised | **None** — direct listing, no primary or secondary offering | Resonac news release §1; explanatory material p.6 |
| ADR / foreign-holder mechanics | Not established as a formal ADR program; see §3 below (U.S. securities-law treatment) | — |

**Collision check:** "Crasus" and "646A" produced no naming collisions in
search results distinct from this transaction. Identity is unambiguous.
**Currency: JPY**, per instruction — no source stated otherwise.

---

## 3. Transaction mechanics (confirmed, primary)

Both the Resonac news release (July 6, 2026 PDF, extracted via
`pdftotext` after WebFetch's binary-PDF ceiling made direct extraction
unreliable — same workaround pattern used for TCS in Pilot 3) and the
explanatory material PDF (same extraction method) give a fully
consistent schedule:

| Date | Event |
|---|---|
| Feb 14, 2024 | Resonac starts assessment of the spin-off |
| Jul 23, 2024 | Petrochemical subsidiary (Crasus) established |
| Oct 22, 2024 | Group restructuring plan announced (simplified absorption-type company split + in-kind dividend) |
| Late Apr 2026 | Crasus files initial listing application with TSE |
| Jun 12, 2026 | Business reorganization plan approved under Japan's Act on Strengthening Industrial Competitiveness |
| Jul 6, 2026 | **Detailed disclosure of the Spin-off plan** (this record's primary source) |
| Late Aug 2026 | Resonac board resolution to implement the in-kind dividend (planned) |
| Sep 28, 2026 (Mon) | Last trading day with dividend rights for Resonac shares |
| **Sep 29, 2026 (Tue)** | Ex-rights date for Resonac shares / **scheduled listing date of Crasus shares on the TSE** |
| Sep 30, 2026 (Wed) | Record date for the in-kind dividend |
| Oct 1, 2026 (Thu) | Effective date of the spin-off / distribution date — Crasus shares received |

This **confirms Scout's cited dates independently** (listing ~Sep 29;
distribution ~Oct 1; 1:1 ratio) and **refines** the "Resonac retaining
less than 20%" claim from an approximation to an issuer-stated ceiling.

**Direct-listing mechanics:** no book-building, no IPO price. Mizuho
Securities (lead managing trading participant) submits a reference
price to the TSE; the TSE sets a "first center price on the trading
board"; the actual opening price is then established via the TSE's
Itayose (call-auction) method based on real investor supply/demand,
within a band of 0.75x-2.3x the first center price. **This is a
textbook direct-listing price-discovery process (structurally similar
to Spotify's or Slack's U.S. direct listings) — day-one price formation
is driven by order-book supply/demand, not a syndicate-set IPO price.**

**Fractional shares / shareholder count:** not addressed in either
primary document reviewed. **Evidence gap**, not resolved by inference.

**Financial advisors:** Mizuho Securities and Goldman Sachs Japan Co.,
Ltd., per the explanatory material (p.3).

---

## 4. Alleged constrained sellers — mechanism-by-mechanism (load-bearing)

### A. Cross-border / U.S. tax

**Japan-domestic tax treatment is directly primary-sourced and
decisive: this is a tax-qualified partial spin-off.** Per the Resonac
news release §2(4) and the explanatory material p.9:

> "For Japanese tax purposes, the Company will not be subject to
> taxation on capital gains or losses arising from the in-kind dividend
> ... The Company's shareholders receiving such Crasus Chemical Shares
> will not be subject to taxation in connection with the Spin-off."

Tax basis is simply split between the two securities using a disclosed
"proportion of distributed assets" (~0.09 as of the evidence date) —
**no deemed-dividend taxation, no forced cash need to cover a tax bill,
for Japanese resident shareholders.** This directly **refutes** a
domestic-tax-driven forced-selling story for the majority of Resonac's
holder base.

**U.S. federal tax treatment of U.S. holders was not addressed by
either primary document** (both explicitly disclaim coverage of
non-Japanese jurisdictions and advise consulting a tax advisor).
**Evidence gap** — Atlas did not manufacture a US tax conclusion.

**A separate, non-tax, U.S. mechanism is confirmed and is more
concrete than tax:** both primary documents carry the standard
disclaimer that Crasus shares "have not been, and will not be,
registered under the U.S. Securities Act of 1933 ... and may not be
offered or sold in the United States absent registration ... or an
applicable exemption." **This is a real securities-law constraint, not
a tax incentive** — it raises the question of whether U.S.-resident
Resonac shareholders can actually receive tradable Crasus shares at
all, or whether a transfer agent/custodian would instead need to sell
on their behalf and remit cash (the common practice for many
cross-border spin-off distributions to U.S. holders of foreign stock).
**Neither primary document specifies which outcome applies here — a
genuine, unresolved evidence gap**, not inferred or assumed either way.

**Classification, per instruction:**
- Japanese resident shareholders: **`DISCRETIONARY`** (no tax
  compulsion; any sale is a portfolio choice).
- U.S.-resident shareholders, if a non-delivery/cash-out mechanism
  applies: would be **`STRUCTURALLY_CONSTRAINED`** by securities law,
  not by tax — but this record cannot confirm whether that mechanism
  actually applies. **Not classified with confidence.**
- No holder population is labeled a forced seller on tax grounds alone,
  per instruction.

### B. Sector / mandate mismatch

Resonac's own stated rationale for the spin-off is to "concentrate
management resources on its mainstay semiconductor and electronic
materials business" (Nikkei, Japanese-language coverage, echo/context —
consistent with, and unsurprising given, Resonac's disclosed segment
structure in its own materials: Semiconductor and Electronic Materials,
Mobility, Innovation Enabling Materials, Chemicals, with Crasus/
petrochemicals being carved out as a "Financial Asset" post-spin). This
establishes a plausible **business-mix mismatch**: a shareholder base
assembled around Resonac's semiconductor-materials growth story may not
have chosen, and may not wish to continue holding, a standalone basic
petrochemical commodity producer.

**No specific fund or mandate-level evidence was found** confirming
that identifiable semiconductor/tech-mandate holders of Resonac exist
in size and would be compelled or inclined to exit Crasus. This
mismatch is **plausible, not holder-confirmed** — the same caution the
sourcing design requires ("do not assume Resonac holder = Crasus
seller").

### C. Index / benchmark mismatch — the most concrete confirmed mechanism

**Confirmed, near-primary (Nikkei Inc.'s own index-methodology
reporting):** the Nikkei 225 revised its rules in **July 2025**,
specifically in response to a prior Japanese direct-listing spin-off
(Sony Group's spin-off of Sony Financial Group, September 2025), to
handle exactly this situation. Under the revised rule:

> A spun-off entity is temporarily included in the Nikkei 225 index
> calculation from the ex-rights date until the business day after its
> official TSE listing, using an offering/reference price (since no
> market price exists pre-listing), and is **removed from the index on
> the business day following its official listing.**

Nikkei Asia's own reporting states plainly that this is exactly what
will happen to Crasus: **"temporarily included in the benchmark stock
index on its listing date [Sept 29] and removed the following day
[Sept 30]."**

This is a **genuine, dated, mechanical, disclosed forced-transaction
rule** for any fund that tracks the Nikkei 225 and must hold its
constituents: such a fund receives Crasus shares via the spin-off,
then is index-mandated to sell essentially the entire position within
about one trading day of listing, regardless of its fundamental view.
This is the **cleanest, most concrete mechanism found in this triage.**

**TOPIX treatment could not be confirmed either way.** Resonac is a
TOPIX (and Nikkei 225) constituent (Prime Market), but post-2022 TOPIX
methodology ties routine index eligibility to the Prime Market; new
Standard Market listings such as Crasus are only eligible via a
discretionary "Non-Periodic Addition" review, not automatic inclusion.
Atlas could not access JPX's own TOPIX methodology page directly
(HTTP 403) and found no dated confirmation of a decision either way for
Crasus specifically. **Evidence gap — not resolved, not assumed.**

---

## 5. Foreign-ownership test

Resonac's foreign institutional ownership is approximately **34%**
(Simply Wall St aggregator data — **`CONTEXT`, not primary**, flagged
as such per instruction; not independently verified against a primary
Japanese shareholder disclosure). Domestic trust banks (Master Trust
Bank of Japan ~16.4%, Custody Bank of Japan ~6.2%) are large holders
but these are Japanese nominee/custodian accounts for domestic pension
and investment trusts, **not** evidence of foreign ownership themselves.

Given that Japan-domestic tax treatment is confirmed non-punitive
(§4A), the foreign-ownership figure that actually matters for a
tax/securities-law-driven thesis is **not** the full 34% but the
narrower subset of specifically **U.S.-person** holders subject to
Securities Act registration constraints — a figure this record could
not size. **34% foreign ownership in aggregate is large enough that a
U.S.-specific subset could plausibly matter, but "plausibly could
matter" is not the same as "confirmed to matter," and no attempt was
made to convert the aggregate figure into a false precision estimate.**

---

## 6. Potential constrained supply — not quantifiable at this stage

Unlike Vylor (where CTVA was already trading and a coarse order-of-
magnitude share estimate was possible from CTVA's existing market cap),
**Crasus has no market price and no market capitalization yet** — it
is a pre-listing direct listing. Nikkei 225 is a **price-weighted**
index with capping/adjustment factors Atlas does not have visibility
into pre-listing, making even a coarse constrained-share estimate
speculative in a way that would misrepresent precision. **No number is
manufactured.**

Keeping the three buckets separate, per instruction:

- **`IDENTIFIABLE_CONSTRAINED`**: Nikkei-225-tracking passive funds,
  mechanically required to exit within ~1 trading day of listing —
  identifiable as a class, magnitude unquantified.
- **`ECONOMICALLY_INCENTIVIZED`**: none identified with confidence.
  The Japan-tax-driven incentive Scout proposed does not hold up (§4A);
  a U.S.-securities-law-driven incentive is plausible but unconfirmed
  in mechanism.
- **`POSSIBLE_DISCRETIONARY`**: the sector/mandate-mismatch holder
  population (§4B) — plausible, unconfirmed at the holder level, and
  the bulk of Resonac's ~66% non-foreign, non-index-fund shareholder
  base, who face no tax or index compulsion at all.

These are **not aggregated into one forced-selling number**, per
instruction.

---

## 7. Liquidity / market-impact test

Crasus is a new direct listing — no trading history, no ADV. Day-one
price discovery runs through the TSE's Itayose call-auction mechanism
(§3) within a 0.75x-2.3x band around a reference price submitted by
Mizuho Securities. **Expected free/tradable float, expected shareholder
count, and initial liquidity depth were not disclosed in either primary
document reviewed** — a genuine evidence gap, consistent with the
information a direct listing typically withholds until closer to the
listing date.

**Context only, cautiously labeled, per instruction:** the July 2025
Nikkei 225 rule revision was itself prompted by Sony Group's September
2025 direct-listing spin-off of Sony Financial Group — a real, recent
precedent transaction of the same structural type (Japanese direct-
listing spin-off, temporary index inclusion, T+1 removal). Atlas did
**not** independently research how Sony Financial Group traded
post-listing; it is noted here only as evidence that this exact
mechanism has occurred at least once before, not as a return
comparable. **No flow score is created.**

---

## 8. Original-source validation

| Claim | Source | Classification |
|---|---|---|
| Transaction structure, dates, ratio, retained %, tax treatment | Resonac's own July 6, 2026 news release + explanatory material (official IR PDFs) | **ORIGINAL** |
| Crasus's own FY2025 results, 2026 guidance withdrawal, business strategy | Crasus's own May 15, 2026 news release (official PDF) | **ORIGINAL** |
| Nikkei 225 temporary-inclusion/T+1-removal rule | Nikkei Inc.'s own methodology reporting (Nikkei Global Services, Nikkei Asia) — the index provider describing its own rule | **ORIGINAL** (index-provider self-description, not third-party commentary) |
| Japan ethylene utilization rates (68.6%/67.3% record lows) | Argus Media, Hydrocarbon Processing, citing Japan Petrochemical Industry Association data | **ORIGINAL** trade-press reporting of primary industry statistics |
| Resonac foreign ownership ~34%, shareholder concentration | Simply Wall St aggregator | **CONTEXT / ECHO** — explicitly flagged, not treated as primary |
| TOPIX treatment of Crasus | Not found in any accessible source | **EVIDENCE GAP** — no claim made |
| Smartkarma/Travis Lundy analyst primer and "synthetic expert call transcript" (dated Sep 8, 2026) | Paywalled (HTTP 403); not accessible to Atlas | **CONTEXT/ECHO by inference from headline only** — not used as evidence for any finding in this record, only as a discovery-clock data point (§11) |

No repeated media coverage of the same underlying Resonac/Crasus
release was counted as independent corroboration.

---

## 9. Fundamental-separation check — material finding

**This is not a clean case, and the fundamentals themselves already
explain a plausible weak trade — this matters more here than it did
at Vylor, as anticipated.**

From Crasus's own May 15, 2026 pre-listing disclosure (original,
issuer-sourced):

- **Operating profit fell from ¥8.6 billion (2024) to ¥4.2 billion
  (2025) — a 51% year-over-year decline**, on a management-accounting
  basis restated to Crasus's own consolidated figures.
- **ROE fell from 7.8% to 4.7%; ROIC fell from 4.5% to 2.4%** — both
  roughly halved in one year.
- **2026 operating-profit target: "Under review"** — Crasus's own
  release states it as of May 2026: "we are currently reviewing the
  targets for the year ending December 31, 2026, as the continued
  conflict in the Middle East is making the outlook for the supply of
  naphtha ... and our customers' demand unclear, and their impact on
  our business plan unpredictable." **This is an issuer-disclosed,
  currently unresolved guidance withdrawal**, not an Atlas inference.
- **Japan's ethylene-industry utilization hit record lows in 2026**
  (68.6% in March, 67.3% in April, per JPCA data via Argus Media/
  Hydrocarbon Processing) — driven by the same naphtha-supply
  disruption (linked to Middle East conflict) plus heavy planned
  cracker maintenance across the industry. **Crasus's own cracker was
  under extended maintenance from February 2026.**
- **Structural, not merely cyclical, industry contraction is already
  underway**: Crasus's own release states 4 of Japan's 12 ethylene
  plants will be shut down by ~2030 to bring domestic capacity in line
  with flat domestic demand (~4 million tons/year, "almost flat until
  around 2030"), while Asian/Chinese oversupply continues to exceed
  regional demand through the same period.
- Long-run **ROIC target is ~10%, versus a current 2.4%** — a large,
  named, unresolved gap between current economics and management's own
  stated aspiration, structurally similar in kind (though not in cause)
  to NNBR's dilution-earnback gap and Vylor's dis-synergy gap.
- **DOE (dividend-on-equity) target of 5%**, explicitly positioned
  (per Japanese-language press coverage, context/echo) to attract
  income-seeking retail shareholders — consistent with a mature, low-
  growth, cash-generative-but-currently-thin-margin commodity business
  being marketed on yield rather than growth.

**Core question answered plainly: yes — if Crasus trades weakly after
listing, poor petrochemical fundamentals (record-low sector
utilization, a halved-in-one-year profitability profile, an
issuer-acknowledged unresolved 2026 outlook) already provide a
sufficient, primary-sourced explanation for that weakness, with no
need to invoke any ownership dislocation at all.** This does not mean
no forced selling will occur (§4C's Nikkei 225 mechanism is real); it
means forced selling would be **layered on top of, not distinguishable
from,** a genuine, current fundamental headwind.

---

## 10. Strongest market-could-be-right case

Built without a strawman:

1. **Japanese domestic holders dominate and face no tax compulsion**
   (§4A, confirmed primary) — the largest slice of the shareholder base
   has no forced-selling incentive at all.
2. **The petrochemical cycle is genuinely, currently bad** — record-low
   national utilization, an issuer-withdrawn 2026 guidance target, and
   a halved profitability profile in the single most recent disclosed
   year (§9). A rational market may price Crasus for cyclical weakness
   entirely independent of any spin-off mechanics.
3. **Structural industry contraction (4 of 12 domestic plants closing
   by 2030) is a genuine long-run headwind**, not a short-term
   dislocation that will reverse.
4. **The Nikkei 225 mechanical seller population, while real, may be
   too small to matter.** Nikkei 225 is price-weighted with capping
   factors; Resonac's own weight in the index (and thus Crasus's
   implied temporary weight) has not been shown to be large, and one
   trading day of index-driven selling in an actively-traded direct
   listing with fresh institutional and retail interest may be readily
   absorbed.
5. **TOPIX may simply not include Crasus at all** (§4C) — removing a
   second, potentially larger, mechanical-selling channel entirely, not
   merely delaying it.
6. **Direct-listing price discovery (Itayose call auction, §3) already
   incorporates real-time supply and demand** from the moment of
   listing — unlike a traditional IPO with a fixed offering price that
   can lag fundamentals, this mechanism is explicitly designed to let
   the market clear on day one, which argues against a persistent,
   exploitable price/value gap surviving past the opening auction.
7. **Sector/mandate mismatch is plausible but unconfirmed at the
   specific-holder level** (§4B) — it may be more theoretical than
   real, exactly as the work order's own challenge frames it.
8. **The DOE 5% yield target is a real, disclosed capital-return
   commitment** that could itself attract natural, price-insensitive
   buyers (income-seeking retail and institutional yield funds),
   providing a demand-side offset to any index-driven supply.

**No single item above is dismissed; several are independently
sufficient to weaken the forced-flow thesis on their own.**

---

## 11. Discovery-clock result

Reconstructed timeline of public disclosure versus Scout's discovery:

- Feb 14, 2024 — initial spin-off assessment announced.
- Jul 23, 2024 / Oct 22, 2024 — subsidiary formation / restructuring
  plan announced.
- Late Apr 2026 — TSE listing application filed.
- May 15, 2026 — Crasus's own pre-listing business-strategy/targets
  release, including the guidance-withdrawal disclosure (§9).
- Jun 12, 2026 — METI business-reorganization approval.
- **Jul 6, 2026 — full detailed disclosure of the Spin-off plan** (this
  record's primary source; over **two months** before Scout's
  discovery).
- Sep 8, 2026 — a Smartkarma "synthetic expert call transcript" on
  Crasus (646A JP) is already published, per its own dateline —
  evidence that professional Japan special-situations analysts were
  actively producing granular research on this exact security **six
  days before** Scout surfaced it to Atlas.
- **Sep 14, 2026 — Scout discovers/surfaces the situation to Atlas**
  (today, this record's evidence date).
- Sep 29, 2026 — scheduled listing (**15 days after Scout's
  discovery**).
- Oct 1, 2026 — distribution effective date.

**Answer: no, Atlas did not identify this potential dislocation
particularly early.** The core transaction terms have been public for
over two months, and specialist Japan-focused investors (a dedicated
research platform publishing a primer and an "expert call transcript")
were already engaged with this exact situation before Scout's
discovery date. This stands in clear contrast to Vylor, where Atlas's
Pilot 5 engagement occurred **before any price discovery had begun at
all** (pre-when-issued-trading). **Crasus is being discovered
materially later in its own recognition cycle than Vylor was in its.**

---

## 12. Cheapest falsification result

**Test:** is there a sufficiently large and identifiable holder
population structurally constrained or materially incentivized to sell
Crasus for reasons unrelated to fundamentals?

Evaluated against each stated kill condition:

- **Foreign ownership immaterial?** No — ~34% is not immaterial in
  aggregate, but the specifically tax/securities-law-constrained
  subset (§4A, §5) is unconfirmed and likely much smaller.
- **Tax treatment creates little actual sale incentive?** **Yes, for
  the dominant Japanese-domestic holder base** — confirmed
  tax-qualified, no deemed-dividend taxation (§4A). This kill condition
  is **satisfied** for the largest part of the shareholder base.
- **Index treatment prevents meaningful forced selling?** **Mixed.**
  Nikkei 225 confirms a real T+1 mechanical seller population (not
  prevented); TOPIX treatment is unconfirmed either way (§4C).
- **Sector mismatch cannot be tied to actual holders?** **Yes** —
  plausible but unconfirmed at the specific-holder level (§4B). This
  kill condition is **satisfied**.
- **Natural demand appears likely to overwhelm potential supply?**
  Unknown/unconfirmed — but a real, disclosed 5% DOE yield target and
  fresh direct-listing interest are at least plausible demand-side
  offsets (§10).

**Net result: two of the five proposed kill conditions are
affirmatively satisfied by primary evidence (Japan-domestic tax, and
unconfirmed sector-mismatch-at-holder-level), one is genuinely mixed
(index treatment — real but only partially confirmed and unquantified),
and the fundamental-separation check (§9) independently supplies a
sufficient, primary-sourced explanation for potential price weakness
that has nothing to do with ownership dislocation.** The forced-flow
hypothesis is **not cleanly killed** (the Nikkei 225 mechanism is real
and dated), but it also does **not survive as a clean, well-isolated
non-fundamental thesis** the way Vylor's did. The honest reading is
that any post-listing weakness in Crasus would be very difficult to
attribute cleanly to ownership dislocation rather than to a genuinely
troubled, currently-guidance-withdrawn petrochemical business.

---

## 13. Best-expression observation

If a genuine ownership dislocation exists here, **Crasus itself, not
Resonac, is the cleaner expression** — Resonac retains less than 20%
of Crasus post-spin and is a large, diversified semiconductor/
electronic-materials company where any petrochemical-specific
mispricing would be a small, diluted factor. This mirrors the same
structural logic found for Vylor relative to Corteva. **No trade is
constructed; no arbitrage is designed.** This observation is
subordinate to §9's finding that the fundamental case for Crasus
itself is genuinely weak on its own terms, independent of expression.

---

## 14. Pilot 5 comparative learning — Crasus vs. Vylor

1. **Which has the more identifiable constrained seller?** **Vylor.**
   Corteva's own primary-sourced risk-factor language names index
   funds directly as a potential forced seller of Vylor stock if S&P
   500 inclusion is not achieved. Crasus's clearest mechanism (Nikkei
   225 T+1 removal) is confirmed and dated but was established through
   the index provider's own methodology reporting, not the issuer's own
   risk-factor disclosure, and its Japan-domestic tax and sector-
   mismatch mechanisms were actively **weakened**, not strengthened, by
   primary evidence in this triage.
2. **Which has the cleaner non-fundamental mechanism?** **Vylor.**
   Crasus's fundamental-separation check (§9) found a genuine,
   currently unresolved, issuer-acknowledged cyclical/guidance problem
   that materially confounds any forced-flow read; Vylor's
   fundamental-separation check found a clean picture (raised guidance,
   growing segment EBITDA).
3. **Which can be quantified more credibly with public evidence?**
   **Vylor**, though only coarsely (§6 here vs. Vylor's own 65-135M-
   share estimate, itself already re-labeled `EXPLORATORY_CONTEXT_ONLY`
   in the Vylor fundamental-underwriting record). Crasus could not be
   quantified at all pre-listing — a stricter data constraint than
   Vylor faced.
4. **Which is more likely to experience actual supply/demand
   distortion?** Genuinely uncertain for both, but Crasus's Nikkei 225
   mechanism has one advantage Vylor's does not: it is **dated and
   procedurally certain** (T+1 removal is a rule, not a probabilistic
   index-committee decision), even though its magnitude is unknown.
   Vylor's mechanism is larger in principle (S&P 500 vs. Nikkei 225
   passive AUM) but conditional on an inclusion decision that has not
   yet been made.
5. **Which did Atlas identify earlier relative to price discovery?**
   **Vylor, clearly.** Atlas engaged with Vylor before any trading
   existed. Crasus is being triaged after two-plus months of public
   disclosure and after specialist analysts had already published
   detailed primers — materially later in its own recognition cycle
   (§11).

This comparison is for Pilot-5 learning only; **no capital ranking is
implied.**

---

## 15. What Atlas added beyond Scout

Scout surfaced "Resonac → Crasus cross-border/shareholder mismatch"
with an implied cross-border-tax framing (per the work order's own
description of "Scout currently suggests ... Resonac retaining less
than 20%" and a tax-treatment hypothesis to test). Atlas:

- **Confirmed** the transaction mechanics precisely from primary
  issuer documents (exact dates, exact ratio, the >80%/<20% split).
- **Refuted** the implied Japan-domestic-tax-driven forced-selling
  narrative — the spin-off is confirmed tax-qualified with no
  shareholder taxation event in Japan.
- **Identified a different, more concrete mechanism** than the one
  Scout's framing emphasized: the Nikkei 225's own T+1 temporary-
  inclusion/removal rule, sourced to the index provider itself.
- **Surfaced a genuine, material, issuer-disclosed fundamental
  headwind** (halved profitability, withdrawn 2026 guidance, record-low
  sector utilization) that Scout's discovery did not mention and that
  materially confounds the forced-flow thesis.
- **Established the discovery-clock finding** that this situation is
  being engaged with considerably later, relative to its own public
  disclosure and analyst-recognition timeline, than Vylor was — a
  direct, evidenced answer Scout's surfacing did not provide.

Atlas did **not** find a positive, clean, investable forced-flow
edge — consistent with the instruction not to force a positive
finding.

---

## 16. Final disposition

## `NO_DEMONSTRATED_FORCED_FLOW_EDGE`

A real, dated, mechanical index-driven seller population exists
(Nikkei 225's T+1 removal rule), but: (1) the dominant proposed
mechanism (Japan-domestic tax) is refuted by primary evidence, (2) the
sector-mismatch mechanism is unconfirmed at the holder level, (3) TOPIX
treatment is an unresolved evidence gap, (4) the magnitude of any
confirmed mechanical selling cannot be quantified even coarsely
pre-listing, and (5) most importantly, a genuine, current,
issuer-acknowledged fundamental headwind (halved profitability,
withdrawn 2026 guidance, record-low national ethylene utilization)
already provides a sufficient explanation for potential post-listing
price weakness, independent of any ownership dislocation. The forced-
flow thesis is not cleanly killed outright, but it does not clear the
bar to justify fundamental underwriting as a forced-flow opportunity at
this time. **This is not a judgment that Crasus is a bad company or a
bad investment at some price — only that Pilot 5's specific
forced-flow information family does not, on this evidence, produce a
demonstrated edge here.**

---

## 17. Preserved Pilot 5 state (restated)

- **Vylor → `READY_FOR_WI_PRICE_TEST`** — unchanged. No new Vylor work.
- **MSG Rangers (MSGR) → `SURFACE_FOR_TRIAGE`** — unchanged, untouched.
- **Crasus (646A) → `NO_DEMONSTRATED_FORCED_FLOW_EDGE`** — closed by
  this record.

---

## What this record does not do

No deep or fundamental underwriting of Crasus. No research of MSG
Rangers. No modification of either Vylor record. No Stage 7 or Stage 8.
No capital allocated. No new Pilot 5 discovery scan. No architecture,
scoring, ranking, or new engine added. No permanent taxonomy created
from the `STRUCTURALLY_CONSTRAINED` / `ECONOMICALLY_INCENTIVIZED` /
`DISCRETIONARY` or `IDENTIFIABLE_CONSTRAINED` / `ECONOMICALLY_
INCENTIVIZED` / `POSSIBLE_DISCRETIONARY` labels used above — both are
this record's case-specific application of Pilot 5's existing
vocabulary, not new fields.

**Capital status: NO REAL PORTFOLIO ACTION.**
