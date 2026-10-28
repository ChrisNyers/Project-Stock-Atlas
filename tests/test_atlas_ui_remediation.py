"""Adversarial regression tests for the independent review of fe268b5 (F1-F7 + artifact guard).

Every rejected funded path asserts the decision ledger is byte-identical afterwards (zero new rows).
Real facade / DecisionStore / Gate B code; FIXTURE price provider only; paper only.
"""
import copy
import hashlib
import json
import math
import shutil
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from atlas_ui import app as appmod
from atlas_ui import canonical, demo
from atlas_ui.__main__ import build
from atlas_ui.service import Blocked, Rejected, Stage7Service, _pct, read_index
from live_session_calendar import latest_completed_session
from operating_mvp import ledger
from stock_atlas.models import SecurityDecision

from test_atlas_ui import NOW, good_req, http_app, req, s8  # noqa: F401  (fixtures re-used)


@pytest.fixture
def demo_app(tmp_path):
    return build(True, tmp_path / "demo")


def ledger_bytes(app) -> bytes:
    p = Path(app.ws.facade.store.path)
    return p.read_bytes() if p.exists() else b""


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in Path(root).rglob("*") if p.is_file()):
        h.update(f.relative_to(root).as_posix().encode() + f.read_bytes())
    return h.hexdigest()


class Spy:
    """Capture what the UI hands the frozen facade, without changing behavior."""

    def __init__(self, app, monkeypatch):
        self.calls = []
        real = app.ws.facade.run_stage7

        def wrapped(*a, **k):
            self.calls.append((a, k))
            return real(*a, **k)

        monkeypatch.setattr(app.ws.facade, "run_stage7", wrapped)

    @property
    def underwriting(self):
        return self.calls[-1][0][0]

    @property
    def portfolio(self):
        return self.calls[-1][0][1]


# ===================== F1: one unambiguous percent unit ======================================
@pytest.mark.parametrize("text,expected", [("0", 0.0), ("0.5", 0.005), ("1", 0.01), ("3", 0.03), ("12", 0.12),
                                           ("-2", -0.02), ("12%", 0.12), (" 1 ", 0.01), ("100", 1.0), ("-100", -1.0)])
def test_f1_percent_boundaries_are_never_reinterpreted(text, expected):
    assert _pct(text, "x") == pytest.approx(expected)


@pytest.mark.parametrize("bad", ["nan", "NaN", "inf", "-inf", "abc", "", "  ", "101", "-100.5", "1e9", None])
def test_f1_non_finite_and_out_of_range_rejected(bad):
    with pytest.raises(Blocked):
        _pct(bad, "x")


def test_f1_half_to_one_percent_is_half_to_one_percent_not_50_to_100(demo_app, monkeypatch):
    spy = Spy(demo_app, monkeypatch)
    demo_app.svc.run(good_req(ret_low="0.5", ret_high="1", req_low="0.5", req_high="1",
                              spy_low="0.2", spy_high="0.4", tsy_low="0.1", tsy_high="0.2"), NOW)
    u = spy.underwriting
    assert (u.return_band.low, u.return_band.high) == pytest.approx((0.005, 0.01))
    assert (u.required_return_band.low, u.required_return_band.high) == pytest.approx((0.005, 0.01))
    alts = spy.calls[-1][0][3]
    assert (alts[0].return_band.low, alts[0].return_band.high) == pytest.approx((0.002, 0.004))
    assert (alts[1].return_band.low, alts[1].return_band.high) == pytest.approx((0.001, 0.002))


def test_f1_equal_bounds_of_one_is_one_percent_not_100(demo_app, monkeypatch):
    spy = Spy(demo_app, monkeypatch)
    demo_app.svc.run(good_req(ret_low="1", ret_high="1"), NOW)
    assert (spy.underwriting.return_band.low, spy.underwriting.return_band.high) == pytest.approx((0.01, 0.01))


def test_f1_mixed_bounds_and_inverted_bounds(demo_app, monkeypatch):
    spy = Spy(demo_app, monkeypatch)
    demo_app.svc.run(good_req(ret_low="0.5", ret_high="12"), NOW)
    assert (spy.underwriting.return_band.low, spy.underwriting.return_band.high) == pytest.approx((0.005, 0.12))
    with pytest.raises(Blocked, match="low exceeds high"):
        demo_app.svc.run(good_req(ret_low="12", ret_high="0.5"), NOW)


