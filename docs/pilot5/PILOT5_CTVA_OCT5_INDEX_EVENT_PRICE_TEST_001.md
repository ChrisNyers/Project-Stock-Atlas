# PILOT 5 — CTVA OCTOBER 5 INDEX-EVENT PRICE TEST 001

> **PAPER / SHADOW ONLY — NO REAL PORTFOLIO ACTION**
> Price test against the frozen pre-event underwriting only. No capital
> decision. No Stage 7. No revision of the frozen ranges or threshold.

| | |
|---|---|
| Date | Monday, October 5, 2026 (evidence through ~6:00 PM EDT, after the close) |
| Frozen baseline | `529286a` (ranges and ≈$10.40 threshold unchanged); legal checkpoints `e78d254`, `8063046` |
| Event | CTVA S&P 500 deletion and S&P MidCap 400 addition effective before the Oct 6 open, executed at the Oct 5 close |

---

## 1. Legal re-check (done first)

**Status: `LEGAL_OUTCOME_PENDING_VERIFICATION` — no invalidating order is
established.**

- **No authoritative record of the Oct 2 Indiana TRO hearing outcome** was
  found: no order or docket entry (court records not reachable), no official AG
  release reporting a result (Indiana, Oregon, Maryland, Vermont checked), and
  no reliable press report of the outcome. Trade and legal press
  (Indiana Lawyer, IBJ, Agri-Pulse, Insurance Journal, Business Record) stops at
  "scheduled for Friday." Silence is **not** read as denial or as a favorable
  result.
- **Corteva SEC filings:** the only filing after Oct 1 is an **Oct 5 8-K**
  (Items 1.01, 2.01, 9.01) reporting completion of the separation. It does not
  mention the lawsuit, the TRO, or PFAS. Its attached Separation and
  Distribution Agreement (dated Sept 29) allocates liabilities under the
  2021 DWDP PFAS MOU, including escrow funding, to **RemainCo (Corteva)** as
  "Legacy Liabilities," with mutual indemnities. That is consistent with
  the frozen underwriting, which kept PFAS with New Corteva, and it adds no
  new quantification.
- **Requested relief is not an order.** The Oct 1 complaint (Cause No.
  49D01-2610-CE-054574) prays for avoidance of the Vylor transfers, TRO and
  injunctions barring disposition of proceeds and shareholder distributions,
  and a constructive trust. These are allegations and requests.
- **Conflation guard:** "court denied TRO" in press refers to the federal D.S.C.
  denial (Sept 29–30), not Indiana.
- **Consequence:** the frozen adverse-TRO trigger is neither tripped nor
  cleared. I proceeded with the observation, labeled as such, because no
  invalidating order is established. If an adverse order exists and was
  missed, the framework treats it as invalidating.

---

## 2. October 5 session data and certification

**Certification: `UNCERTIFIED`.** `TWELVEDATA_API_KEY` is absent; Gate B is
BLOCKED for CTVA. The data below is from public aggregators and is research
evidence only.

| Session | Open | High | Low | Close | Change | Volume (Yahoo / StockAnalysis) |
|---|---|---|---|---|---|---|
| Oct 1 | 14.44 | 14.44 | 11.84 | 12.57 | (spin adjustment) | 88.38M / 88.38M |
| Oct 2 | 12.39 | 13.04 | 11.87 | 11.92 | **−5.2%** | 78.72M / 78.56M |
| **Oct 5** | **11.81** | **12.63** | **11.74** | **12.39** | **+3.9%** | **183.06M / 182.32M** |

- The two sources agree on OHLC; volumes differ by ≤0.4%. They may share a
  feed, so agreement is not independent confirmation. Yahoo shows an
  after-hours print of 12.44 at 5:51 PM.
- Oct 5 volume ≈ **27% of the ≈667.2M shares** and ≈**26x** Yahoo's average
  volume (6.94M; the average rose from 4.45M a few days earlier). It is 2.1x
  Oct 1 and 2.3x Oct 2. Three-session volume is ≈350M shares (≈52% of shares
  outstanding).
- **Comparators (Yahoo, uncertified):**

| | Oct 2 | Oct 5 |
|---|---|---|
| CTVA | −5.2% | +3.9% |
| S&P 500 | +0.73% | +0.66% |
| XLB (Materials) | +0.66% | +1.31% |
| S&P MidCap 400 index | +0.96% | +0.28% |
| VYLR (anomalous row, see below) | −1.5% | +9.0% |

  CTVA lagged the market by ≈5.9 points on Oct 2 and led it by ≈3.3 points on
  Oct 5. Yahoo's VYLR Oct 5 row shows a low (66.64) **above** its open
  (66.60), so that row is internally inconsistent; I use only its close
  loosely and draw nothing from it.
- **Not available:** closing-auction volume and imbalance (no public source
  found), intraday bars, and the Oct 6 open.

---

## 3. Index-flow evidence: observed versus inferred

**Observed**
- The index changes were published and unchanged (S&P DJI release).
- Oct 5 volume was exceptional (≈183M shares) and the price **rose** into the
  close: open 11.81, close 12.39, +3.9% on the day, ahead of the S&P 500,
  Materials, and MidCap 400.
- CTVA's weakness came **earlier**: −5.2% on Oct 2, with 78.7M shares traded,
  against rising markets.
- The lowest print across the three post-spin sessions was **11.74**.

