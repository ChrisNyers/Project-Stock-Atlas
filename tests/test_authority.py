"""Source-of-truth tooling: the authority reference, preflight, test-run classification and delivery packaging.

The preflight must PASS on the real repository and must FAIL (or WARN, where the rule says so) on each way the approved state can silently drift:
a control edited, the pin moved without an authorization record, a changed baseline, an unparked or tampered candidate ledger, a Master Plan without
the authority pointer or with the Pilot 2 list still reading as active, deleted plan lines, a missing milestone review, an unapproved HEAD.
Copies in temp dirs only; nothing here touches the real records.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from atlas_ui import authority, verify

ROOT = Path(__file__).resolve().parent.parent
GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def status(checks, name_part):
    (c,) = [c for c in checks if name_part in c.name]
    return c


def copy_repo(dest: Path) -> Path:
    shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".git", ".venv", "venv", "deliverables", "__pycache__", ".pytest_cache", ".env", ".env.*", "*.pyc", "*.zip"))
    return dest


@pytest.fixture
def tree(tmp_path):
    return copy_repo(tmp_path / "stock-atlas")


def edit_authority(tree: Path, fn):
    p = tree / verify.AUTHORITY
    text = p.read_text()
    m = re.search(r"```json\n(.*?)\n```", text, re.S)
    a = json.loads(m.group(1))
    fn(a)
    p.write_text(text[:m.start(1)] + json.dumps(a, indent=2, ensure_ascii=False) + text[m.end(1):])


HUMAN = {"by": "HUMAN", "date": "2026-10-29", "record": "Decision Log: SOURCE_OF_TRUTH_AND_PORTABILITY", "quote": "test approval"}


def approve_state(tree: Path, sha: str):
    """The human accepts a commit: one appended register event that supersedes the previous approved state."""
    reg = tree / authority.REGISTER
    prev = authority.resolve(reg).approved_state["commit"]
    authority.append(reg, "APPROVED_STATE", {"commit": sha, "supersedes": prev, "status": "test acceptance"}, approval=HUMAN)


def git_init(tree: Path) -> str:
    run = lambda *a: subprocess.run(["git", "-C", str(tree), *a], env=GIT_ENV, capture_output=True, text=True, check=True).stdout.strip()
    run("init", "-q", "-b", "main")
    run("add", "-A")
    run("commit", "-q", "-m", "baseline")
    sha = run("rev-parse", "HEAD")
    approve_state(tree, sha)
    run("add", "-A")
    run("commit", "-q", "-m", "authority names the baseline")   # HEAD is now one commit ahead of the approved state
    return sha


def commit(tree: Path, msg: str):
    subprocess.run(["git", "-C", str(tree), "add", "-A"], env=GIT_ENV, check=True)
    subprocess.run(["git", "-C", str(tree), "commit", "-q", "-m", msg], env=GIT_ENV, check=True, capture_output=True)


# ---- the real repository ----------------------------------------------------------------------------------------------------------------
def test_preflight_passes_on_the_real_repository_with_no_failures():
    checks = verify.preflight(ROOT)
    assert [c.line() for c in checks if c.status == "FAIL"] == []
    names = {c.name for c in checks}
    for must in ("frozen controls pinned", "pin file matches authority", "authority register", "approved portfolio snapshot", "candidate ledger chain + restrictions",
                 "outdated Pilot 2 work list marked superseded", "master plan points to the authority reference", "latest milestone review present"):
        assert must in names, must


def test_the_cli_exits_zero_on_the_repository_and_one_on_a_drifted_copy(tree):
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST")}
    ok = subprocess.run([sys.executable, "-m", "atlas_ui", "preflight"], cwd=ROOT, env=env, capture_output=True, text=True)
    assert ok.returncode == 0 and "PREFLIGHT PASS" in ok.stdout, ok.stdout
    (tree / "capital_decision_facade.py").write_text((tree / "capital_decision_facade.py").read_text() + "\n# drift\n")
    bad = subprocess.run([sys.executable, "-m", "atlas_ui", "preflight"], cwd=tree, env=env, capture_output=True, text=True)
    assert bad.returncode == 1 and "PREFLIGHT FAIL" in bad.stdout and "frozen controls pinned" in bad.stdout


def test_historical_documents_carry_the_not_governing_note_and_claude_md_points_to_the_authority():
    for f in ("README.md", "INDEX.md"):
        assert (ROOT / f).read_text().startswith("> **Historical (Sprint 1 era).**") and "CURRENT_AUTHORITY.md" in (ROOT / f).read_text()[:400], f
    assert "docs/CURRENT_AUTHORITY.md" in (ROOT / "CLAUDE.md").read_text() and "preflight" in (ROOT / "CLAUDE.md").read_text()
    plan = (ROOT / "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md").read_text()
    assert plan.index("Current active task: EXECUTE PILOT 2") < plan.index("SUPERSEDED AS THE ACTIVE WORK LIST")   # the old text is intact, and followed by the note


# ---- drift is detected -------------------------------------------------------------------------------------------------------------------
def test_an_edited_control_file_fails(tree):
    f = tree / "stock_atlas" / "controls.py"
    f.write_text(f.read_text() + "\n# edit\n")
    assert status(verify.preflight(tree, use_git=False), "frozen controls pinned").status == "FAIL"


def test_moving_the_pin_without_the_authority_record_fails(tree):
    pin = tree / "atlas_ui" / "FROZEN_CONTROL_SHA256.txt"
    pin.write_text(pin.read_text() + "\n")
    assert status(verify.preflight(tree, use_git=False), "pin file matches authority").status == "FAIL"


def test_an_approved_snapshot_record_edited_after_approval_fails(tree):
    b = tree / "docs/controlled_live_pilot/CYCLE0_BASELINE_001.md"
    b.write_text(b.read_text() + "\nsilent addition\n")
    c = status(verify.preflight(tree, use_git=False), "approved portfolio snapshot")
    assert c.status == "FAIL" and "edited after approval" in c.detail


def test_tampering_with_the_candidate_ledger_fails(tree):
    led = tree / "operating_mvp/data/candidate_ledger.jsonl"
    text = led.read_text()
    assert '"MCD"' in text
    led.write_text(text.replace('"MCD"', '"MCX"', 1))   # an edited recorded event: the hash chain must reject it
    assert status(verify.preflight(tree, use_git=False), "candidate ledger chain").status == "FAIL"


def test_a_plan_without_the_pointer_or_with_the_pilot2_list_unmarked_fails(tree):
    plan = tree / "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md"
    t = plan.read_text()
    plan.write_text(t.replace("SUPERSEDED AS THE ACTIVE WORK LIST (2026-10-29)", "(note removed)"))
    assert status(verify.preflight(tree, use_git=False), "Pilot 2 work list").status == "FAIL"
    plan.write_text(t.replace("docs/CURRENT_AUTHORITY.md", "docs/SOMETHING_ELSE.md", 1) if t.count("docs/CURRENT_AUTHORITY.md") == 1 else
                    re.sub(r"\[`docs/CURRENT_AUTHORITY.md`\]\(CURRENT_AUTHORITY.md\)", "x", t, count=1).replace("(`python -m atlas_ui preflight`)", "", 1))
    assert status(verify.preflight(tree, use_git=False), "points to the authority").status == "FAIL"


def test_a_missing_or_incomplete_milestone_review_fails(tree):
    plan = tree / "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md"
    t = plan.read_text()
    plan.write_text(t.replace("**What we should do next.**", "**Later.**"))
    c = status(verify.preflight(tree, use_git=False), "milestone review")
    assert c.status == "FAIL" and "What we should do next" in c.detail
    plan.write_text(t.replace("### October 29, 2026 — Milestone review", "### October 29, 2026 — Notes"))
    assert status(verify.preflight(tree, use_git=False), "milestone review").status == "FAIL"


def test_a_missing_record_or_unreadable_authority_fails(tree):
    (tree / "docs/STOCK_ATLAS_DECISION_LOG.md").unlink()
    assert status(verify.preflight(tree, use_git=False), "referenced records").status == "FAIL"
    (tree / verify.AUTHORITY).write_text("# no manifest here\n")
    assert [c.status for c in verify.preflight(tree, use_git=False)] == ["FAIL"]


def test_a_nonempty_decision_ledger_is_counted_and_its_chain_verified_not_assumed_empty(tree):
    (tree / "atlas_ui/data/live/decisions.jsonl").write_text('{"record":{}}\n')      # not a valid chained row: must not pass as a decision history
    c = status(verify.preflight(tree, use_git=False), "canonical decision ledger")
    assert c.status == "FAIL" and "1 rows" in c.detail or "BROKEN" in c.detail


def test_without_git_the_git_checks_are_skipped_not_passed(tree):
    c = status(verify.preflight(tree, use_git=False), "git position")
    assert c.status == "SKIP"


# ---- git-aware checks (temp repository) ----------------------------------------------------------------------------------------------
def test_newest_commit_is_distinguished_from_the_approved_state(tree):
    base = git_init(tree)
    c = status(verify.preflight(tree), "newest commit vs approved state")
    assert c.status == "INFO" and "NEWEST COMMIT" in c.detail and "1 commit(s) ahead" in c.detail and base[:12] in c.detail and "unapproved" in c.detail
    head = subprocess.run(["git", "-C", str(tree), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    approve_state(tree, head)      # the human accepts HEAD (an uncommitted register append, so HEAD stays put)
    c = status(verify.preflight(tree), "newest commit vs approved state")
    assert c.status == "OK" and "IS the approved state" in c.detail


def test_deleting_or_editing_plan_lines_since_approval_fails_but_appending_is_fine(tree):
    git_init(tree)
    plan = tree / "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md"
    t = plan.read_text()
    plan.write_text(t + "\n### October 30, 2026 — a new dated entry\n")
    assert status(verify.preflight(tree), "append-only").status == "OK"
    plan.write_text(t.replace("Authoritative status record.", "Rewritten status record.", 1) + "\n")
    c = status(verify.preflight(tree), "append-only")
    assert c.status == "FAIL" and "STOCK_ATLAS_MASTER_PROJECT_PLAN.md" in c.detail
    plan.write_text(t)
    log = tree / "docs/STOCK_ATLAS_DECISION_LOG.md"
    log.write_text("\n".join(log.read_text().splitlines()[:-3]) + "\n")
    assert status(verify.preflight(tree), "append-only").status == "FAIL"


def test_a_control_changed_since_approval_is_flagged_even_if_the_pin_was_updated(tree):
    git_init(tree)
    f = tree / "allocation_rationale.py"
    f.write_text(f.read_text() + "\n# authorized-looking edit\n")
    import hashlib
    pin = tree / "atlas_ui/FROZEN_CONTROL_SHA256.txt"
    pin.write_text(re.sub(r"[0-9a-f]{64}(\s+allocation_rationale.py)", hashlib.sha256(f.read_bytes()).hexdigest() + r"\1", pin.read_text()))
    edit_authority(tree, lambda a: a["controls"].__setitem__("pin_file_sha256", hashlib.sha256(pin.read_bytes()).hexdigest()))
    cs = verify.preflight(tree)
    assert status(cs, "frozen controls pinned").status == "OK" and status(cs, "pin file matches authority").status == "OK"
    c = status(cs, "changed since the approved state")
    assert c.status == "WARN" and "allocation_rationale.py" in c.detail


def test_an_approved_commit_that_is_not_an_ancestor_fails(tree):
    base = git_init(tree)
    subprocess.run(["git", "-C", str(tree), "checkout", "-q", "-b", "other", base], env=GIT_ENV, check=True)
    (tree / "side.txt").write_text("x")
    commit(tree, "side branch")
    side = subprocess.run(["git", "-C", str(tree), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "-C", str(tree), "checkout", "-q", "main"], env=GIT_ENV, check=True)
    approve_state(tree, side)
    assert status(verify.preflight(tree), "ancestor").status == "FAIL"


def test_an_unknown_approved_commit_fails(tree):
    git_init(tree)
    approve_state(tree, "0" * 40)
    assert status(verify.preflight(tree), "approved state in history").status == "FAIL"


# ---- test-run summary and skip classification ---------------------------------------------------------------------------------------
SAMPLE = """....s..
SKIPPED [1] tests/test_gate_b_live_binding.py:217: TWELVEDATA_API_KEY absent — Gate B live binding is BLOCKED, not passing
SKIPPED [24] tests/test_gate_b_live_binding.py:239: TWELVEDATA_API_KEY absent — Gate B live binding is BLOCKED, not passing
SKIPPED [1] tests/test_atlas_ui.py:432: accepted baseline commit not present in this checkout
SKIPPED [2] tests/test_x.py:9: because someone said so
FAILED tests/test_a.py::test_b - assert 1 == 2
1 failed, 560 passed, 28 skipped, 1 warning in 12.14s
"""


def test_skips_are_classified_and_never_counted_as_passes():
    s = verify.summarize_pytest(SAMPLE)
    assert (s["passed"], s["failed"], s["skipped"], s["warnings"]) == (560, 1, 28, 1) and s["failed_tests"] == ["tests/test_a.py::test_b"]
    assert s["skip_classes"] == {"BLOCKED — live credential absent (not a pass)": 25, "ENVIRONMENT — needs git history": 1, "OTHER — investigate": 2}
    text = verify.render_tests("x", s)
    assert "560 passed, 1 failed" in text and "25 BLOCKED" in text and "OTHER — investigate" in text and "FAILED" in text


# ---- delivery packaging --------------------------------------------------------------------------------------------------------------------
def test_deliver_builds_one_zip_one_patch_and_one_report_from_one_commit(tree):
    base = git_init(tree)
    (tree / "NEWFILE.txt").write_text("a change after the approved state\n")
    commit(tree, "a change")
    out = verify.deliver(tree, out=tree.parent / "out", run_tests=False)
    files = sorted(p.name for p in out.iterdir())
    head = subprocess.run(["git", "-C", str(tree), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert files == sorted(["DELIVERY.md", f"SOURCE_DIFF_{base[:7]}_to_{head[:7]}.patch", f"Stock_Atlas_{head[:7]}_full_source.zip"])   # exactly three artifacts
    md = (out / "DELIVERY.md").read_text()
    assert head in md and base in md and "NEWFILE.txt" in md and "NOT RUN (run_tests=False)" in md and "`.env` members: none" in md
    assert "Frozen controls" in md and "**CHANGED**" not in md and "PREFLIGHT" in md
    import zipfile
    names = zipfile.ZipFile(next(out.glob("*.zip"))).namelist()
    assert "stock-atlas/NEWFILE.txt" in names and not any(re.search(r"(^|/)\.env($|\.(?!example))", n) for n in names)
    assert "NEWFILE.txt" in next(out.glob("*.patch")).read_text()


def test_deliver_refuses_a_dirty_tree(tree):
    git_init(tree)
    (tree / "uncommitted.txt").write_text("x")
    with pytest.raises(SystemExit, match="uncommitted"):
        verify.deliver(tree, out=tree.parent / "out", run_tests=False)


# ---- an empty, unparseable or failing test run can never be reported as a success -----------------------------------------------------------
def test_an_empty_or_unparseable_run_is_not_clean_and_is_rendered_as_a_failure():
    empty = verify.summarize_pytest("ERROR collecting\nImportError: nope\n")
    empty.update(returncode=2, tail="ImportError: nope")
    assert not verify.tests_clean(empty) and "NO PYTEST SUMMARY" in verify.render_tests("repo", empty) and "treat as FAILED" in verify.render_tests("repo", empty)
    ok = {**verify.summarize_pytest("1 passed in 0.1s\n"), "returncode": 0}
    assert verify.tests_clean(ok)
    for bad in ({**ok, "returncode": 1}, {**ok, "failed": 1}, {**ok, "error": 2}, {**ok, "passed": 0}, None):
        assert not verify.tests_clean(bad)


def test_deliver_extracts_outside_the_repo_runs_both_suites_and_fails_loudly_when_they_are_not_clean(tree, monkeypatch):
    git_init(tree)
    calls = []

    def fake(cwd, *, hide_original=None):
        calls.append((Path(cwd).resolve(), hide_original))
        return {**verify.summarize_pytest("2 passed in 0.1s\n"), "returncode": 0, "tail": ""} if len(calls) == 1 else {**verify.summarize_pytest(""), "returncode": 2, "tail": "boom"}

    monkeypatch.setattr(verify, "run_pytest", fake)
    with pytest.raises(SystemExit, match="DELIVERY NOT CLEAN"):
        verify.deliver(tree, out=tree.parent / "out")
    (repo_cwd, repo_hide), (zip_cwd, zip_hide) = calls
    assert repo_cwd == tree.resolve() and repo_hide is None
    assert tree.resolve() not in zip_cwd.parents and zip_cwd != tree.resolve() and zip_hide == tree      # extracted elsewhere, original tree blocked
    report = next((tree.parent / "out").glob("DELIVERY.md")).read_text()
    assert "FAILED OR INCOMPLETE" in report and "NO PYTEST SUMMARY" in report
