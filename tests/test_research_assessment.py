"""Workstreams B-E: SEC research adapter, descriptive assessment, unranked cohort, linked observation, read-only live check.

Offline: synthetic SEC company facts (no network) and fixture workspaces. The committed discovery ledger is only read.
Paper only; no Stage 7, no decision.
"""
import hashlib
import json
import os
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import identity_resolver
from atlas_ui import app as appmod
from atlas_ui import research
from atlas_ui.__main__ import build, live_check
from operating_mvp import ledger

DT = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
KEY, ISS = "SEC-CIK:0000000123:XYZ", "SEC-CIK:0000000123"


def fact(val, start, end, accn, filed, form="10-K", fp="FY"):
    d = {"val": val, "end": end, "accn": accn, "fy": int(end[:4]), "fp": fp, "form": form, "filed": filed}
    if start:
        d["start"] = start
    return d


def facts_doc(extra=None, drop=(), conflict=False):
    def duration(vals, concept="Revenues", unit="USD"):
        return {concept: {"units": {unit: [fact(v, f"{y}-01-01", f"{y}-12-31", f"0000000123-{y + 1 - 2000}-00000{i}", f"{y + 1}-02-20")
                                            for i, (y, v) in enumerate(vals.items(), 1)]}}}
    us = {}
    us.update(duration({2023: 1000e6, 2024: 1100e6, 2025: 1250e6}, "Revenues"))
    us.update(duration({2023: 300e6, 2024: 330e6, 2025: 400e6}, "OperatingIncomeLoss"))
    us.update(duration({2023: 200e6, 2024: 220e6, 2025: 290e6}, "NetIncomeLoss"))
    us.update(duration({2023: 2.0, 2024: 2.2, 2025: 2.9}, "EarningsPerShareDiluted", "USD/shares"))
    us.update(duration({2023: 330e6, 2024: 360e6, 2025: 420e6}, "NetCashProvidedByUsedInOperatingActivities"))
    us.update(duration({2023: 80e6, 2024: 90e6, 2025: 100e6}, "PaymentsToAcquirePropertyPlantAndEquipment"))
    us.update(duration({2023: 100e6, 2024: 100e6, 2025: 100e6}, "WeightedAverageNumberOfDilutedSharesOutstanding", "shares"))
    for k in drop:
        us.pop(k, None)
    if conflict:  # a second approved capex concept disagreeing on FY2025 (same period)
        us["CapitalExpenditure"] = {"units": {"USD": [fact(55e6, "2025-01-01", "2025-12-31", "0000000123-26-000006", "2026-02-20")]}}
    if extra:
        us.update(extra)
    return {"cik": 123, "entityName": "XYZ Corp", "facts": {"us-gaap": us}}


@pytest.fixture
def env(tmp_path, monkeypatch):
    lp = tmp_path / "c.jsonl"
    ledger.surface(lp, name="XYZ Corp", ticker="XYZ", source="HUMAN", why_surfaced="w", investment_question="q?")
    monkeypatch.setattr(identity_resolver, "resolve_security",
                        lambda t, a=None: SimpleNamespace(resolved=True, security_key=KEY, issuer_key=ISS))
    return lp, tmp_path / "research"


def run(env, facts, when=DT, price=None):
    lp, out = env
    return research.research_candidate(lp, "XYZ", out, decision_time=when, adapter=SimpleNamespace(), facts=facts, price_evidence=price)


def price_ev(price=100.0, key=KEY):
    return {"price_binding": {"security_key": key, "price": price, "price_session_date": "2026-10-28"}}


# ---- C: source -> evidence, point in time, fail closed ------------------------------------------------------------
def test_selected_facts_become_primary_evidence_with_accession_known_at_period_units(env):
    r = run(env, facts_doc())
    ev = ledger.replay(env[0])["XYZ"]["evidence"]
    assert r["evidence_added"] == len(ev) > 20 and all(i["grade"] == "PRIMARY" and i["tag"] == "FACT" for i in ev)
    rev = next(i for i in ev if i["text"].startswith("Revenue FY ending 2025-12-31"))
    assert "$1.25B" in rev["text"] and "10-K" in rev["text"] and "ANNUAL" in rev["text"] and "us-gaap:Revenues" in rev["text"]
    assert rev["source_ref"].startswith("https://www.sec.gov/Archives/edgar/data/123/") and rev["known_at"] == "2026-02-20"
    assert "0000000123-26-" in rev["text"]


