"""Backfill MCD and RPM from the frozen Cycle 1-2 records.

Every event is flagged backfilled=True and uses only facts already in those
records; nothing here is new research. Seeds an EMPTY ledger only.
"""
from pathlib import Path

from . import ledger

D = "docs/controlled_live_pilot/"


def seed(path: Path = ledger.DEFAULT_LEDGER) -> int:
    if ledger.read_events(path):
        raise ledger.LedgerError("ledger is not empty; refusing to seed")
    kw = dict(backfilled=True)
    ledger.surface(
        path, name="McDonald's", ticker="MCD", source="HUMAN", effective_date="2026-10-07",
        source_detail="Selected by the human operator (Chris) for Cycle 1; not surfaced by Atlas or Scout.",
        why_surfaced="Human-selected for research. Frozen pre-Atlas stance: neutral — would research, would not buy on "
                     "current knowledge; primary concern is valuation.",
        investment_question="Are the quality and durability of the business already fully reflected in the price — does "
                            "underwriting show attractive risk/reward and a meaningful advantage vs SPY, Treasury/Cash and Do Nothing?",
        refs=[D + "CYCLE1_MCD_PRE_ATLAS_STANCE_001.md"], **kw)
    ledger.change_state(
        path, candidate_id="MCD", to_state="UNDERWRITING", effective_date="2026-10-07",
        reason="Human ordered underwriting after the pre-Atlas stance was frozen (QUICK_TEST step not used).",
        refs=[D + "CYCLE1_MCD_UNDERWRITING_001.md"], **kw)
    ledger.add_note(
        path, candidate_id="MCD", effective_date="2026-10-07",
        text="Underwriting disposition was CONTINUE_UNDERWRITING_FOR_SPECIFIC_EVIDENCE (= remain in UNDERWRITING). "
             "Variant not demonstrated; advantage vs SPY not demonstrated; price evidence uncertified.", **kw)
    ledger.change_state(
        path, candidate_id="MCD", to_state="PARKED", effective_date="2026-10-07",
        reason="Official Investor Day Select Slides contain no partnering schedule, 2027-28 earnings framework or "
               "numeric bridge; the decisive evidence is dated.",
        waiting_on="Q3 2026 results and call (U.S. comp / guest counts vs guidance, September/Q4 trend, FY2026 outlook) "
                   "and any published partnering schedule / 2027-28 earnings framework.",
        parked_until="2026-11-04", parked_until_verified=True,
        revisit_questions=[
            "Q3 U.S. comp and guest-count trend vs the 'slightly negative' guidance?",
            "Are September/Q4 U.S. comps turning positive?",
            "Is the FY2026 outlook (operating margin, FCF conversion, capex) unchanged?",
            "Is a partnering schedule / 2027-28 earnings framework now published (currently untestable)?"],
        refs=[D + "CYCLE1_MCD_UNDERWRITING_001.md"], **kw)

    ledger.surface(
        path, name="RPM International", ticker="RPM", source="HUMAN", effective_date="2026-10-09",
        source_detail="Selected by the human operator (Chris) for Cycle 2; not surfaced by Atlas or Scout.",
        why_surfaced="Human-selected for research. Frozen pre-Atlas stance: neutral — does not know RPM well enough to "
                     "have a buy view; main concern is whether the slowdown is the start of a broader demand downturn.",
        investment_question="Is the construction slowdown temporary or cyclical, is the business fundamentally healthy, "
                            "and does the current valuation reflect those risks appropriately?",
        refs=[D + "CYCLE2_RPM_PRE_ATLAS_STANCE_001.md"], **kw)
    ledger.change_state(
        path, candidate_id="RPM", to_state="UNDERWRITING", effective_date="2026-10-12",
        reason="Human ordered underwriting after the pre-Atlas stance was frozen (QUICK_TEST step not used).",
        refs=[D + "CYCLE2_RPM_UNDERWRITING_001.md"], **kw)
    ledger.change_state(
        path, candidate_id="RPM", to_state="PARKED", effective_date="2026-10-12",
        reason="Human challenge accepted: evidence does not establish that the current valuation fully compensates for a "
               "cyclical downturn; decisive evidence is dated. Research hold until the Investor Day.",
        waiting_on="2026-11-09 Investor Day (company-announced): does it change the margin, restructuring, "
                   "capital-allocation or earnings framework.",
        parked_until="2026-11-09", parked_until_verified=True,
        revisit_questions=[
            "Is CPG weakness stabilizing, recovering, or deteriorating?",
            "Does primary evidence support the claim that the polyol disruption was material and is resolved?",
            "Is backlog/order commentary improving or deteriorating?",
            "Is pricing beginning to recover raw-material inflation?",
            "Does the November 9 Investor Day materially change RPM's medium-term margin, restructuring, "
            "capital-allocation, or earnings framework?"],
        refs=[D + "CYCLE2_RPM_UNDERWRITING_001.md"], **kw)
    return len(ledger.read_events(path))


