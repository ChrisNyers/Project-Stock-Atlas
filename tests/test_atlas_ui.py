"""UI integration tests — real facade / DecisionStore / Gate B code; FIXTURE price provider only.

No test here proves a live Stage 7 run: TWELVEDATA_API_KEY is absent, so the live
price path is BLOCKED and tested only for its fail-closed behaviour. Every funded
outcome below uses the clearly-labelled FIXTURE-DEMO provider in an isolated
workspace. Paper only. Capital status: NO REAL PORTFOLIO ACTION.
"""
import ast
import http.client
import json
import shutil
import subprocess
import threading
import urllib.parse
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from atlas_ui import app as appmod
from atlas_ui import canonical, demo
from atlas_ui.__main__ import build
from atlas_ui.service import Blocked, Rejected, Stage7Service, Workspace, read_index
from capital_decision_facade import ControlFailure
from operating_mvp import ledger

REPO = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc)


def good_req(**over):
    r = dict(cand="DEMOCO", candidate_id="DEMOCO", ticker="DEMOCO", increment="13000", horizon_years="5",
             ret_low="13", ret_high="17", req_low="10", req_high="11", spy_low="7", spy_high="10",
             tsy_low="3.5", tsy_high="4.5", tsy_ref_key="UST-13W", tsy_ref_value="3.9",
             tsy_ref_date=NOW.date().isoformat(), tsy_duration="VERIFIED",
             spy_notes="coarse SPY range (fixture)", tsy_notes="duration normalized (fixture)",
             regime="priced for modest growth", regime_evidence="fixture", variant="fixture variant",
             variant_evidence="fixture evidence", band_basis="fixture basis", provenance="fixture provenance",
             uncertainties="OPERATING | demand | NO", drivers="fixture driver", revisit_price="+/-25%",
             revisit_date=(NOW + timedelta(days=200)).date().isoformat(), gate="CLEAR", capacity="AVAILABLE",
             remaining_capacity="10", classification="STARTER", tax="VERIFIED", liquidity="VERIFIED",
             execution="VERIFIED", decision="BUY", decision_basis="evidence ledger items #1-#4 (fixture)",
             tsy_source_ref="home.treasury.gov par curve page (fixture)", tsy_attest="1", baseline_ack="1")
    r.update(over)
    return r


@pytest.fixture
def demo_app(tmp_path):
    return build(True, tmp_path / "demo")


@pytest.fixture
def canon_app(tmp_path, monkeypatch):
    monkeypatch.delenv("TWELVEDATA_API_KEY", raising=False)
    copy = tmp_path / "candidates.jsonl"
    shutil.copyfile(ledger.DEFAULT_LEDGER, copy)  # tests never touch the committed ledger
    return build(False, tmp_path / "live", candidate_ledger=copy)


def s8(**over):
    d = dict(action="INITIATE", rationale="paper rationale", confirm="1", why_vs="a", why_size="b", wrong_if="c",
             tsy_ref_value="3.9", tsy_ref_date=NOW.date().isoformat(), tsy_source_ref="home.treasury.gov (fixture)", tsy_attest="1")
    d.update(over)
    return d


# ---- 1. canonical read-only state ---------------------------------------------------
def test_canonical_baseline_loads_and_reconciles():
    c0 = canonical.load_cycle0()
    assert len(c0.holdings) == 28 and str(c0.stocks_total) == "624905.93" and str(c0.identified_value) == "683905.93"
    snap = canonical.build_portfolio_snapshot(c0, as_of=NOW)
    assert snap.add_only_policy and not snap.trims_permitted and snap.funding_pocket.deployable_amount == 50_000
    assert abs(sum(h.weight for h in snap.holdings) - float(c0.stocks_total / c0.identified_value)) < 1e-9
    with pytest.raises(canonical.CanonicalError):
        canonical.build_portfolio_snapshot(c0, as_of=NOW, funding_amount=60_000)


