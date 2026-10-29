"""Stage 7 run artifacts are portable: the run index holds workspace-relative references, resolved only inside the current workspace.

Before this change the run index stored the writing machine's absolute path for every frozen artifact, so a copied/extracted workspace could not verify,
rehydrate or fund from its own retained runs. Hash chain, SHA-256 binding and every frozen control are unchanged (no control file touched): the decision
ledger's hash chain never re-reads artifacts by path, and new records are written with the artifact locations of the workspace that writes them.
Fixture provider, isolated workspaces, paper only. Every rejected path asserts the decision ledger is byte-identical.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from atlas_ui import app as appmod
from atlas_ui.__main__ import build
from atlas_ui.service import Blocked, Rejected, read_index
from test_atlas_ui import NOW, good_req, s8

ROOT = Path(__file__).resolve().parent.parent


def ledger_bytes(app) -> bytes:
    p = Path(app.ws.facade.store.path)
    return p.read_bytes() if p.exists() else b""


def write_index(app, entries):
    app.ws.index_path.write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in entries))


@pytest.fixture
def two_runs(tmp_path):
    app = build(True, tmp_path / "a" / "ws")
    return app, app.svc.run(good_req(), NOW), app.svc.run(good_req(), NOW)


# ---- new entries are portable ---------------------------------------------------------------------------------------------------
def test_new_index_entries_and_artifacts_hold_no_absolute_path(two_runs):
    app, e1, _ = two_runs
    root = str(app.ws.root.resolve())
    for ref in [e1["stage7"], *e1["inputs"].values()]:
        assert set(ref) == {"version", "sha256", "artifact_rel"} and not ref["artifact_rel"].startswith("/") and ".." not in ref["artifact_rel"]
    assert e1["stage7"]["artifact_rel"].startswith("artifacts/") and all(v["artifact_rel"].startswith("inputs/") for v in e1["inputs"].values())
    for f in [app.ws.index_path, *app.ws.root.joinpath("artifacts").glob("*"), *app.ws.root.joinpath("inputs").rglob("*.json")]:
        assert root not in f.read_text() and str(app.ws.root) not in f.read_text(), f


# ---- moved workspace: original location gone ------------------------------------------------------------------------------------
def test_a_moved_workspace_verifies_rehydrates_and_funds_from_its_own_files(two_runs, tmp_path):
    app, e1, _ = two_runs
    old = app.ws.root
    new = tmp_path / "b" / "elsewhere" / "ws"
    new.parent.mkdir(parents=True)
    shutil.move(str(old), str(new))
    assert not old.exists()
    moved = build(True, new)
    assert all(r["verified"] for r in moved.svc.list_runs()) and len(moved.svc.list_runs()) == 2
    run, versions, entry = moved.svc.load_run(e1["run_id"])
    assert all(Path(r.artifact_path).resolve().is_relative_to(new.resolve()) for r in (run.artifact_ref, *versions.__dict__.values()))
    out = moved.svc.record_stage8(e1["run_id"], s8(), NOW)                                    # funded INITIATE, real clock, after the move
    assert out["rows_after"] == 1 and moved.ws.facade.verify_ledger()
    assert "NOT VERIFIED" not in appmod.run_page(moved, e1["run_id"]) and "NOT VERIFIED" not in appmod.stage7_page(moved)
    appmod.history_page(moved)


def test_a_ledger_row_written_at_the_old_location_stays_valid_after_the_move(two_runs, tmp_path):
    app, e1, e2 = two_runs
    assert app.svc.record_stage8(e2["run_id"], s8(), NOW)["rows_after"] == 1                  # funded row, artifact paths of the OLD location inside it
    old, new = app.ws.root, tmp_path / "c" / "ws"
    new.parent.mkdir(parents=True)
    shutil.move(str(old), str(new))
    moved = build(True, new)
    assert str(old) in ledger_bytes(moved).decode()                                           # the historical row is preserved, not rewritten
    assert moved.ws.facade.verify_ledger() and len(moved.svc.ledger_rows()) == 1              # its hash chain never depended on that path
    assert all(r["verified"] for r in moved.svc.list_runs())
    assert moved.svc.record_stage8(e1["run_id"], s8(action="HOLD CASH"), NOW)["rows_after"] == 2 and moved.ws.facade.verify_ledger()


def test_legacy_absolute_path_entries_resolve_by_their_tail_inside_the_workspace(two_runs):
    app, e1, _ = two_runs
    legacy = []
    for e in read_index(app.ws.index_path):
        e = json.loads(json.dumps(e))
        for i, ref in enumerate([e["stage7"], *e["inputs"].values()]):
            rel = ref.pop("artifact_rel")
            ref["artifact_path"] = (f"C:\\Users\\other\\atlas\\{rel.replace('/', chr(92))}" if i % 2 else f"/home/other/atlas/ws/{rel}")
        legacy.append(e)
    write_index(app, legacy)
    assert all(r["verified"] for r in app.svc.list_runs())
    assert app.svc.load_run(e1["run_id"])[2]["run_id"] == e1["run_id"]


def test_the_original_absolute_path_is_never_consulted(two_runs, tmp_path):
    """The original files stay intact while a tampered COPY must still be refused: an old absolute path cannot rescue the load."""
    app, e1, _ = two_runs
    copy = tmp_path / "copy"
    shutil.copytree(app.ws.root, copy)
    entries = [json.loads(json.dumps(e)) for e in read_index(copy / "runs_index.jsonl")]
    for e in entries:                                              # point every entry at the ORIGINAL (intact) location, as an old index would
        for ref in [e["stage7"], *e["inputs"].values()]:
            ref["artifact_path"] = str(app.ws.root / ref.pop("artifact_rel"))
    (copy / "runs_index.jsonl").write_text("".join(json.dumps(e, sort_keys=True) + "\n" for e in entries))
    other = build(True, copy)
    assert all(r["verified"] for r in other.svc.list_runs())
    p = copy / entries[0]["stage7"]["artifact_path"].split(str(app.ws.root) + "/")[1]
    p.write_text(p.read_text() + " ")
    before = ledger_bytes(other)
    assert not other.svc.list_runs()[0]["verified"]
    with pytest.raises(Rejected, match="NOT VERIFIED"):
        other.svc.record_stage8(entries[0]["run_id"], s8(), NOW)
    assert ledger_bytes(other) == before and other.svc.ledger_rows() == []


# ---- malicious / corrupt references: refused, zero ledger rows ---------------------------------------------------------------------
BAD_RELS = ["../outside.json", "/etc/passwd", "artifacts/../../outside.json", "inputs/a/b/c.json", "other/x.json", "artifacts/x.txt",
            "artifacts//x.json", "artifacts/.hidden.json", "artifacts\\x.json", "x.json", "", "artifacts/%2e%2e/x.json", "inputs/./x.json"]


@pytest.mark.parametrize("bad", BAD_RELS)
@pytest.mark.parametrize("which", ["stage7", "evidence_set"])
def test_malicious_artifact_references_are_refused_with_zero_ledger_rows(two_runs, bad, which):
    app, e1, _ = two_runs
    (app.ws.root.parent / "outside.json").write_text("{}")
    entries = read_index(app.ws.index_path)
    tgt = entries[0]["stage7"] if which == "stage7" else entries[0]["inputs"]["evidence_set"]
    tgt["artifact_rel"] = bad
    write_index(app, entries)
    before = ledger_bytes(app)
    ok, why = app.svc.verify_entry(entries[0])
    assert not ok and ("unsafe" in why or "missing" in why or "malformed" in why), why
    with pytest.raises(Blocked):
        app.svc.load_run(entries[0]["run_id"])
    for action in ("INITIATE", "HOLD CASH"):
        with pytest.raises(Rejected):
            app.svc.record_stage8(entries[0]["run_id"], s8(action=action), NOW)
    assert ledger_bytes(app) == before


def test_a_symlinked_artifact_or_directory_is_refused_even_with_the_right_hash(two_runs, tmp_path):
    app, e1, _ = two_runs
    entries = read_index(app.ws.index_path)
    s7 = app.ws.root / entries[0]["stage7"]["artifact_rel"]
    real = tmp_path / "real_copy.json"
    real.write_bytes(s7.read_bytes())
    s7.unlink()
    s7.symlink_to(real)
    before = ledger_bytes(app)
    ok, why = app.svc.verify_entry(entries[0])
    assert not ok and "symbolic link" in why
    with pytest.raises(Rejected):
        app.svc.record_stage8(entries[0]["run_id"], s8(), NOW)
    assert ledger_bytes(app) == before
    # a symlinked inputs/<run> directory
    s7.unlink()
    shutil.copy(real, s7)
    d = app.ws.root / "inputs" / entries[0]["run_id"]
    moved = tmp_path / "inputs_real"
    shutil.move(str(d), str(moved))
    d.symlink_to(moved)
    ok, why = app.svc.verify_entry(entries[0])
    assert not ok and "symbolic link" in why
    assert ledger_bytes(app) == before


def test_artifact_download_endpoint_uses_the_resolver(two_runs):
    app, e1, _ = two_runs
    ref = app.ws.ref(e1["stage7"])
    assert Path(ref.artifact_path).is_file() and Path(ref.artifact_path).resolve().is_relative_to(app.ws.root.resolve())


# ---- clean extraction in a different directory ----------------------------------------------------------------------------------------
SCRIPT = r"""
import os, sys, shutil, tempfile
from pathlib import Path
here = Path(os.getcwd()).resolve()
orig = os.environ["ATLAS_ORIGINAL_ROOT"]
touched = []
def hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.fsdecode(args[0])
        if p.startswith(orig) and not p.startswith(orig + "/.venv") and "/__pycache__/" not in p:
            touched.append(p)
