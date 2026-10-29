"""The MCD R1/R2 research result (committed artifact + ledger records) stays reproducible, honest and consistent.

Works offline from committed files only: the derived artifact, the retained U.S. Treasury CSVs, the candidate ledger and the register. The raw provider
series is deliberately NOT committed (storage terms), so these tests re-derive what can be re-derived and pin what cannot.
"""
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import pytest

from atlas_ui import authority, valuation as V
from operating_mvp import ledger as L

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "atlas_ui/evidence/mcd_r1_r2"
ART = EV / "MCD_R1_R2_result.json"
R = json.loads(ART.read_text())
CUT = date.fromisoformat(R["cutoff_session"])


def treasury_rows():
    out = {}
    for f in sorted(EV.glob("treasury_par_yield_curve_*.csv")):
        for r in csv.DictReader(f.read_text().splitlines()):
            m, d, y = r["Date"].split("/")
            out[date(int(y), int(m), int(d))] = {k: float(v) for k, v in r.items() if k != "Date" and v}
    return out


def test_the_retained_treasury_files_are_exactly_the_ones_the_result_was_computed_from():
    got = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(EV.glob("treasury_par_yield_curve_*.csv"))}
    assert got == R["inputs"]["treasury_csv_sha256"] and len(got) == 21


def test_treasury_values_in_the_result_match_the_committed_official_files_and_the_earlier_human_attestations():
    t, rows = R["treasury_evaluation"], treasury_rows()
    assert t["rows"] == len(rows) and t["first_date"] == min(rows).isoformat() and t["last_date"] == max(rows).isoformat() == CUT.isoformat()
    for c, v in t["latest_yields_pct"].items():
        assert rows[CUT][c] == v["yield"]
    # the two attestations written by hand in earlier records (CYCLE1 §3 on 2026-10-06; CYCLE2 on 2026-10-08)
    assert (rows[date(2026, 10, 6)]["3 Mo"], rows[date(2026, 10, 6)]["2 Yr"], rows[date(2026, 10, 6)]["10 Yr"]) == (4.21, 4.79, 5.27)
    assert (rows[date(2026, 10, 8)]["3 Mo"], rows[date(2026, 10, 8)]["2 Yr"], rows[date(2026, 10, 8)]["10 Yr"]) == (4.23, 4.75, 5.22)
    assert all(v["all_match"] for v in t["reproduces_values_previously_recorded_by_the_human_attestation"].values())
    assert t["non_numeric_cells"] == [] and t["days_between_last_observation_and_cutoff"] == 0


def test_cash_returns_in_the_result_are_reproduced_from_the_committed_treasury_files():
    ys = [(d, r["3 Mo"]) for d, r in treasury_rows().items() if "3 Mo" in r]                        # blank cells are skipped, as in the run
    for label, w in R["benchmarks"]["windows"].items():
        if "status" in w:
            continue
        got = V.cash_accrual(ys, date.fromisoformat(w["start_used"]), CUT)
        assert got["total_return"] == pytest.approx(w["cash_3mo_par_proxy"], abs=1e-9), label


def test_reverse_valuation_and_cases_are_arithmetically_consistent_with_their_stated_inputs():
    rv = R["reverse_valuation"]
    f, m = rv["inputs"]["label_FACT"], rv["inputs"]["label_MARKET_DATA"]
    base = dict(price0=f["price_p0_2026-10-28"], as_of=CUT, eps_base=f["eps_fy2025_diluted_sec"], base_fy=2025, exit_date=date(2030, 12, 31),
                dps_run_rate=m["dps_run_rate_used_from_underwriting_record_primary"])
    pe = rv["inputs"]["label_ASSUMPTION"]["exit_pe_set"]
    n = 0
    for hurdle in rv["implied_cagr"].values():
        for name, g in hurdle["implied_eps_cagr_by_exit_pe"].items():
            if g is not None:
                assert V.scenario_irr(cagr=g, exit_pe=pe[name], **base) == pytest.approx(hurdle["hurdle"], abs=1e-6)
                n += 1
    assert n >= 15
    named = R["scenarios"]["named"]
    cases = [v for v in named.values() if "irr" in v]
    assert len(cases) == 3
    for v in cases:
        assert V.scenario_irr(cagr=v["eps_cagr"], exit_pe=v["exit_pe"], **base) == pytest.approx(v["irr"], abs=1e-9)
    bear, mid, bull = cases
    assert bear["irr"] < mid["irr"] < bull["irr"] and bear["exit_pe"] < mid["exit_pe"] < bull["exit_pe"]
    for gk, row in R["scenarios"]["grid_irr"].items():
        for pk, irr in row.items():
            assert V.scenario_irr(cagr=int(gk[:-1]) / 100, exit_pe=float(pk[:-1]), **base) == pytest.approx(irr, abs=1e-9)
    ref = next(v for k, v in named.items() if k.startswith("REFERENCE"))
    assert ref["irr_at_2026-10-07_close_230.88"] > ref["irr_at_2026-10-28_price_250.50"]            # a higher entry price lowers the return, all else equal