@pytest.mark.parametrize("field,val", [("ret_low", "nan"), ("ret_high", "inf"), ("tsy_ref_value", "-inf"),
                                       ("remaining_capacity", "abc"), ("spy_low", "999"), ("horizon_years", "inf")])
def test_f1_bad_numeric_inputs_stop_the_run_with_nothing_written(demo_app, field, val):
    before = tree_hash(demo_app.ws.root)
    with pytest.raises(Blocked):
        demo_app.svc.run(good_req(**{field: val}), NOW)
    assert read_index(demo_app.ws.index_path) == [] and tree_hash(demo_app.ws.root) == before


def test_f1_remaining_capacity_and_treasury_yield_share_the_percent_unit(demo_app, monkeypatch):
    spy = Spy(demo_app, monkeypatch)
    demo_app.svc.run(good_req(remaining_capacity="10", tsy_ref_value="3.9"), NOW)
    assert spy.calls[-1][0][2].remaining_capacity == pytest.approx(0.10)
    assert spy.calls[-1][0][3][1].market_reference.value == pytest.approx(0.039)


# ===================== F2: no implicit BUY ===================================================
@pytest.mark.parametrize("val", [None, "", "  ", "buy!", "STRONG BUY"])
def test_f2_missing_or_invalid_security_decision_is_refused(demo_app, val):
    r = good_req()
    if val is None:
        r.pop("decision")
    else:
        r["decision"] = val
    before = tree_hash(demo_app.ws.root)
    with pytest.raises(Blocked, match="explicitly"):
        demo_app.svc.run(r, NOW)
    assert read_index(demo_app.ws.index_path) == [] and tree_hash(demo_app.ws.root) == before


def test_f2_decision_needs_its_evidence_basis(demo_app):
    with pytest.raises(Blocked, match="evidence basis"):
        demo_app.svc.run(good_req(decision_basis=" "), NOW)


def test_f2_explicit_non_buy_decision_is_respected_not_overwritten(demo_app, monkeypatch):
    spy = Spy(demo_app, monkeypatch)
    e = demo_app.svc.run(good_req(decision="WATCH"), NOW)
    assert spy.underwriting.security_decision is SecurityDecision.WATCH
    assert e["status"] == "WATCH / NO DECISION"
    with pytest.raises(Rejected) as ei:
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert ei.value.rows_before == ei.value.rows_after == 0


def test_f2_form_has_no_preselected_buy_and_a_blank_first_option(demo_app):
    html = appmod.stage7_page(demo_app)
    sel = html[html.index('name="decision"'):]
    sel = sel[:sel.index("</select>")]
    assert sel.index("<option></option>") < sel.index("<option>BUY</option>") and "selected" not in sel


# ===================== F3: candidate / ticker identity binding ==================================
def test_f3_cross_ticker_forgery_on_a_ready_candidate_is_refused(demo_app):
    with pytest.raises(Blocked, match="ticker mismatch"):
        demo_app.svc.run(good_req(candidate_id="DEMOCO", ticker="MCD"), NOW)
    assert read_index(demo_app.ws.index_path) == []


def test_f3_cannot_borrow_a_ready_ticker_to_run_a_parked_candidate(demo_app):
    for cid in ("MCD", "RPM"):
        with pytest.raises(Blocked, match="mismatch|PARKED"):
            demo_app.svc.run(good_req(candidate_id=cid, ticker="DEMOCO"), NOW)
        with pytest.raises(Blocked, match="PARKED until"):
            demo_app.svc.run(good_req(candidate_id=cid, ticker=cid), NOW)
    assert read_index(demo_app.ws.index_path) == []


def test_f3_ticker_comes_from_the_server_side_record_not_the_client(demo_app, monkeypatch):
    spy = Spy(demo_app, monkeypatch)
    r = good_req()
    r.pop("ticker")  # the client names no ticker: the recorded one is used
    e = demo_app.svc.run(r, NOW)
    assert e["ticker"] == "DEMOCO" and spy.underwriting.ticker == "DEMOCO"