def test_baseline_tamper_fails_closed(tmp_path):
    src = canonical.BASELINE_DOC.read_text()
    bad = tmp_path / "b.md"
    bad.write_text(src.replace("| AVGO | $142,388.77 |", "| AVGO | $142,388.78 |"))
    with pytest.raises(canonical.CanonicalError, match="not adjusted"):
        canonical.load_cycle0(bad)
    bad.write_text(src.split("## Correction 002")[0])
    with pytest.raises(canonical.CanonicalError):
        canonical.load_cycle0(bad)
    with pytest.raises(canonical.CanonicalError):
        canonical.load_cycle0(tmp_path / "missing.md")


def test_overview_shows_canonical_state_not_the_handoff_snapshot(canon_app):
    h = appmod.overview(canon_app)
    for needle in ("≈ $683,906", "APPROXIMATE", "HUMAN-SUPPLIED", "2026-10-07", "NOT RUN / NOT VERIFIED", "PARKED until 2026-11-04",
                   "PARKED until 2026-11-09", "ABSENT", "BLOCKED", "not</b> the canonical baseline"):
        assert needle in h, needle
    assert "$500,000" not in h.replace("handoff's $500K", "")
    st = appmod.api_state(canon_app)
    assert st["baseline"]["sha256"] == canonical.load_cycle0().doc_sha256 and st["stage7_runs"] == []
    assert st["decision_rows"] == 0 and st["twelvedata_key"] == "ABSENT" and st["paper_only"] is True


# ---- 2. immutable intake -----------------------------------------------------------
def test_intake_freezes_stance_and_never_edits(canon_app):
    p = canon_app.ws.candidate_ledger
    ev = ledger.surface(p, name="Liqn Co", ticker="LQN1", source="LIQN", why_surfaced="w", investment_question="q")
    s1 = ledger.freeze_stance(p, candidate_id="LQN1", stance_text="NEUTRAL — no view.")
    before = p.read_bytes()
    ledger.change_state(p, candidate_id="LQN1", to_state="QUICK_TEST", reason="r")
    s2 = ledger.freeze_stance(p, candidate_id="LQN1", stance_text="Now leaning positive.")
    ledger.change_state(p, candidate_id="LQN1", to_state="QUICK_TEST", reason="r") if False else None
    c = ledger.replay(p)["LQN1"]
    assert [x["version"] for x in c["stances"]] == [1, 2]
    assert c["stances"][0]["pre_atlas"] is True and c["stances"][1]["pre_atlas"] is False  # later version = revision
    assert c["source"] == "LIQN" and p.read_bytes().startswith(before)
    assert ledger.verify_chain(p) is None
    with pytest.raises(ledger.LedgerError):
        ledger.freeze_stance(p, candidate_id="LQN1", stance_text="  ")


def test_stance_after_underwriting_is_not_pre_atlas(demo_app):
    ledger.freeze_stance(demo_app.ws.candidate_ledger, candidate_id="DEMOCO", stance_text="late", intended_action="x")
    last = ledger.replay(demo_app.ws.candidate_ledger)["DEMOCO"]["stances"][-1]
    assert last["version"] == 2 and last["pre_atlas"] is False


# ---- 3. Gate B: fail closed, key never exposed ---------------------------------------
def test_live_binding_blocked_without_key_and_nothing_retained(canon_app):
    with pytest.raises(Blocked, match="TWELVEDATA_API_KEY is absent"):
        canon_app.svc.bind_price("MCD", NOW)
    p = canon_app.ws.candidate_ledger
    # MCD is PARKED: Stage 7 cannot even start; and nothing is written either way.
    with pytest.raises(Blocked, match="PARKED until 2026-11-04"):
        canon_app.svc.run(good_req(candidate_id="MCD", ticker="MCD", cand="MCD"), NOW)
    assert read_index(canon_app.ws.index_path) == [] and not list(canon_app.ws.facade.artifact_dir.glob("*"))
    assert canon_app.svc.ledger_rows() == []