def test_no_lookahead_facts_filed_after_the_decision_date_are_excluded(env):
    early = datetime(2025, 6, 1, tzinfo=timezone.utc)  # FY2025 10-K was filed 2026-02-20
    run(env, facts_doc(), when=early)
    texts = " ".join(i["text"] for i in ledger.replay(env[0])["XYZ"]["evidence"])
    assert "FY ending 2025-12-31" not in texts and "FY ending 2024-12-31" in texts
    assert all(i["known_at"] <= "2025-06-01" for i in ledger.replay(env[0])["XYZ"]["evidence"])


def test_missing_and_conflicting_facts_are_unresolved_never_imputed(env):
    run(env, facts_doc(conflict=True))
    c = ledger.replay(env[0])["XYZ"]
    qs = " ".join(u["question"] for u in c["unresolved"])
    assert "Capital expenditures for fiscal period ending 2025-12-31 is CONFLICTED" in qs
    assert "Dividends paid" in qs and "UNVERIFIED" in qs
    texts = " ".join(i["text"] for i in c["evidence"])
    assert "Capital expenditures FY ending 2025-12-31" not in texts  # no value chosen
    snap = research.latest_snapshot(env[1], "XYZ")["data"]
    assert "free_cash_flow" not in snap["derived_inference"]["2025-12-31"]  # a derived metric needs every SEC leg


def test_a_missing_concept_is_reported_unverified_and_blocks_derived_metrics(env):
    run(env, facts_doc(drop=("PaymentsToAcquirePropertyPlantAndEquipment",)))
    c = ledger.replay(env[0])["XYZ"]
    assert any("Capital expenditures for fiscal period ending 2025-12-31 is UNVERIFIED" in u["question"] for u in c["unresolved"])
    assert "free_cash_flow" not in research.latest_snapshot(env[1], "XYZ")["data"]["derived_inference"]["2025-12-31"]


def test_net_debt_never_imputes_a_missing_leg_as_zero():
    p = {"2025-12-31": {"cash": {"value": 10}, "long_term_debt": {"value": 50}}}
    assert "net_debt" not in research.derive(p)["2025-12-31"]
    p["2025-12-31"]["short_term_debt"] = {"value": 5}
    assert research.derive(p)["2025-12-31"]["net_debt"] == 45


def test_rerun_is_idempotent_and_history_only_grows(env):
    run(env, facts_doc())
    before = ledger.DEFAULT_LEDGER and env[0].read_bytes()
    r2 = run(env, facts_doc(), when=datetime(2026, 10, 29, tzinfo=timezone.utc))
    assert r2["evidence_added"] == 0 and r2["gaps_recorded"] == 0 and env[0].read_bytes() == before
    assert len(research.latest_snapshot(env[1], "XYZ")["data"]["periods"]) == 3
    ledger.verify_chain(env[0])


def test_derived_values_are_labelled_arithmetic_on_selected_facts(env):
    run(env, facts_doc())
    m = research.latest_snapshot(env[1], "XYZ")["data"]["derived_inference"]["2025-12-31"]
    assert m["operating_margin"] == pytest.approx(0.32) and m["revenue_growth"] == pytest.approx(1250 / 1100 - 1)
    assert m["free_cash_flow"] == pytest.approx(320e6) and m["fcf_conversion_of_net_income"] == pytest.approx(320 / 290)


