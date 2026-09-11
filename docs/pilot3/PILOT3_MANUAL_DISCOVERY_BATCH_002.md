# PILOT 3 — MANUAL DISCOVERY BATCH 002

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Temporary manual-discovery bridge. Agent World (`PILOT3_AGENT_WORLD_BATCH_001.md`)
> is not yet fully operational; Stock Atlas continues generating opportunity
> candidates manually rather than pausing Pilot 3. **This is temporary and
> does not alter the long-term architecture.**

| | |
|---|---|
| Date registered | September 7, 2026 |
| Pilot | Pilot 3 — Opportunity Discovery Shadow Test |
| Source | `MANUAL_DISCOVERY_BRIDGE` |
| Batch | 002 |

---

## Source provenance

**Source:** `MANUAL_DISCOVERY_BRIDGE`

**Reason:** Agent World is not yet fully operational. Rather than pause
Pilot 3, Stock Atlas continues generating discovery candidates manually.

**Governing principle, unchanged:**

> **Preserve provenance. Remove privilege.**

Manual candidates receive **no underwriting advantage** relative to Agent
World candidates or any other source, exactly as Batch 001 gave none to
Agent World candidates over any other source.

---

## Batch 002 — frozen registration

| Candidate | Discovery signal (secondary) | Initial state | Atlas triage disposition |
|---|---|---|---|
| PATH | Beat estimates, sold off on Q3 guide; concern centers on forward ARR/growth mechanics and agentic-AI competitive pressure | `SURFACE_FOR_TRIAGE` | `NO_DEMONSTRATED_EDGE` (see triage record) |
| MDB | Strong revenue growth, raised FY guide; sold off because Atlas growth held near 29% rather than accelerating | `SURFACE_FOR_TRIAGE` | `PROMOTE_TO_DEEP_UNDERWRITING` (see triage record) |
| SPXC | Material share-price decline despite a prior earnings beat and guidance raise; concern centers on margin softness | `SURFACE_WITH_EVIDENCE_GAP` | `PROMOTE_TO_DEEP_UNDERWRITING` (see triage record) |
| SOLS | Large proposed merger terminated; company announced a meaningful buyback; stock repriced sharply | `EVENT_DRIVEN_HOLD` | Not triaged this record |
| PCG | Major selloff tied to wildfire-liability uncertainty; strategic review announced; capital plan reportedly altered | `SURFACE_WITH_EVIDENCE_GAP` | Not triaged this record |
| DOCU | Strong quarterly performance; IAM product growing as share of ARR; capital returned via buybacks | `SURFACE_WITH_EVIDENCE_GAP` | `PROMOTE_TO_DEEP_UNDERWRITING` (see triage record) |

**Only PATH and MDB receive primary-evidence triage in this record.**
SPXC, SOLS, PCG, and DOCU are registered with their initial discovery state
only — no underwriting, no evidence review, no disposition beyond what is
listed above. SPXC and DOCU need earnings/filing evidence before any triage;
SOLS needs the post-merger standalone capital structure examined before its
event-driven state can be resolved into a real variant or dismissed as a
one-day trade; PCG's initial state explicitly instructs that its low price
is not to be treated as edge given the scale of wildfire-liability
uncertainty.

---

## PATH — full primary-evidence triage

Recorded separately in `PILOT3_PATH_PRIMARY_EVIDENCE_TRIAGE_001.md`.

## MDB — full primary-evidence triage

Recorded separately in `PILOT3_MDB_PRIMARY_EVIDENCE_TRIAGE_001.md`.

## SPXC — full primary-evidence triage

Recorded separately in `PILOT3_SPXC_PRIMARY_EVIDENCE_TRIAGE_001.md`.
Disposition: `PROMOTE_TO_DEEP_UNDERWRITING`. Q2 2026 organic growth (16.9%
company-wide) accounts for roughly 74% of total reported growth (22.9%) —
not acquisition-manufactured. HVAC segment margin fell 260bps for two
specific, disclosed, plausibly temporary reasons (capacity-expansion
startup costs, tariffs), while Detection & Measurement margin expanded
610bps on favorable mix; FY2026 guidance was raised meaningfully across
revenue, adjusted EBITDA, and adjusted EPS. Leverage remains low (~1.5x
pro forma) despite an active five-deal acquisition program. The market's
own initial post-print selloff (−14.4%) fully reversed within a week, but
the stock then gave back the entire recovery over the following five to
six weeks for reasons no evidence gathered in this record explains — named
explicitly as the central open question for deep underwriting. Coarse
valuation (~22x P/E, ~16x EV/EBITDA on raised guidance) is full, not
statistically cheap.