def test_fixture_prices_are_refused_in_canonical_mode(canon_app, monkeypatch):
    p = canon_app.ws.candidate_ledger
    for st, kw in (("QUICK_TEST", {}), ("UNDERWRITING", {}), ("READY_FOR_CAPITAL_COMPARISON", {})):
        pass
    ledger.surface(p, name="Fx", ticker="FXCO", source="HUMAN", why_surfaced="w", investment_question="q")
    ledger.change_state(p, candidate_id="FXCO", to_state="QUICK_TEST", reason="r")
    ledger.record_falsification(p, candidate_id="FXCO", test="t", result="SURVIVED", grade="PRIMARY")
    ledger.change_state(p, candidate_id="FXCO", to_state="UNDERWRITING", reason="r")
    ledger.change_state(p, candidate_id="FXCO", to_state="READY_FOR_CAPITAL_COMPARISON", reason="r")
    svc = Stage7Service(canon_app.ws, provider_factory=demo.FixtureProvider, identity_fn=lambda t: demo.DEMO_KEY,
                        allowed_providers={"twelvedata"}, key_present=lambda: True)
    with pytest.raises(Blocked, match="not permitted in CANONICAL mode"):
        svc.run(good_req(candidate_id="FXCO", ticker="FXCO"), NOW)
    assert read_index(canon_app.ws.index_path) == [] and canon_app.svc.ledger_rows() == []


@pytest.mark.parametrize("label,kw,identity,needle", [
    ("identity mismatch", {}, lambda t: "SEC-CIK:0000000001:OTHER", "Security identity mismatch"),
    ("unsupported venue", {"mic": "XNAS"}, None, "MIC"),
])
def test_gate_b_stops_are_exact_not_green(demo_app, label, kw, identity, needle):
    svc = Stage7Service(demo_app.ws, provider_factory=lambda: demo.FixtureProvider(**kw),
                        identity_fn=identity or (lambda t: demo.DEMO_KEY), allowed_providers={demo.DEMO_PROVIDER},
                        key_present=lambda: True)
    with pytest.raises(Blocked, match=needle):
        svc.bind_price("DEMOCO", NOW)
    assert read_index(demo_app.ws.index_path) == []


def test_stale_quote_cannot_back_a_funded_decision(demo_app):
    svc = Stage7Service(demo_app.ws, provider_factory=lambda: demo.FixtureProvider(clock=lambda: NOW - timedelta(days=10)),
                        identity_fn=lambda t: demo.DEMO_KEY, allowed_providers={demo.DEMO_PROVIDER}, key_present=lambda: True)
    e = svc.run(good_req(), NOW)
    assert e["status"] != "ELIGIBLE FOR STAGE 8"
    with pytest.raises(Rejected, match="requires Stage 7 status"):
        svc.record_stage8(e["run_id"], s8(), NOW)
    assert len(svc.ledger_rows()) == 0


def test_api_key_never_reaches_the_browser(demo_app, monkeypatch):
    monkeypatch.setenv("TWELVEDATA_API_KEY", "sk-TESTSECRET-123456")
    e = demo_app.svc.run(good_req(), NOW)
    pages = [appmod.overview(demo_app), appmod.stage7_page(demo_app), appmod.run_page(demo_app, e["run_id"]),
             appmod.history_page(demo_app), json.dumps(appmod.api_state(demo_app), default=str),
             Path(e["stage7"]["artifact_path"]).read_text(), Path(e["inputs"]["evidence_set"]["artifact_path"]).read_text()]
    assert all("sk-TESTSECRET" not in p for p in pages)
    assert all("<script" not in p.lower() for p in pages[:4])


