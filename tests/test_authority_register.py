"""Dynamic authority: the latest HUMAN-APPROVED records govern, nothing operating-level is hardcoded, history stays reconstructable, conflicts fail closed,
and a failed preflight can never produce a successful delivery.

Acceptance scenarios (isolated temp records unless a test says it runs on a copy of the repository; the real register is never touched):
  1 a new approved portfolio snapshot supersedes the earlier one without altering historical evidence
  2 a candidate's approved status change is followed by the current-state resolver
  3 an expired revisit trigger does not promote a candidate
  4 an unapproved newer record cannot supersede the approved record
  5 conflicting authority records fail closed
  6 a failed preflight prevents a successful delivery
"""
import ast
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from atlas_ui import authority, canonical, verify
from operating_mvp import ledger as L
from test_authority import GIT_ENV, ROOT, approve_state, commit, git_init, status, tree  # noqa: F401  (tree is a fixture)

HUMAN = {"by": "HUMAN", "date": "2026-10-29", "record": "Decision Log: TEST_APPROVAL", "quote": "I approve this record."}
REG = authority.REGISTER


# ---------------------------------------------------------------------------------------------------------------- isolated records
def snapshot_doc(path: Path, rows: dict[str, str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# test snapshot\n\n## Holdings\n\n| Ticker | Value |\n|---|---|\n" + "".join(f"| {t} | ${v} |\n" for t, v in rows.items()))


def spec(root: Path, doc: str, sid: str, as_of: str, supersedes=None, rows=None):
    raw = (root / doc).read_bytes()
    total = sum(Decimal(v.replace(",", "")) for v in (rows or {}).values())
    return {"snapshot_id": sid, "doc": doc, "doc_sha256": hashlib.sha256(raw).hexdigest(), "table_marker": "## Holdings", "as_of": as_of,
            "holdings": len(rows), "stocks_total": str(total), "defensive_approx": "1000", "supersedes": supersedes}


@pytest.fixture
def iso(tmp_path):
    root = tmp_path / "iso"
    (root / "docs").mkdir(parents=True)
    (root / "docs/STOCK_ATLAS_DECISION_LOG.md").write_text("# log\n\n## TEST_APPROVAL\n\nthe human approved.\n")
    return root


def put(root: Path, type_, payload, approval=HUMAN):
    return authority.append(root / REG, type_, payload, approval=approval, check_record=(lambda r: authority.record_exists(root, r)) if approval else None)


A_ROWS = {"AAA": "6,000.00", "BBB": "4,000.00"}
B_ROWS = {"AAA": "5,000.00", "BBB": "4,000.00", "CCC": "3,000.00"}


def two_snapshots(root: Path):
    snapshot_doc(root / "docs/snap_a.md", A_ROWS)
    snapshot_doc(root / "docs/snap_b.md", B_ROWS)
    return spec(root, "docs/snap_a.md", "SNAP-A", "2026-01-01", None, A_ROWS), spec(root, "docs/snap_b.md", "SNAP-B", "2026-06-01", "SNAP-A", B_ROWS)


def candidate_ledger(root: Path, *, parked_until="2026-03-01") -> Path:
    led = root / "candidate_ledger.jsonl"
    L.surface(led, name="Xco", ticker="XCO", source="HUMAN", why_surfaced="w", investment_question="q", effective_date="2026-01-02")
    L.change_state(led, candidate_id="XCO", to_state="QUICK_TEST", reason="start", effective_date="2026-01-03")
    L.record_falsification(led, candidate_id="XCO", test="t", result="SURVIVED", grade="PRIMARY", effective_date="2026-01-04")
    L.change_state(led, candidate_id="XCO", to_state="UNDERWRITING", reason="go", effective_date="2026-01-05")
    L.change_state(led, candidate_id="XCO", to_state="PARKED", reason="wait", waiting_on="the 10-K", parked_until=parked_until, effective_date="2026-01-06")
    return led


def accept_ledger(root: Path, led: Path):
    last = L.read_events(led)[-1]
    put(root, "LEDGER_ACCEPTED_THROUGH", {"through_seq": last["seq"], "through_event_hash": last["event_hash"]})


# ---------------------------------------------------------------------------------------------------------------- 1 snapshots
def test_1_a_new_approved_snapshot_supersedes_the_earlier_one_without_altering_history(iso):
    a, b = two_snapshots(iso)
    put(iso, "PORTFOLIO_SNAPSHOT", a)
    assert canonical.current_portfolio(iso).snapshot_id == "SNAP-A"
    a_doc, a_line = (iso / a["doc"]).read_bytes(), (iso / REG).read_text().splitlines()[0]
    put(iso, "PORTFOLIO_SNAPSHOT", b)                                                    # data only: no software change
    now = canonical.current_portfolio(iso)
    assert (now.snapshot_id, now.as_of, len(now.holdings), now.stocks_total) == ("SNAP-B", "2026-06-01", 3, Decimal("12000.00"))
    assert (iso / a["doc"]).read_bytes() == a_doc and (iso / REG).read_text().splitlines()[0] == a_line     # history untouched, byte for byte
    past = canonical.portfolio_as_of("2026-03-15", iso)                                  # a past analysis is reconstructable
    assert (past.snapshot_id, len(past.holdings), past.stocks_total) == ("SNAP-A", 2, Decimal("10000.00"))
    assert canonical.portfolio_as_of("2026-06-01", iso).snapshot_id == "SNAP-B"
    with pytest.raises(canonical.CanonicalError, match="in force"):
        canonical.portfolio_as_of("2025-12-31", iso)
    assert [s["snapshot_id"] for s in authority.resolve(iso / REG).snapshots] == ["SNAP-A", "SNAP-B"]
    assert canonical.build_portfolio_snapshot(now, as_of=now.effective_at).snapshot_id == "SNAP-B"      # the id a Stage 7 artifact will name


def test_1b_on_the_repository_a_new_snapshot_is_followed_and_the_cycle0_record_is_untouched(tree):
    before = (tree / "docs/controlled_live_pilot/CYCLE0_BASELINE_001.md").read_bytes()
    snapshot_doc(tree / "docs/PORTFOLIO_SNAPSHOT_NEXT.md", {"AAPL": "10,000.00", "MSFT": "5,000.00"})
    nxt = spec(tree, "docs/PORTFOLIO_SNAPSHOT_NEXT.md", "SNAP-2026-11", "2026-11-02", "CYCLE0-ef35534d5e04", {"AAPL": "10,000.00", "MSFT": "5,000.00"})
    put(tree, "PORTFOLIO_SNAPSHOT", nxt, {**HUMAN, "record": "Decision Log: SOURCE_OF_TRUTH_AND_PORTABILITY"})
    cur = canonical.current_portfolio(tree)
    assert cur.snapshot_id == "SNAP-2026-11" and cur.weight("AAPL") == pytest.approx(10000 / 16000)
    old = canonical.portfolio_as_of("2026-10-20", tree)
    assert old.portfolio_snapshot_id == "CYCLE0-ef35534d5e04" and len(old.holdings) == 28 and old.stocks_total == Decimal("624905.93")
    assert (tree / "docs/controlled_live_pilot/CYCLE0_BASELINE_001.md").read_bytes() == before
    c = status(verify.preflight(tree, use_git=False), "approved portfolio snapshot")
    assert c.status == "OK" and "SNAP-2026-11" in c.detail and "CYCLE0-ef35534d5e04" in c.detail and "still loadable" in c.detail


def test_1c_the_bootstrap_snapshot_loads_identically_to_the_frozen_cycle0_loader():
    new, old = canonical.current_portfolio(ROOT), canonical.load_cycle0()
    assert (new.holdings, new.stocks_total, new.defensive_approx, new.identified_value, new.as_of, new.doc_path, new.doc_sha256, new.label) == \
           (old.holdings, old.stocks_total, old.defensive_approx, old.identified_value, old.as_of, old.doc_path, old.doc_sha256, old.label)
    assert new.portfolio_snapshot_id == old.portfolio_snapshot_id == f"CYCLE0-{old.doc_sha256[:12]}"     # earlier Stage 7 runs still reconstruct


# ---------------------------------------------------------------------------------------------------------------- 2 candidates
def test_2_a_candidates_approved_status_change_is_followed_and_an_unapproved_one_is_not(iso):
    led = candidate_ledger(iso)
    accept_ledger(iso, led)
    res = authority.resolve(iso / REG)
    c = authority.resolve_candidates(res, led, date(2026, 1, 10))["XCO"]
    assert (c["state"], c["parked_until"], c["pending"]) == ("PARKED", "2026-03-01", [])
    L.change_state(led, candidate_id="XCO", to_state="UNDERWRITING", reason="human re-opened", effective_date="2026-02-01")
    seq = L.read_events(led)[-1]["seq"]
    c = authority.resolve_candidates(res, led, date(2026, 2, 2))["XCO"]
    assert c["state"] == "PARKED" and [p["seq"] for p in c["pending"]] == [seq]            # newer, unapproved: listed, not followed
    assert L.replay(led)["XCO"]["state"] == "UNDERWRITING" and any(h["seq"] == seq for h in c["history"])   # the record of it is kept and visible
    put(iso, "CANDIDATE_STATUS_APPROVED", {"ledger_seq": seq, "ledger_event_hash": L.read_events(led)[-1]["event_hash"]})
    c = authority.resolve_candidates(authority.resolve(iso / REG), led, date(2026, 2, 2))["XCO"]
    assert (c["state"], c["parked_until"], c["pending"], c["state_since"]) == ("UNDERWRITING", "", [], "2026-02-01")   # followed once approved, restriction cleared by data
    assert all(h["type"] != "STATE_CHANGE" or h["seq"] <= seq for h in c["history"])


def test_2b_on_the_repository_an_approved_unpark_is_followed_by_preflight_without_any_code_change(tree):
    led = tree / "operating_mvp/data/candidate_ledger.jsonl"
    L.change_state(led, candidate_id="MCD", to_state="UNDERWRITING", reason="human: evidence arrived", effective_date="2026-11-04")
    ev = L.read_events(led)[-1]
    c = status(verify.preflight(tree, use_git=False), "candidate status awaiting approval")
    assert c.status == "WARN" and "MCD" in c.detail and "still PARKED" in c.detail          # visible, and not yet the authoritative status
    assert "MCD PARKED until 2026-11-04" in status(verify.preflight(tree, use_git=False), "candidate ledger chain").detail
    put(tree, "CANDIDATE_STATUS_APPROVED", {"ledger_seq": ev["seq"], "ledger_event_hash": ev["event_hash"]}, {**HUMAN, "record": "Decision Log: SOURCE_OF_TRUTH_AND_PORTABILITY"})
    cs = verify.preflight(tree, use_git=False)
    d = status(cs, "candidate ledger chain").detail
    assert "MCD" not in d and "RPM PARKED until 2026-11-09" in d and not [x for x in cs if x.status in ("FAIL", "WARN") and "awaiting" in x.name]


# ---------------------------------------------------------------------------------------------------------------- 3 revisit
def test_3_an_expired_revisit_trigger_does_not_promote_a_candidate(iso):
    led = candidate_ledger(iso, parked_until="2026-03-01")
    accept_ledger(iso, led)
    res, before = authority.resolve(iso / REG), led.read_bytes()
    for today in (date(2026, 2, 28), date(2026, 3, 1), date(2026, 9, 1), date(2030, 1, 1)):
        c = authority.resolve_candidates(res, led, today)["XCO"]
        assert c["state"] == "PARKED" and c["state"] != "READY_FOR_CAPITAL_COMPARISON" and c["revisit_due"] is (today >= date(2026, 3, 1))
    assert led.read_bytes() == before                                                     # resolving never writes: no automatic transition
    assert L.replay(led)["XCO"]["state"] == "PARKED"


def test_3b_on_the_repository_a_reached_revisit_date_is_a_flag_not_a_promotion():
    cs = verify.preflight(ROOT, use_git=False, today=date(2027, 1, 1))
    due = [c for c in cs if c.name == "revisit trigger"]
    assert {c.detail.split()[0] for c in due} == {"MCD", "RPM"} and all(c.status == "INFO" and "NOT a promotion" in c.detail and "stays PARKED" in c.detail for c in due)
    assert not [c for c in cs if c.status == "FAIL"]
    res = authority.resolve(ROOT / REG)
    got = authority.resolve_candidates(res, ROOT / "operating_mvp/data/candidate_ledger.jsonl", date(2027, 1, 1))
    assert got["MCD"]["state"] == "PARKED" and got["RPM"]["state"] == "PARKED" and got["GEV"]["state"] == "SURFACED"


# ---------------------------------------------------------------------------------------------------------------- 4 unapproved
@pytest.mark.parametrize("bad", [
    None,
    {"by": "CLAUDE", "date": "2026-10-29", "record": "Decision Log: TEST_APPROVAL", "quote": "q"},
    {"by": "HUMAN", "date": "2026-10-29", "record": "Decision Log: TEST_APPROVAL", "quote": "  "},
    {"by": "HUMAN", "date": "2026-10-29", "record": "", "quote": "q"},
    {"by": "HUMAN", "date": "yesterday", "record": "Decision Log: TEST_APPROVAL", "quote": "q"},
    {"date": "2026-10-29", "record": "Decision Log: TEST_APPROVAL", "quote": "q"},
], ids=["none", "not-human", "blank-quote", "blank-record", "bad-date", "no-by"])
def test_4_an_unapproved_newer_record_cannot_supersede_the_approved_one(iso, bad):
    a, b = two_snapshots(iso)
    put(iso, "PORTFOLIO_SNAPSHOT", a)
    ev = {"seq": 2, "type": "PORTFOLIO_SNAPSHOT", "recorded_on": "2026-10-30", "payload": b, "approval": bad}
    prev = authority.read_register(iso / REG)[-1]["event_hash"]
    ev.update(prev_hash=prev, event_hash=authority._hash(prev, {k: ev[k] for k in ("seq", "type", "recorded_on", "payload", "approval")}))
    with open(iso / REG, "a") as fh:
        fh.write(json.dumps(ev) + "\n")                                                  # written raw: even a hand-appended event with a bad approval is only a draft
    res = authority.resolve(iso / REG)
    assert res.current_snapshot["snapshot_id"] == "SNAP-A" and [d["payload"]["snapshot_id"] for d in res.drafts] == ["SNAP-B"]
    assert canonical.current_portfolio(iso).snapshot_id == "SNAP-A"


def test_4b_drafts_are_recorded_through_the_api_and_never_followed_for_any_family(iso):
    a, b = two_snapshots(iso)
    put(iso, "PORTFOLIO_SNAPSHOT", a)
    put(iso, "APPROVED_STATE", {"commit": "a" * 40, "supersedes": None, "status": "accepted"})
    put(iso, "ACTIVE_WORK", {"work_id": "W1", "supersedes": None, "plan_heading_prefix": "### W1", "summary": "s", "state": "x"})
    put(iso, "PORTFOLIO_SNAPSHOT", b, approval=None)
    put(iso, "APPROVED_STATE", {"commit": "b" * 40, "supersedes": "a" * 40, "status": "newer commit"}, approval=None)
    put(iso, "ACTIVE_WORK", {"work_id": "W2", "supersedes": "W1", "plan_heading_prefix": "### W2", "summary": "s", "state": "y"}, approval=None)
    res = authority.resolve(iso / REG)
    assert (res.current_snapshot["snapshot_id"], res.approved_state["commit"], res.active_work["work_id"]) == ("SNAP-A", "a" * 40, "W1")
    assert len(res.drafts) == 3
    with pytest.raises(authority.AuthorityConflict, match="not an approved record"):       # a draft cannot be the thing a later approved record supersedes
        put(iso, "PORTFOLIO_SNAPSHOT", {**b, "snapshot_id": "SNAP-C", "supersedes": "SNAP-B", "as_of": "2026-08-01"})


def test_4c_on_the_repository_a_draft_snapshot_and_a_draft_approved_state_change_nothing(tree):
    snapshot_doc(tree / "docs/DRAFT_SNAPSHOT.md", {"ZZZ": "1,000.00"})
    put(tree, "PORTFOLIO_SNAPSHOT", spec(tree, "docs/DRAFT_SNAPSHOT.md", "DRAFT-1", "2026-12-01", "CYCLE0-ef35534d5e04", {"ZZZ": "1,000.00"}), approval=None)
    put(tree, "APPROVED_STATE", {"commit": "c" * 40, "supersedes": "8cbcb37c82ac6367415d517f2938cf2d0c50e2d5", "status": "unreviewed HEAD"}, approval=None)
    assert canonical.current_portfolio(tree).snapshot_id == "CYCLE0-ef35534d5e04"
    assert authority.resolve(tree / REG).approved_state["commit"].startswith("8cbcb37")
    cs = verify.preflight(tree, use_git=False)
    assert [c.line() for c in cs if c.status == "FAIL"] == []
    assert len([c for c in cs if c.name == "unapproved record (draft)"]) == 2 and "2 draft(s)" in status(cs, "authority register").detail


def test_4d_a_new_commit_does_not_become_the_approved_state_by_existing(tree):
    git_init(tree)
    (tree / "NEW.txt").write_text("a newer commit nobody approved\n")
    commit(tree, "newer")
    c = status(verify.preflight(tree), "newest commit vs approved state")
    assert c.status == "INFO" and "unapproved" in c.detail and "LATEST APPROVED STATE" in c.detail
    head = subprocess.run(["git", "-C", str(tree), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert authority.resolve(tree / REG).approved_state["commit"] != head


# ---------------------------------------------------------------------------------------------------------------- 5 conflicts
def raw_append(root: Path, type_, payload, approval=HUMAN):
    """Append bypassing append()'s own pre-check, as a hand edit or merge would."""
    evs = authority.read_register(root / REG) if (root / REG).exists() else []
    prev = evs[-1]["event_hash"] if evs else authority.GENESIS
    body = {"seq": len(evs) + 1, "type": type_, "recorded_on": "2026-10-30", "payload": payload, "approval": approval}
    with open(root / REG, "a") as fh:
        fh.write(json.dumps({**body, "prev_hash": prev, "event_hash": authority._hash(prev, body)}) + "\n")


def conflict_cases(root):
    a, b = two_snapshots(root)
    return {
        "fork: two approved records supersede the same one": [("PORTFOLIO_SNAPSHOT", a), ("PORTFOLIO_SNAPSHOT", b), ("PORTFOLIO_SNAPSHOT", {**b, "snapshot_id": "SNAP-B2"})],
        "two roots": [("PORTFOLIO_SNAPSHOT", a), ("PORTFOLIO_SNAPSHOT", {**b, "supersedes": None})],
        "duplicate id": [("PORTFOLIO_SNAPSHOT", a), ("PORTFOLIO_SNAPSHOT", {**a, "supersedes": "SNAP-A"})],
        "unknown predecessor": [("PORTFOLIO_SNAPSHOT", a), ("PORTFOLIO_SNAPSHOT", {**b, "supersedes": "NOPE"})],
        "successor not dated after its predecessor": [("PORTFOLIO_SNAPSHOT", a), ("PORTFOLIO_SNAPSHOT", {**b, "as_of": "2026-01-01"})],
        "two approved states fork": [("APPROVED_STATE", {"commit": "a" * 40, "supersedes": None, "status": "s"}), ("APPROVED_STATE", {"commit": "b" * 40, "supersedes": None, "status": "s"})],
    }


@pytest.mark.parametrize("name", [
    "fork: two approved records supersede the same one", "two roots", "duplicate id", "unknown predecessor",
    "successor not dated after its predecessor", "two approved states fork"])
def test_5_conflicting_approved_records_fail_closed(iso, name):
    for type_, payload in conflict_cases(iso)[name]:
        raw_append(iso, type_, payload)
    with pytest.raises(authority.AuthorityConflict):
        authority.resolve(iso / REG)
    with pytest.raises(canonical.CanonicalError, match="authority register"):             # the app/service path refuses; it does not fall back to an older snapshot
        canonical.current_portfolio(iso)
    with pytest.raises(canonical.CanonicalError):
        canonical.portfolio_as_of("2026-03-01", iso)


def test_5b_append_refuses_an_event_that_would_create_a_conflict_and_writes_nothing(iso):
    a, b = two_snapshots(iso)
    put(iso, "PORTFOLIO_SNAPSHOT", a)
    put(iso, "PORTFOLIO_SNAPSHOT", b)
    before = (iso / REG).read_bytes()
    with pytest.raises(authority.AuthorityConflict):
        put(iso, "PORTFOLIO_SNAPSHOT", {**b, "snapshot_id": "SNAP-B2"})
    assert (iso / REG).read_bytes() == before and not list((iso / "docs").glob("*.check"))


def test_5c_tampered_or_truncated_register_and_edited_snapshot_fail_closed(iso):
    a, b = two_snapshots(iso)
    put(iso, "PORTFOLIO_SNAPSHOT", a)
    put(iso, "PORTFOLIO_SNAPSHOT", b)
    good = (iso / REG).read_text()
    (iso / REG).write_text(good.replace("SNAP-B", "SNAP-X", 1))
    with pytest.raises(authority.AuthorityError, match="integrity"):
        authority.resolve(iso / REG)
    (iso / REG).write_text("\n".join(good.splitlines()[1:]) + "\n")                       # the first approved event deleted
    with pytest.raises(authority.AuthorityError, match="integrity"):
        authority.resolve(iso / REG)
    (iso / REG).write_text(good)
    (iso / "docs/snap_a.md").write_text((iso / "docs/snap_a.md").read_text() + "| DDD | $1.00 |\n")       # historical evidence edited after approval
    with pytest.raises(canonical.CanonicalError, match="edited after approval"):
        canonical.portfolio_as_of("2026-03-01", iso)
    (iso / "docs/snap_b.md").write_text("not a snapshot")
    with pytest.raises(canonical.CanonicalError):
        canonical.current_portfolio(iso)


def test_5d_ledger_acceptance_that_does_not_match_the_ledger_fails_closed(iso):
    led = candidate_ledger(iso)
    last = L.read_events(led)[-1]
    put(iso, "LEDGER_ACCEPTED_THROUGH", {"through_seq": last["seq"], "through_event_hash": "0" * 64})
    with pytest.raises(authority.AuthorityConflict, match="does not contain"):
        authority.resolve_candidates(authority.resolve(iso / REG), led)
    iso2 = iso.parent / "iso2"
    (iso2 / "docs").mkdir(parents=True)
    (iso2 / "docs/STOCK_ATLAS_DECISION_LOG.md").write_text("## TEST_APPROVAL\n")
    led2 = candidate_ledger(iso2)
    note_seq = L.add_note(led2, candidate_id="XCO", text="n")["seq"]
    put(iso2, "CANDIDATE_STATUS_APPROVED", {"ledger_seq": note_seq, "ledger_event_hash": L.read_events(led2)[-1]["event_hash"]})   # approves a NOTE as a status change
    with pytest.raises(authority.AuthorityConflict, match="STATE_CHANGE"):
        authority.resolve_candidates(authority.resolve(iso2 / REG), led2)
    iso3 = iso.parent / "iso3"
    (iso3 / "docs").mkdir(parents=True)
    (iso3 / "docs/STOCK_ATLAS_DECISION_LOG.md").write_text("## TEST_APPROVAL\n")
    led3 = candidate_ledger(iso3)
    sc = [e for e in L.read_events(led3) if e["event_type"] == "STATE_CHANGE"][-1]
    put(iso3, "CANDIDATE_STATUS_APPROVED", {"ledger_seq": sc["seq"], "ledger_event_hash": sc["event_hash"]})
    with pytest.raises(authority.AuthorityConflict, match="two different hashes"):         # refused at write time ...
        put(iso3, "CANDIDATE_STATUS_APPROVED", {"ledger_seq": sc["seq"], "ledger_event_hash": "f" * 64})
    raw_append(iso3, "CANDIDATE_STATUS_APPROVED", {"ledger_seq": sc["seq"], "ledger_event_hash": "f" * 64})
    with pytest.raises(authority.AuthorityConflict, match="two different hashes"):         # ... and when it arrives by hand
        authority.resolve(iso3 / REG)


def test_5e_preflight_and_the_cli_fail_on_a_conflicting_register_and_do_not_pass_dependent_checks(tree):
    snapshot_doc(tree / "docs/S2.md", {"AAA": "1.00"})
    raw_append(tree, "PORTFOLIO_SNAPSHOT", spec(tree, "docs/S2.md", "S2", "2026-12-01", "CYCLE0-ef35534d5e04", {"AAA": "1.00"}))
    raw_append(tree, "PORTFOLIO_SNAPSHOT", {**spec(tree, "docs/S2.md", "S3", "2026-12-02", "CYCLE0-ef35534d5e04", {"AAA": "1.00"})})
    cs = verify.preflight(tree, use_git=False)
    assert status(cs, "authority register").status == "FAIL" and "CONFLICT" in status(cs, "authority register").detail
    assert status(cs, "approved portfolio snapshot").status == "SKIP" and status(cs, "candidate ledger chain").status == "SKIP"
    import os
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST")}
    r = subprocess.run([sys.executable, "-m", "atlas_ui", "preflight"], cwd=tree, env=env, capture_output=True, text=True)
    assert r.returncode == 1 and "PREFLIGHT FAIL" in r.stdout


# ---------------------------------------------------------------------------------------------------------------- nothing operating-level is hardcoded
def test_the_authority_reference_and_the_preflight_hardcode_no_operating_value():
    manifest = json.dumps(verify.load_authority(ROOT))
    src = (ROOT / "atlas_ui/verify.py").read_text()
    for text in (manifest, src):
        for literal in ("2026-10-07", "2026-11-04", "2026-11-09", "624905.93", "683905.93", "8cbcb37", "MCD", "RPM", "CYCLE0", "Cycle 0"):
            assert literal not in text, literal
        assert not re.search(r"\b[0-9a-f]{40}\b", text)                                    # no commit id
    for gone in ("approved_state", "portfolio_baseline", "parked", "canonical_decision_rows", "last_milestone_review", "active_work"):
        assert gone not in verify.load_authority(ROOT)
    assert verify.load_authority(ROOT)["register"] == REG


def test_the_app_and_the_stage7_service_resolve_the_portfolio_through_the_register_only():
    for f in ("app.py", "service.py"):
        tree_ = ast.parse((ROOT / "atlas_ui" / f).read_text())
        calls = {n.func.attr for n in ast.walk(tree_) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        assert "load_cycle0" not in calls and "current_portfolio" in calls, f


def test_normal_updates_need_no_software_change_end_to_end(tree):
    """A new approved snapshot, an approved candidate change and a newly accepted commit: data appended to records, then a clean preflight."""
    git_init(tree)
    snapshot_doc(tree / "docs/NEXT_SNAPSHOT.md", {"AAA": "7,000.00", "BBB": "3,000.00"})
    put(tree, "PORTFOLIO_SNAPSHOT", spec(tree, "docs/NEXT_SNAPSHOT.md", "NEXT", "2026-12-01", "CYCLE0-ef35534d5e04", {"AAA": "7,000.00", "BBB": "3,000.00"}),
        {**HUMAN, "record": "Decision Log: SOURCE_OF_TRUTH_AND_PORTABILITY"})
    led = tree / "operating_mvp/data/candidate_ledger.jsonl"
    L.change_state(led, candidate_id="RPM", to_state="REJECTED", reason="human rejected after the Investor Day", effective_date="2026-11-09")
    ev = L.read_events(led)[-1]
    put(tree, "CANDIDATE_STATUS_APPROVED", {"ledger_seq": ev["seq"], "ledger_event_hash": ev["event_hash"]}, {**HUMAN, "record": "Decision Log: SOURCE_OF_TRUTH_AND_PORTABILITY"})
    commit(tree, "new snapshot, RPM rejected")
    head = subprocess.run(["git", "-C", str(tree), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    approve_state(tree, head)
    commit(tree, "human accepts")
    for cs in (verify.preflight(tree), verify.preflight(tree, use_git=False)):
        assert [c.line() for c in cs if c.status == "FAIL"] == []
        assert "NEXT as of 2026-12-01" in status(cs, "approved portfolio snapshot").detail
        d = status(cs, "candidate ledger chain").detail
        assert "RPM REJECTED" in d and "MCD PARKED until 2026-11-04" in d


def test_the_cli_records_drafts_and_approvals_and_refuses_what_it_cannot_check(iso, tmp_path):
    a, _ = two_snapshots(iso)
    put(iso, "PORTFOLIO_SNAPSHOT", a)
    with pytest.raises(authority.AuthorityError, match="approval must be"):
        authority.append(iso / REG, "ACTIVE_WORK", {"work_id": "W", "plan_heading_prefix": "#", "summary": "s", "state": "s"}, approval={"by": "HUMAN"})
    with pytest.raises(authority.AuthorityError, match="does not resolve"):
        put(iso, "ACTIVE_WORK", {"work_id": "W", "plan_heading_prefix": "#", "summary": "s", "state": "s"}, {**HUMAN, "record": "Decision Log: NO_SUCH_ENTRY"})
    with pytest.raises(authority.AuthorityError, match="lacks|requires"):
        put(iso, "APPROVED_STATE", {"commit": "a" * 40})
    with pytest.raises(authority.AuthorityError, match="unknown type"):
        put(iso, "SOMETHING_ELSE", {})
    assert len(authority.read_register(iso / REG)) == 1


# ---------------------------------------------------------------------------------------------------------------- 6 delivery
def clean_run(cwd, *, hide_original=None):
    return {**verify.summarize_pytest("5 passed in 0.1s\n"), "returncode": 0, "tail": ""}


def zipless(out: Path):
    return sorted(p.name for p in out.iterdir())


def test_6_a_failed_repository_preflight_prevents_delivery_even_when_every_test_passes(tree, monkeypatch):
    git_init(tree)
    log = tree / "docs/STOCK_ATLAS_DECISION_LOG.md"
    log.write_text("\n".join(log.read_text().splitlines()[:-3]) + "\n")                  # a real, git-visible violation: history deleted since the approved state
    commit(tree, "deletes decision-log lines")
    monkeypatch.setattr(verify, "run_pytest", clean_run)
    with pytest.raises(SystemExit, match=r"repository preflight FAILED \(append-only"):
        verify.deliver(tree, out=tree.parent / "out")
    out = tree.parent / "out"
    md = (out / "DELIVERY.md").read_text()
    assert "PASS (both runs clean)" in md and "repository **FAIL**" in md and "clean extraction PASS" in md and "DELIVERY NOT CLEAN" in md
    assert not list(out.glob("*.zip")) and not list(out.glob("*.patch")) and len(list(out.glob("*.REJECTED"))) == 2     # nothing deliverable-looking remains


def test_6b_a_failed_clean_extraction_preflight_prevents_delivery_even_when_every_test_passes(tree, monkeypatch):
    git_init(tree)
    monkeypatch.setattr(verify, "run_pytest", clean_run)
    real = verify.preflight

    def zip_fails(repo, **kw):
        cs = real(repo, **kw)
        return [*cs, verify.Check("simulated", "FAIL", "only the extracted copy fails")] if kw.get("use_git") is False else cs

    monkeypatch.setattr(verify, "preflight", zip_fails)
    with pytest.raises(SystemExit, match="clean-extraction preflight FAILED"):
        verify.deliver(tree, out=tree.parent / "out")
    md = (tree.parent / "out/DELIVERY.md").read_text()
    assert "repository PASS" in md and "clean extraction **FAIL**" in md and not list((tree.parent / "out").glob("*.zip"))


def test_6c_a_preflight_that_crashes_is_a_failed_preflight(tree, monkeypatch):
    git_init(tree)
    monkeypatch.setattr(verify, "run_pytest", clean_run)
    real = verify.preflight

    def boom(repo, **kw):
        if kw.get("use_git") is False:
            raise RuntimeError("preflight exploded")
        return real(repo, **kw)

    monkeypatch.setattr(verify, "preflight", boom)
    with pytest.raises(SystemExit, match="clean-extraction preflight FAILED"):
        verify.deliver(tree, out=tree.parent / "out")


def test_6d_with_both_preflights_and_both_test_runs_clean_the_delivery_succeeds_and_keeps_its_artifacts(tree, monkeypatch):
    git_init(tree)
    monkeypatch.setattr(verify, "run_pytest", clean_run)
    out = verify.deliver(tree, out=tree.parent / "out")
    names = zipless(out)
    assert len(names) == 3 and not any(n.endswith(".REJECTED") for n in names) and "Verdict:** CLEAN" in (out / "DELIVERY.md").read_text()


def test_6e_the_blocker_rule_treats_each_gate_independently():
    ok, bad = [verify.Check("x", "OK")], [verify.Check("bad", "FAIL", "d")]
    assert verify.delivery_blockers(run_tests=True, tests_ok=True, repo_checks=ok, zip_checks=ok) == []
    assert len(verify.delivery_blockers(run_tests=True, tests_ok=True, repo_checks=bad, zip_checks=ok)) == 1
    assert len(verify.delivery_blockers(run_tests=True, tests_ok=True, repo_checks=ok, zip_checks=bad)) == 1
    assert len(verify.delivery_blockers(run_tests=True, tests_ok=False, repo_checks=bad, zip_checks=bad)) == 3
    assert verify.delivery_blockers(run_tests=False, tests_ok=False, repo_checks=ok, zip_checks=ok) == []      # tests not requested (documented NOT RUN)
    warn_only = [verify.Check("w", "WARN"), verify.Check("i", "INFO"), verify.Check("s", "SKIP")]
    assert verify.delivery_blockers(run_tests=True, tests_ok=True, repo_checks=warn_only, zip_checks=warn_only) == []   # only FAIL blocks
