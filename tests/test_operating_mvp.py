"""Operating MVP v0.1 — workflow-support tests (no capital path, no network)."""
import ast
import http.client
import threading
import urllib.parse
from datetime import date
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from operating_mvp import ledger, seed, ui

PKG = Path(ledger.__file__).parent


@pytest.fixture
def lp(tmp_path):
    return tmp_path / "ledger.jsonl"


def _surface(lp, name="Acme", source="HUMAN", **kw):
    return ledger.surface(lp, name=name, source=source, why_surfaced="why", investment_question="q?",
                          effective_date="2026-10-01", **kw)


# ---- vocabulary / transitions -------------------------------------------------
def test_single_vocabulary():
    assert ledger.STATES == ("SURFACED", "QUICK_TEST", "UNDERWRITING", "PARKED", "REJECTED",
                             "READY_FOR_CAPITAL_COMPARISON")


def test_surfaced_start_and_allowed_path(lp):
    _surface(lp, ticker="AAA")
    assert ledger.replay(lp)["AAA"]["state"] == "SURFACED"
    for s in ("QUICK_TEST", "UNDERWRITING", "READY_FOR_CAPITAL_COMPARISON"):
        ledger.change_state(lp, candidate_id="AAA", to_state=s, reason="r")
        assert ledger.replay(lp)["AAA"]["state"] == s


def test_disallowed_transitions(lp):
    _surface(lp, ticker="AAA")
    with pytest.raises(ledger.LedgerError):  # cannot skip to READY
        ledger.change_state(lp, candidate_id="AAA", to_state="READY_FOR_CAPITAL_COMPARISON", reason="r")
    with pytest.raises(ledger.LedgerError):  # UNDERWRITING -> UNDERWRITING is a NOTE, not a state change
        ledger.change_state(lp, candidate_id="AAA", to_state="UNDERWRITING", reason="r")
        ledger.change_state(lp, candidate_id="AAA", to_state="UNDERWRITING", reason="r")
    with pytest.raises(ledger.LedgerError):
        ledger.change_state(lp, candidate_id="AAA", to_state="BUY", reason="r")


def test_continue_underwriting_is_a_note_not_a_state(lp):
    _surface(lp, ticker="AAA")
    ledger.change_state(lp, candidate_id="AAA", to_state="UNDERWRITING", reason="r")
    ledger.add_note(lp, candidate_id="AAA", text="continue underwriting: need Q3")
    c = ledger.replay(lp)["AAA"]
    assert c["state"] == "UNDERWRITING" and c["notes"][0]["text"].startswith("continue")


def test_parked_requires_waiting_on_and_verified_requires_date(lp):
    _surface(lp, ticker="AAA")
    with pytest.raises(ledger.LedgerError):
        ledger.change_state(lp, candidate_id="AAA", to_state="PARKED", reason="r")
    with pytest.raises(ledger.LedgerError):
        ledger.change_state(lp, candidate_id="AAA", to_state="PARKED", reason="r", waiting_on="x",
                            parked_until_verified=True)
    with pytest.raises(ledger.LedgerError):
        ledger.change_state(lp, candidate_id="AAA", to_state="PARKED", reason="r", waiting_on="x",
                            parked_until="11/04/2026")
    ledger.change_state(lp, candidate_id="AAA", to_state="PARKED", reason="r", waiting_on="Q3")
    assert ledger.replay(lp)["AAA"]["parked_until"] == ""  # undated park allowed; not invented


def test_rejected_only_reopens_to_surfaced_with_reason(lp):
    _surface(lp, ticker="AAA")
    ledger.change_state(lp, candidate_id="AAA", to_state="REJECTED", reason="no edge")
    with pytest.raises(ledger.LedgerError):
        ledger.change_state(lp, candidate_id="AAA", to_state="UNDERWRITING", reason="r")
    with pytest.raises(ledger.LedgerError):
        _surface(lp, ticker="AAA")  # re-open through a state change, not a duplicate
    ledger.change_state(lp, candidate_id="AAA", to_state="SURFACED", reason="new filing")
    assert ledger.replay(lp)["AAA"]["state"] == "SURFACED"
    assert len(ledger.replay(lp)["AAA"]["history"]) == 3  # history preserved


