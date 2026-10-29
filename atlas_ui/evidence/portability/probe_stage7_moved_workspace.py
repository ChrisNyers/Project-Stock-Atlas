"""Probe: does a Stage 7 run survive moving its workspace to another directory? (run: python atlas_ui/evidence/portability/probe_stage7_moved_workspace.py)"""
import shutil, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
from atlas_ui.__main__ import build
from atlas_ui.service import Rejected
from test_atlas_ui import good_req, s8
now = datetime.now(timezone.utc)
a = Path(tempfile.mkdtemp(prefix="atlas_a_")) / "ws"
app = build(True, a)
e = app.svc.run(good_req(), now)
print("run created in", a, "| verified there:", app.svc.list_runs()[0]["verified"])
b = Path(tempfile.mkdtemp(prefix="atlas_b_")) / "ws"
shutil.move(str(a), str(b))
moved = build(True, b)
r = moved.svc.list_runs()[0]
print("moved to", b, "(old location removed) | verified:", r["verified"], "|", r["verify_note"][:110])
try:
    moved.svc.record_stage8(e["run_id"], s8(), now)
    print("funded INITIATE after the move: ACCEPTED")
except Rejected as exc:
    print("funded INITIATE after the move: REJECTED —", str(exc)[:110])
