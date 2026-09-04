# PILOT 2 — INITIAL DISCOVERY TRIAGE 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> This record uses Discovery Contract v0.1 states. **SURFACED means "worth
> underwriting attention," nothing more.** No security below is BUY, HOLD,
> eligible, promoted, or funded by this record.

| | |
|---|---|
| Date | September 4, 2026 |
| Pilot | Pilot 2 — Variant Edge & Intentional Allocation |
| Stage | Discovery (SURFACED / NOT SURFACED only — no underwriting performed) |
| Basket | Frozen, `docs/pilot2_variant_edge/PILOT2_VARIANT_EDGE_CHARTER_001.md` §18 |
| Sentiment used | None (`SHADOW ONLY`, per charter — not consulted) |

---

## Method and evidence discipline

For each name I gathered current operating evidence via live web search against
each company's own disclosed results (earnings releases, 8-K/6-K exhibits,
investor-relations materials, and financial-press coverage of the same). This
is **secondary aggregation of primary disclosures**, not a direct read of raw
filing text — I did not pull 10-Q/10-K/20-F/6-K documents through Atlas's own
`sec_adapter.py` pipeline for this pass. That is a real evidence-quality
limitation, disclosed per name below, and is the first thing deeper
underwriting should upgrade for any name that advances.

No price, valuation multiple, or return estimate was used to decide
advancement. No sentiment source was consulted. Analyst-consensus framing is
noted only as evidence that a live market disagreement exists, never adopted
as Atlas's own thesis.

List order below is the frozen basket's transcription order. It carries no
ranking.

---

## Triage table