# ---- intake / provenance ------------------------------------------------------
@pytest.mark.parametrize("src", ["HUMAN", "SCOUT", "SUE", "NUTSTUFF"])
def test_intake_accepts_each_named_source(lp, src):
    _surface(lp, name=f"Co {src}", source=src)
    assert ledger.replay(lp)[f"CO-{src}"]["source"] == src


def test_other_source_requires_detail_and_bad_source_rejected(lp):
    with pytest.raises(ledger.LedgerError):
        _surface(lp, source="OTHER")
    with pytest.raises(ledger.LedgerError):
        _surface(lp, source="TWITTER")
    _surface(lp, source="OTHER", source_detail="friend at conference")


def test_intake_requires_why_and_question_and_dedupes(lp):
    with pytest.raises(ledger.LedgerError):
        ledger.surface(lp, name="X", source="HUMAN", why_surfaced="", investment_question="q")
    with pytest.raises(ledger.LedgerError):
        ledger.surface(lp, name="X", source="HUMAN", why_surfaced="w", investment_question=" ")
    _surface(lp, ticker="aaa")
    with pytest.raises(ledger.LedgerError):
        _surface(lp, ticker="AAA", source="SCOUT")


def test_no_source_privilege_in_ordering(lp):
    # Same state and date, different sources: order must follow id only.
    for name, src in (("Zeta", "HUMAN"), ("Alpha", "NUTSTUFF"), ("Mid", "SCOUT"), ("Beta", "SUE")):
        _surface(lp, name=name, source=src)
    html = ui.render_board(lp, today=date(2026, 10, 14))
    pos = [html.index(f'id="c-{n}"') for n in ("ALPHA", "BETA", "MID", "ZETA")]
    assert pos == sorted(pos)


def test_source_is_not_read_by_ui_logic():
    src = (PKG / "ui.py").read_text()
    for forbidden in ('c["source"] ==', "sort(key=lambda c: c[\"source\"]", "SOURCES.index"):
        assert forbidden not in src


# ---- integrity ---------------------------------------------------------------
def test_chain_detects_tamper_and_removal(lp):
    _surface(lp, ticker="AAA"); _surface(lp, ticker="BBB")
    ledger.verify_chain(lp)
    lines = lp.read_text().splitlines()
    lp.write_text(lines[0].replace("why", "WHY") + "\n" + lines[1] + "\n")
    with pytest.raises(ledger.LedgerError):
        ledger.verify_chain(lp)
    lp.write_text(lines[1] + "\n")
    with pytest.raises(ledger.LedgerError):
        ledger.verify_chain(lp)


def test_committed_ledger_verifies_and_holds_mcd_rpm_parked():
    ledger.verify_chain()
    cands = ledger.replay()
    for cid, until in (("MCD", "2026-11-04"), ("RPM", "2026-11-09")):
        c = cands[cid]
        assert c["state"] == "PARKED" and c["parked_until"] == until and c["parked_until_verified"]
        assert all(h["backfilled"] for h in c["history"])


def test_seed_refuses_non_empty_and_reproduces_states(lp):
    assert seed.seed(lp) == 7
    with pytest.raises(ledger.LedgerError):
        seed.seed(lp)
    assert {c["state"] for c in ledger.replay(lp).values()} == {"PARKED"}


# ---- UI ---------------------------------------------------------------------
def test_board_answers_the_five_questions_and_flags_due(lp):
    seed.seed(lp)
    _surface(lp, name="New Idea", source="SUE")
    h = ui.render_board(lp, today=date(2026, 11, 5))
    assert "Attention now" in h and "Rejected" in h and "Parked" in h and "Underwriting" in h
    assert "Why it surfaced" in h and "REVISIT DUE" in h and "NEW-IDEA" in h
    assert "2026-11-04" in h and "officially verified" not in h.split("Dated catalysts")[0]
    soon = ui.render_board(lp, today=date(2026, 10, 14))
    assert "revisit in 21d" in soon  # MCD 11-04 from 10-14


def test_price_certification_is_never_certified():
    assert ui.price_certification({})[0] == "UNCERTIFIED"
    assert "BLOCKED" in ui.price_certification({})[1]
    assert ui.price_certification({"TWELVEDATA_API_KEY": "k"})[0] == "UNCERTIFIED"


