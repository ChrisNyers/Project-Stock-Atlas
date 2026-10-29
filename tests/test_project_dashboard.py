"""The Project oversight dashboard (/project): a read-only view over records that already exist.

What must hold: it reads the real records every time it is viewed; Git HEAD, the published GitHub position and the approved state stay three different
things; a milestone is COMPLETE only if a human approved it AND its evidence resolves; unapproved, unsupported or missing information is shown as such or as
UNKNOWN; no percentage is invented; nothing is inferred from prose; conflicting authority records fail closed; viewing writes nothing.
Hermetic: temporary copies of the repository and a temporary bare 'origin'. The real records are never touched.
"""
import hashlib
import json
import subprocess
import threading
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from atlas_ui import app as appmod
from atlas_ui import authority, project, verify
from atlas_ui.__main__ import build
from test_atlas_ui import req
from test_authority import GIT_ENV, ROOT, approve_state, git_init, status, tree  # noqa: F401  (tree is a fixture)

REG = authority.REGISTER
HUMAN = {"by": "HUMAN", "date": "2026-10-30", "record": "Decision Log: SOURCE_OF_TRUTH_AND_PORTABILITY", "quote": "test: the human approves this"}
NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)


def put(root, type_, payload, approval=HUMAN):
    return authority.append(root / REG, type_, payload, approval=approval, check_record=(lambda r: authority.record_exists(root, r)) if approval else None)


def ms(root, mid, status_, *, approval=HUMAN, evidence=("file:CLAUDE.md",), phase=(9, "Test phase"), **extra):
    return put(root, "MILESTONE", {"milestone_id": mid, "phase": phase[1], "phase_order": phase[0], "title": f"title {mid}", "status": status_, "evidence": list(evidence), **extra}, approval)


def git(root, *a):
    return subprocess.run(["git", "-C", str(root), *a], env=GIT_ENV, capture_output=True, text=True, check=True).stdout.strip()


def with_origin(tree: Path) -> Path:
    bare = tree.parent / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
    git(tree, "remote", "add", "origin", str(bare))
    git(tree, "push", "-q", "origin", "main")
    return bare


def data(tree, **kw):
    return project.status(tree, now=NOW, capabilities=appmod.CAPABILITIES, **kw)


@pytest.fixture
def served(tmp_path, monkeypatch):
    """The real app (demo workspace) serving a project page that reads a hermetic repository copy."""
    app = build(True, tmp_path / "demo")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), appmod.make_handler(app))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield app, srv.server_address[1], monkeypatch
    srv.shutdown()


# ------------------------------------------------------------------------------------------------------ three different things
def test_head_published_and_approved_are_separate_facts(tree):
    base = git_init(tree)                                  # approved = the first commit; HEAD = one commit later
    bare = with_origin(tree)
    t = data(tree)["truth"]
    head, pub, appr = t["head"]["sha"], t["published"]["sha"], t["approved"]["commit"]
    assert head == pub != appr == base and t["published_vs_head"] == "SAME" and t["head_is_approved"] is False
    assert [c[0] for c in t["ahead_of_approved"]] == [head[:7]] and "NOT a live check" in t["published"]["basis"]
    (tree / "NEW.txt").write_text("x")
    git(tree, "add", "-A"); git(tree, "commit", "-q", "-m", "unpublished work")
    t = data(tree)["truth"]
    assert t["head"]["sha"] != t["published"]["sha"] and "1 commit(s) ahead of the published branch" in t["published_vs_head"] and len(t["ahead_of_approved"]) == 2
    approve_state(tree, t["head"]["sha"])
    assert data(tree)["truth"]["head_is_approved"] is True and data(tree)["truth"]["approved"]["commit"] == t["head"]["sha"]


def test_no_published_position_is_unknown_not_assumed_same(tree):
    git_init(tree)
    t = data(tree)["truth"]
    assert t["published"] is None and t["published_vs_head"] == project.UNKNOWN


def test_live_github_check_is_read_only_reports_failures_as_unknown_and_never_leaks_credentials(tree):
    git_init(tree)
    bare = with_origin(tree)
    before = (tree / REG).read_bytes(), git(tree, "rev-parse", "HEAD"), git(tree, "status", "--porcelain")
    ok = project.check_github(tree)
    assert ok["ok"] is True and ok["sha"] == git(tree, "rev-parse", "HEAD") and ok["checked_at"].endswith("+00:00")
    d = data(tree, github_live=ok)["truth"]
    assert d["live_vs_head"] == "SAME"
    git(tree, "remote", "set-url", "origin", "https://user:s3cretTOKEN@example.invalid/x.git")
    t = data(tree)["truth"]
    assert "s3cretTOKEN" not in json.dumps(t) and "user:" not in t["remote"]
    bad = project.check_github(tree, timeout=5)
    assert bad["ok"] is False and bad["sha"] is None and "s3cretTOKEN" not in json.dumps(bad)
    assert (tree / REG).read_bytes() == before[0] and git(tree, "rev-parse", "HEAD") == before[1]