| Ticker | Prior state | Core operating evidence (source, approx. date) | Apparent market narrative | Potential Atlas variant | Principal uncertainty | Evidence quality | Decision | Reason |
|---|---|---|---|---|---|---|---|---|
| **FIS** | NOT SURFACED | Completed Jan 2026: sold remaining 45% Worldpay stake, acquired Global Payments' Issuer Solutions (ex-TSYS) business. Disclosed FCF accretion: ~$500M in 2026 rising to ~$700M by 2028. Same cycle: FY26 guidance cut, driven by a *different* segment (capital markets). (FIS 8-K/investor release, Q1–Q2 2026) | Mixed/negative — headline reads as "FIS lost Worldpay, cut guidance." | Whether the disclosed FCF accretion from full-control Issuer Solutions economics is being offset in perception by the capital-markets guidance cut and the "lost Worldpay" framing, rather than weighed on its own quantified terms. | Whether the $500–700M FCF figure is real and durable, and how large the capital-markets shortfall actually is — both unverified beyond press releases. | Secondary aggregation; specific dollar figures not cross-checked against the 8-K exhibit text directly. | **ADVANCE** | A specific, quantified, testable tension exists between disclosed accretion and headline optics — not merely "cheap" or "turnaround." |
| **FISV** | NOT SURFACED | FY26 organic revenue guidance cut to −1%–0% (from +1%–3%); adjusted EPS guidance cut to $7.20–$7.40 (from $8.00–$8.30). Q2 adjusted EPS missed and fell 26% YoY; revenue missed and declined. New CEO resetting guidance. Stock ≈ −60% over 12 months. Clover (POS/SMB) still growing (+9% GPV) as a partial offset. (Fiserv guidance/earnings coverage, Q2 2026) | Negative — broad "broken growth story" narrative, already reflected in a −60% stock move. | None identified this pass. No evidence yet distinguishes *temporary* (Argentina FX, delayed implementations) from *structural* (competitive share loss) deterioration. | Whether the guidance reset marks a floor or an ongoing decline — unknowable from earnings-release text alone. | Secondary aggregation; no segment-level primary data reviewed. | **DO NOT ADVANCE** | Evidence shows real, broad-based deterioration already priced via a large stock decline, with no specific expectations gap identified — matches the "recently fell" / "turnaround narrative" exclusions, not a demonstrated variant. |
| **MELI** | NOT SURFACED | Q2 2026: net revenue $10.2B, +50% YoY (fastest in 4 years). Operating margin 6.7%, −550bps YoY — a *disclosed, deliberate* reinvestment choice, not a miss. Credit portfolio $16.4B, +75% YoY; NPLs "near historical lows" (7.0% total, 4.6% credit card). (MELI 8-K / Q2 2026 earnings call) | Positive/consensus growth story, with a standing bear case around LatAm consumer-credit risk during rapid scaling. | Whether the disclosed low-NPL trend genuinely holds up as the credit book scales 75% YoY, or whether credit quality is deteriorating faster than headline NPL figures show (vintage-level data not examined). | This may be an already well-known, widely debated bull/bear split rather than an Atlas-specific angle — flagged honestly, not resolved. | Secondary aggregation; NPL figures not decomposed by vintage or product. | **ADVANCE (tentative)** | A specific, numeric, falsifiable question exists (credit quality vs. scale) that primary-source underwriting can resolve — advanced for investigation, not because growth is high. |
| **JD** | NOT SURFACED | Q2 2026: revenue **−2.9%** YoY; non-GAAP net income **+21%** YoY to RMB8.9B, margin +50bps to 2.6%. Driver: JD Food Delivery operating loss narrowed >50% YoY (a discretionary, self-inflicted loss being wound down), not core-retail acceleration. (JD Q2 2026 earnings coverage/8-K) | Positive framing ("profit inflection") built on a shrinking discretionary loss, while core top line is declining. | Whether the market is correctly rewarding capital-allocation discipline (exiting a bad bet) or under-weighting a genuinely slowing/share-losing core retail franchise masked by the food-delivery optics. | Segment-level GMV/active-buyer trend not examined; cannot yet tell if the top-line decline is broad or narrow. | Secondary aggregation; no primary segment data reviewed. | **ADVANCE (tentative)** | A specific tension exists between a declining top line and an improving bottom line driven by a one-off exit — worth resolving with primary segment data, not advanced on "profit beat" alone. |
| **ADBE** | NOT SURFACED | Firefly AI-ARR crossed $500M, tripled YoY — but is ~1.9% of FY26 guided revenue ($26.5–26.6B, +10.2% ARR growth). FY26 guidance raised. Freemium strategy is explicitly *dampening* near-term ARR growth by design. CEO transition underway. (Adobe FY26 Q1–Q2 coverage) | The single most consensus-saturated debate in software: "is Adobe's moat being disrupted by native AI tools, or is Firefly proof it's monetizing AI." | None identified this pass distinct from the general market debate. | Whether freemium-driven ARR deceleration is temporary strategy or a symptom of pricing power erosion — not distinguishable from this evidence. | Secondary aggregation. | **DO NOT ADVANCE** | Matches the charter's explicit caution: AI narrative dominates every fact found here, and no Atlas-specific expectations gap was identified distinct from the widely covered bull/bear debate. |
| **SNOW** | NOT SURFACED | Q2 2026: product revenue +37% YoY, third consecutive quarter of *acceleration*. FY27 opex-margin guidance *raised* to 14.5% even as product gross margin *guidance cut* to 74%, reflecting AI-product mix dilution. (Snowflake Q2 FY27 earnings coverage) | Strong AI-beneficiary growth story; margin dilution is a known, disclosed trade-off. | None identified this pass — management's own raised opex-margin guide, alongside the gross-margin cut, suggests the trade-off is already understood and priced by the company itself, weakening the case for a market misread. | Whether accelerating growth durably outruns AI-driven margin dilution — a real question, but not one this evidence isolates as mispriced. | Secondary aggregation. | **DO NOT ADVANCE** | Real, quantified margin/growth tension exists, but nothing found here distinguishes it from the AI-beneficiary story already reflected in raised guidance and consensus coverage. |
| **WCC** | NOT SURFACED | Q1 2026: data-center sales +~70% YoY (24% of total sales); stock +17% on the print. Q2 2026: record sales +13% YoY, EPS +35% YoY, beat consensus by ~15%; FY26 guidance raised twice. (Wesco Q1–Q2 2026 releases) | Textbook AI-infrastructure "picks and shovels" beneficiary — one of the most widely covered industrial AI-capex plays. | None identified this pass. Execution is real and strong, but the +17% single-day stock reaction indicates the market is actively and immediately re-rating on this evidence, not ignoring it. | Whether data-center demand growth (45–70% YoY, decelerating between Q1 and Q2 in the figures found) continues at pace or normalizes. | Secondary aggregation. | **DO NOT ADVANCE** | Matches the explicit exclusion: strong results plus "AI beneficiary" framing alone, with the market visibly and immediately pricing the news — no demonstrated gap between evidence and price reaction. |
| **GLNG** | NOT SURFACED | Q2 2026: net income +145% YoY; H1 net income +411% YoY. FLNG Hilli: 100% economic uptime over an 8-year contract, repositioning for a new 20-year contract from 2027. FLNG Gimi overproducing 15% vs. committed volume. Targeting a 4th (and possibly 5th) FLNG newbuild, ~$2.45B capex. Guided to ~$800M run-rate EBITDA by 2028. (Golar LNG Q2 2026 earnings call/interim report) | Thin — this is a specialized, less-followed structure (floating LNG contract economics), not a mainstream narrative either way. | Not yet formable from this evidence. FLNG economics turn on charter-party contract terms, counterparty credit, and newbuild financing/dilution risk — none of which this pass examined. | Whether the ~$800M 2028 run-rate guidance and the new-unit financing plan hold up is unknown without reading the actual contract and financing disclosures. | **Evidence gap, not a negative finding** — headline results are strong, but the structure is too specialized to triage confidently from earnings-release summaries alone. | **DO NOT ADVANCE (evidence gap)** | Distinguished deliberately from a "no variant" finding: this is "requires dedicated primary-document work before even a discovery-level call is well-founded," per the charter's WCC/GLNG test of unfamiliar structures. |
| **NTR** | NOT SURFACED | H1 2026: record potash volumes; FY26 potash guidance raised to 14.2–14.8M tonnes; controllable cash costs held flat, targeting <$60/tonne. Capex guidance *lowered* $50M on capital efficiency. Company maintains industry-wide 2026 shipment forecast of 74–77M tonnes — i.e., no disclosed structural supply-discipline thesis beyond company-level execution. (Nutrien Q2 2026 release/earnings call) | Straightforward commodity-upcycle strength. | None identified. No evidence found of a durable-cycle-vs-peak-cycle disagreement between Atlas and the market — only that the current cycle is good and Nutrien is executing well within it. | Whether the current potash upcycle is early, mid, or late — not addressed by this evidence. | Secondary aggregation. | **DO NOT ADVANCE** | Matches the explicit exclusion: "cyclical strength" without a demonstrated structural mispricing. |
| **CVS** | NOT SURFACED | Aetna medical benefit ratio: ~95% (Q3 2024) → 89.9% (Q2 2025) → 87.4% (Q2 2026); FY26 EPS guidance raised **twice** in 2026 (to $7.30–$7.50, then to $7.90–$8.10); Q2 net income ≈3× YoY. Widely covered as "Aetna turnaround gains steam/traction" across multiple outlets already. (CVS Q1–Q2 2026 releases) | Already well-documented, multiply-reported beat-and-raise turnaround. | None identified. No evidence found of a *remaining* gap between what's priced and what's real — the pattern found is confirmatory of an already-recognized trend, not a hidden one. | Whether the string of raises has room to continue or is now fully reflected in expectations — not addressed by this evidence. | Secondary aggregation. | **DO NOT ADVANCE** | Matches the explicit exclusion: "low valuation / turnaround optics" without a demonstrated remaining gap — this turnaround is unusually well covered already. |

