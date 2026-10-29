"""The two server-side capital entry points (Stage 7 ``run`` and funded Stage 8 ``record_stage8``) decide on the candidate status the AUTHORITY REGISTER
approves, not on the raw candidate ledger. An unapproved promotion never opens capital comparison; an unapproved change of any kind closes it until the
register and the ledger agree. Real facade / DecisionStore / Gate B code; FIXTURE provider; paper only; no repository record is touched.

Every refused path asserts: nothing written (decision ledger byte-identical, zero rows, no run index entry, no retained artifact).
"""
import ast
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from atlas_ui import app as appmod
from atlas_ui import authority, demo
from atlas_ui.__main__ import build
from atlas_ui.service import Blocked, Rejected, Workspace, read_index
from operating_mvp import ledger

from test_atlas_ui import NOW, good_req, s8

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / authority.REGISTER


@pytest.fixture
def demo_app(tmp_path):
    return build(True, tmp_path / "demo")


@pytest.fixture
def canon_app(tmp_path, monkeypatch):
    monkeypatch.delenv("TWELVEDATA_API_KEY", raising=False)
    (tmp_path / "live").mkdir()
    shutil.copyfile(ledger.DEFAULT_LEDGER, tmp_path / "candidates.jsonl")          # the committed ledger and register are never touched
    shutil.copyfile(REG, tmp_path / "live" / "authority_register.jsonl")
    return build(False, tmp_path / "live", candidate_ledger=tmp_path / "candidates.jsonl")


def promote(ws, cid="PROMO"):
    """Walk a new candidate to READY through the raw ledger only: the research workflow, with NO register approval."""
    p = ws.candidate_ledger
    ledger.surface(p, name=f"{cid} Co", ticker=cid, source="HUMAN", why_surfaced="w", investment_question="q")
    ledger.change_state(p, candidate_id=cid, to_state="QUICK_TEST", reason="r")
    ledger.record_falsification(p, candidate_id=cid, test="t", result="SURVIVED", grade="PRIMARY")
    ledger.change_state(p, candidate_id=cid, to_state="UNDERWRITING", reason="r")
    ledger.change_state(p, candidate_id=cid, to_state="READY_FOR_CAPITAL_COMPARISON", reason="human: ready")


def snap(app):
    """Everything a refused request must leave exactly as it was."""
    h = hashlib.sha256()
    for f in sorted(p for p in app.ws.root.rglob("*") if p.is_file()):
        h.update(f.relative_to(app.ws.root).as_posix().encode() + f.read_bytes())
    return h.hexdigest()


def decision_bytes(app) -> bytes:
    p = Path(app.ws.facade.store.path)
    return p.read_bytes() if p.exists() else b""


def refused_stage7(app, **over):
    before, rows = snap(app), len(app.svc.ledger_rows())
    with pytest.raises(Blocked) as exc:
        app.svc.run(good_req(candidate_id="PROMO", ticker="PROMO", cand="PROMO", **over), NOW)
    assert snap(app) == before and read_index(app.ws.index_path) == [] and len(app.svc.ledger_rows()) == rows == 0
    return str(exc.value)


# ---------------------------------------------------------------------------------------------------------------- unapproved READY is blocked
def test_an_unapproved_ready_promotion_cannot_start_stage_7(demo_app):
    promote(demo_app.ws)
    assert ledger.replay(demo_app.ws.candidate_ledger)["PROMO"]["state"] == "READY_FOR_CAPITAL_COMPARISON"        # the raw ledger says READY ...
    msg = refused_stage7(demo_app)                                                                                  # ... the gate does not follow it
    assert "NOT approved in the authority register" in msg and "SURFACED" in msg and "READY_FOR_CAPITAL_COMPARISON" in msg


def test_the_views_do_not_offer_or_describe_an_unapproved_ready_candidate_as_ready(demo_app):
    promote(demo_app.ws)
    page = appmod.stage7_page(demo_app)
    options = page.split('name="cand"')[1].split("</select>")[0]
    assert 'value="PROMO"' not in options and 'value="DEMOCO"' in options                                                                                # the approved READY candidate is still offered
    cp = appmod.candidate_page(demo_app, "PROMO")
    assert "Not ready" in cp and "NOT approved in the authority register" in cp and "READY — a human marked" not in cp


