"""Record the MCD R1/R2 research result in the EXISTING candidate ledger (append-only): evidence, open questions, a linked observation, and a
DRAFT_BY_RECORDER assessment. No state change, no stance, no allocation: MCD stays PARKED. Run once; it refuses to run twice for the same artifact.

    .venv/bin/python atlas_ui/evidence/mcd_r1_r2/record_to_ledger.py
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from operating_mvp import ledger as L  # noqa: E402

HERE = Path(__file__).resolve().parent
ART = HERE / "MCD_R1_R2_result.json"
REL = "atlas_ui/evidence/mcd_r1_r2/MCD_R1_R2_result.json"
TODAY = "2026-10-29"
pc = lambda x, d=1: f"{100 * x:+.{d}f}%"


def main():
    sha = hashlib.sha256(ART.read_bytes()).hexdigest()
    r = json.loads(ART.read_text())
    cid = "MCD"
    c = L.replay()[cid]
    if any(sha[:16] in (e.get("source_ref") or "") for e in c["evidence"]):
        raise SystemExit("this artifact is already recorded for MCD; nothing written")
    assert c["state"] == "PARKED", "MCD must be PARKED; this run changes no state"
    ref = f"{REL} (sha256 {sha[:16]}…)"
    w, t, h, rv, sc, pcx = r["benchmarks"]["windows"], r["treasury_evaluation"], r["history"], r["reverse_valuation"], r["scenarios"]["named"], r["price_context"]
    y = t["latest_yields_pct"]
    ev = lambda tag, direction, grade, text, src: L.add_evidence(candidate_id=cid, tag=tag, direction=direction, grade=grade, text=text, source_ref=src, known_at=TODAY, effective_date=TODAY)

    ev("FACT", "NEUTRAL", "PRIMARY",
       f"U.S. Treasury par yield curve on 2026-10-28 (keyless official CSV): 3-month {y['3 Mo']['yield']}%, 2-year {y['2 Yr']['yield']}%, 5-year {y['5 Yr']['yield']}%, 10-year {y['10 Yr']['yield']}%. "
       f"The same files reproduce, exactly, the 3-month/2-year/10-year values hand-attested on 2026-10-06 (4.21/4.79/5.27) and 2026-10-08 (4.23/4.75/5.22).",
       f"home.treasury.gov Daily Treasury Par Yield Curve Rates; {ref}")
    ev("FACT", "NEUTRAL", "SECONDARY",
       f"MCD closes (provider, independent XNYS calendar): ${pcx['close_at_cutoff']:.2f} on 2026-10-28 (equals the Gate B bind) and ${pcx['close_2026-10-07']:.2f} on 2026-10-07 (the underwriting record used an uncertified $232.24). "
       f"Price change since 2026-10-07 = {pc(pcx['price_change_since_2026-10-07'])} (the earlier observation said +7.9% against the uncertified close). 52-week high close ${pcx['52w_high_close']['close']:.2f} ({pcx['52w_high_close']['date']}); "
       f"the price is {pc(pcx['below_52w_high'])} from it; worst peak-to-trough in the last year {pc(pcx['max_drawdown_last_year'])}.", ref)
    rows = []
    for k in ("1 year", "3 years", "5 years", "10 years"):
        v = w[k]
        rows.append(f"{k}: MCD {pc(v['mcd_total_return'])} vs SPY {pc(v['spy_total_return'])} vs cash {pc(v['cash_3mo_par_proxy'])}")
    full = next(v for k, v in w.items() if k.startswith("full"))
    ev("FACT", "NEUTRAL", "SECONDARY",
       "Matched total returns to 2026-10-28 (dividend-adjusted series, same dates; cash = 3-month par yield compounded): " + "; ".join(rows) +
       f"; since {full['start_used']}: MCD {pc(full['mcd_total_return'], 0)} ({pc(full['annualized']['mcd'])}/yr) vs SPY {pc(full['spy_total_return'], 0)} ({pc(full['annualized']['spy'])}/yr). "
       "MCD lagged SPY in every window of 1-10 years and led over the full history: relative performance is regime-dependent. Dividends were NOT added to the adjusted series (that would double count; the diagnostic quantifies the error).",
       ref)
    ev("FACT", "NEUTRAL", "PRIMARY",
       "SEC annual diluted EPS (10-K, XBRL) FY2014-FY2025: " + ", ".join(f"{yr} {v['eps']}" for yr, v in h["year_end_trailing_pe"].items() if yr.isdigit()) + ". Year-end trailing P/E (unadjusted close / that EPS): " +
       ", ".join(f"{yr[2:]}: {v['trailing_pe']:.1f}x" for yr, v in h["year_end_trailing_pe"].items()) +
       f"; observed range {h['pe_summary']['min']:.1f}x-{h['pe_summary']['max']:.1f}x, median {h['pe_summary']['median']:.1f}x; today {rv['inputs']['label_ASSUMPTION']['exit_pe_set']['current (P0 / FY2025 EPS)']:.1f}x. "
       "The 2021-2025 values reproduce those in the underwriting record (26.7, 31.6, 25.6, 25.5, 25.6).", ref)
    imp = rv["implied_cagr"]
    cur = lambda k: next(v for kk, v in imp.items() if kk.startswith(k))["implied_eps_cagr_by_exit_pe"]["current (P0 / FY2025 EPS)"]
    ev("INFERENCE", "NEUTRAL", "SECONDARY",
       f"REVERSE VALUATION at ${pcx['close_at_cutoff']:.2f} with the exit multiple UNCHANGED at {rv['inputs']['label_ASSUMPTION']['exit_pe_set']['current (P0 / FY2025 EPS)']:.1f}x and exit on 2030-12-31 (dividends $7.44/yr scaled with EPS): constant EPS growth needed from FY2025 "
       f"to match cash {pc(cur('cash'))}/yr, the 5-year Treasury {pc(cur('5-year'))}, the 10-year Treasury {pc(cur('10-year'))}, SPY's full-history return ({pc(r['benchmarks']['windows'][next(k for k in w if k.startswith('full'))]['annualized']['spy'])}) {pc(cur('SPY annualized'))}, SPY's trailing 10-year return "
       f"({pc(w['10 years']['annualized']['spy'])}) {pc(cur('SPY trailing'))}. For comparison: latest 2-year EPS CAGR {pc(r['scenarios']['eps_cagr_reference_points']['latest_2y_FY2023_FY2025'])}; median 5-year window {pc(r['scenarios']['eps_cagr_reference_points']['five_year_windows']['median'])}. "
       "Arithmetic on stated inputs; not a forecast.", ref)
    names = list(sc)
    bear, base, bull, rec = (sc[n] for n in names[:4])
    ev("INFERENCE", "NEUTRAL", "SECONDARY",
       f"REFERENCE CASES (inputs are observed reference points, NOT forecasts or probabilities; BASE is the middle case, not the likeliest): BEAR (recent 2-year EPS growth persists {pc(bear['eps_cagr'])}, exit {bear['exit_pe']:.1f}x) IRR {pc(bear['irr'])}; "
       f"BASE (median 5-year EPS growth {pc(base['eps_cagr'])}, multiple unchanged {base['exit_pe']:.1f}x) IRR {pc(base['irr'])}; BULL (same growth, multiple back to the 12-year median {bull['exit_pe']:.1f}x) IRR {pc(bull['irr'])}. "
       f"Same assumptions as the 2026-10-07 underwriting base (5% EPS growth, 19x): IRR {pc(rec['irr_at_2026-10-07_close_230.88'])} at the 2026-10-07 close vs {pc(rec['irr_at_2026-10-28_price_250.50'])} at the 2026-10-28 price: the +8.5% move alone cost "
       f"{100 * (rec['irr_at_2026-10-07_close_230.88'] - rec['irr_at_2026-10-28_price_250.50']):.1f} points of prospective return.", ref)
    ev("FACT", "NEUTRAL", "SECONDARY",
       "Adjustment convention verified: the provider's adjust=all series is DIVIDEND-ADJUSTED (adjust=none = raw closes); its price return equals raw-close return plus reinvested dividends to within 0.3 percentage points even over 10 years (MCD 184%, SPY 325%). "
       "Dividends inferred from the series tie to the SEC's declared per-share dividends within 0.9% for every fiscal year 2008-2025 (2.5% in FY2007, the first year). Adding dividends to the adjusted series would have overstated MCD's 5-year return by about 15 points.", ref)

    gaps = r["gaps"]
    for g in (gaps[0], gaps[1], gaps[2], gaps[3]):
        L.add_unresolved(candidate_id=cid, question=g, effective_date=TODAY)
    L.add_unresolved(candidate_id=cid, effective_date=TODAY, question="Treasury integration: the keyless official source reproduces every hand-attested value, but using it inside Stock Atlas needs the human's approval (a new data source) and, for any funded Stage 8, the Treasury reference stays human re-attested unless a frozen-control change record is authorized.")

    oldobs = c["observations"][-1]
    L.record_observation(candidate_id=cid, observed_on="2026-10-28", effective_date=TODAY,
                         linked_to=f"{oldobs['linked_to']} and observation #{oldobs['seq']}",
                         what_changed="Matched benchmark evidence now exists for the earlier price-only observation, and its reference price is corrected from an uncertified $232.24 to the provider's $230.88 close on 2026-10-07. The thesis evidence is unchanged (Q3 2026 results are due 2026-11-04); nothing is unparked.",
                         price=pcx["close_at_cutoff"], price_session="2026-10-28", price_source_ref=f"Gate B bind and provider close; {ref}", price_grade="SECONDARY",
                         original_price=pcx["close_2026-10-07"], original_price_ref=f"provider close 2026-10-07; {ref}", original_price_grade="SECONDARY",
                         benchmark_note=(f"Matched window 2026-10-07 to 2026-10-28 (3 weeks; far too short to say anything about skill): MCD total return {pc(w['since 2026-10-07 (underwriting reference date)']['mcd_total_return'])}, "
                                         f"SPY {pc(w['since 2026-10-07 (underwriting reference date)']['spy_total_return'])}, cash (3-month par) {pc(w['since 2026-10-07 (underwriting reference date)']['cash_3mo_par_proxy'])}. "
                                         "Longer windows are in the linked evidence; adjusted total-return series, Treasury primary."))

    asm = dict(candidate_id=cid, disposition="PARKED_FOR_REVISIT", effective_date=TODAY, status="DRAFT_BY_RECORDER",
               authored_by=f"Claude (recorder) from SEC XBRL facts, provider closes and U.S. Treasury par yields; R1/R2 run {ref}; not human-accepted",
               priced_in_view=(f"At the certified ${pcx['close_at_cutoff']:.2f} (2026-10-28) MCD trades at {rv['inputs']['label_ASSUMPTION']['exit_pe_set']['current (P0 / FY2025 EPS)']:.1f}x FY2025 diluted EPS, near the low end of its 12-year year-end range "
                               f"({h['pe_summary']['min']:.1f}x-{h['pe_summary']['max']:.1f}x, median {h['pe_summary']['median']:.1f}x) and {pc(-pcx['below_52w_high'] * -1)} from its 52-week high close. With the multiple unchanged, the price needs about "
                               f"{pc(cur('cash'))} to {pc(cur('10-year'))} a year of EPS growth to match cash and Treasuries, about {pc(cur('SPY annualized'))} to match SPY's full-history return and about {pc(cur('SPY trailing'))} to match SPY's trailing 10 years. "
                               f"The last two years of EPS growth were {pc(r['scenarios']['eps_cagr_reference_points']['latest_2y_FY2023_FY2025'])}; the long-run median 5-year window is {pc(r['scenarios']['eps_cagr_reference_points']['five_year_windows']['median'])}. What drives the difference (U.S. traffic, partnering costs) is NOT yet evidenced."),
               return_band=f"{pc(bear['irr'])} to {pc(bull['irr'])} a year to 2030-12-31 across three reference cases (bear {pc(bear['irr'])}, base {pc(base['irr'])}, bull {pc(bull['irr'])}); cash {y['3 Mo']['yield']}%, 10-year Treasury {y['10 Yr']['yield']}%, SPY {pc(w['10 years']['annualized']['spy'])}/yr over 10 years and {pc(full['annualized']['spy'])}/yr over its full history",
               return_band_basis=f"Arithmetic on observed reference points, not forecasts and not probabilities: the width of the band IS the finding (growth regime persists vs normalizes). Inputs, formulas and gaps: {ref}; Addendum 003 of CYCLE1_MCD_UNDERWRITING_001.",
               drivers=["Whether EPS growth stays near its recent ~1.7% or returns toward its ~9% long-run median (U.S. traffic and comps; NEXT partnering costs and franchisee payback)",
                        "The multiple: today's ~21x versus its 12-year range, with the 10-year Treasury at 5.05%",
                        "Capital returns versus rising capex (FCF conversion)"],
               risks=["U.S. traffic erosion persists while partnering cash costs precede benefits (the bear case is below cash)", "The recent-regime growth rate is the evidence; the long-run rate may not return",
                      "Multiple compression if rates stay high", "Entry price: the +8.5% move since 2026-10-07 lowered the prospective return of every case"],
               falsifiers=["Q3 U.S. comp below -2.0% or a material FY2026 outlook cut (pre-registered in the underwriting record)", "A partnering schedule implying flat 2027-28 operating income",
                           "FY2026 reported EPS growth at or below the recent ~1.7% regime with no demonstrated acceleration"],
               what_would_change=["Q3 2026 results on 2026-11-04 (official IR calendar): U.S. comp, guest counts, FY2026 outlook, any 2027-28 earnings framework", "A published partnering schedule", "The human's own stance and assumptions (none recorded)"],
               evidence_gaps=[g.split(";")[0] for g in gaps[:4]] + ["No MCD-versus-SPY edge is demonstrated: MCD lagged SPY over 1, 3, 5 and 10 years; whether it can lead is the open question"],
               existing_holdings_note="")
    L.record_assessment(**asm)
    print("recorded: 7 evidence, 5 unresolved, 1 observation, assessment v%d (DRAFT_BY_RECORDER); MCD state %s; artifact sha256 %s" % (len(L.replay()[cid]["assessments"]), L.replay()[cid]["state"], sha))


if __name__ == "__main__":
    main()
