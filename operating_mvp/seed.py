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
