"""Research snapshot references are portable, bound to their SHA-256, confined to the research workspace, and fail LOUDLY.

Independent review of 1683f98, Material finding 2: the committed ``research_index.jsonl`` held the writing Mac's absolute paths, so a ZIP
extracted anywhere else could not load the saved MCD/GEV/RMD/ORCL snapshots. (My own earlier "clean extract" check passed only because the original
Mac path still existed on the machine that produced the ZIP — so the tests below never let the original absolute path rescue a load: they tamper
the copy while the original is intact, and the subprocess test audits every file open for the original tree.)
Offline; fixture data; the committed historical evidence is only read.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from atlas_ui import app as appmod
from atlas_ui import research
from atlas_ui.__main__ import build
from test_research_assessment import env, facts_doc, run  # noqa: F401  (fixtures/helpers)

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "atlas_ui" / "data" / "live"
COMMITTED = LIVE / "research"
NAMES = ("MCD", "GEV", "RMD", "ORCL")
# Historical evidence written 2026-10-29: its index lines and snapshot bytes must never change.
HISTORICAL_INDEX_PREFIX_SHA256 = "96a3c536397bb4259a5f78b15056f7143b8c6389461a2da983dda233aec3a606"  # first 4 lines of research_index.jsonl
HISTORICAL_SNAPSHOT_SHA256 = {
    "GEV": "f7defbab60d027184469401de6347163fa99d7267c95b4bfd48b2f2d05ddf021",
    "MCD": "99f601bede6c07a31bf3f369f6f8616c2d7857287951001a6a11ef1c2261e5a9",
    "ORCL": "e6f00cdbdadd9b101e969616bfc9e0025cd657c6d7d4a00d5ef79455afa266c2",
    "RMD": "c34f98a51b913244f4341d7347c7ef6dc56f7198e1753b6e779419c8ac260421",
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rows(rd: Path) -> list[dict]:
    return [json.loads(l) for l in (rd / "research_index.jsonl").read_text().splitlines() if l.strip()]


def write_rows(rd: Path, rs: list[dict]) -> None:
    (rd / "research_index.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rs))


# ---- new entries are portable ------------------------------------------------------------------------------------------------------------
def test_new_index_entries_hold_only_a_bare_file_name(env):
    run(env, facts_doc())
    (row,) = rows(env[1])
    assert set(row["snapshot"]) == {"sha256", "artifact_rel"} and "/" not in row["snapshot"]["artifact_rel"] and "\\" not in row["snapshot"]["artifact_rel"]
    text = (env[1] / "research_index.jsonl").read_text()
    assert str(env[1]) not in text and str(env[1].parent) not in text and "/private" not in text and "/Users" not in text


def test_a_moved_workspace_still_loads_and_resolves_inside_itself(env, tmp_path):
    run(env, facts_doc())
    moved = tmp_path / "somewhere" / "else" / "research"
    shutil.copytree(env[1], moved)
    shutil.rmtree(env[1])
    snap = research.latest_snapshot(moved, "XYZ")
    assert snap["data"]["ticker"] == "XYZ" and Path(snap["resolved_path"]).parent == moved.resolve()


def test_two_runs_keep_both_snapshots_and_serve_the_newest(env):
    run(env, facts_doc())
    run(env, facts_doc(), when=research.datetime(2026, 10, 30, 12, 0, tzinfo=research.timezone.utc))
    assert len(rows(env[1])) == 2 and len(list(env[1].glob("XYZ-*.json"))) == 2
    assert research.latest_snapshot(env[1], "XYZ")["recorded_at"].startswith("2026-10-30")


# ---- historical (absolute-path) entries: preserved byte for byte, resolved inside the workspace ---------------------------------------
def test_historical_evidence_is_byte_preserved():
    idx = (COMMITTED / "research_index.jsonl").read_bytes()
    assert sha(b"".join(idx.splitlines(keepends=True)[:4])) == HISTORICAL_INDEX_PREFIX_SHA256
    for t, h in HISTORICAL_SNAPSHOT_SHA256.items():
        (f,) = COMMITTED.glob(f"{t}-*.json")
        assert sha(f.read_bytes()) == h
    legacy = [json.loads(l) for l in idx.splitlines()[:4]]
    assert all("artifact_path" in r["snapshot"] and "artifact_rel" not in r["snapshot"] for r in legacy)  # the history was not rewritten


def test_all_four_committed_snapshots_load_from_a_copy_elsewhere_without_touching_the_original(tmp_path):
    dest = tmp_path / "x" / "y" / "research"
    shutil.copytree(COMMITTED, dest)
    for t in NAMES:
        s = research.latest_snapshot(dest, t)
        assert s is not None and Path(s["resolved_path"]).parent == dest.resolve() and s["data"]["ticker"] == t
        assert sha(Path(s["resolved_path"]).read_bytes()) == HISTORICAL_SNAPSHOT_SHA256[t] == s["snapshot"]["sha256"]


def test_the_original_absolute_path_is_never_consulted(tmp_path):
    """The original files are intact on this machine. A tampered COPY must still be refused: the old absolute path cannot rescue the load."""
    dest = tmp_path / "copy"
    shutil.copytree(COMMITTED, dest)
    (f,) = dest.glob("MCD-*.json")
    f.write_text(f.read_text().replace("MCD", "MCX", 1))
    with pytest.raises(research.ResearchIntegrityError, match="SHA-256"):
        research.latest_snapshot(dest, "MCD")
    (g,) = dest.glob("GEV-*.json")
    g.unlink()
    with pytest.raises(research.ResearchIntegrityError, match="missing"):
        research.latest_snapshot(dest, "GEV")


def test_a_windows_style_or_foreign_absolute_legacy_path_resolves_by_name_inside_the_workspace(env):
    run(env, facts_doc())
    rs = rows(env[1])
    name = rs[0]["snapshot"].pop("artifact_rel")
    for foreign in (f"C:\\Users\\someone\\atlas\\research\\{name}", f"/home/other/atlas/research/{name}", f"/nonexistent/{name}"):
        rs[0]["snapshot"]["artifact_path"] = foreign
        write_rows(env[1], rs)
        assert Path(research.latest_snapshot(env[1], "XYZ")["resolved_path"]).name == name


# ---- explicit errors, never silent "no research" ---------------------------------------------------------------------------------------
def test_absent_is_none_but_untrustworthy_is_an_error(env, tmp_path):
    assert research.latest_snapshot(tmp_path / "nowhere", "XYZ") is None          # no index at all
    run(env, facts_doc())
    assert research.latest_snapshot(env[1], "OTHER") is None                       # index exists, nothing for this candidate
    (f,) = env[1].glob("XYZ-*.json")
    f.unlink()
    with pytest.raises(research.ResearchIntegrityError, match="missing"):
        research.latest_snapshot(env[1], "XYZ")


def test_a_corrupt_newest_snapshot_is_never_replaced_by_an_older_valid_one(env):
    run(env, facts_doc())
    run(env, facts_doc(), when=research.datetime(2026, 10, 30, 12, 0, tzinfo=research.timezone.utc))
    newest = sorted(env[1].glob("XYZ-*.json"))[-1]
    newest.write_text(newest.read_text() + " ")
    with pytest.raises(research.ResearchIntegrityError, match="SHA-256"):
        research.latest_snapshot(env[1], "XYZ")


def test_an_unreadable_index_line_is_an_error_not_an_empty_index(env):
    run(env, facts_doc())
    with open(env[1] / "research_index.jsonl", "a") as fh:
        fh.write("{not json\n")
    with pytest.raises(research.ResearchIntegrityError, match="line 2"):
        research.latest_snapshot(env[1], "XYZ")


def test_a_snapshot_bound_to_another_security_is_refused(tmp_path):
    dest = tmp_path / "copy"
    shutil.copytree(COMMITTED, dest)
    rs = rows(dest)
    mcd = next(r for r in rs if r["candidate_id"] == "MCD")
    gev = next(r for r in rs if r["candidate_id"] == "GEV")
    gev["snapshot"] = dict(mcd["snapshot"])  # GEV's index entry now designates MCD's (genuine, correctly hashed) file
    write_rows(dest, rs)
    with pytest.raises(research.ResearchIntegrityError, match="belongs to MCD"):
        research.latest_snapshot(dest, "GEV")


# ---- malicious references --------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("bad", ["../outside.json", "/etc/passwd", "/abs/outside.json", "sub/dir.json", "a\\b.json", "..", ".", "",
                                 ".hidden.json", "snapshot.txt", "x.json\x00.txt", "..\\outside.json", "%2e%2e/outside.json"])
def test_malicious_artifact_rel_is_refused(env, bad):
    run(env, facts_doc())
    outside = env[1].parent / "outside.json"
    outside.write_text(json.dumps({"ticker": "XYZ"}))
    rs = rows(env[1])
    rs[0]["snapshot"] = {"sha256": sha(outside.read_bytes()), "artifact_rel": bad}   # even with a matching hash
    write_rows(env[1], rs)
    with pytest.raises(research.ResearchIntegrityError):
        research.latest_snapshot(env[1], "XYZ")


def test_legacy_path_with_traversal_is_refused(env):
    run(env, facts_doc())
    outside = env[1].parent / "outside.json"
    outside.write_text("{}")
    rs = rows(env[1])
    rs[0]["snapshot"] = {"sha256": sha(outside.read_bytes()), "artifact_path": f"{env[1]}/../outside.json"}
    write_rows(env[1], rs)
    with pytest.raises(research.ResearchIntegrityError, match="traversal"):
        research.latest_snapshot(env[1], "XYZ")


def test_a_symlinked_snapshot_is_refused_even_with_the_right_hash(env):
    run(env, facts_doc())
    (f,) = env[1].glob("XYZ-*.json")
    outside = env[1].parent / "outside_real.json"
    outside.write_bytes(f.read_bytes())
    f.unlink()
    f.symlink_to(outside)
    with pytest.raises(research.ResearchIntegrityError, match="symbolic link"):
        research.latest_snapshot(env[1], "XYZ")


def test_missing_or_malformed_sha_is_refused(env):
    run(env, facts_doc())
    for bad in (None, "", "abc", "G" * 64, 123):
        rs = rows(env[1])
        rs[0]["snapshot"]["sha256"] = bad
        write_rows(env[1], rs)
        with pytest.raises(research.ResearchIntegrityError):
            research.latest_snapshot(env[1], "XYZ")


# ---- the UI shows the failure; it does not read it as "no research" -------------------------------------------------------------------
def test_ui_and_api_surface_an_integrity_failure_instead_of_hiding_it(tmp_path):
    app = build(True, tmp_path / "d")
    rd = appmod.research_dir(app)
    rd.mkdir(parents=True, exist_ok=True)
    shutil.copytree(COMMITTED, rd, dirs_exist_ok=True)
    # the demo workspace has its own candidate ids; bind the committed MCD row to the demo ledger's MCD
    from operating_mvp import ledger
    assert "MCD" in ledger.replay(app.ws.candidate_ledger)
    ok_page = appmod.cohort_page(app)
    assert "RESEARCH EVIDENCE ERROR" not in ok_page
    (f,) = rd.glob("MCD-*.json")
    f.write_text(f.read_text() + " ")
    page = appmod.cohort_page(app)
    assert "RESEARCH EVIDENCE ERROR" in page and "SHA-256" in page
    api = {r["candidate_id"]: r for r in appmod.api_cohort(app)}
    assert api["MCD"]["research_error"] and api["MCD"]["snapshot_sha256"] is None
    assert api["GEV"]["research_error"] is None if "GEV" in api else True
    cand = ledger.replay(app.ws.candidate_ledger)["MCD"]
    panel = appmod.assessment_panel(app, cand)
    assert "RESEARCH EVIDENCE UNAVAILABLE" in panel and "not an absence of research" in panel


# ---- clean extraction in a different directory, original tree audited ------------------------------------------------------------------
def _copy_tree(dest: Path) -> None:
    shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".git", ".venv", "venv", "deliverables", "__pycache__", ".pytest_cache", ".env", ".env.*",
                                                              "*.pyc", "*.zip"))


EXTRACT_SCRIPT = r"""
import os, sys
orig = Path = None
from pathlib import Path
here = Path(os.getcwd()).resolve()
original_root = os.environ["ATLAS_ORIGINAL_ROOT"]
touched = []
def hook(event, args):
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.fsdecode(args[0])
        # the interpreter's own packages (.venv) legitimately live in the original tree; the PROJECT's files must not be read from it
        if p.startswith(original_root) and not p.startswith(original_root + "/.venv") and "/__pycache__/" not in p:
            touched.append(p)