def test_identity_failures_stop_the_run_and_write_nothing(env, monkeypatch):
    lp, out = env
    before = lp.read_bytes()
    monkeypatch.setattr(identity_resolver, "resolve_security", lambda t, a=None: SimpleNamespace(resolved=False, security_key=None, issuer_key=None))
    with pytest.raises(research.ResearchError, match="did not resolve"):
        run(env, facts_doc())
    monkeypatch.setattr(identity_resolver, "resolve_security", lambda t, a=None: SimpleNamespace(resolved=True, security_key=KEY, issuer_key=ISS))
    other = facts_doc(); other["cik"] = 999
    with pytest.raises(research.ResearchError, match="does not match the resolved issuer"):
        run(env, other)
    with pytest.raises(research.ResearchError, match="no ANNUAL"):
        run(env, {"cik": 123, "facts": {"us-gaap": {}}})
    with pytest.raises(research.ResearchError, match="unavailable"):
        research.research_candidate(lp, "XYZ", out, decision_time=DT, adapter=SimpleNamespace(get_company_facts=lambda c: None))
    with pytest.raises(research.ResearchError, match="unknown candidate"):
        research.research_candidate(lp, "NOPE", out, decision_time=DT, adapter=SimpleNamespace(), facts={})
    assert lp.read_bytes() == before and not out.exists()


def test_candidate_without_a_ticker_cannot_be_researched(tmp_path):
    lp = tmp_path / "c.jsonl"
    ledger.surface(lp, name="No Ticker", source="HUMAN", why_surfaced="w", investment_question="q")
    with pytest.raises(research.ResearchError, match="no recorded ticker"):
        research.research_candidate(lp, "NO-TICKER", tmp_path / "r", decision_time=DT, adapter=SimpleNamespace(), facts={})


def test_price_evidence_for_another_security_class_is_refused(env):
    with pytest.raises(research.ResearchError, match="does not match the resolved security"):
        run(env, facts_doc(), price=price_ev(key="SEC-CIK:0000000123:XYZ.B"))


def test_price_relative_ratios_need_bound_price_and_verified_share_scale(env):
    run(env, facts_doc())
    assert "BLOCKED" in research.latest_snapshot(env[1], "XYZ")["data"]["price_relative_inference"]["status"]
    run(env, facts_doc(), when=datetime(2026, 10, 29, tzinfo=timezone.utc), price=price_ev(58.0))
    pr = research.latest_snapshot(env[1], "XYZ")["data"]["price_relative_inference"]
    assert pr["pe_on_latest_fy_diluted_eps"] == pytest.approx(20.0) and pr["fcf_yield_on_weighted_diluted_shares"] == pytest.approx((320e6 / 100e6) / 58.0)
    # share count tagged in millions is accepted ONLY because EPS x shares reproduces net income
    assert research._share_scale(2.9, 100e6, 290e6) == 1 and research._share_scale(2.9, 100.0, 290e6) == 1e6
    assert research._share_scale(12.0, 718.0, 8.6e9) == 1e6
    assert research._share_scale(2.9, 55.0, 290e6) is None  # unexplained scale -> omitted, never guessed


def test_tampered_snapshot_is_not_served(env):
    run(env, facts_doc())
    snap = research.latest_snapshot(env[1], "XYZ")
    p = Path(snap["snapshot"]["artifact_path"])
    p.write_text(p.read_text().replace("XYZ", "XYQ", 1))
    assert research.latest_snapshot(env[1], "XYZ") is None


# ---- D: descriptive assessment / unranked cohort ------------------------------------------------------------------------------
def rec(lp, cid="XYZ", **kw):
    base = dict(candidate_id=cid, disposition="INSUFFICIENT_EVIDENCE", priced_in_view="not established", authored_by="tester")
    base.update(kw)
    return ledger.record_assessment(lp, **base)


def test_assessment_validation_and_versioning(env):
    lp = env[0]
    with pytest.raises(ledger.LedgerError):
        rec(lp, disposition="BUY")
    with pytest.raises(ledger.LedgerError):
        rec(lp, disposition="PARKED_FOR_REVISIT")  # lifecycle is not PARKED
    with pytest.raises(ledger.LedgerError):
        rec(lp, return_band="5-9%")  # a band needs its basis
    with pytest.raises(ledger.LedgerError):
        rec(lp, drivers=["a", "b", "c", "d"])
    with pytest.raises(ledger.LedgerError):
        rec(lp, authored_by=" ")
    with pytest.raises(ledger.LedgerError):
        rec(lp, priced_in_view=" ")
    with pytest.raises(ledger.LedgerError):
        rec(lp, status="APPROVED")
    rec(lp); rec(lp, disposition="NOT_SUPPORTED", return_band="2-4%", return_band_basis="scenario record #12")
    c = ledger.replay(lp)["XYZ"]
    assert [a["version"] for a in c["assessments"]] == [1, 2] and c["state"] == "SURFACED"  # an assessment never moves the lifecycle