def test_a_tree_without_git_history_reports_unknown(tree):
    t = data(tree, use_git=False)["truth"]
    assert t["available"] is False and t["head"] is None and t["published_vs_head"] == project.UNKNOWN and "UNKNOWN" in t["note"]


# ------------------------------------------------------------------------------------------------------ milestones: approval + evidence
def totals(tree):
    return data(tree)["milestones"]["totals"]


def test_a_milestone_counts_as_complete_only_if_human_approved_and_its_evidence_resolves(tree):
    base = totals(tree)
    ms(tree, "T1", "COMPLETE")                                                            # approved, evidence resolves
    ms(tree, "T2", "COMPLETE", approval=None)                                             # a proposal: nobody approved it
    ms(tree, "T3", "COMPLETE", evidence=("file:does/not/exist.py",))                      # approved, evidence does not resolve
    ms(tree, "T4", "COMPLETE", evidence=())                                               # approved, no evidence cited at all
    t = totals(tree)
    assert t["complete"] == base["complete"] + 1 and t["milestones"] == base["milestones"] + 4
    assert t["awaiting_acceptance"] == base["awaiting_acceptance"] + 1 and t["complete_but_evidence_unverified"] == base["complete_but_evidence_unverified"] + 2
    items = {i["id"]: i for ph in data(tree)["milestones"]["phases"] for i in ph["items"]}
    assert items["T1"]["counts_as_complete"] and not items["T2"]["approved"] and items["T2"]["status"] == "NOT APPROVED" and items["T2"]["proposed"]["status"] == "COMPLETE"
    assert not items["T3"]["counts_as_complete"] and not items["T4"]["counts_as_complete"] and items["T3"]["status"] == "COMPLETE"


def test_status_history_is_append_only_and_the_latest_approved_event_governs(tree):
    ms(tree, "T5", "IN_PROGRESS")
    first = (tree / REG).read_text().splitlines()[-1]
    ms(tree, "T5", "COMPLETE")
    ms(tree, "T5", "BLOCKED", blocker="a reviewer found a gap")                           # approved: the human reopened it
    ms(tree, "T5", "COMPLETE", approval=None)                                             # a later proposal; not followed
    m = authority.resolve(tree / REG).milestones["T5"]
    assert m["current"]["payload"]["status"] == "BLOCKED" and m["proposed"]["payload"]["status"] == "COMPLETE" and len(m["history"]) == 4
    assert (tree / REG).read_text().splitlines()[-4] == first                             # the first line is exactly as written
    item = [i for ph in data(tree)["milestones"]["phases"] for i in ph["items"] if i["id"] == "T5"][0]
    assert item["status"] == "BLOCKED" and item["blocker"] == "a reviewer found a gap" and not item["counts_as_complete"]


def test_nothing_is_inferred_from_prose_in_the_master_plan_or_decision_log(tree):
    before = data(tree)["milestones"]
    for f in ("docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md", "docs/STOCK_ATLAS_DECISION_LOG.md"):
        p = tree / f
        p.write_text(p.read_text() + "\n\n## ALL_MILESTONES_COMPLETE\n\n| Status | **COMPLETE — ACCEPTED BY THE HUMAN** |\n\nR0.1 is COMPLETE. B1-R4.1 ACCEPTED. 100% done.\n")
    after = data(tree)["milestones"]
    assert after == before
    ds = data(tree)["recent"]["decisions"][0]
    assert ds["name"] == "ALL_MILESTONES_COMPLETE" and "COMPLETE" in ds["status_text"]   # shown verbatim as text; it moved no status


def test_milestone_events_are_validated(tree):
    ok = {"milestone_id": "TX", "phase": "p", "phase_order": 1, "title": "t", "status": "UPCOMING", "evidence": []}
    for bad in ({"status": "DONE"}, {"status": "complete"}, {"evidence": "file:x"}, {"phase_order": "3"}):
        with pytest.raises(authority.AuthorityError):
            put(tree, "MILESTONE", {**ok, **bad})
    with pytest.raises(authority.AuthorityError, match="requires"):
        put(tree, "MILESTONE", {"milestone_id": "TY", "phase": "p"})
    assert "TX" not in authority.resolve(tree / REG).milestones                              # nothing invalid was written


