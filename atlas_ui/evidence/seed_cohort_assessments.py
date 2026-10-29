"""Record the DRAFT research assessments and the one linked observation for the research cohort (MCD parked; GEV/RMD/ORCL insufficient).

Run once against the canonical discovery ledger after `python -m atlas_ui research <ticker>` has retained snapshots. Numbers in the texts
are computed from the retained SEC/Gate B snapshot, not typed. Authored by the recorder (Claude); status DRAFT_BY_RECORDER until a human accepts.
No promotion, no capital verdict, no score. MCD's park is not lifted.
"""
import sys
from datetime import date
from pathlib import Path

from atlas_ui import research
from operating_mvp import ledger

ROOT = Path(__file__).resolve().parents[2]
LP = ledger.DEFAULT_LEDGER
RD = ROOT / "atlas_ui" / "data" / "live" / "research"
BY = "Claude (recorder) from retained SEC facts + Gate B price; not human-accepted"


def facts(t):
    s = research.latest_snapshot(RD, t)["data"]
    le = max(s["periods"])
    m = s["derived_inference"][le]
    pr = s["price_relative_inference"]
    return s, le, m, pr, (lambda f: (s["periods"][le].get(f) or {}).get("value"))


def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def priced_in(t):
    s, le, m, pr, g = facts(t)
    i = pr["inputs"]
    return (f"At the Gate B bound ${i['price']:g} (XNYS session {i['price_session']}) the shares trade at {pr['pe_on_latest_fy_diluted_eps']:.1f}x FY{le[:4]} diluted EPS "
            f"(earnings yield {pct(pr['earnings_yield'])}). What growth or margin expectations that multiple embeds is NOT established here (no consensus or guidance evidence retained).")


if __name__ == "__main__":
    if any(c["assessments"] for c in ledger.replay(LP).values()):
        sys.exit("assessments already recorded; refusing to re-seed")
    # ---- MCD: parked example
    s, le, m, pr, g = facts("MCD")
    ledger.record_assessment(
        LP, candidate_id="MCD", disposition="PARKED_FOR_REVISIT", authored_by=BY,
        priced_in_view=priced_in("MCD") + f" FCF yield {pct(pr.get('fcf_yield_on_weighted_diluted_shares'))} on weighted diluted shares (scale verified). The 2026-10-07 valuation cases in CYCLE1_MCD_UNDERWRITING_001 were built at an uncertified $232.24 and are NOT re-run at today's price.",
        return_band="", return_band_basis="",
        drivers=["U.S. comparable sales / traffic vs the 'slightly negative' Q3 guidance", "NEXT partnering cost and franchisee payback (no annual schedule published)", "Capital returns vs rising capex (FCF conversion)"],
        risks=["U.S. traffic erosion persists while partnering cash costs precede benefits", f"Leverage: FY{le[:4]} net debt not computed from SEC facts (a debt leg is conflicted/unavailable)", "Multiple can compress further if rates stay high"],
        falsifiers=["Q3 U.S. comp below -2.0% or a material FY2026 outlook cut (pre-registered in the underwriting record)", "A partnering schedule implying flat 2027-28 operating income"],
        what_would_change=["Q3 2026 results on 2026-11-04 (official IR calendar): U.S. comp, guest counts, September/Q4 trend, FY2026 outlook", "Any published partnering schedule / 2027-28 earnings framework"],
        evidence_gaps=["Dividends-paid and short-term-debt facts UNVERIFIED/CONFLICTED in SEC company facts (not imputed)", "No variant demonstrated; advantage vs SPY not demonstrated (per the underwriting record)"],
        existing_holdings_note="MCD is not among the 28 baseline holdings.")
    ledger.record_observation(
        LP, candidate_id="MCD", observed_on=date.today(), linked_to="docs/controlled_live_pilot/CYCLE1_MCD_UNDERWRITING_001.md §3 (reference price $232.24, 2026-10-07)",
        what_changed="Price-only observation at the Gate B bound close. The thesis evidence is unchanged (Q3 results pending 2026-11-04); the earlier cases were not re-run and nothing is unparked.",
        price=pr["inputs"]["price"], price_session=pr["inputs"]["price_session"], price_source_ref="docs/controlled_live_pilot/evidence/LIVE_CHECK_001_MCD.json (Gate B, independent XNYS calendar)",
        price_grade="SECONDARY", original_price=232.24, original_price_ref="CYCLE1_MCD_UNDERWRITING_001 §3 (Yahoo close 2026-10-07)", original_price_grade="UNCERTIFIED")
    # ---- cohort names that are only SURFACED: honest insufficient-evidence assessments
    gaps_common = ["No pre-Atlas stance frozen yet (human to supply before QUICK_TEST)", "QUICK_TEST (cheapest falsification) not run",
                   "No variant view, guidance, segment or competitor evidence retained; no scenario basis for any return band"]
    notes = {
        "GEV": ("Operating margin is thin relative to the multiple and the FY2025 EPS growth is a base-effect-sensitive figure; capex was not selected from SEC facts (UNVERIFIED), so free cash flow cannot be established.",
                ["Margin sensitivity: FY operating margin in the low single digits", "Cash conversion cannot be assessed (capex UNVERIFIED)"]),
        "RMD": ("Source-backed economics look strong on the facts retained (margins, growth, buyback-driven share shrink) but nothing here establishes what is priced in or a variant.",
                ["Net income CONFLICTED between approved concepts, so cash conversion and the FCF yield are not shown"]),
        "ORCL": ("Free cash flow is negative in the latest fiscal year on SEC facts (capex-heavy) and diluted shares rose; funding and leverage are not established (debt legs UNVERIFIED).",
                 ["Negative free cash flow in the latest fiscal year", "Dilution (diluted share count up) and unverified debt legs"]),
    }
    for t in ("GEV", "RMD", "ORCL"):
        s, le, m, pr, g = facts(t)
        eco = (f"FY{le[:4]} revenue {pct(m.get('revenue_growth'))} growth, operating margin {pct(m.get('operating_margin'))}"
               + (f", free cash flow ${m['free_cash_flow'] / 1e9:,.2f}B" if "free_cash_flow" in m else ", free cash flow not established")
               + (f", diluted shares {m['diluted_share_change'] * 100:+.1f}%" if "diluted_share_change" in m else ""))
        ledger.record_assessment(
            LP, candidate_id=t, disposition="INSUFFICIENT_EVIDENCE", authored_by=BY,
            priced_in_view=priced_in(t) + " Retained facts: " + eco + ". " + notes[t][0],
            return_band="", return_band_basis="", drivers=[],
            risks=notes[t][1], falsifiers=["Not yet defined: needs the human's stance and a QUICK_TEST design"],
            what_would_change=["A frozen pre-Atlas stance, a passed QUICK_TEST, and primary-source narrative evidence (guidance, segments, competitors)", "Resolution of the UNVERIFIED/CONFLICTED SEC facts listed under gaps"],
            evidence_gaps=gaps_common + [x for x in s["gaps"][:3]],
            existing_holdings_note=f"{t} is not among the 28 baseline holdings; driver overlap is not assigned (human-authored at Stage 7).")
    print("recorded; chain:", ledger.verify_chain(LP) or "OK")