def test_default_dispositions_come_from_lifecycle_only(env):
    lp = env[0]
    c = ledger.replay(lp)["XYZ"]
    assert appmod.effective_disposition(c)[0] == "INSUFFICIENT_EVIDENCE"
    ledger.change_state(lp, candidate_id="XYZ", to_state="PARKED", reason="r", waiting_on="Q3")
    assert appmod.effective_disposition(ledger.replay(lp)["XYZ"])[0] == "PARKED_FOR_REVISIT"


def test_cohort_is_alphabetical_unranked_and_escapes_text(tmp_path):
    app = build(True, tmp_path / "d")
    ledger.surface(app.ws.candidate_ledger, name="<b>Zed</b>", ticker="ZED", source="SUE", why_surfaced="w", investment_question="q")
    rec(app.ws.candidate_ledger, "ZED", priced_in_view="<script>x()</script>", risks=["<img src=x>"])
    h = appmod.cohort_page(app)
    ids = [h.index(f'>{i}</a>') for i in ("DEMOCO", "MCD", "RPM", "ZED")]
    assert ids == sorted(ids) and "unranked" in h.lower() and "<script>" not in h and "<img src=x>" not in h
    api = appmod.api_cohort(app)
    assert all(row["rank"] is None for row in api) and [r["candidate_id"] for r in api] == sorted(r["candidate_id"] for r in api)
    assert "Capital alternatives" in h and "Do Nothing" in h and "Stage 7 only" in h


def test_cohort_never_offers_stage7_or_capital_action(tmp_path):
    h = appmod.cohort_page(build(True, tmp_path / "d"))
    assert "<form" not in h and 'action="/stage' not in h


# ---- E: linked, append-only observation -------------------------------------------------------------------------------------------
def test_observation_is_linked_dated_price_only_and_benchmark_unverified_by_default(env):
    lp = env[0]
    before = lp.read_bytes()
    ledger.record_observation(lp, candidate_id="XYZ", observed_on="2026-10-28", linked_to="record #7", what_changed="price moved",
                              price=110.0, price_session="2026-10-28", price_source_ref="gate B evidence", original_price=100.0, original_price_ref="2026-10-07 quote")
    o = ledger.replay(lp)["XYZ"]["observations"][0]
    assert o["price_change_only"] == pytest.approx(0.10) and "not a total return" in o["price_change_note"] and o["benchmark"].startswith("UNVERIFIED")
    assert lp.read_bytes().startswith(before)  # nothing earlier was touched
    for bad in (dict(linked_to=""), dict(what_changed=""), dict(price_session=""), dict(price_source_ref="")):
        kw = dict(candidate_id="XYZ", observed_on="2026-10-28", linked_to="r", what_changed="w", price=1.0, price_session="2026-10-28", price_source_ref="s")
        kw.update(bad)
        with pytest.raises(ledger.LedgerError):
            ledger.record_observation(lp, **kw)
    with pytest.raises(ledger.LedgerError):
        ledger.record_observation(lp, candidate_id="XYZ", observed_on="2026-10-28", linked_to="r", what_changed="w", price=1.0,
                                  price_session="2026-10-28", price_source_ref="s", original_price=0.9)  # original needs its ref