def test_evidence_references_are_checked_and_cannot_escape_the_repository(tree):
    res = authority.resolve(tree / REG)
    got = {x["ref"]: x["ok"] for x in project.verify_evidence(tree, [
        "file:CLAUDE.md", "file:../outside.txt", "file:/etc/passwd", "decision-log:BASELINE_ACCEPTED_0733C77", "decision-log:NO_SUCH", "register:5", "register:9999", "register:x", "bogus:thing"], res, use_git=False)}
    assert got == {"file:CLAUDE.md": True, "file:../outside.txt": False, "file:/etc/passwd": False, "decision-log:BASELINE_ACCEPTED_0733C77": True,
                   "decision-log:NO_SUCH": False, "register:5": True, "register:9999": False, "register:x": False, "bogus:thing": False}
    assert project.verify_evidence(tree, ["commit:" + "a" * 40], res, use_git=False)[0]["ok"] is None        # cannot be checked without history: UNKNOWN, never a pass
    git_init(tree)
    assert project.verify_evidence(tree, ["commit:" + "a" * 40], res, use_git=True)[0]["ok"] is False


def test_preflight_rejects_a_complete_milestone_whose_evidence_does_not_resolve(tree):
    ms(tree, "T6", "COMPLETE", evidence=("decision-log:NO_SUCH_ENTRY",))
    c = status(verify.preflight(tree, use_git=False), "milestone evidence resolves")
    assert c.status == "FAIL" and "T6" in c.detail
    git_init(tree)
    assert status(verify.preflight(tree), "milestone evidence resolves").status == "FAIL"


def test_the_real_registers_closed_phase_is_fully_accepted_with_verified_evidence():
    d = project.status(ROOT, now=NOW, capabilities=appmod.CAPABILITIES, run_preflight=False)
    phases = {p["order"]: p for p in d["milestones"]["phases"]}
    assert phases[1]["counts"]["complete"] == phases[1]["counts"]["total"] == 8 or not project.has_git(ROOT)      # commit evidence needs git history
    assert all(i["status"] != "COMPLETE" for o, p in phases.items() if o > 1 for i in p["items"])                 # nothing after the closed phase is recorded COMPLETE as approved
    assert [i["id"] for p in phases.values() for i in p["items"] if i["status"] == "BLOCKED"] == ["L1"]


# ------------------------------------------------------------------------------------------------------ the page
def view(served, tree, path="/project", **kw):
    app, port, mp = served
    mp.setattr(project, "REPO", tree)
    st, body, hd = req(port, "GET", path)
    return st, body, hd


def test_the_page_renders_from_the_records_and_never_shows_a_percentage_or_a_script(served, tree):
    git_init(tree); with_origin(tree)
    ms(tree, "T7", "COMPLETE", approval=None)
    st, body, hd = view(served, tree)
    assert st == 200 and "<script" not in body.lower() and "Where the project stands" in body
    main = body.split("<main", 1)[1]
    assert "%" not in main.replace("100%", "").split("</style>", 1)[1]                    # no completion percentage anywhere in the content
    for needle in ("Git HEAD (this Mac)", "Published on GitHub", "Approved baseline (human)", "Needs attention", "AWAITING ACCEPTANCE", "Active assignment", "Upcoming dates",
                   "Milestones by phase", "Verified capabilities", "Research pipeline", "Recent changes", "Sources and when each last changed", "Check GitHub now", "Refresh now"):
        assert needle in main, needle
    assert "MCD PARKED until 2026-11-04" in main and "a trigger to reassess, not a promotion" in main
    assert hd["Content-Security-Policy"].startswith("default-src 'none'")


def test_it_rereads_the_records_every_time_it_is_viewed(served, tree):
    git_init(tree)
    _s, before, _h = view(served, tree)
    ms(tree, "T8", "BLOCKED", blocker="waiting for a human decision about T8")
    _s, after, _h = view(served, tree)
    assert "waiting for a human decision about T8" not in before and "waiting for a human decision about T8" in after
    assert "Rendered 20" in after and "Last changed" in after and "Authority register" in after and "Candidate ledger" in after


def test_missing_information_is_unknown_never_completed(served, tmp_path):
    bare = tmp_path / "bare"
    (bare / "docs").mkdir(parents=True)
    authority.append(bare / REG, "PORTFOLIO_SNAPSHOT", {"snapshot_id": "S", "doc": "docs/x.md", "doc_sha256": "0" * 64, "table_marker": "m", "as_of": "2026-01-01", "holdings": 1,
                                                        "stocks_total": "1", "defensive_approx": "1", "supersedes": None}, approval=None)
    st, body, _h = view(served, bare)
    assert st == 200
    main = body.split("<main", 1)[1]
    assert main.count('class="unk"') >= 4 and "No milestone is recorded" not in main
    assert "UNKNOWN" in main and "Milestones accepted" in main and "8 of 18" not in main
    d = project.status(bare, now=NOW, run_preflight=False)
    assert d["active"] is None and d["milestones"]["totals"]["milestones"] == 0 and d["truth"]["available"] is False


