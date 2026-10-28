"""python -m atlas_ui serve [--demo] [--port N] | matrix"""
import argparse
import os
import tempfile
import threading
from pathlib import Path

from operating_mvp import ledger as mvp_ledger
from operating_mvp import ui as mvp_ui

from . import app as appmod
from . import demo
from .service import Stage7Service, Workspace

REPO = Path(__file__).resolve().parent.parent
CANONICAL_ROOT = REPO / "atlas_ui" / "data" / "live"


def build(demo_mode: bool, root: Path | None = None, candidate_ledger: Path | None = None) -> appmod.App:
    if demo_mode:
        root = Path(root or tempfile.mkdtemp(prefix="atlas_ui_demo_"))
        demo.seed_demo_workspace(root, mvp_ledger.DEFAULT_LEDGER)
        ws = Workspace(root, "DEMO", candidate_ledger=root / "candidate_ledger.jsonl")
        svc = Stage7Service(ws, provider_factory=demo.FixtureProvider, identity_fn=lambda t: demo.DEMO_KEY,
                            allowed_providers={demo.DEMO_PROVIDER}, key_present=lambda: True)
        return appmod.App(ws, svc)
    root = Path(root or CANONICAL_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    # Canonical mode reads/writes the SAME discovery ledger the Discovery board uses (no copy, no second store).
    ws = Workspace(root, "CANONICAL", candidate_ledger=Path(candidate_ledger or mvp_ledger.DEFAULT_LEDGER))

    def provider():
        import market_data_providers as mdp
        return mdp.TwelveDataProvider()

    def identity(t):
        from identity_resolver import market_price_join_key
        return market_price_join_key(t)

    svc = Stage7Service(ws, provider_factory=provider, identity_fn=identity, allowed_providers={"twelvedata"},
                        key_present=lambda: bool((os.environ.get("TWELVEDATA_API_KEY") or "").strip()))
    return appmod.App(ws, svc)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="atlas_ui")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve"); s.add_argument("--demo", action="store_true"); s.add_argument("--port", type=int, default=8770)
    s.add_argument("--board-port", type=int, default=8765)
    sub.add_parser("matrix")
    x = ap.parse_args(argv)
    if x.cmd == "matrix":
        print(appmod.matrix_markdown())
        return 0
    app = build(x.demo)
    mvp_ui.Handler.ledger_path = app.ws.candidate_ledger
    from http.server import ThreadingHTTPServer
    board = ThreadingHTTPServer(("127.0.0.1", x.board_port), mvp_ui.Handler)
    threading.Thread(target=board.serve_forever, daemon=True).start()
    print(f"Discovery board (evidence ledger, same ledger) on http://127.0.0.1:{x.board_port}")
    appmod.serve(app, x.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