def seed_evidence(path: Path = ledger.DEFAULT_LEDGER) -> int:
    """Append template/evidence entries for MCD and RPM, transcribed from the frozen
    Cycle 1-2 records (no new research). Appends only; earlier history is untouched.
    Grade rule for INFERENCE / CAPITAL IMPLICATION: the weakest input source.
    "Strongest" designations are the recorder's reading of those records."""
    cands = ledger.replay(path)
    if not {"MCD", "RPM"} <= set(cands) or any(cands[c]["evidence"] for c in ("MCD", "RPM")):
        raise ledger.LedgerError("evidence already seeded, or MCD/RPM missing")
    n0 = len(ledger.read_events(path))
    kw = dict(backfilled=True)
    M, R = D + "CYCLE1_MCD_UNDERWRITING_001.md", D + "CYCLE2_RPM_UNDERWRITING_001.md"

    def ev(cid, tag, direction, grade, text, ref, known_at, date_):
        return ledger.add_evidence(path, candidate_id=cid, tag=tag, direction=direction, grade=grade,
                                   text=text, source_ref=ref, known_at=known_at, effective_date=date_, **kw)

    ledger.record_falsification(
        path, candidate_id="MCD", effective_date="2026-10-07", known_at="2026-10-07", grade="UNCERTIFIED",
        test="F1-F4 case-killers: valuation stretched; parent-business deterioration; balance-sheet fragility; "
             "return clearly inferior to alternatives.",
        result="SURVIVED", source_ref=M + " §1 (ran as part of underwriting; QUICK_TEST step not used)", **kw)
    f1 = ev("MCD", "FACT", "FOR", "UNCERTIFIED",
            "Year-end trailing P/E ran ~25.5-25.6x in 2023-25 vs ~18.9x on TTM GAAP EPS $12.31 at an uncertified "
            "price ($232.24); H1 2026 EPS +6% (+3% cc). Price component is uncertified.", M + " §1 F1, §3", "2026-10-07", "2026-10-07")
    ev("MCD", "FACT", "AGAINST", "PRIMARY",
       "Official Investor Day Select Slides (22) give no annual partnering schedule, no rent-relief/capital split, "
       "no remodel counts, no 2027-28 operating-income or EPS framework and no numeric bridge from the margin target.",
       M + " Addendum 002", "2026-10-07", "2026-10-07")
    ev("MCD", "MANAGEMENT_CLAIM", "NEUTRAL", "PRIMARY",
       "Slides: payback ~4 years for franchisees after partnering and ~5-6 years for McDonald's on restaurant-level "
       "investment; forward-looking company estimates.", M + " Addendum 002", "2026-10-07", "2026-10-07")
    ev("MCD", "MANAGEMENT_CLAIM", "FOR", "SECONDARY",
       "U.S. softness is an execution miss, not a strategy flaw; September U.S. comps positive (third-party "
       "transcript of the 2026-09-23 Investor Day, not checked against audio).", M + " §5", "2026-09-23", "2026-10-07")
    ev("MCD", "CONTEXT", "AGAINST", "UNCERTIFIED",
       "The 10-year Treasury at 5.27% (primary) sets a high hurdle; industry traffic is flat (per management); the stock "
       "fell ~4.8% on the 2026-09-23 Investor Day to new 52-week lows (Yahoo, uncertified).", M + " §5", "2026-10-06", "2026-10-07")
    ev("MCD", "INFERENCE", "FOR", "UNCERTIFIED",
       "The price needs only ~1.5-3.5% EPS growth to beat the 10-year, so much of the pessimism is already in the price.",
       M + " §5", "2026-10-07", "2026-10-07")
    ev("MCD", "INFERENCE", "AGAINST", "UNCERTIFIED",
       "Market-could-be-right: if EPS growth stays near the ~2.5% 2023-TTM CAGR, at 16-19x the stock earns ~2-6%, "
       "at or below the 10-year (5.27%) and below SPY's likely return.", M + " §6", "2026-10-07", "2026-10-07")
    ev("MCD", "VARIANT", "NEUTRAL", "UNCERTIFIED",
       "Candidates only, NOT demonstrated: V1 parent EPS compounds >=5% through 2030 despite flat U.S. traffic; "
       "V2 the de-rating from ~25x to ~19x over-extrapolates a U.S. execution lapse.", M + " §5", "2026-10-07", "2026-10-07")
    ev("MCD", "CAPITAL_IMPLICATION", "NEUTRAL", "UNCERTIFIED",
       "Scenario-weighted IRR ~8.0% (severe/downside/base/strong -2.7/+2.0/+8.9/+15.4% at 10/20/45/25) vs 10-yr 5.27% "
       "and 3-mo 4.21%; advantage vs SPY not demonstrated. Illustrative, not a forecast.", M + " §4, §8", "2026-10-07", "2026-10-07")
    a1 = [e_ for e_ in ledger.replay(path)["MCD"]["evidence"] if e_["tag"] == "FACT" and e_["direction"] == "AGAINST"][0]["seq"]
    ledger.set_strongest(path, candidate_id="MCD", direction="FOR", target_seq=f1["seq"], effective_date="2026-10-07", **kw)
    ledger.set_strongest(path, candidate_id="MCD", direction="AGAINST", target_seq=a1, effective_date="2026-10-07", **kw)
    for q in ("Does MCD offer a meaningful expected advantage vs SPY? (not demonstrated)",
              "Can parent EPS compound >=~5% through 2030 despite flat U.S. traffic (V1)? Not evidenced beyond H1 "
              "results and management claims; the primary slides contain no EPS/OI framework."):
        ledger.add_unresolved(path, candidate_id="MCD", question=q, effective_date="2026-10-07", **kw)

    r_against = ev("RPM", "FACT", "AGAINST", "PRIMARY",
                   "CPG organic growth by quarter: Q1 FY26 +5.4%, Q2 +0.8%, Q3 +6.9%, Q4 +5.7%, then Q1 FY27 -1.7%; "
                   "CPG adj. EBITDA -9.7% to $166.2M.", R + " §2", "2026-10-06", "2026-10-12")
    r_for = ev("RPM", "FACT", "FOR", "PRIMARY",
               "Q1 FY27: PCG organic +7.9%, Consumer organic +5.2%; consolidated organic +3.1%, record adj. EBITDA "
               "$405.5M (+4.5%), adj. EPS $1.98 (+5.3%).", R + " §2", "2026-10-06", "2026-10-12")
    ev("RPM", "MANAGEMENT_CLAIM", "FOR", "SECONDARY",
       "School/hospital slowdowns temporary; polyol shortage resolved; backlog rebuilding; CPG back to positive "
       "organic growth by fiscal year-end (auto-generated call transcripts, unverified against primary).",
       R + " §2, §5", "2026-10-06", "2026-10-12")
    ev("RPM", "CONTEXT", "AGAINST", "SECONDARY",
       "Census put-in-place spending through Aug 2026 (nominal, FRED mirror): health care -3.0% YoY, educational "
       "-0.5%, commercial -5.4% (-21% below its Sep-2023 peak).", R + " §2", "2026-08-31", "2026-10-12")
    ev("RPM", "INFERENCE", "FOR", "SECONDARY",
       "The ~7-point CPG reversal is far larger than the 0-3% YoY decline in healthcare/education spending, which "
       "points to company-specific causes in addition to end-market softness.", R + " §2", "2026-10-12", "2026-10-12")
    ev("RPM", "INFERENCE", "AGAINST", "SECONDARY",
       "Tremco/WTI backlog shrinkage predates and is separate from the polyol shortage; institutional demand looks "
       "cyclical-leaning and is unquantified. Temporary-vs-cyclical is mixed and not resolvable on current evidence.",
       R + " §2", "2026-10-12", "2026-10-12")
    ev("RPM", "VARIANT", "NEUTRAL", "UNCERTIFIED",
       "Candidates only, NOT demonstrated: V1 roughly half or more of the CPG shortfall is transitory; V2 the de-rating "
       "to ~17x over-discounts a bounded cyclical risk. No quantified backlog, order data or primary leading-indicator reads.",
       R + " §5", "2026-10-12", "2026-10-12")
    ev("RPM", "CAPITAL_IMPLICATION", "NEUTRAL", "UNCERTIFIED",
       "If V1/V2 hold, base IRR ~10% vs 5.22% 10-yr / 4.23% bill; if the downside holds, ~-3%. Price $97.64 "
       "(2026-10-12) uncertified; advantage vs SPY not demonstrated. After Addendum 001: RPM has materially de-rated, "
       "but the evidence does not establish that the valuation fully compensates for a cyclical downturn.",
       R + " §4, §5, Addendum 001", "2026-10-12", "2026-10-12")
    ledger.set_strongest(path, candidate_id="RPM", direction="FOR", target_seq=r_for["seq"], effective_date="2026-10-12", **kw)
    ledger.set_strongest(path, candidate_id="RPM", direction="AGAINST", target_seq=r_against["seq"], effective_date="2026-10-12", **kw)
    for q in ("Is the CPG shortfall mostly transitory (supply + timing) or backlog-driven and cyclical? Mixed; "
              "no quantified backlog or order data exists.",
              "Does RPM offer a meaningful expected advantage vs SPY? (not demonstrated)"):
        ledger.add_unresolved(path, candidate_id="RPM", question=q, effective_date="2026-10-12", **kw)
    return len(ledger.read_events(path)) - n0
