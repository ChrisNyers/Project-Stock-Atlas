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


def _to_underwriting(lp, cid, result="SURVIVED"):
    ledger.change_state(lp, candidate_id=cid, to_state="QUICK_TEST", reason="r")
    ledger.record_falsification(lp, candidate_id=cid, test="t", result=result, grade="PRIMARY")
    ledger.change_state(lp, candidate_id=cid, to_state="UNDERWRITING", reason="r")


def test_surfaced_start_and_allowed_path(lp):
    _surface(lp, ticker="AAA")
    assert ledger.replay(lp)["AAA"]["state"] == "SURFACED"
    _to_underwriting(lp, "AAA")
    assert ledger.replay(lp)["AAA"]["state"] == "UNDERWRITING"
    ledger.change_state(lp, candidate_id="AAA", to_state="READY_FOR_CAPITAL_COMPARISON", reason="r")
    assert ledger.replay(lp)["AAA"]["state"] == "READY_FOR_CAPITAL_COMPARISON"


def test_disallowed_transitions(lp):
    _surface(lp, ticker="AAA")
    with pytest.raises(ledger.LedgerError):  # cannot skip to READY
        ledger.change_state(lp, candidate_id="AAA", to_state="READY_FOR_CAPITAL_COMPARISON", reason="r")
    _to_underwriting(lp, "AAA")
    with pytest.raises(ledger.LedgerError):  # UNDERWRITING -> UNDERWRITING is a NOTE, not a state change
        ledger.change_state(lp, candidate_id="AAA", to_state="UNDERWRITING", reason="r")
    with pytest.raises(ledger.LedgerError):
        ledger.change_state(lp, candidate_id="AAA", to_state="BUY", reason="r")


def test_continue_underwriting_is_a_note_not_a_state(lp):
    _surface(lp, ticker="AAA")
    _to_underwriting(lp, "AAA")
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
        ledger.change_state(lp, candidate_id="AAA", to_state="QUICK_TEST", reason="r")
    with pytest.raises(ledger.LedgerError):
        _surface(lp, ticker="AAA")  # re-open through a state change, not a duplicate
    ledger.change_state(lp, candidate_id="AAA", to_state="SURFACED", reason="new filing")
    assert ledger.replay(lp)["AAA"]["state"] == "SURFACED"
    assert len(ledger.replay(lp)["AAA"]["history"]) == 3  # history preserved


# ---- intake / provenance ------------------------------------------------------
@pytest.mark.parametrize("src", ["HUMAN", "SCOUT", "SUE", "NUTSTUFF", "LIQN"])
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
    for name, src in (("Zeta", "HUMAN"), ("Alpha", "NUTSTUFF"), ("Mid", "SCOUT"), ("Beta", "SUE"), ("Gamma", "LIQN")):
        _surface(lp, name=name, source=src)
    html = ui.render_board(lp, today=date(2026, 10, 14))
    pos = [html.index(f'id="c-{n}"') for n in ("ALPHA", "BETA", "GAMMA", "MID", "ZETA")]
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
    assert seed.seed(lp) == 7  # history events only; evidence is seeded separately
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


# ---- QUICK_TEST mandatory for new candidates ----------------------------------
def test_new_candidate_cannot_skip_quick_test(lp):
    _surface(lp, ticker="NEW")
    with pytest.raises(ledger.LedgerError, match="QUICK_TEST is mandatory"):
        ledger.change_state(lp, candidate_id="NEW", to_state="UNDERWRITING", reason="r")


def test_new_candidate_cannot_bypass_via_parked(lp):
    _surface(lp, ticker="NEW")
    ledger.change_state(lp, candidate_id="NEW", to_state="PARKED", reason="r", waiting_on="x")
    with pytest.raises(ledger.LedgerError, match="QUICK_TEST is mandatory"):
        ledger.change_state(lp, candidate_id="NEW", to_state="UNDERWRITING", reason="r")