sys.addaudithook(hook)
sys.path.insert(0, str(here))
from atlas_ui import app as appmod, research
from atlas_ui.__main__ import build
app = build(False, root=here / "atlas_ui" / "data" / "live", candidate_ledger=here / "operating_mvp" / "data" / "candidate_ledger.jsonl")
rd = appmod.research_dir(app)
assert rd.resolve() == (here / "atlas_ui" / "data" / "live" / "research").resolve(), rd
for t in ("MCD", "GEV", "RMD", "ORCL"):
    s = research.latest_snapshot(rd, t)
    assert s is not None, t
    assert Path(s["resolved_path"]).resolve().is_relative_to(here), s["resolved_path"]
page = appmod.cohort_page(app)
assert "RESEARCH EVIDENCE ERROR" not in page
for t in ("MCD", "GEV", "RMD", "ORCL"):
    assert f">{t}</a>" in page, t
api = {r["candidate_id"]: r for r in appmod.api_cohort(app)}
assert all(api[t]["snapshot_sha256"] and api[t]["research_error"] is None for t in ("MCD", "GEV", "RMD", "ORCL")), api
assert "$250.5" in page and "$878.03" in page and "$250.17" in page and "$144.54" in page, "bound prices missing from the cohort page"
for t in ("MCD", "GEV", "RMD", "ORCL"):
    panel = appmod.assessment_panel(app, __import__("operating_mvp.ledger", fromlist=["x"]).replay(app.ws.candidate_ledger)[t])
    assert "RESEARCH EVIDENCE UNAVAILABLE" not in panel and "SEC EDGAR company facts" in panel, t
assert not touched, f"read files from the ORIGINAL tree: {touched[:3]}"
print("OK all four loaded, rendered, and nothing was read from", original_root)
"""


def test_clean_extraction_in_a_different_directory_loads_and_renders_all_four(tmp_path):
    dest = tmp_path / "unzipped" / "stock-atlas"
    _copy_tree(dest)
    env_ = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST") and k != "PYTHONPATH"}
    env_["ATLAS_ORIGINAL_ROOT"] = str(ROOT)
    r = subprocess.run([sys.executable, "-c", EXTRACT_SCRIPT], cwd=dest, env=env_, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0 and r.stdout.startswith("OK all four"), r.stdout + r.stderr


def test_the_extracted_trees_own_research_tests_pass_there(tmp_path):
    dest = tmp_path / "unzipped" / "stock-atlas"
    _copy_tree(dest)
    env_ = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST") and k != "PYTHONPATH"}
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_research_assessment.py", "tests/test_research_portability.py",
                        "-k", "not clean_extraction and not extracted_trees_own"],
                       cwd=dest, env=env_, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-1000:]