def test_html_escaping_of_untrusted_intake(lp):
    ledger.surface(lp, name="<script>alert(1)</script>", ticker="XSS", source="OTHER",
                   source_detail="<img src=x onerror=1>", why_surfaced="<b>w</b>", investment_question="q")
    h = ui.render_board(lp) + ui.render_candidate("XSS", lp)
    assert "<script>alert" not in h and "<img src=x" not in h and "&lt;script&gt;" in h


def test_static_render_has_no_forms(lp):
    seed.seed(lp)
    assert "<form" not in ui.render_board(lp, interactive=False)


# ---- boundary: workflow support only ----------------------------------------
def test_package_never_imports_capital_or_control_layer():
    banned = {"capital_decision_facade", "stock_atlas", "live_price_binding", "database", "requests"}
    for f in PKG.glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text())):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                mods = [node.module or ""]
            for m in mods:
                assert m.split(".")[0] not in banned, f"{f.name} imports {m}"


def test_no_capital_vocabulary_actions_in_ui():
    src = (PKG / "ui.py").read_text() + (PKG / "ledger.py").read_text()
    for word in ("INITIATE", "PortfolioAction", "DecisionRecord", "execute(", "subprocess", "place_order"):
        assert word not in src


# ---- server ------------------------------------------------------------------
@pytest.fixture
def server(lp):
    seed.seed(lp)
    ui.Handler.ledger_path = lp
    srv = ThreadingHTTPServer(("127.0.0.1", 0), ui.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield srv.server_address[1], lp
    srv.shutdown()


def _req(port, method, path, body=None, headers=None):
    c = http.client.HTTPConnection("127.0.0.1", port)
    h = {"Host": f"127.0.0.1:{port}", **(headers or {})}
    if body is not None:
        h["Content-Type"] = "application/x-www-form-urlencoded"
    c.request(method, path, urllib.parse.urlencode(body) if body else None, h)
    r = c.getresponse()
    return r.status, r.read().decode(), dict(r.getheaders())


def test_server_board_candidate_and_doc(server):
    port, _ = server
    assert _req(port, "GET", "/")[0] == 200
    assert "Waiting on" in _req(port, "GET", "/c/MCD")[1]
    st, body, _h = _req(port, "GET", "/doc/CYCLE1_MCD_PRE_ATLAS_STANCE_001.md")
    assert st == 200 and "Frozen stance" in body
    assert _req(port, "GET", "/doc/..%2F..%2Frequirements.txt")[0] == 404
    assert _req(port, "GET", "/doc/nonexistent.md")[0] == 404


def test_server_rejects_foreign_host_and_origin(server):
    port, _ = server
    assert _req(port, "GET", "/", headers={"Host": "evil.example"})[0] == 403
    assert _req(port, "POST", "/surface", {"name": "x"}, {"Origin": "http://evil.example"})[0] == 403


def test_server_intake_and_state_flow(server):
    port, lp = server
    st, _b, h = _req(port, "POST", "/surface", {
        "name": "Nut Idea", "ticker": "NUT", "source": "NUTSTUFF", "why_surfaced": "w", "investment_question": "q"})
    assert st == 303 and h["Location"] == "/c/NUT"
    assert ledger.replay(lp)["NUT"]["source"] == "NUTSTUFF"
    st, _b, _h = _req(port, "POST", "/state", {"candidate_id": "NUT", "to_state": "QUICK_TEST", "reason": "r"})
    assert st == 303 and ledger.replay(lp)["NUT"]["state"] == "QUICK_TEST"
    st, body, _h = _req(port, "POST", "/state", {"candidate_id": "NUT", "to_state": "READY_FOR_CAPITAL_COMPARISON", "reason": "r"})
    assert st == 400 and "not an allowed transition" in body
    st, body, _h = _req(port, "POST", "/surface", {"name": "dup", "ticker": "NUT", "source": "SUE",
                                                    "why_surfaced": "w", "investment_question": "q"})
    assert st == 400 and "already tracked" in body
    ledger.verify_chain(lp)


def test_server_binds_loopback_only():
    src = (PKG / "ui.py").read_text()
    assert '("127.0.0.1", port)' in src and '"0.0.0.0"' not in src