def test_quick_test_state_alone_is_not_enough(lp):
    _surface(lp, ticker="NEW")
    ledger.change_state(lp, candidate_id="NEW", to_state="QUICK_TEST", reason="r")
    with pytest.raises(ledger.LedgerError, match="falsification"):
        ledger.change_state(lp, candidate_id="NEW", to_state="UNDERWRITING", reason="r")


def test_falsified_blocks_underwriting_but_inconclusive_and_survived_pass(lp):
    _surface(lp, ticker="DEAD")
    with pytest.raises(ledger.LedgerError):  # cannot record before QUICK_TEST
        ledger.record_falsification(lp, candidate_id="DEAD", test="t", result="SURVIVED", grade="PRIMARY")
    ledger.change_state(lp, candidate_id="DEAD", to_state="QUICK_TEST", reason="r")
    ledger.record_falsification(lp, candidate_id="DEAD", test="t", result="FALSIFIED", grade="PRIMARY")
    with pytest.raises(ledger.LedgerError, match="FALSIFIED"):
        ledger.change_state(lp, candidate_id="DEAD", to_state="UNDERWRITING", reason="r")
    ledger.change_state(lp, candidate_id="DEAD", to_state="REJECTED", reason="killed by quick test")
    _surface(lp, name="Maybe", ticker="MAYBE")
    _to_underwriting(lp, "MAYBE", result="INCONCLUSIVE")
    assert ledger.replay(lp)["MAYBE"]["state"] == "UNDERWRITING"


def test_retracting_the_only_falsification_reblocks(lp):
    _surface(lp, ticker="NEW")
    ledger.change_state(lp, candidate_id="NEW", to_state="QUICK_TEST", reason="r")
    f = ledger.record_falsification(lp, candidate_id="NEW", test="t", result="SURVIVED", grade="PRIMARY")
    ledger.resolve_item(lp, candidate_id="NEW", target_seq=f["seq"], status="RETRACTED", note="wrong date")
    with pytest.raises(ledger.LedgerError):
        ledger.change_state(lp, candidate_id="NEW", to_state="UNDERWRITING", reason="r")


def test_grandfathered_history_is_preserved_in_committed_ledger():
    events = ledger.read_events()
    assert events[6]["event_hash"] == "c87cb6c6ce3e5aee339583e3813bc0d4f758cfa1b7991c7f76e99d55293ecc37"  # the original 7 events are byte-for-byte unchanged
    for cid in ("MCD", "RPM"):
        c = ledger.replay()[cid]
        states = [h["summary"] for h in c["history"] if h["type"] in ("SURFACED", "STATE_CHANGE")]
        assert states == ["SURFACED", "UNDERWRITING", "PARKED"] and c["grandfathered"]


def test_only_mcd_rpm_are_grandfathered(lp):
    assert ledger.GRANDFATHERED == {"MCD", "RPM"}
    seed.seed(lp)
    _surface(lp, ticker="ZZZ")
    assert not ledger.replay(lp)["ZZZ"]["grandfathered"]


# ---- evidence ledger ---------------------------------------------------------
def _ev(lp, cid, **kw):
    base = dict(candidate_id=cid, tag="FACT", direction="FOR", grade="PRIMARY", text="t")
    return ledger.add_evidence(lp, **{**base, **kw})


def test_evidence_requires_valid_tag_grade_direction_text(lp):
    _surface(lp, ticker="AAA")
    for bad in ({"tag": "OPINION"}, {"grade": "TRUSTED"}, {"direction": "UP"}, {"text": " "}, {"known_at": "yesterday"}):
        with pytest.raises(ledger.LedgerError):
            _ev(lp, "AAA", **bad)
    e = _ev(lp, "AAA", source_ref="10-K FY2025", known_at="2026-02-24")
    item = ledger.replay(lp)["AAA"]["evidence"][0]
    assert item["seq"] == e["seq"] and item["grade"] == "PRIMARY" and item["known_at"] == "2026-02-24"


