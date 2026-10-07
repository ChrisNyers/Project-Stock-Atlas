# CONTROLLED LIVE PILOT — CYCLE 0 BASELINE 001

> **HUMAN-SUPPLIED BASELINE — APPROXIMATE BY DESIGN**
> Human Stage 8 remains the sole capital authority. No automated execution.
> No investment alpha is established. No candidate selected. No Stage 7 run.
> No broker login, account number, or credential is stored in this repo.

| | |
|---|---|
| Date frozen | 2026-10-07 |
| Provenance | Every value below was **supplied by Chris** in the Cycle 0 work order of 2026-10-07. Nothing was inferred, reconstructed from price snapshots, or taken from older test portfolios (the Pilot 2 $50,000 paper basket and the Investor Policy's example exposures are not used). |
| Repo at freeze | `71e461a` |
| Gate B | `COMPLETE — PASS / GATE B CLOSED` (see Master Plan, "Gate B Closure Verdict") |
| Governing policy | Phase 2 Calibration & Investor Policy v1.0, retained outside the repo at `OneDrive/Stock Atlas/Stock_Atlas_Phase2_Calibration_Investor_Policy_v1.0.md` — **SHA-256 `d20019fd06d8f9b40fbdebf3f25844ccd1eab41750565dba3d475fbf65deb104`** (9,433 bytes) |

> **Superseded in part by "Correction 001 (2026-10-07)" at the end of this file.** The ≈$750,000 denominator, the ≈$691,000 stock figure, "T-bills only", and the T+2 funding pocket below are the original freeze and are preserved as history; the corrected values govern.

---

## 1. Frozen baseline (as supplied)

| Item | Frozen value |
|---|---|
| Account scope | **One account: taxable brokerage.** Include in household portfolio: YES. No other account is in scope. The Policy §17 sub-type (Individual / Joint / Trust / Other Taxable) was **not supplied**; recorded as `TAXABLE_BROKERAGE`, sub-type `UNVERIFIED`. |
| Denominator | **≈ $750,000 total account value, governing.** Rounding is intentional. As-of basis: the Cycle 0 baseline supplied by Chris on 2026-10-07; not reconstructed from price snapshots. |
| Reconciliation | **≈ $691,000 stocks + ≈ $59,000 T-bills/cash-equivalent = $750,000.** Checked: it sums exactly. Implied weights: stocks ≈ 92.13%, T-bills ≈ 7.87%. |
| Defensive allocation | **≈ $59,000 T-bills / cash-equivalent.** It is the current defensive allocation and part of the denominator. It is **not** the pilot's funding source. |
| Funding pocket | **New outside capital, deployable range $25,000–$50,000, available T+2.** Funding mode: `EXTERNAL_NEW_CAPITAL` only. |
| Existing cash as funding | **NO** for this pilot. |
| Recycle / trim | **NO.** Policy is **ADD-ONLY**: existing holdings may not be trimmed or recycled unless Chris explicitly changes the rule. No recycle comparison is permitted in Stage 7 under this policy. |
| Required Liquidity Reserve | **N/A** — no separately protected reserve in this baseline. None created. |
| Annual Distribution Reserve | **N/A** — none created. |
| Concentration overrides | **NONE.** Frozen Atlas calibration applies; no new sector or position limits added. |
| Execution | Manual, by Chris. No automated execution. |

## 2. Holdings (all in the one taxable account)

Tickers supplied (28): AVGO, AAPL, MSFT, ABBV, JPM, COST, NEE, ALL, HD, MRK, CVX, RTX, PAYX, MS, C, LLY, GS, WEC, ETN, FAST, OKE, TROW, PFE, IBM, GD, COR, KMB, WSO.

- **Only one position has a supplied value:** WSO — 8 shares × $280.905 reference = **≈ $2,247.24** (≈ 0.30% of $750,000).
- **Per-holding approximate market values were not supplied for the other 27 names.** The ≈ $691,000 stock total is **not allocated across tickers**, and no weight is inferred from the order of the list or from any price snapshot.
- The wording "including" leaves open whether the 28 tickers are the complete list; completeness is **`UNVERIFIED`**.
- The frozen `Holding` contract also needs a `security_key` (SEC-CIK based) per name. None was bound; that is identity binding done at materialization, not research, and was **not** performed here.
- Exact share counts and cost basis are not required now (a future trim/sale would make them material, and trims are barred by the ADD-ONLY policy).

## 3. Fields left UNVERIFIED (may stay so until material; fail closed)

Tax lots and basis; bracket and state-tax implications; liquidity and execution (per candidate, human-attested); per-holding dominant-driver overlap; ETF look-through if relevant; Treasury/Cash yield reference and duration basis; candidate-specific capacity; account sub-type; completeness of the holdings list; per-holding values for 27 names; per-holding `security_key`.

**Fail-closed consequence under the existing controls (verified against the code):** a funded `INITIATE`/`ADD` cannot be persisted unless tax, liquidity, and execution constraints are all `VERIFIED` (`decision_store.py`); Stage 7's funding check requires `VERIFIED` or an explicit human acceptance. They must therefore be attested `VERIFIED` by Chris at the Cycle 1 decision, or the decision becomes REVIEW.

## 4. Validation against the existing frozen contracts

Run on 2026-10-07 with the repo's own classes (`PortfolioSnapshot`, `FundingPocket`, `validate_funding_pocket`, `capacity_curve_dollars`); the script lived outside the repo and no control was changed.

| Check | Result |
|---|---|
| `PortfolioSnapshot` builds at $750,000, ADD-ONLY, trims off | **PASS** |
| Trims and ADD-ONLY are mutually exclusive (control guard) | **PASS** (guard confirmed) |
| Denominator reconciles ($691,000 + $59,000) | **PASS** |
| Funding pocket as supplied (T+2) — `t_plus_1_deployable=False` | **FAIL-CLOSED: "No deployable funding capacity"**, at $25,000 and at $50,000 (deployable amount computes to $0) |
| Same pocket if the funds have landed (`t_plus_1_deployable=True`) | Passes only with tax/liquidity/execution `VERIFIED`, or with explicit human acceptance when `UNVERIFIED` |
| Full holdings table | **Cannot be built** — 27 of 28 values not supplied (not invented) |

**Result: the baseline does NOT fully validate under the existing frozen contracts.** I did **not** set `t_plus_1_deployable=True` to make the pocket pass, and I did not fill holdings. The frozen control treats a pocket not deployable by T+1 as zero; T+2 availability is therefore a **real open item**, not a rounding issue. It is a timing condition (Cycle 1 can start only when the outside capital has landed and is deployable), and it is Chris's call how to record it.

## 5. Open items blocking `CYCLE 1 READY`

1. **Per-holding approximate market values** for the 27 unvalued names (rounded is fine), and confirmation that the 28-ticker list is complete.
2. **Funding pocket deployability.** Either the outside capital has landed (then record it as deployable and state the amount), or Cycle 1 waits until it does. The controls will not accept a T+2 pocket as deployable.

## 6. Informational: what the frozen calibration implies for sizing (no candidate, no recommendation)

At a $750,000 base with new outside capital, post-trade portfolio weights correspond to (repo `capacity_curve_dollars`): 1% ≈ $7,576; 2% ≈ $15,306; 3% ≈ $23,196; 5% ≈ $39,474; 10% ≈ $83,333. Frozen Position Stages (Policy §2): STARTER 1–2%, PARTIAL >2–4%, STANDARD >4–7%. A $25,000–$50,000 pocket is ≈ 3.3%–6.7% of the base, so **one new name cannot absorb the whole pocket as a STARTER** (≈ $15,306 maximum). How much of the pocket any cycle uses is Chris's Stage 8 decision; unused pocket stays in the Treasury/Cash alternative.

## 7. Status after this freeze

> **`CONTROLLED LIVE PILOT — CYCLE 0 BASELINE FROZEN, TWO OPEN ITEMS — CYCLE 1 NOT READY`**
> (Authorization unchanged: `AUTHORIZED TO BEGIN UNDER HUMAN STAGE 8`.)

The status `CYCLE 0 COMPLETE / CYCLE 1 READY` was **not** granted because the baseline does not validate (§4). Cycle 1 has not started. The `TWELVEDATA_API_KEY` remains absent and will block any price bind in Cycle 1; it does not affect this baseline.

**Capital status: NO REAL PORTFOLIO ACTION.**

---

## Correction 001 (2026-10-07) — append-only

Chris clarified the remaining baseline items. These **supersede** the original
values where they differ; the original sections above are not rewritten.

| Item | Corrected, governing value |
|---|---|
| Stocks | **$624,905.93 exact** (sum of the exact per-holding market values Chris supplied). The rounded ≈$691,000 is superseded. |
| Holdings list | **Complete: 28 names** (AVGO, AAPL, MSFT, ABBV, JPM, COST, NEE, ALL, HD, MRK, CVX, RTX, PAYX, MS, C, LLY, GS, WEC, ETN, FAST, OKE, TROW, PFE, IBM, GD, COR, KMB, WSO) in the one taxable account. WSO = 8 sh × $280.905 reference = $2,247.24 (≈ 0.33% of the identified value). |
| Defensive balance | **≈ $59,000 across T-bills AND money market** (split not supplied). It is not "T-bills only". |
| Identified portfolio value | **≈ $683,905.93** = $624,905.93 + ≈$59,000. Weights: stocks ≈ 91.37%, defensive ≈ 8.63%. The ≈$750,000 figure was a rough estimate and is **superseded**. **No residual position was invented** to reconcile to it. |
| Funding pocket | **New outside capital, available now, $25,000–$50,000, deployable T+1.** Existing holdings and existing T-bills/money market are **not** the funding source. |
| Policy | **ADD-ONLY**; no trims; no recycle. Reserves N/A; concentration overrides NONE (unchanged). |
| Cycle 1 sizing rule | Use the **specific contemplated increment** within $25,000–$50,000 for any actual decision; do not assume the full $50,000. |

**Validation (existing frozen contracts, run 2026-10-07, script outside the repo, no control changed)**

| Check | Result |
|---|---|
| `PortfolioSnapshot` at $683,905.93, ADD-ONLY, trims off | **PASS** |
| Funding pocket at $25,000 and at $50,000, T+1 deployable | **PASS** — deployable amount equals the full amount; the earlier T+2 "no deployable capacity" failure is **resolved** by the clarification (it was not overridden) |
| Stage-7 funding check with tax/liquidity/execution `UNVERIFIED` and no human acceptance | **FAIL-CLOSED**, as designed; passes when attested `VERIFIED` (or with explicit human acceptance at Stage 7; final persistence still needs `VERIFIED`) |
| Dollar capacity on this base, new outside capital: 1% ≈ $6,908; 2% ≈ $13,957 (STARTER ceiling); 3% ≈ $21,152; 5% ≈ $35,995; 10% ≈ $75,990 | informational |
| Pocket as share of base | $25,000 ≈ 3.66%; $50,000 ≈ 7.31%. One new name cannot absorb the whole pocket as a STARTER (≈ $13,957 max). Sizing remains Chris's Stage 8 decision. |

**One item remains open: the 28 per-holding values.** Chris's message says the
exact values were originally supplied, and gives their exact sum. **The
individual values are not in this repo, in the retained project files, or in
any session record available to the recorder** — only the sum and WSO's value
were present in this workstream. They were **not** reconstructed, estimated
from prices, or allocated from the total. Until they are entered, the frozen
`Holding` table (value, weight, account per name) cannot be built, and
per-name exposure and common-driver tests cannot run, so the baseline is **not**
declared complete. **Acceptance check when supplied:** the 28 values must sum to
**exactly $624,905.93** (WSO = $2,247.24); a mismatch is reported, not
adjusted. Account sub-type and per-holding identity keys remain `UNVERIFIED`
(identity binding, not research).

**Remaining case-by-case (`UNVERIFIED` until material; fail closed):** tax
lots/basis and tax implications; liquidity and execution (per candidate,
human-attested); per-holding dominant-driver overlap; ETF look-through;
Treasury/Cash yield reference and duration basis (the defensive balance is
T-bills + money market); candidate-specific capacity; account sub-type.

**Status after Correction 001:**

> **`CONTROLLED LIVE PILOT — CYCLE 0 BASELINE CORRECTED, HOLDING VALUES OUTSTANDING — CYCLE 1 NOT READY`**
> (Authorization unchanged. Cycle 1 not started. No candidate, no Stage 7.)

`CYCLE 0 COMPLETE / CYCLE 1 READY` will apply once the 28 values are entered and
reconcile to $624,905.93.

**Capital status: NO REAL PORTFOLIO ACTION.**