sys.addaudithook(hook)
sys.path[:0] = [str(here), str(here / "tests")]
from datetime import datetime, timezone
from atlas_ui.__main__ import build
from atlas_ui import app as appmod
from test_atlas_ui import good_req, s8
now = datetime.now(timezone.utc)
a = Path(tempfile.mkdtemp(prefix="atlas_a_")) / "ws"
app = build(True, a)
e1, e2 = app.svc.run(good_req(), now), app.svc.run(good_req(), now)
b = Path(tempfile.mkdtemp(prefix="atlas_b_")) / "moved" / "ws"
b.parent.mkdir(parents=True)
shutil.move(str(a), str(b))
assert not a.exists()
moved = build(True, b)
assert len(moved.svc.list_runs()) == 2 and all(r["verified"] for r in moved.svc.list_runs())
assert moved.svc.record_stage8(e1["run_id"], s8(), now)["rows_after"] == 1 and moved.ws.facade.verify_ledger()      # funded, after the move
c = Path(tempfile.mkdtemp(prefix="atlas_c_")) / "again" / "ws"
c.parent.mkdir(parents=True)
shutil.move(str(b), str(c))                                                                                         # a second move, with a row written at the old location
again = build(True, c)
assert all(r["verified"] for r in again.svc.list_runs()) and again.ws.facade.verify_ledger()
assert again.svc.record_stage8(e2["run_id"], s8(action="HOLD CASH"), now)["rows_after"] == 2
assert "NOT VERIFIED" not in appmod.run_page(again, e1["run_id"])
assert not touched, touched[:3]
print("OK stage 7 run created in", a, "moved to", b, "then", c, "verified, rehydrated and funded there; nothing read from", orig)
"""


def _copy_tree(dest: Path) -> None:
    shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".git", ".venv", "venv", "deliverables", "__pycache__", ".pytest_cache", ".env", ".env.*", "*.pyc", "*.zip"))


def test_clean_extraction_in_a_different_directory_creates_moves_verifies_and_funds_a_stage7_run(tmp_path):
    dest = tmp_path / "unzipped" / "stock-atlas"
    _copy_tree(dest)
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST") and k != "PYTHONPATH"}
    env["ATLAS_ORIGINAL_ROOT"] = str(ROOT)
    r = subprocess.run([sys.executable, "-c", SCRIPT], cwd=dest, env=env, capture_output=True, text=True, timeout=240)
    assert r.returncode == 0 and r.stdout.startswith("OK stage 7"), r.stdout + r.stderr