def test_evidence_reference_and_date_are_optional_but_visible(lp):
    _surface(lp, ticker="AAA")
    _ev(lp, "AAA", grade="UNCERTIFIED")
    assert "no reference" in ui.render_candidate("AAA", lp)


def test_strongest_is_human_designated_and_never_computed(lp):
    _surface(lp, ticker="AAA")
    h = ui.render_candidate("AAA", lp)
    assert h.count("not designated") >= 2
    _ev(lp, "AAA", direction="FOR"); a = _ev(lp, "AAA", direction="AGAINST")
    assert ledger.replay(lp)["AAA"]["strongest"] == {}  # adding evidence designates nothing
    with pytest.raises(ledger.LedgerError):
        ledger.set_strongest(lp, candidate_id="AAA", direction="FOR", target_seq=a["seq"])  # wrong direction
    ledger.set_strongest(lp, candidate_id="AAA", direction="AGAINST", target_seq=a["seq"])
    assert "★ strongest AGAINST" in ui.render_candidate("AAA", lp)


def test_retraction_keeps_history_and_clears_strongest_display(lp):
    _surface(lp, ticker="AAA")
    a = _ev(lp, "AAA", direction="AGAINST", text="wrong date item")
    ledger.set_strongest(lp, candidate_id="AAA", direction="AGAINST", target_seq=a["seq"])
    ledger.resolve_item(lp, candidate_id="AAA", target_seq=a["seq"], status="RETRACTED", note="date was unverified")
    c = ledger.replay(lp)["AAA"]
    assert c["evidence"][0]["status"] == "RETRACTED" and len(c["history"]) == 4
    h = ui.render_candidate("AAA", lp)
    assert "RETRACTED" in h and "★ strongest AGAINST" not in h
    with pytest.raises(ledger.LedgerError):
        ledger.resolve_item(lp, candidate_id="AAA", target_seq=a["seq"], status="RETRACTED", note="again")
    with pytest.raises(ledger.LedgerError):
        ledger.set_strongest(lp, candidate_id="AAA", direction="AGAINST", target_seq=a["seq"])


def test_unresolved_open_resolve_and_evidence_cannot_be_resolved(lp):
    _surface(lp, ticker="AAA")
    u = ledger.add_unresolved(lp, candidate_id="AAA", question="what is the backlog?")
    e = _ev(lp, "AAA")
    with pytest.raises(ledger.LedgerError):
        ledger.resolve_item(lp, candidate_id="AAA", target_seq=e["seq"], status="RESOLVED", note="n")
    with pytest.raises(ledger.LedgerError):
        ledger.resolve_item(lp, candidate_id="AAA", target_seq=u["seq"], status="RESOLVED", note="")
    ledger.resolve_item(lp, candidate_id="AAA", target_seq=u["seq"], status="RESOLVED", note="Q3 call: 1.2 book-to-bill")
    assert ledger.replay(lp)["AAA"]["unresolved"][0]["status"] == "RESOLVED"


def test_cannot_touch_another_candidates_items(lp):
    _surface(lp, ticker="AAA"); _surface(lp, name="Bee", ticker="BBB")
    e = _ev(lp, "AAA")
    with pytest.raises(ledger.LedgerError):
        ledger.resolve_item(lp, candidate_id="BBB", target_seq=e["seq"], status="RETRACTED", note="n")


def test_seed_evidence_appends_only_and_is_complete(lp):
    seed.seed(lp)
    before = ledger.read_events(lp)
    n = seed.seed_evidence(lp)
    after = ledger.read_events(lp)
    assert after[:len(before)] == before and len(after) == len(before) + n
    ledger.verify_chain(lp)
    with pytest.raises(ledger.LedgerError):
        seed.seed_evidence(lp)
    for cid in ("MCD", "RPM"):
        c = ledger.replay(lp)[cid]
        assert {i["tag"] for i in c["evidence"]} == set(ledger.EVIDENCE_TAGS)
        assert all(i["grade"] in ledger.GRADES and i["backfilled"] for i in c["evidence"])
        assert set(c["strongest"]) == {"FOR", "AGAINST"} and c["unresolved"]
        assert c["state"] == "PARKED"  # state untouched by evidence