def test_the_history_inputs_to_the_cases_come_from_the_committed_evidence_and_are_observed_not_chosen():
    h = R["history"]
    eps = {int(y): v["eps"] for y, v in R["facts"]["eps_by_fiscal_year"].items()}
    assert V.rolling_cagrs(eps, 5) == {int(k): pytest.approx(v) for k, v in h["eps_cagr_5y_by_end_year"].items()}
    pts = R["scenarios"]["eps_cagr_reference_points"]
    assert pts["latest_2y_FY2023_FY2025"] == pytest.approx((eps[2025] / eps[2023]) ** 0.5 - 1) and pts["five_year_windows"]["median"] == pytest.approx(V.quantile_summary(list(h["eps_cagr_5y_by_end_year"].values()))["median"])
    named = [v for v in R["scenarios"]["named"].values() if "irr" in v]
    pes = h["pe_summary"]
    assert named[0]["eps_cagr"] == pytest.approx(pts["latest_2y_FY2023_FY2025"]) and named[0]["exit_pe"] == pytest.approx(pes["min"])
    assert named[1]["eps_cagr"] == pytest.approx(pts["five_year_windows"]["median"]) and named[2]["exit_pe"] == pytest.approx(pes["median"])
    assert all(v["eps"] > 0 for v in R["facts"]["eps_by_fiscal_year"].values())
    for fy, v in R["facts"]["eps_by_fiscal_year"].items():
        assert v["accession"] and v["filed"], fy                                                      # every EPS fact carries its filing


def test_the_result_is_derived_only_labelled_and_makes_no_recommendation_or_probability():
    text = ART.read_text()
    assert len(text) < 80_000 and "apikey" not in text.lower() and "TWELVEDATA" not in text and not re.search(r"\b[0-9a-f]{32}\b(?!.*sha)", text.replace(R["inputs"]["sec_company_facts_sha256"], ""))
    assert '"values"' not in text and "open" not in json.dumps(R["market_data"]).lower().replace("unfinished", "")                      # no raw daily bars are stored
    assert "NOT forecasts" in R["scenarios"]["construction"] and "NOT the most likely" in R["scenarios"]["construction"].replace("NOT the most likely outcome", "NOT the most likely")
    low = text.lower()
    for banned in ("recommend", "should buy", "should sell", "price target", "undervalued", "overvalued", "probability weight", "expected return of"):
        assert banned not in low, banned
    assert len(R["gaps"]) >= 6 and any("/dividends endpoint" in g or "paid plan" in g for g in R["gaps"]) and any("SPY" in g for g in R["gaps"])


def test_the_adjustment_convention_finding_is_pinned_so_dividends_are_never_added_twice():
    conv = R["adjustment_convention"]
    assert all(d["verdict"] == "DIVIDEND_ADJUSTED" for d in conv["diagnostics"].values())
    for k, d in conv["diagnostics"].items():
        assert abs(d["candidate_price_return"] - d["unadjusted_total_return_with_reinvested_dividends"]) < 0.003, k
        assert d["double_counting_error_if_dividends_were_added_to_the_candidate"] > 0.01, k
    assert "never add dividends" in conv["finding"].lower() and "NOT available on the free plan" in conv["dividends_endpoint"]
    yrs = R["dividend_cross_check"]["years"]
    assert len(yrs) >= 15 and all(abs(v["difference"]) / v["sec_declared"] < 0.01 for y, v in yrs.items() if int(y) >= 2008)     # inferred vs SEC-declared: within 1% every year from FY2008
    assert abs(yrs["2007"]["difference"]) / yrs["2007"]["sec_declared"] < 0.03                                                    # FY2007 (first year) is looser: 2.5%


def test_the_ledger_records_point_at_this_artifact_and_this_run_changed_no_state_or_stance():
    sha = hashlib.sha256(ART.read_bytes()).hexdigest()
    c = L.replay(ROOT / "operating_mvp/data/candidate_ledger.jsonl")["MCD"]
    mine = [e for e in c["evidence"] if sha[:16] in e["source_ref"]]
    assert len(mine) == 7 and {e["tag"] for e in mine} == {"FACT", "INFERENCE"} and all(e["direction"] == "NEUTRAL" for e in mine)
    a = c["assessments"][-1]
    assert a["version"] >= 2 and a["status"] == "DRAFT_BY_RECORDER" and a["disposition"] == "PARKED_FOR_REVISIT" and "not human-accepted" in a["authored_by"] and sha[:16] in a["authored_by"]
    named = [v for v in R["scenarios"]["named"].values() if "irr" in v]
    for v in named:
        assert f"{100 * v['irr']:+.1f}%" in a["return_band"]                                           # the band shown in the UI is the artifact's numbers
    assert "no probability" in a["return_band_basis"].lower() or "not probabilities" in a["return_band_basis"].lower()
    obs = c["observations"][-1]
    assert obs["original_price"] == pytest.approx(R["price_context"]["close_2026-10-07"]) and obs["price"] == pytest.approx(250.5) and "far too short" in obs["benchmark"]
    states = [e for e in L.read_events(ROOT / "operating_mvp/data/candidate_ledger.jsonl") if e["candidate_id"] == "MCD" and e["event_type"] == "STATE_CHANGE"]
    first_research_seq = min(e["seq"] for e in mine)
    assert states[-1]["seq"] < first_research_seq and c["state"] == "PARKED"                           # the latest state change predates the research: nothing was moved
    assert not [e for e in L.read_events(ROOT / "operating_mvp/data/candidate_ledger.jsonl") if e["event_type"] == "STANCE" and e["seq"] >= first_research_seq]   # no stance was written by this run


def test_the_register_still_parks_mcd_and_rpm_and_there_is_no_decision():
    res = authority.resolve(ROOT / authority.REGISTER)
    cands = authority.resolve_candidates(res, ROOT / "operating_mvp/data/candidate_ledger.jsonl", date(2026, 10, 29))
    assert (cands["MCD"]["state"], cands["MCD"]["parked_until"], cands["MCD"]["pending"]) == ("PARKED", "2026-11-04", [])
    assert (cands["RPM"]["state"], cands["RPM"]["parked_until"]) == ("PARKED", "2026-11-09")
    assert all(cands[t]["state"] == "SURFACED" for t in ("GEV", "RMD", "ORCL"))
    assert (ROOT / "atlas_ui/data/live/decisions.jsonl").read_text() == ""