# ---- the committed record ---------------------------------------------------------------------------------------------------------------
def test_committed_cohort_state():
    ledger.verify_chain()
    c = ledger.replay()
    assert (c["MCD"]["state"], c["MCD"]["parked_until"], c["RPM"]["state"], c["RPM"]["parked_until"]) == ("PARKED", "2026-11-04", "PARKED", "2026-11-09")
    assert c["MCD"]["assessments"][-1]["disposition"] == "PARKED_FOR_REVISIT" and c["MCD"]["assessments"][-1]["status"] == "DRAFT_BY_RECORDER"
    for t in ("GEV", "RMD", "ORCL"):
        assert c[t]["state"] == "SURFACED" and c[t]["source"] == "HUMAN" and not c[t]["stances"] and not c[t]["falsifications"]  # not promoted, nothing invented
        assert c[t]["assessments"][-1]["disposition"] == "INSUFFICIENT_EVIDENCE" and c[t]["assessments"][-1]["return_band"] == ""
    o = c["MCD"]["observations"][0]
    assert o["price_change_only"] == pytest.approx(250.5 / 232.24 - 1) and o["price_grade"] == "SECONDARY" and o["original_price_grade"] == "UNCERTIFIED"
    for t in ("MCD", "GEV", "RMD", "ORCL"):
        sec = [i for i in c[t]["evidence"] if "[SEC " in i["text"]]
        assert len(sec) >= 20 and all(i["grade"] == "PRIMARY" and i["source_ref"].startswith("https://www.sec.gov/Archives/edgar/data/") and i["known_at"] for i in sec)


def test_committed_research_snapshots_verify_and_are_gate_b_priced():
    rd = Path(__file__).resolve().parent.parent / "atlas_ui" / "data" / "live" / "research"
    for t in ("MCD", "GEV", "RMD", "ORCL"):
        s = research.latest_snapshot(rd, t)
        assert s is not None, t
        pe = s["data"]["price_evidence"]["price_binding"]
        assert pe["provider"] == "twelvedata" and pe["freshness_status"] == "FRESH" and pe["currency"] == "USD" and "XNYS" in pe["quoted_instrument"]
        assert s["data"]["price_evidence"]["session_attestation"]["authority"] == "independent exchange calendar"
        assert "api_key" not in json.dumps(s["data"]).lower() and "apikey" not in json.dumps(s["data"]).lower()


def test_live_check_evidence_is_sanitized():
    t = (Path(__file__).resolve().parent.parent / "docs/controlled_live_pilot/evidence/LIVE_CHECK_001_MCD.json").read_text()
    d = json.loads(t)
    assert d["check"]["stage7_started"] is False and d["check"]["decision_written"] is False and d["price_binding"]["provider"] == "twelvedata"
    env_key = dict(l.strip().partition("=")[::2] for l in open(Path(__file__).resolve().parent.parent / ".env") if "=" in l).get("TWELVEDATA_API_KEY", "").strip('"\' ') \
        if (Path(__file__).resolve().parent.parent / ".env").exists() else ""
    assert not env_key or env_key not in t


# ---- B: the read-only live check CLI ---------------------------------------------------------------------------------------------------------
def test_live_check_without_a_key_is_blocked_and_exits_nonzero(monkeypatch, capsys):
    monkeypatch.delenv("TWELVEDATA_API_KEY", raising=False)
    assert live_check("MCD", None, None) == 2
    assert "BLOCKED" in capsys.readouterr().out


def test_live_check_reads_the_key_from_an_env_file_without_ever_printing_it(tmp_path, monkeypatch, capsys):
    from atlas_ui.service import Blocked, Stage7Service
    monkeypatch.delenv("TWELVEDATA_API_KEY", raising=False)
    envf = tmp_path / ".env"
    envf.write_text("OTHER=1\nTWELVEDATA_API_KEY=sk-SECRET-VALUE-123\n")
    seen = {}

    def fake(self, ticker, now):
        seen["key"] = os.environ.get("TWELVEDATA_API_KEY")
        raise Blocked("provider said no (sk-SECRET-VALUE-123)")

    monkeypatch.setattr(Stage7Service, "bind_price", fake)
    assert live_check("MCD", str(envf), None) == 2
    out = capsys.readouterr().out
    assert seen["key"] == "sk-SECRET-VALUE-123" and "sk-SECRET" not in out  # loaded for the process, redacted on output
    monkeypatch.delenv("TWELVEDATA_API_KEY", raising=False)


def test_live_check_cannot_start_stage7_or_write_a_decision():
    src = (Path(__file__).resolve().parent.parent / "atlas_ui" / "__main__.py").read_text()
    body = src[src.index("def live_check"):src.index("def main(")]
    assert "run_stage7" not in body and "record_final_decision" not in body and ".run(" not in body