**Inferred (not verified)**
- Much of Oct 5's volume is probably index-related, because the S&P 500
  sellers and MidCap 400 buyers execute at the close; with gross index
  trading estimated at roughly 140–167M shares sold and 73–87M bought, the
  matched crossing would account for a large share of the day. I could not
  see the auction.
- The Oct 2 decline may reflect anticipation of the S&P announcement (which
  was published after the Oct 1 close), the Oct 2 legal hearing, or other
  selling. **I found no news that explains it, and I do not attribute it.**
- The estimated **net-sale direction** (S&P 500 passive share larger than
  MidCap 400 passive share) remains plausible, but the data cannot confirm it.
  Rising into the close is the opposite of what a large, un-offset net
  forced sale would normally show, so the net imbalance was either smaller
  than my fragile 25–95M-share bracket, absorbed by buyers, or already
  priced on Oct 2.
- **Anticipation:** the pattern (a decline before the event day and a
  recovery on it) is consistent with substantial anticipation. It is not proof.
- A falling stock would not have proved forced selling, and a rising one does
  not disprove it. This record concludes only that **no price dislocation
  appeared at the event.**

---

## 4. Comparison with the frozen valuation (unchanged)

| Frozen item | Level | Oct 5 close $12.39 |
|---|---|---|
| Further-review threshold | ≈ $10.40 | **19% above** |
| Downside case | ≈ $10.4–12.0 | **3% above the top** of the band |
| Base case | ≈ $15.9–18.7 | 22–34% below the base band |
| Strong case | ≈ $23.0–26.3 | far below |

The lowest print of the event session, $11.74, was 12.9% above the
threshold. The stock never traded within the "further review" zone on Oct 1,
Oct 2, or Oct 5. Market capitalization at the close is ≈$8.27B. The
ranges were **not** moved.

---

## 5. Fundamental-change assessment

- **PFAS litigation:** no ruling or order found. The Oct 5 8-K confirms PFAS
  MOU liabilities sit with Corteva, as underwritten. The complaint's
  allegations (≈$14B retained business; PFAS liabilities "well into the tens of
  billions") remain unproven and unquantified.
- **Regulatory:** nothing new beyond the FTC order already recorded.
- **Operating and capital-structure disclosures:** none beyond the
  separation-completion 8-K. No new EBITDA, debt, or cash figures.
- **Analyst targets** ($15–18 Buy ratings per an aggregator summary) were
  seen but not used; they are secondary and I did not verify them.
- **Is any weakness better explained by a change in value?** The Oct 2 decline
  is unexplained. No evidence ties it to a value change, and no evidence ties
  it to forced flow. It did not carry price to the threshold.

---

## 6. Market-could-be-right case

CTVA's price, at or just above the top of the frozen downside band, may
already reflect what the framework said: a crop-protection stub with a
downgraded rating, a 10-year conduct remedy, and a contested-asset lawsuit
seeking to reach value that left with Vylor. The unresolved Oct 2 outcome
means the market could be pricing a tail that no one can bound. The
Oct 5 rally may be short covering or index-arbitrage unwinds, and the Oct 6
open and later docket events could still move the price either way.

---

## 7. Final disposition

> ## `NO_DEMONSTRATED_INVESTABLE_DISLOCATION`

**Does the Oct 5 event justify a Stage 7 capital comparison? No.** The price
stayed above the frozen downside band and 19% above the ≈$10.40 threshold
through the event session; it rose into the close; relative weakness
occurred on Oct 2 and was not shown to be flow. A price-based dislocation,
the only thing this test could demonstrate, did not appear. This is **not** a
statement that CTVA is cheap or expensive, that the net-sale direction was
wrong, or that the legal tail is benign. It is also not
`BLOCKED_BY_MATERIAL_UNCERTAINTY`: the unresolved legal outcome would matter
for an entry decision, but the price test fails on price regardless.
`CONTINUE_OBSERVATION_FOR_SPECIFIC_EVIDENCE` was not chosen because no
specific pending evidence would revive the threshold test on this frozen
framework except a >16% drop (below $10.40), which a new work order can
address if it happens.

---

## 8. What Pilot 5 learned from CTVA

- A **documented** index migration is not a dislocation. Volume reached ≈26x
  the average and ≈27% of shares in one session, yet price rose into the close.
- The mechanics were right and the price effect was absent or already spent.
  Pre-registering the threshold made the result pass/fail within minutes
  of the close.
- The weakness that did appear (Oct 2) came before the event, which supports
  the market-anticipation reading of the Discovery clock: early relative to the
  event is not early relative to recognition.
- Dirty-fundamental stubs with a live legal tail are poor forced-flow tests.
  The Crasus, MSGR, and CTVA records agree.
- Atlas's contribution was framing and discipline: the migration (not
  one-way selling) framing, the ex-spin price basis, a fragile-flow
  bracket, and freezing the valuation before the event. It did not produce an
  investable edge.
- Evidence gaps that mattered: no certified prices, no closing-auction data,
  no court record. Aggregator rows can be internally inconsistent (VYLR
  Oct 5).
- Across Pilot 5 so far (VYLR, Crasus, MSGR, CTVA) no situation has
  produced a demonstrated investable edge.

---

## 9. Controls and isolation

CBRS remains **surfaced only**: not researched, not triaged. Unchanged: the
`529286a` underwriting and its ranges, the Scan 002 triage record, the Vylor
records (including the price test), Crasus, MSG Rangers, Pilot 4, the frozen
control layer, and the facade. No code, test, or configuration change. No
Scan 003, no Stage 7, no new valuation exercise.

**Capital status: NO REAL PORTFOLIO ACTION.**