def test_committed_ledger_has_seeded_template_for_mcd_and_rpm():
    ledger.verify_chain()
    for cid in ("MCD", "RPM"):
        c = ledger.replay()[cid]
        assert len(c["evidence"]) >= 7 and set(c["strongest"]) == {"FOR", "AGAINST"}
    assert ledger.replay()["MCD"]["falsifications"][0]["result"] == "SURVIVED"
    assert ledger.replay()["RPM"]["falsifications"] == []  # no quick test was run; not invented


# ---- candidate page ----------------------------------------------------------
def test_candidate_page_shows_template_glance_and_placeholders():
    h = ui.render_candidate("MCD", today=date(2026, 10, 14))
    for needle in ("Why it surfaced", "Survived QUICK_TEST?", "Strongest evidence FOR", "Strongest evidence AGAINST",
                   "Unresolved question", "Current state", "Next dated catalyst", "2026-11-04", "officially verified",
                   "Investment question", "Cheapest falsification and result", "MANAGEMENT CLAIM", "CAPITAL IMPLICATION",
                   "PRIMARY", "UNCERTIFIED", "SECONDARY", "SPY", "Treasury / Cash", "Do Nothing",
                   "Relevant existing holdings", "placeholders only", "grandfathered"):
        assert needle in h, needle
    r = ui.render_candidate("RPM", today=date(2026, 10, 14))
    assert "No QUICK_TEST recorded" in r and "2026-11-09" in r


def test_placeholders_invoke_nothing_and_page_has_no_stage7_action():
    h = ui.render_candidate("MCD")
    assert 'action="/stage7' not in h and "capital_decision" not in h
    src = (PKG / "ui.py").read_text()
    for word in ("stage7_status", "run_stage7", "compare_capital"):
        assert word not in src


def test_candidate_page_escapes_evidence_text(lp):
    _surface(lp, ticker="AAA")
    _ev(lp, "AAA", text="<script>x()</script>", source_ref="<img src=y>")
    ledger.add_unresolved(lp, candidate_id="AAA", question="<b>q</b>")
    h = ui.render_candidate("AAA", lp)
    assert "<script>x" not in h and "<img src=y" not in h and "<b>q</b>" not in h


def test_server_template_flow_and_quick_test_gate(server):
    port, lp = server
    _req(port, "POST", "/surface", {"name": "Gate", "ticker": "GATE", "source": "SCOUT", "why_surfaced": "w", "investment_question": "q"})
    st, body, _h = _req(port, "POST", "/state", {"candidate_id": "GATE", "to_state": "UNDERWRITING", "reason": "r"})
    assert st == 400 and "not an allowed transition" in body or "QUICK_TEST is mandatory" in body
    _req(port, "POST", "/state", {"candidate_id": "GATE", "to_state": "QUICK_TEST", "reason": "r"})
    st, _b, _h = _req(port, "POST", "/falsify", {"candidate_id": "GATE", "test": "t", "result": "SURVIVED", "grade": "PRIMARY"})
    assert st == 303
    st, _b, _h = _req(port, "POST", "/evidence", {"candidate_id": "GATE", "tag": "FACT", "direction": "FOR", "grade": "PRIMARY",
                                                   "text": "x", "source_ref": "10-K", "known_at": "2026-01-01"})
    assert st == 303
    seq = ledger.replay(lp)["GATE"]["evidence"][0]["seq"]
    assert _req(port, "POST", "/strongest", {"candidate_id": "GATE", "direction": "FOR", "target_seq": str(seq)})[0] == 303
    assert _req(port, "POST", "/unresolved", {"candidate_id": "GATE", "question": "open?"})[0] == 303
    assert _req(port, "POST", "/state", {"candidate_id": "GATE", "to_state": "UNDERWRITING", "reason": "r"})[0] == 303
    assert _req(port, "POST", "/resolve", {"candidate_id": "GATE", "target_seq": "abc", "status": "RESOLVED", "note": "n"})[0] == 400
    ledger.verify_chain(lp)