---

## Summary

**Advanced to deeper underwriting (3 of 10):** FIS, MELI (tentative), JD (tentative)

**Not advanced (7 of 10):** FISV, ADBE, SNOW, WCC, GLNG (evidence gap), NTR, CVS

`NO DEMONSTRATED EDGE` is the honest outcome for 6 of the 7 not-advanced names.
GLNG is recorded distinctly as an **evidence gap** — the structure is too
specialized for this triage pass to call confidently either way, which is a
valid and expected discovery-stage result for an unfamiliar structure, not a
negative finding.

MELI and JD are advanced on **tentative** grounds and flagged honestly: the
questions identified may turn out, on deeper work, to be the same
already-priced consensus debates I used to reject ADBE, SNOW and WCC. That
risk is named here rather than hidden. Underwriting is where it gets resolved.

---

## Discrimination pairs — outcome

| Pair | Outcome | Basis for the split (or non-split) |
|---|---|---|
| FIS vs. FISV | **Split** — FIS advances, FISV does not | Genuinely different fact patterns: FIS is a one-time, quantified portfolio-reshaping event with an identifiable optics/economics tension; FISV is broad, ongoing operational deterioration already reflected in a large stock decline, with no identified expectations gap. |
| MELI vs. JD | **No split** — both advance, tentatively | Both cleared on specific, numeric, segment-level questions (credit quality at scale; core-retail trend vs. loss-reduction optics), not on "fast growth" or "e-commerce" as such. Symmetry here reflects the evidence found, not a forced outcome. |
| ADBE vs. SNOW | **No split** — neither advances | Both fact patterns are dominated by the same consensus AI-narrative; neither pass isolated a company-specific expectations gap distinct from that narrative. |
| WCC vs. GLNG | **No split, but distinct reasons** — neither advances | WCC: strong, already-and-immediately-priced AI-beneficiary execution, no demonstrated gap. GLNG: a genuine evidence gap from a specialized structure, not a negative finding. |
| NTR | **Does not advance** | Commodity-cycle strength only; no structural mispricing thesis identified. |
| CVS | **Does not advance** | Turnaround already extensively documented and repeatedly re-guided; no remaining gap identified. |