def test_f3_ready_candidate_without_recorded_ticker_cannot_run(demo_app):
    p = demo_app.ws.candidate_ledger
    ledger.surface(p, name="No Ticker Co", source="HUMAN", why_surfaced="w", investment_question="q")
    cid = "NO-TICKER-CO"
    ledger.change_state(p, candidate_id=cid, to_state="QUICK_TEST", reason="r")
    ledger.record_falsification(p, candidate_id=cid, test="t", result="SURVIVED", grade="PRIMARY")
    ledger.change_state(p, candidate_id=cid, to_state="UNDERWRITING", reason="r")
    ledger.change_state(p, candidate_id=cid, to_state="READY_FOR_CAPITAL_COMPARISON", reason="r")
    with pytest.raises(Blocked, match="no recorded ticker"):
        demo_app.svc.run(good_req(candidate_id=cid, ticker="DEMOCO"), NOW)


def test_f3_bound_price_ticker_must_match(demo_app):
    class Odd(demo.FixtureProvider):
        def latest_price(self, symbol):
            r = super().latest_price(symbol).to_dict()
            return type(super().latest_price(symbol))(r)

    svc = Stage7Service(demo_app.ws, provider_factory=Odd, identity_fn=lambda t: "OTHER-KEY", allowed_providers={demo.DEMO_PROVIDER},
                        key_present=lambda: True)
    with pytest.raises(Blocked):  # identity from the resolver does not match what the provider quotes
        svc.run(good_req(), NOW)


def test_f3_http_forged_pairing_returns_400_and_writes_nothing(http_app):
    app, port = http_app
    form = {k: v for k, v in good_req().items() if k not in ("candidate_id",)}
    form.update(cand="DEMOCO", ticker="MCD")
    st, body, _h = req(port, "POST", "/stage7/run", form)
    assert st == 400 and "ticker mismatch" in body
    form.update(cand="MCD", ticker="DEMOCO")
    st, body, _h = req(port, "POST", "/stage7/run", form)
    assert st == 400 and read_index(app.ws.index_path) == [] and app.svc.ledger_rows() == []


# ===================== F4: Treasury evidence is human-attested, never self-labelled verified =======
def test_f4_typed_recent_date_without_attestation_is_not_accepted(demo_app):
    r = good_req()
    r.pop("tsy_attest")
    with pytest.raises(Blocked, match="attestation"):
        demo_app.svc.run(r, NOW)
    with pytest.raises(Blocked, match="source reference"):
        demo_app.svc.run(good_req(tsy_source_ref=""), NOW)
    assert read_index(demo_app.ws.index_path) == []


def test_f4_future_dated_and_malformed_references_rejected(demo_app):
    with pytest.raises(Blocked, match="future"):
        demo_app.svc.run(good_req(tsy_ref_date=(NOW + timedelta(days=30)).date().isoformat()), NOW)
    with pytest.raises(Blocked, match="YYYY-MM-DD"):
        demo_app.svc.run(good_req(tsy_ref_date="yesterday"), NOW)


def test_f4_attested_but_old_reference_is_stale_and_blocks_stage7_and_funding(demo_app):
    e = demo_app.svc.run(good_req(tsy_ref_date=(NOW - timedelta(days=30)).date().isoformat()), NOW)
    assert e["status"] == "BLOCKED"
    run = demo_app.svc.load_run(e["run_id"])[0]
    assert any("STALE" in r for r in run.result.reasons)
    before = ledger_bytes(demo_app)
    with pytest.raises(Rejected):
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert ledger_bytes(demo_app) == before


def test_f4_evidence_is_recorded_as_human_attested_and_unverified_by_atlas(demo_app, monkeypatch):
    spy = Spy(demo_app, monkeypatch)
    e = demo_app.svc.run(good_req(), NOW)
    ref = spy.calls[-1][0][3][1].market_reference
    assert "HUMAN-ATTESTED" in ref.provider and "not independently verified" in ref.provider
    ev = json.loads(Path(e["inputs"]["evidence_set"]["artifact_path"]).read_text())["treasury_evidence"]
    assert ev["verification"] == "UNVERIFIED_BY_ATLAS" and ev["human_attested"] is True and ev["source_ref"]
    assert "NOT source verification" in ev["freshness_label_basis"]
    assert "HUMAN-ATTESTED, not independently verified" in appmod.run_page(demo_app, e["run_id"])