# ---- LIQN: a named source, with no privilege -----------------------------------
def test_liqn_is_a_named_source_and_in_ui_and_cli_choices(lp):
    assert "LIQN" in ledger.SOURCES
    _surface(lp, name="Liqn Idea", ticker="LQ1", source="LIQN")  # no source_detail needed (only OTHER needs it)
    assert ledger.replay(lp)["LQ1"]["source"] == "LIQN"
    assert "<option>LIQN</option>" in ui.render_board(lp)


@pytest.mark.parametrize("src", ledger.SOURCES)
def test_every_source_faces_identical_quick_test_and_falsification_gates(lp, src):
    detail = {"source_detail": "x"} if src == "OTHER" else {}
    _surface(lp, name="Gate Co", ticker="GC", source=src, **detail)
    c = ledger.replay(lp)["GC"]
    assert not c["grandfathered"] and c["state"] == "SURFACED"
    with pytest.raises(ledger.LedgerError, match="QUICK_TEST is mandatory"):  # no direct skip
        ledger.change_state(lp, candidate_id="GC", to_state="UNDERWRITING", reason="r")
    with pytest.raises(ledger.LedgerError):  # falsification cannot precede QUICK_TEST
        ledger.record_falsification(lp, candidate_id="GC", test="t", result="SURVIVED", grade="PRIMARY")
    ledger.change_state(lp, candidate_id="GC", to_state="QUICK_TEST", reason="r")
    with pytest.raises(ledger.LedgerError, match="falsification"):  # QUICK_TEST alone is not enough
        ledger.change_state(lp, candidate_id="GC", to_state="UNDERWRITING", reason="r")
    ledger.record_falsification(lp, candidate_id="GC", test="t", result="FALSIFIED", grade="PRIMARY")
    with pytest.raises(ledger.LedgerError, match="FALSIFIED"):
        ledger.change_state(lp, candidate_id="GC", to_state="UNDERWRITING", reason="r")
    ledger.record_falsification(lp, candidate_id="GC", test="t2", result="SURVIVED", grade="PRIMARY")
    ledger.change_state(lp, candidate_id="GC", to_state="UNDERWRITING", reason="r")
    assert ledger.replay(lp)["GC"]["state"] == "UNDERWRITING"


@pytest.mark.parametrize("src", ledger.SOURCES)
def test_every_source_faces_identical_evidence_rules(lp, src):
    detail = {"source_detail": "x"} if src == "OTHER" else {}
    _surface(lp, name="Ev Co", ticker="EV", source=src, **detail)
    for bad in ({"tag": "SOURCE_SAYS_SO"}, {"grade": "TRUSTED_SOURCE"}, {"text": ""}):
        with pytest.raises(ledger.LedgerError):
            _ev(lp, "EV", **bad)
    e = _ev(lp, "EV", direction="FOR")
    assert ledger.replay(lp)["EV"]["strongest"] == {}  # source does not designate strongest evidence
    with pytest.raises(ledger.LedgerError):
        ledger.set_strongest(lp, candidate_id="EV", direction="AGAINST", target_seq=e["seq"])


def test_liqn_confers_no_grandfathering_and_no_ordering_in_logic():
    assert "LIQN" not in ledger.GRANDFATHERED
    for f in ("ui.py", "ledger.py"):
        src = (PKG / f).read_text()
        assert '== "LIQN"' not in src and "'LIQN'" not in src
        assert src.count('"LIQN"') <= 1  # only the vocabulary tuple names it