# ---- 4. Stage 7 through the real facade -------------------------------------------
def test_stage7_runs_through_facade_is_retained_and_rehydrates_exactly(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    assert e["status"] == "ELIGIBLE FOR STAGE 8" and e["mode"] == "DEMO"
    run, versions, entry = demo_app.svc.load_run(e["run_id"])
    assert run.artifact_ref.sha256 == e["stage7"]["sha256"] and Path(run.artifact_ref.artifact_path).exists()
    assert not hasattr(run.result, "portfolio_action") and "NO PORTFOLIO ACTION" in run.result.comparison_header
    assert set(entry["inputs"]) == {"portfolio_snapshot", "scenario_model", "exposure_map", "evidence_set", "control_contract"}
    ctr = json.loads(Path(entry["inputs"]["control_contract"]["artifact_path"]).read_text())
    assert ctr["accepted_baseline"] == "4c71d06afe0853389beb4a77ec2708656c3fc708" and "stock_atlas/controls.py" in ctr["control_files_sha256"]
    assert demo_app.svc.list_runs()[0]["verified"] is True
    assert demo_app.svc.ledger_rows() == []  # Stage 7 alone writes no decision


def test_tampered_artifact_is_not_verified_and_blocks_stage8(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    path = Path(e["stage7"]["artifact_path"])
    path.write_text(path.read_text().replace("ELIGIBLE FOR STAGE 8", "ELIGIBLE FOR STAGE 9"))
    assert demo_app.svc.list_runs()[0]["verified"] is False
    with pytest.raises(Blocked, match="NOT VERIFIED"):
        demo_app.svc.load_run(e["run_id"])
    with pytest.raises(Rejected) as ei:
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert ei.value.rows_before == ei.value.rows_after == 0
    assert "NOT VERIFIED" in appmod.run_page(demo_app, e["run_id"])


def test_stage7_requires_a_human_ready_candidate_and_complete_inputs(demo_app):
    with pytest.raises(Blocked, match="PARKED"):
        demo_app.svc.run(good_req(candidate_id="RPM", ticker="RPM"), NOW)
    with pytest.raises(Blocked, match="unknown candidate"):
        demo_app.svc.run(good_req(candidate_id="NOPE", ticker="NOPE"), NOW)
    with pytest.raises(Blocked, match="unknown candidate"):
        demo_app.svc.run({k: v for k, v in good_req().items() if k != "candidate_id"}, NOW)
    for field in ("ret_low", "tsy_ref_date", "revisit_date", "increment"):
        with pytest.raises(Blocked):
            demo_app.svc.run(good_req(**{field: ""}), NOW)
    with pytest.raises(Blocked, match="TYPE"):
        demo_app.svc.run(good_req(uncertainties="not structured"), NOW)
    assert read_index(demo_app.ws.index_path) == []


def test_unverified_inputs_fail_closed_at_stage7(demo_app):
    e = demo_app.svc.run(good_req(capacity="UNVERIFIED"), NOW)
    assert e["status"] == "BLOCKED"
    e2 = demo_app.svc.run(good_req(gate="UNVERIFIED"), NOW + timedelta(seconds=1))
    assert e2["status"] == "WATCH / NO DECISION"
    e3 = demo_app.svc.run(good_req(ret_low="8", ret_high="12"), NOW + timedelta(seconds=2))
    assert e3["status"] == "NOT DISTINGUISHABLE"  # overlapping bands cannot be ordered on return alone


# ---- 5. Human Stage 8, paper only -----------------------------------------------------
def test_paper_initiate_records_to_the_real_ledger_with_proof(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    out = demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert (out["rows_before"], out["rows_after"], out["ledger_verified"], out["paper_only"]) == (0, 1, True, True)
    rows = demo_app.svc.ledger_rows()
    rec = rows[0]["record"]
    assert rec["human_stage8_action"] == "INITIATE" and rec["stage7_status"] == "ELIGIBLE FOR STAGE 8"
    assert rec["stage7_artifact"]["sha256"] == e["stage7"]["sha256"] and rows[0]["entry_hash"] == out["entry_hash"]
    assert "paper" in appmod.run_page(demo_app, e["run_id"]).lower()


def test_non_action_stays_available_after_eligible_and_after_blocked(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    out = demo_app.svc.record_stage8(e["run_id"], s8(action="DO NOTHING", why_vs="", why_size="", wrong_if=""), NOW)
    assert out["rows_after"] == 1
    b = demo_app.svc.run(good_req(capacity="UNVERIFIED"), NOW + timedelta(seconds=1))
    assert b["status"] == "BLOCKED"
    assert demo_app.svc.record_stage8(b["run_id"], s8(action="HOLD CASH"), NOW)["rows_after"] == 2


@pytest.mark.parametrize("form,needle", [
    (dict(action="TRIM"), "not available"), (dict(action="EXIT"), "not available"), (dict(action=""), "not available"),
    (dict(confirm=""), "confirmation"), (dict(rationale=" "), "rationale"),
])
def test_crafted_requests_are_rejected_with_zero_rows(demo_app, form, needle):
    e = demo_app.svc.run(good_req(), NOW)
    with pytest.raises(Rejected, match=needle) as ei:
        demo_app.svc.record_stage8(e["run_id"], s8(**form), NOW)
    assert ei.value.rows_before == ei.value.rows_after == 0 and demo_app.svc.ledger_rows() == []


def test_unknown_run_and_duplicate_decision_rejected(demo_app):
    with pytest.raises(Rejected, match="no retained Stage 7 run"):
        demo_app.svc.record_stage8("S7-FAKE-1", s8(), NOW)
    e = demo_app.svc.run(good_req(), NOW)
    demo_app.svc.record_stage8(e["run_id"], s8(action="DO NOTHING"), NOW)
    with pytest.raises(Rejected, match="already exists"):
        demo_app.svc.record_stage8(e["run_id"], s8(action="DO NOTHING"), NOW)
    assert len(demo_app.svc.ledger_rows()) == 1


def test_funded_action_needs_verified_constraints_even_if_stage7_passed(demo_app):
    e = demo_app.svc.run(good_req(tax="UNVERIFIED", accept_unverified="1"), NOW)
    assert e["status"] == "ELIGIBLE FOR STAGE 8"  # human accepted UNVERIFIED at Stage 7
    run, versions, entry = demo_app.svc.load_run(e["run_id"])
    assert run.result.constraint_state.value == "UNVERIFIED"
    with pytest.raises(Rejected, match="VERIFIED"):
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    # defense in depth: even bypassing the UI service, the facade/store refuse the funded record
    with pytest.raises(ControlFailure):
        demo_app.ws.facade.record_final_decision(
            run, record_id="BYPASS", human_stage8_action="INITIATE", human_rationale="x",
            alternatives_considered=("SPY", "Treasury/Cash", "Do Nothing"), input_versions=versions, created_at=NOW,
            portfolio_snapshot_id="X", dominant_drivers=("d",), starter_cap_weight=0.02)
    assert demo_app.svc.ledger_rows() == []


def test_funded_decision_over_starter_cap_is_refused_by_the_store(demo_app):
    e = demo_app.svc.run(good_req(increment="50000"), NOW)  # ~6.8% > the frozen 2% STARTER cap
    assert e["status"] == "ELIGIBLE FOR STAGE 8"
    with pytest.raises(Rejected, match="STARTER"):
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert demo_app.svc.ledger_rows() == []
    # weights are recomputed on the post-money denominator, not assumed
    pos = demo_app.svc.load_run(e["run_id"])[0].result.position
    assert abs(pos.post_trade_weight - 50000 / (683905.93 + 50000)) < 1e-6


# ---- 6. history / revisit immutability ------------------------------------------------
def test_revisit_is_a_linked_event_and_never_edits_the_record(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    demo_app.svc.record_stage8(e["run_id"], s8(action="DO NOTHING"), NOW)
    ledger_file = demo_app.ws.facade.store.path
    before = Path(ledger_file).read_bytes()
    ledger.add_note(demo_app.ws.candidate_ledger, candidate_id="DEMOCO", text=f"REVISIT of S8-{e['run_id']}: price moved")
    assert Path(ledger_file).read_bytes() == before
    h = appmod.history_page(demo_app)
    assert "REVISIT of S8-" in h and "LEDGER VERIFIED" in h and "NOT IMPLEMENTED" in h


# ---- 7. HTTP surface ---------------------------------------------------------------------
@pytest.fixture
def http_app(demo_app):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), appmod.make_handler(demo_app))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield demo_app, srv.server_address[1]
    srv.shutdown()


def req(port, method, path, body=None, headers=None):
    c = http.client.HTTPConnection("127.0.0.1", port)
    h = {"Host": f"127.0.0.1:{port}", **(headers or {})}
    if body is not None:
        h["Content-Type"] = "application/x-www-form-urlencoded"
    c.request(method, path, urllib.parse.urlencode(body) if body is not None else None, h)
    r = c.getresponse()
    return r.status, r.read().decode(), dict(r.getheaders())


def test_every_page_renders_with_csp_and_no_script(http_app):
    app, port = http_app
    for path in ("/", "/intake", "/stage7", "/desk", "/history", "/capabilities", "/candidate/MCD", "/candidate/DEMOCO"):
        st, body, hd = req(port, "GET", path)
        assert st == 200 and "<script" not in body.lower(), path
        assert "default-src 'none'" in hd["Content-Security-Policy"]
    assert req(port, "GET", "/candidate/NOPE")[0] == 404


def test_http_flow_stage7_then_crafted_and_real_stage8(http_app):
    app, port = http_app
    form = {k: v for k, v in good_req().items() if k not in ("candidate_id", "ticker")}
    form["cand"] = "DEMOCO"
    st, _b, h = req(port, "POST", "/stage7/run", form)
    assert st == 303 and h["Location"].startswith("/run/S7-DEMOCO-")
    run_id = urllib.parse.unquote(h["Location"][5:])
    st, body, _h = req(port, "GET", h["Location"])
    assert st == 200 and "ELIGIBLE FOR STAGE 8" in body and "Side-by-side" in body and "Treasury" in body and "Do Nothing" in body
    assert "Existing holdings / recycle" in body and "UNMEASURED" in body
    # crafted request: no confirmation -> 400 + zero rows
    st, body, _h = req(port, "POST", "/stage8", {"run_id": run_id, "action": "INITIATE", "rationale": "x"})
    assert st == 400 and "zero rows written" in body and app.svc.ledger_rows() == []
    # crafted request against a fabricated run id
    st, body, _h = req(port, "POST", "/stage8", {"run_id": "S7-FAKE", "action": "INITIATE", "rationale": "x", "confirm": "1"})
    assert st == 400 and app.svc.ledger_rows() == []
    st, _b, _h = req(port, "POST", "/stage8", {"run_id": run_id, **s8()})
    assert st == 303 and len(app.svc.ledger_rows()) == 1
    st, body, _h = req(port, "GET", "/api/ledger")
    assert json.loads(body)["verified"] is True and len(json.loads(body)["rows"]) == 1
    st, body, _h = req(port, "GET", f"/api/runs/{run_id}")
    assert st == 200 and json.loads(body)["result"]["status"] == "ELIGIBLE FOR STAGE 8"
    assert req(port, "GET", f"/artifact/{run_id}/stage7.json")[0] == 200
    assert req(port, "GET", f"/artifact/{run_id}/../../x.json")[0] == 404


def test_http_stage7_refused_for_parked_candidate(http_app):
    app, port = http_app
    form = {k: v for k, v in good_req().items() if k not in ("candidate_id", "ticker")}
    form["cand"] = "MCD"
    st, body, _h = req(port, "POST", "/stage7/run", form)
    assert st == 400 and "PARKED until 2026-11-04" in body and read_index(app.ws.index_path) == []


def test_http_intake_records_candidate_with_stance_and_source_provenance(http_app):
    app, port = http_app
    st, _b, h = req(port, "POST", "/intake", {"name": "New <b>Co</b>", "ticker": "NWC", "source": "LIQN", "source_detail": "",
                                           "why_surfaced": "w", "investment_question": "q", "stance_text": "Neutral — no view."})
    assert st == 303 and h["Location"] == "/candidate/NWC"
    body = req(port, "GET", "/candidate/NWC")[1]
    assert "PRE-ATLAS BASELINE" in body and "source: LIQN" in body and "<b>Co</b>" not in body
    st, body, _h = req(port, "POST", "/intake", {"name": "dup", "ticker": "NWC", "source": "SUE", "why_surfaced": "w",
                                              "investment_question": "q", "stance_text": "s"})
    assert st == 400 and "already tracked" in body


def test_http_rejects_foreign_host_and_origin(http_app):
    _app, port = http_app
    assert req(port, "GET", "/", headers={"Host": "evil.example"})[0] == 403
    assert req(port, "POST", "/stage8", {"run_id": "x"}, {"Origin": "http://evil.example"})[0] == 403


# ---- 8. boundaries ---------------------------------------------------------------------------
def test_atlas_ui_has_no_second_capital_writer_and_no_execution_surface():
    banned_names = {"DecisionStore", "PortfolioAction"}
    for f in (REPO / "atlas_ui").glob("*.py"):
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "decision_store" in node.module:
                pytest.fail(f"{f.name} imports DecisionStore directly")
            if isinstance(node, ast.alias) and node.name in banned_names:
                pytest.fail(f"{f.name} imports {node.name}")
            if isinstance(node, ast.Attribute) and node.attr in ("append", "overwrite") and isinstance(node.value, ast.Attribute) and node.value.attr == "store":
                pytest.fail(f"{f.name} writes through store directly")
    src = "".join(f.read_text() for f in (REPO / "atlas_ui").glob("*.py")).lower()
    for word in ("place_order", "submit_order", "alpaca", "ibkr", "schwab", "interactive brokers"):
        assert word not in src
    for line in src.splitlines():  # "broker" may appear only in negations such as "No broker"
        line = line.replace("brokerage", "")
        if "broker" in line:
            assert any(n in line for n in ("no broker", "no real", "not", "never")), line


def test_frozen_control_layer_changed_only_by_the_authorized_change_record():
    """stock_atlas/ equals the accepted 4c71d06 EXCEPT pipeline.py, whose only change is the price_basis
    authorized by docs/controlled_live_pilot/FROZEN_CONTROL_CHANGE_001.md."""
    git = ["git", "-C", str(REPO), "diff", "4c71d06afe0853389beb4a77ec2708656c3fc708"]
    try:
        rest = subprocess.run(git + ["--stat", "--", "stock_atlas", ":!stock_atlas/pipeline.py"], capture_output=True, text=True, timeout=20)
        pipe = subprocess.run(git + ["-U0", "--", "stock_atlas/pipeline.py"], capture_output=True, text=True, timeout=20)
    except Exception:
        pytest.skip("git unavailable")
    if rest.returncode != 0:
        pytest.skip("accepted baseline commit not present in this checkout")
    assert rest.stdout.strip() == ""  # every other control-layer file is byte-identical to the accepted baseline
    removed = [l for l in pipe.stdout.splitlines() if l.startswith("-") and not l.startswith("---")]
    assert removed == []  # purely additive: no existing Stage 7 line was changed or removed
    added = "\n".join(l for l in pipe.stdout.splitlines() if l.startswith("+") and not l.startswith("+++"))
    assert "price_basis" in added and "evaluate_stage7_candidate" not in added


def test_capability_matrix_is_honest_and_in_sync():
    allowed = ("PROVEN LIVE", "PROVEN CANONICAL OFFLINE", "FIXTURE-TESTED", "BLOCKED", "NOT IMPLEMENTED")
    assert all(s.split(" (")[0] in allowed for _, s, _ in appmod.CAPABILITIES)
    status = {n.split(".")[0]: s for n, s, _ in appmod.CAPABILITIES}
    assert status["D"] == "BLOCKED" and status["E"] == "FIXTURE-TESTED" and status["F"] == "FIXTURE-TESTED"
    assert status["C2"] == "NOT IMPLEMENTED" and not any(s == "PROVEN LIVE" for s in status.values())  # nothing is live-proven
    doc = (REPO / "atlas_ui" / "CAPABILITY_MATRIX.md").read_text()
    assert appmod.matrix_markdown() in doc