# ===================== F5: portfolio as-of / precision ===========================================
def test_f5_snapshot_as_of_is_the_baseline_valuation_date_not_decision_time(demo_app, monkeypatch):
    spy = Spy(demo_app, monkeypatch)
    e = demo_app.svc.run(good_req(), NOW)
    assert spy.portfolio.as_of == datetime(2026, 10, 7, tzinfo=timezone.utc) and spy.portfolio.as_of != NOW
    snap = json.loads(Path(e["inputs"]["portfolio_snapshot"]["artifact_path"]).read_text())
    assert snap["baseline_effective_at"].startswith("2026-10-07") and snap["evaluated_at"][:10] == NOW.date().isoformat()
    assert snap["baseline_age_days"] == (NOW - datetime(2026, 10, 7, tzinfo=timezone.utc)).days
    assert "approximate" in snap["valuation_uncertainty"] and "≈ $59,000" in snap["valuation_uncertainty"]


def test_f5_baseline_acknowledgement_is_required(demo_app):
    r = good_req()
    r.pop("baseline_ack")
    with pytest.raises(Blocked, match="acknowledge"):
        demo_app.svc.run(r, NOW)
    assert read_index(demo_app.ws.index_path) == []


def test_f5_overview_does_not_present_the_approximate_total_to_the_cent(demo_app):
    h = appmod.overview(demo_app)
    assert "≈ $683,906" in h and "$683,905.93" not in h and "$624,905.93" in h  # stocks exact, total approximate
    assert "days old" in h and "not live" in h


# ===================== F6: Stage 7 -> fresh-price check -> Stage 8 ===================================
class Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


def clocked_svc(app, clock):
    return Stage7Service(app.ws, provider_factory=lambda: demo.FixtureProvider(clock=clock), identity_fn=lambda t: demo.DEMO_KEY,
                         allowed_providers={demo.DEMO_PROVIDER}, key_present=lambda: True)


def test_f6_week_old_eligible_run_cannot_fund_a_paper_initiate(demo_app):
    clk = Clock(NOW - timedelta(days=8))
    svc = clocked_svc(demo_app, clk)
    e = svc.run(good_req(tsy_ref_date=(NOW - timedelta(days=8)).date().isoformat(),
                         revisit_date=(NOW + timedelta(days=100)).date().isoformat()), clk())
    assert e["status"] == "ELIGIBLE FOR STAGE 8"  # it WAS eligible when run
    before = ledger_bytes(demo_app)
    clk.t = NOW
    with pytest.raises(Rejected, match="STALE Stage 7 run") as ei:
        svc.record_stage8(e["run_id"], s8(action="INITIATE"), NOW)
    assert (ei.value.rows_before, ei.value.rows_after) == (0, 0) and ledger_bytes(demo_app) == before
    with pytest.raises(Rejected, match="STALE"):
        svc.record_stage8(e["run_id"], s8(action="ADD"), NOW)
    assert ledger_bytes(demo_app) == before and demo_app.ws.facade.verify_ledger()


def test_f6_newer_completed_session_since_the_run_forces_a_rerun(demo_app):
    close = latest_completed_session(NOW).session_close_utc
    t1, t2 = close - timedelta(minutes=1), close + timedelta(hours=1)  # run priced the previous session
    clk = Clock(t1)
    svc = clocked_svc(demo_app, clk)
    e = svc.run(good_req(tsy_ref_date=t1.date().isoformat(), revisit_date=(NOW + timedelta(days=100)).date().isoformat()), t1)
    assert e["priced_session"] != latest_completed_session(t2).session_date.isoformat()
    clk.t = t2
    before = ledger_bytes(demo_app)
    with pytest.raises(Rejected, match="STALE price") as ei:
        svc.record_stage8(e["run_id"], s8(), t2)
    assert ei.value.rows_after == 0 and ledger_bytes(demo_app) == before