def test_conflicting_authority_records_fail_closed_on_the_page(served, tree):
    ev = authority.read_register(tree / REG)
    prev = ev[-1]["event_hash"]
    body_ = {"seq": len(ev) + 1, "type": "APPROVED_STATE", "recorded_on": "2026-10-30", "payload": {"commit": "f" * 40, "supersedes": None, "status": "second root"}, "approval": HUMAN}
    with open(tree / REG, "a") as fh:
        fh.write(json.dumps({**body_, "prev_hash": prev, "event_hash": authority._hash(prev, body_)}) + "\n")
    st, body, _h = view(served, tree)
    assert st == 200 and "AUTHORITY RECORDS DO NOT RESOLVE" in body
    d = project.status(tree, now=NOW, run_preflight=False)
    assert d["authority"]["ok"] is False and d["milestones"] is None and d["active"] is None and d["truth"]["approved"] is None


def test_auto_refresh_is_opt_in_and_bounded(served, tree):
    git_init(tree)
    assert 'http-equiv="refresh"' not in view(served, tree)[1]
    assert '<meta http-equiv="refresh" content="60">' in view(served, tree, "/project?auto=60")[1]
    assert 'http-equiv="refresh"' not in view(served, tree, "/project?auto=1")[1]      # too fast: ignored
    assert 'http-equiv="refresh"' not in view(served, tree, "/project?auto=x")[1]


def test_check_github_button_does_a_read_only_check_and_shows_the_result_and_its_time(served, tree):
    git_init(tree); with_origin(tree)
    app, port, mp = served
    mp.setattr(project, "REPO", tree)
    st, _b, hd = req(port, "POST", "/project/check-github", {})
    assert st == 303 and hd["Location"] == "/project#truth"
    body = req(port, "GET", "/project")[1]
    assert "live check 20" in body and "matches HEAD" in body and app.github_live["ok"] is True


def test_viewing_the_dashboard_writes_nothing(served, tree):
    git_init(tree)
    app, port, mp = served
    mp.setattr(project, "REPO", tree)
    snap = lambda: hashlib.sha256(b"".join(p.read_bytes() for p in sorted(tree.rglob("*")) if p.is_file() and ".git" not in p.parts)).hexdigest()
    ws_snap = lambda: hashlib.sha256(b"".join(p.read_bytes() for p in sorted(app.ws.root.rglob("*")) if p.is_file())).hexdigest()
    before, wbefore = snap(), ws_snap()
    for path in ("/project", "/project?auto=60", "/api/project"):
        assert req(port, "GET", path)[0] == 200
    assert snap() == before and ws_snap() == wbefore and git(tree, "status", "--porcelain") == ""


def test_the_api_returns_the_same_data_as_json(served, tree):
    git_init(tree)
    app, port, mp = served
    mp.setattr(project, "REPO", tree)
    st, body, _h = req(port, "GET", "/api/project")
    j = json.loads(body)
    assert st == 200 and {"truth", "milestones", "active", "upcoming", "capabilities", "pipeline", "sources", "preflight", "generated_at"} <= set(j)
    assert j["truth"]["head"]["sha"] != j["truth"]["approved"]["commit"] and j["milestones"]["totals"]["milestones"] >= 18
    assert j["capabilities"]["counts"]["PROVEN LIVE"] == 2 and "J. Project oversight" in " ".join(r["name"] for r in j["capabilities"]["rows"])


def test_only_the_local_host_may_use_it(served, tree):
    app, port, mp = served
    assert req(port, "GET", "/project", headers={"Host": "evil.example"})[0] == 403
    assert req(port, "POST", "/project/check-github", {}, headers={"Host": "evil.example"})[0] == 403
    assert req(port, "POST", "/project/check-github", {}, headers={"Origin": "http://evil.example"})[0] == 403


def test_the_dashboard_stays_a_project_view_and_does_not_reach_into_investment_analysis():
    src = (ROOT / "atlas_ui/project.py").read_text()
    for banned in ("bind_price", "price_relative", "load_snapshot", "record_stage8", "run_stage7", "TwelveData", "FundedFreshness", "DecisionStore"):
        assert banned not in src, banned
    page = (ROOT / "atlas_ui/app.py").read_text().split("def project_page", 1)[1].split("def make_handler", 1)[0]
    for banned in ("BUY", "target price", "undervalued", "overvalued", "attractive at", "we recommend"):
        assert banned not in page, banned