## SOLS — not triaged

`EVENT_DRIVEN_HOLD`. Discovery signal only (terminated merger, subsequent
buyback announcement, sharp repricing). The open question for a future
record: does the post-merger standalone capital structure and valuation
create a durable variant, or is this a one-day event trade with no
persistent mispricing? Not answered here.

## PCG — not triaged

`SURFACE_WITH_EVIDENCE_GAP`. Discovery signal only (wildfire-liability
selloff, strategic review, altered capital plan). Explicitly high
uncertainty. **A low price is not treated as edge** — this instruction is
preserved verbatim from the work order and not reinterpreted.

## DOCU — full primary-evidence triage

Recorded separately in `PILOT3_DOCU_PRIMARY_EVIDENCE_TRIAGE_001.md`.
Disposition: `PROMOTE_TO_DEEP_UNDERWRITING`. IAM's share of ARR has grown
every quarter measured (2.3%→10.8%→12.6%→15.1%) with the pace itself
accelerating through the most recent quarter, corroborated by monotonically
improving GAAP margins, a declining SBC-to-revenue ratio, and a genuine,
accelerating reduction in actual share count (not merely dilution-
offsetting). The central open question — whether this converts into a
higher consolidated growth rate rather than continuing to offset core
e-signature maturity (total revenue has held flat at 8–9% YoY for five
consecutive quarters despite IAM's rise) — is unresolved, not refuted, and
is the focus for deep underwriting. A properly Gate-B-certified `FRESH`
price bind could not be obtained this record (market open at decision time,
Gate B correctly returned `STALE`); an unvalidated reference price was used
with explicit caveats.

---

## Lesson applied from AVGO deep underwriting

Per `PILOT3_AVGO_DEEP_UNDERWRITING_001.md` §7 and §11: strong reported
economics plus a stock decline does not by itself prove mispricing. For
both PATH and MDB, this record explicitly reverse-engineers what the
current price already appears to require, rather than promoting because
of a beat, a guidance raise, a selloff, or a below-peer multiple in
isolation. The two candidates reach **different** dispositions from
similar-looking surface patterns (beat + selloff) precisely because the
underlying primary evidence differs — see the individual triage records.

---

## Pilot 3 discovery log — Batch 002

| Candidate | Source | Initial state | Atlas disposition | Survived primary-evidence triage? |
|---|---|---|---|---|
| PATH | `MANUAL_DISCOVERY_BRIDGE` | `SURFACE_FOR_TRIAGE` | `NO_DEMONSTRATED_EDGE` | No — the specific discovery variant (overreaction to near-term mechanics) was contradicted by a primary, guided, material growth-deceleration fact |
| MDB | `MANUAL_DISCOVERY_BRIDGE` | `SURFACE_FOR_TRIAGE` | `PROMOTE_TO_DEEP_UNDERWRITING` | Yes — the specific discovery variant (market over-weighting a lagging metric) was corroborated by primary forward-bookings and management evidence |
| SPXC | `MANUAL_DISCOVERY_BRIDGE` | `SURFACE_WITH_EVIDENCE_GAP` | `PROMOTE_TO_DEEP_UNDERWRITING` | Yes — organic growth (74% of total growth) and a specifically-attributed, testable margin-pressure cause corroborated the discovery variant; an unexplained secondary price decline is named as an open question for deep underwriting |
| SOLS | `MANUAL_DISCOVERY_BRIDGE` | `EVENT_DRIVEN_HOLD` | Not yet triaged | N/A |
| PCG | `MANUAL_DISCOVERY_BRIDGE` | `SURFACE_WITH_EVIDENCE_GAP` | Not yet triaged | N/A |
| DOCU | `MANUAL_DISCOVERY_BRIDGE` | `SURFACE_WITH_EVIDENCE_GAP` | `PROMOTE_TO_DEEP_UNDERWRITING` | Yes — the discovery variant's per-share-economics half was corroborated by primary evidence; the growth-inflection half remains open, not refuted, and is the focus for deep underwriting |

No discovery score. This log records outcomes only.

---

## What this record does not do

No deep underwriting (PATH is closed at `NO_DEMONSTRATED_EDGE`; MDB's
promotion does not begin deep underwriting here). No triage of SPXC, SOLS,
PCG, or DOCU. No Stage 7 or Stage 8. No capital allocated. No architecture
change. Batch 001 (AVGO, XOM, SMH, AAPL, JPM, NVDA) is untouched.

**Capital status: NO REAL PORTFOLIO ACTION.**