def test_f6_failed_fresh_binding_blocks_funding_but_not_a_non_action(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    broken = Stage7Service(demo_app.ws, provider_factory=lambda: demo.FixtureProvider(mic="XNAS"), identity_fn=lambda t: demo.DEMO_KEY,
                           allowed_providers={demo.DEMO_PROVIDER}, key_present=lambda: True)
    before = ledger_bytes(demo_app)
    with pytest.raises(Rejected, match="fresh-price check failed"):
        broken.record_stage8(e["run_id"], s8(), NOW)
    assert ledger_bytes(demo_app) == before
    out = broken.record_stage8(e["run_id"], s8(action="DO NOTHING"), NOW)  # non-action never needs fresh price
    assert out["rows_after"] == 1


def test_f6_missing_key_in_canonical_style_blocks_funded_actions(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    nokey = Stage7Service(demo_app.ws, provider_factory=demo.FixtureProvider, identity_fn=lambda t: demo.DEMO_KEY,
                          allowed_providers={demo.DEMO_PROVIDER}, key_present=lambda: False)
    before = ledger_bytes(demo_app)
    with pytest.raises(Rejected, match="TWELVEDATA_API_KEY is absent"):
        nokey.record_stage8(e["run_id"], s8(), NOW)
    assert ledger_bytes(demo_app) == before


def test_f6_candidate_reparked_after_the_run_cannot_be_funded(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    ledger.change_state(demo_app.ws.candidate_ledger, candidate_id="DEMOCO", to_state="PARKED", reason="new fact",
                        waiting_on="Q3 call", parked_until="2026-12-01", parked_until_verified=True)
    before = ledger_bytes(demo_app)
    with pytest.raises(Rejected, match="PARKED"):
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert ledger_bytes(demo_app) == before
    assert demo_app.svc.record_stage8(e["run_id"], s8(action="HOLD CASH"), NOW)["rows_after"] == 1


def test_f6_successful_funded_paper_action_logs_its_fresh_price_check(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    out = demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert out["rows_after"] == 1
    chk = [json.loads(l) for l in (demo_app.ws.root / "stage8_price_checks.jsonl").read_text().splitlines()]
    assert chk[0]["run_id"] == e["run_id"] and chk[0]["provider"] == demo.DEMO_PROVIDER and chk[0]["session"] == e["priced_session"]


def test_f6_characterization_the_frozen_facade_alone_does_not_check_run_age(tmp_path):
    """Investigation result, recorded as a test: the unchanged facade/store accept an old retained ELIGIBLE run.
    That is why the adapter-level fresh-price checkpoint above exists. (Isolated tmp workspace, fixture data.)"""
    app = build(True, tmp_path / "chr")
    clk = Clock(NOW - timedelta(days=8))
    svc = clocked_svc(app, clk)
    e = svc.run(good_req(tsy_ref_date=(NOW - timedelta(days=8)).date().isoformat(),
                         revisit_date=(NOW + timedelta(days=100)).date().isoformat()), clk())
    run, versions, _entry = svc.load_run(e["run_id"])
    rec = app.ws.facade.record_final_decision(
        run, record_id="CHARACTERIZE", human_stage8_action="INITIATE", human_rationale="characterization only",
        alternatives_considered=("SPY", "Treasury/Cash", "Do Nothing"), input_versions=versions, created_at=NOW,
        portfolio_snapshot_id="X", dominant_drivers=("fixture driver",), starter_cap_weight=0.02,
        revisit_triggers=run.result.position and __import__("stock_atlas.models", fromlist=["RevisitTriggers"]).RevisitTriggers("p", NOW + timedelta(days=90)))
    assert rec.record_id == "CHARACTERIZE"  # facade did not object to an 8-day-old run
    # ...and the UI service refuses the same thing in the real path:
    app2 = build(True, tmp_path / "chr2")
    clk2 = Clock(NOW - timedelta(days=8))
    svc2 = clocked_svc(app2, clk2)
    e2 = svc2.run(good_req(tsy_ref_date=(NOW - timedelta(days=8)).date().isoformat(),
                           revisit_date=(NOW + timedelta(days=100)).date().isoformat()), clk2())
    clk2.t = NOW
    with pytest.raises(Rejected):
        svc2.record_stage8(e2["run_id"], s8(), NOW)
    assert app2.svc.ledger_rows() == []


# ===================== F7: run-id collisions ===========================================================
def test_f7_two_rapid_runs_never_share_an_id_or_overwrite(demo_app):
    a = demo_app.svc.run(good_req(), NOW)
    b = demo_app.svc.run(good_req(), NOW)  # same ticker, same instant
    assert a["run_id"] != b["run_id"]
    assert len({e["run_id"] for e in read_index(demo_app.ws.index_path)}) == 2
    assert all(r["verified"] for r in demo_app.svc.list_runs())


def test_f7_forced_collision_is_rejected_without_mutation(demo_app, monkeypatch):
    monkeypatch.setattr(Stage7Service, "_new_run_id", staticmethod(lambda t, n: "S7-FIXED-ID"))
    a = demo_app.svc.run(good_req(), NOW)
    before = tree_hash(demo_app.ws.root)
    with pytest.raises(Blocked, match="already exists"):
        demo_app.svc.run(good_req(ret_low="14", ret_high="18"), NOW + timedelta(seconds=5))
    assert tree_hash(demo_app.ws.root) == before and len(read_index(demo_app.ws.index_path)) == 1
    assert demo_app.svc.list_runs()[0]["verified"] and a["run_id"] == "S7-FIXED-ID"


# ===================== artifact download guard ===========================================================
def test_artifact_download_fails_closed_when_hash_mismatches(http_app):
    app, port = http_app
    e = app.svc.run(good_req(), NOW)
    rid = urllib.parse.quote(e["run_id"])
    assert req(port, "GET", f"/artifact/{rid}/stage7.json")[0] == 200
    p = Path(e["inputs"]["scenario_model"]["artifact_path"])
    p.write_text(p.read_text().replace("fixture", "tampered"))
    for name in ("stage7.json", "scenario_model.json", "evidence_set.json"):
        st, body, _h = req(port, "GET", f"/artifact/{rid}/{name}")
        assert st == 409 and "NOT VERIFIED" in body


# ===================== MCD / RPM restrictions preserved =====================================================
def test_mcd_rpm_stay_parked_and_cannot_be_promoted_by_revisit_or_ui(demo_app):
    p = demo_app.ws.candidate_ledger
    for cid in ("MCD", "RPM"):
        with pytest.raises(ledger.LedgerError):
            ledger.change_state(p, candidate_id=cid, to_state="READY_FOR_CAPITAL_COMPARISON", reason="try")
        ledger.add_note(p, candidate_id=cid, text="REVISIT of S8-FAKE: attempt to nudge")
        assert ledger.replay(p)[cid]["state"] == "PARKED"
    assert ledger.replay(p)["MCD"]["parked_until"] == "2026-11-04" and ledger.replay(p)["RPM"]["parked_until"] == "2026-11-09"
    ledger.verify_chain(p)


def test_committed_discovery_ledger_still_has_mcd_rpm_parked():
    c = ledger.replay()
    assert (c["MCD"]["state"], c["MCD"]["parked_until"]) == ("PARKED", "2026-11-04")
    assert (c["RPM"]["state"], c["RPM"]["parked_until"]) == ("PARKED", "2026-11-09")
    ledger.verify_chain()


# ===================== every rejected funded path leaves zero rows ===============================================
@pytest.mark.parametrize("mutate", ["tamper_stage7", "tamper_inputs", "unknown_run", "no_confirm", "no_rationale", "bad_action"])
def test_every_rejected_funded_path_adds_zero_ledger_rows(demo_app, mutate):
    e = demo_app.svc.run(good_req(), NOW)
    rid, form = e["run_id"], s8()
    if mutate == "tamper_stage7":
        p = Path(e["stage7"]["artifact_path"]); p.write_text(p.read_text() + " ")
    elif mutate == "tamper_inputs":
        p = Path(e["inputs"]["evidence_set"]["artifact_path"]); p.write_text(p.read_text() + " ")
    elif mutate == "unknown_run":
        rid = "S7-NOPE"
    elif mutate == "no_confirm":
        form["confirm"] = ""
    elif mutate == "no_rationale":
        form["rationale"] = ""
    else:
        form["action"] = "ROTATE"
    before = ledger_bytes(demo_app)
    with pytest.raises(Rejected) as ei:
        demo_app.svc.record_stage8(rid, form, NOW)
    assert (ei.value.rows_before, ei.value.rows_after) == (0, 0)
    assert ledger_bytes(demo_app) == before and demo_app.svc.ledger_rows() == []
    assert demo_app.ws.facade.verify_ledger()


def test_capability_matrix_states_the_attestation_and_stage8_freshness():
    text = " ".join(d for _, _, d in appmod.CAPABILITIES)
    assert "human-attested" in text.lower() and "fresh-price" in text.lower()


def test_frozen_control_files_match_the_pinned_hashes():
    """The remediation did not touch the frozen capital controls. A deliberate, approved control change must update the pin."""
    repo = Path(__file__).resolve().parent.parent
    pins = [l.split() for l in (repo / "atlas_ui" / "FROZEN_CONTROL_SHA256.txt").read_text().splitlines() if l.strip()]
    assert len(pins) == 12 and any(p[1] == "capital_decision_facade.py" for p in pins)
    for digest, rel in pins:
        assert hashlib.sha256((repo / rel).read_bytes()).hexdigest() == digest, f"{rel} changed"