def test_an_approved_promotion_works_for_stage_7_and_a_funded_paper_decision(demo_app, approve_pending):
    promote(demo_app.ws)
    approve_pending(demo_app.ws)
    assert demo_app.ws.candidates()["PROMO"]["state"] == "READY_FOR_CAPITAL_COMPARISON"
    e = demo_app.svc.run(good_req(candidate_id="PROMO", ticker="PROMO", cand="PROMO"), NOW)
    assert e["status"] == "ELIGIBLE FOR STAGE 8" and e["candidate_id"] == "PROMO"
    out = demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert out["rows_after"] == 1
    assert 'value="PROMO"' in appmod.stage7_page(demo_app)


def test_a_funded_decision_is_refused_when_the_ready_status_is_not_approved(demo_app, approve_pending):
    promote(demo_app.ws)
    approve_pending(demo_app.ws)
    e = demo_app.svc.run(good_req(candidate_id="PROMO", ticker="PROMO", cand="PROMO"), NOW)          # legitimately READY at run time
    p = demo_app.ws.candidate_ledger
    ledger.change_state(p, candidate_id="PROMO", to_state="UNDERWRITING", reason="human: more work")
    approve_pending(demo_app.ws)                                                                     # approved: PROMO is back in UNDERWRITING
    ledger.change_state(p, candidate_id="PROMO", to_state="READY_FOR_CAPITAL_COMPARISON", reason="re-promoted")   # NOT approved
    before, idx = decision_bytes(demo_app), read_index(demo_app.ws.index_path)
    with pytest.raises(Rejected, match=r"NOT approved in the authority register") as exc:
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert "UNDERWRITING" in str(exc.value) and exc.value.rows_before == exc.value.rows_after == 0
    assert decision_bytes(demo_app) == before and read_index(demo_app.ws.index_path) == idx and demo_app.svc.ledger_rows() == []
    approve_pending(demo_app.ws)                                                                     # the human approves the re-promotion: the same request now works
    assert demo_app.svc.record_stage8(e["run_id"], s8(), NOW)["rows_after"] == 1


def test_an_unapproved_change_of_any_kind_closes_the_funded_gate_but_not_a_non_funded_action(demo_app):
    e = demo_app.svc.run(good_req(), NOW)
    ledger.change_state(demo_app.ws.candidate_ledger, candidate_id="DEMOCO", to_state="PARKED", reason="new fact", waiting_on="Q3 call",
                        parked_until="2026-12-01", parked_until_verified=True)                     # unapproved restriction
    before = decision_bytes(demo_app)
    with pytest.raises(Rejected, match="PARKED"):
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert decision_bytes(demo_app) == before
    assert demo_app.svc.record_stage8(e["run_id"], s8(action="HOLD CASH"), NOW)["rows_after"] == 1      # HOLD CASH / DO NOTHING stay recordable


# ---------------------------------------------------------------------------------------------------------------- fail closed when authority is unreadable
@pytest.mark.parametrize("damage", ["missing", "tampered", "ledger_chain_broken"])
def test_unresolvable_authority_records_close_both_gates_with_zero_writes(demo_app, approve_pending, damage):
    promote(demo_app.ws)
    approve_pending(demo_app.ws)
    e = demo_app.svc.run(good_req(candidate_id="PROMO", ticker="PROMO", cand="PROMO"), NOW)
    ws = demo_app.ws
    if damage == "missing":
        ws.register.unlink()
    elif damage == "tampered":
        ws.register.write_text(ws.register.read_text().replace("PROMO", "PROMX", 1) if "PROMO" in ws.register.read_text() else ws.register.read_text().replace("DEMO", "DEMX", 1))
    else:
        ws.candidate_ledger.write_text(ws.candidate_ledger.read_text().replace('"MCD"', '"MCX"', 1))
    before, idx = decision_bytes(demo_app), read_index(ws.index_path)
    with pytest.raises(Rejected, match="did not resolve") as exc:
        demo_app.svc.record_stage8(e["run_id"], s8(), NOW)
    assert exc.value.rows_before == exc.value.rows_after == 0 and decision_bytes(demo_app) == before
    with pytest.raises(Blocked, match="did not resolve"):
        demo_app.svc.run(good_req(candidate_id="PROMO", ticker="PROMO", cand="PROMO"), NOW)
    assert read_index(ws.index_path) == idx and demo_app.svc.ledger_rows() == []
    if damage != "ledger_chain_broken":          # (the candidate page itself replays the raw ledger for display; a broken chain is already an error there)
        assert "Not ready" in appmod.candidate_page(demo_app, "DEMOCO") and "did not resolve" in appmod.candidate_page(demo_app, "DEMOCO")