---

## Evidence gaps and blockers for any name that proceeds

1. **No primary-filing read performed.** All evidence above is secondary
   aggregation of disclosed results via web search, not a direct pull of
   10-Q/10-K/20-F/6-K/8-K text through Atlas's `sec_adapter.py` pipeline.
   Deeper underwriting on FIS, MELI or JD should start there.
2. **Foreign private issuer filing forms not verified.** MELI, JD and GLNG's
   exact filer classification (10-K vs. 20-F/6-K) was not confirmed against
   Atlas's identity-resolution layer in this pass.
3. **No fresh-price or session bind was established for any name**, since no
   Stage 7 candidate was produced. If underwriting proceeds, price binding
   follows the existing Gate B–verified path (§18–23 of the charter): NYSE
   names bind through `XNYS`; FISV/MELI/JD/ADBE/GLNG bind through the newly
   supported `XNMS`/`XNGS` → `XNAS` Nasdaq calendar path. This is noted for
   completeness — FISV, ADBE and GLNG are not advancing, so this applies
   concretely only to MELI and JD among the Nasdaq names.
4. **GLNG specifically needs contract- and financing-level primary documents**
   (charter-party terms, counterparty credit, newbuild funding structure)
   before even a discovery-level call can be made with confidence.

---

## Sources consulted (by ticker)

- **FIS:** FIS FY2026 Q1/Q2 results and investor releases; Globe and Mail
  (Worldpay divestiture completion); Seeking Alpha commentary (noted as
  evidence a market disagreement exists, not adopted as thesis); SEC 8-K
  exhibit (Q1 2025 base filing).
- **FISV:** Fiserv 2026 guidance-cut coverage (Yahoo Finance, Globe and Mail,
  PYMNTS, Investing.com, Zacks via Yahoo).
- **MELI:** MercadoLibre Q2 2026 8-K (SEC EDGAR, CIK 0001099590); Q2 2026
  earnings-call coverage (Globe and Mail, Yahoo Finance, StockTitan, Simply
  Wall St).
- **JD:** JD.com Q2 2026 earnings-call coverage (Investing.com, Globe and
  Mail, BigGo Finance, Yahoo Finance).
- **ADBE:** Adobe FY26 Q1–Q2 coverage (Futurum Group, Simply Wall St,
  MarketScale, Alpha Spread).
- **SNOW:** Snowflake Q2 FY27 earnings coverage (SEC EDGAR 8-K exhibit,
  StockStory, Yahoo Finance, 24/7 Wall St.).
- **WCC:** Wesco International Q1–Q2 2026 investor releases and earnings-call
  coverage (Investing.com, GuruFocus, Yahoo Finance).
- **GLNG:** Golar LNG Q2 2026 earnings call and interim report (Investing.com,
  GlobeNewswire, Motley Fool, Yahoo Finance).
- **NTR:** Nutrien Q2 2026 SEC 6-K exhibits; Nutrien investor releases; Yahoo
  Finance coverage.
- **CVS:** CVS Health Q1–Q2 2026 coverage (CNBC, Healthcare Dive, Forbes,
  Insurance Business, BigGo Finance, Yahoo Finance, tikr).

---

## What this record does not do

No return band, required-return band, or return target was created — the
existing early-stage process does not require one at Discovery. No position
size, sizing formula, or capital amount was proposed. No paper capital was
allocated. No Stage 7 comparison or Stage 8 decision was made. No sentiment
source informed any triage call. The frozen basket, venue controls, and
architecture are unchanged.

**Next step, not taken here:** deep underwriting of FIS, MELI and JD, starting
with a primary-filing read for each.

**Capital status: NO REAL PORTFOLIO ACTION.**