# ---------------------------------------------------------------------------------------------------------------- existing restrictions intact
def test_mcd_and_rpm_restrictions_still_block_stage_7_exactly(canon_app):
    for cid, until in (("MCD", "2026-11-04"), ("RPM", "2026-11-09")):
        with pytest.raises(Blocked, match=f"{cid} is PARKED until {until}"):
            canon_app.svc.run(good_req(candidate_id=cid, ticker=cid, cand=cid), NOW)
    assert read_index(canon_app.ws.index_path) == [] and canon_app.svc.ledger_rows() == [] and not list(canon_app.ws.facade.artifact_dir.glob("*"))


def test_a_reached_revisit_date_is_a_flag_and_never_opens_the_gate(canon_app, monkeypatch):
    class Later(date):
        @classmethod
        def today(cls):
            return cls(2027, 1, 1)

    monkeypatch.setattr(authority, "date", Later)
    c = canon_app.ws.candidates()["MCD"]
    assert c["revisit_due"] is True and c["state"] == "PARKED"
    with pytest.raises(Blocked, match="MCD is PARKED until 2026-11-04"):
        canon_app.svc.run(good_req(candidate_id="MCD", ticker="MCD", cand="MCD"), NOW)
    cp = appmod.candidate_page(canon_app, "MCD")
    assert "Revisit date reached: a trigger to reassess, not a promotion" in cp and "MCD" in cp
    assert canon_app.svc.ledger_rows() == []


def test_unparking_mcd_in_the_ledger_without_approval_changes_nothing_at_the_gate(canon_app, approve_pending):
    ledger.change_state(canon_app.ws.candidate_ledger, candidate_id="MCD", to_state="UNDERWRITING", reason="human: nudge")
    with pytest.raises(Blocked, match=r"MCD is PARKED until 2026-11-04; ledger status change\(s\) .* NOT approved"):
        canon_app.svc.run(good_req(candidate_id="MCD", ticker="MCD", cand="MCD"), NOW)
    approve_pending(canon_app.ws)                                                                 # approved: MCD is UNDERWRITING, still not READY
    with pytest.raises(Blocked, match="MCD is UNDERWRITING"):
        canon_app.svc.run(good_req(candidate_id="MCD", ticker="MCD", cand="MCD"), NOW)
    assert canon_app.svc.ledger_rows() == [] and read_index(canon_app.ws.index_path) == []


# ---------------------------------------------------------------------------------------------------------------- demo mode and the repository records
def test_demo_mode_runs_through_the_same_resolver_with_its_own_fixture_register(demo_app, tmp_path):
    reg_before = REG.read_bytes()
    assert demo_app.ws.register == demo_app.ws.root / "authority_register.jsonl" and demo_app.ws.register.is_file()
    ev = authority.read_register(demo_app.ws.register)
    assert len(ev) == 1 and ev[0]["type"] == "LEDGER_ACCEPTED_THROUGH" and "not a real approval" in ev[0]["approval"]["quote"]
    e = demo_app.svc.run(good_req(), NOW)
    assert e["status"] == "ELIGIBLE FOR STAGE 8" and e["mode"] == "DEMO"
    assert REG.read_bytes() == reg_before                                                          # demo never writes the repository's register


def test_the_shared_canonical_ledger_is_governed_by_the_repository_register(tmp_path):
    ws = Workspace(tmp_path / "w", "CANONICAL", candidate_ledger=ledger.DEFAULT_LEDGER)
    assert ws.register.resolve() == REG.resolve()
    other = Workspace(tmp_path / "x", "CANONICAL", candidate_ledger=tmp_path / "copy.jsonl")
    assert other.register == tmp_path / "x" / "authority_register.jsonl"                           # a different ledger never borrows the repository's approvals


def test_services_never_read_the_raw_ledger_for_a_capital_decision_and_never_write_the_register():
    svc = (ROOT / "atlas_ui/service.py").read_text()
    assert "ledger.replay(" not in svc and svc.count("self.ws.candidates()") == 2 and svc.count("capital_gate(") >= 3
    for f in ("service.py", "app.py", "canonical.py", "__main__.py"):                               # only the CLI (verify.py) and the DEMO fixture seed write a register
        text = (ROOT / "atlas_ui" / f).read_text()
        assert "authority.append" not in text and "accept_ledger_tail" not in text, f
