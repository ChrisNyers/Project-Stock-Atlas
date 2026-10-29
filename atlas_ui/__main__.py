"""python -m atlas_ui serve [--demo] [--port N] | matrix | preflight | verify | deliver"""
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


def _load_key(env_file):
    if env_file and not (os.environ.get("TWELVEDATA_API_KEY") or "").strip():
        for line in Path(env_file).read_text(encoding="utf-8").splitlines():
            k, _, v = line.strip().partition("=")
            if k.strip() == "TWELVEDATA_API_KEY" and v.strip().strip("\"'"):
                os.environ["TWELVEDATA_API_KEY"] = v.strip().strip("\"'")


def research_cmd(candidate: str, env_file, no_price: bool) -> int:
    import json
    from datetime import datetime, timezone
    from . import research
    from .service import Blocked
    _load_key(env_file)
    app = build(False)
    now = datetime.now(timezone.utc)
    pe = None
    c = mvp_ledger.replay(app.ws.candidate_ledger).get(candidate)
    if c is None:
        print(f"unknown candidate {candidate!r}")
        return 2
    if not no_price:
        try:
            pe = app.svc.bind_price(c["ticker"], now).to_dict()
        except Blocked as exc:
            print("price BLOCKED —", exc)
    try:
        r = research.research_candidate(app.ws.candidate_ledger, candidate, app.ws.root / "research", decision_time=now, price_evidence=pe)
    except research.ResearchError as exc:
        print("RESEARCH STOPPED —", exc)
        return 2
    print(json.dumps({k: r[k] for k in ("candidate_id", "ticker", "security_key", "latest_fy_end", "evidence_added", "evidence_already_present", "gaps_recorded")}),
          "| price evidence:", "bound (Gate B)" if pe else "none (BLOCKED)")
    return 0


def live_check(ticker: str, env_file: str | None, out: str | None) -> int:
    """Read-only Gate B diagnostic. Never prints the key; refuses to run without one; writes nothing but the optional sanitized JSON."""
    import json
    from datetime import datetime, timezone
    if env_file and not (os.environ.get("TWELVEDATA_API_KEY") or "").strip():
        for line in Path(env_file).read_text(encoding="utf-8").splitlines():
            k, _, v = line.strip().partition("=")
            if k.strip() == "TWELVEDATA_API_KEY" and v.strip().strip("\"'"):
                os.environ["TWELVEDATA_API_KEY"] = v.strip().strip("\"'")
    app = build(False)
    from .service import Blocked
    now = datetime.now(timezone.utc)
    try:
        ev = app.svc.bind_price(ticker.strip().upper(), now)
    except Blocked as exc:
        from live_price_binding import redact
        print("BLOCKED —", redact(str(exc)))
        return 2
    d = ev.to_dict()
    d["check"] = {"mode": "READ-ONLY", "decision_time_utc": now.isoformat(), "stage7_started": False, "decision_written": False,
                  "key_in_this_file": False}
    text = json.dumps(d, indent=2, default=str)
    key = os.environ.get("TWELVEDATA_API_KEY", "")
    assert not key or key not in text, "credential leaked into evidence; refusing to emit"
    if out:
        Path(out).write_text(text, encoding="utf-8")
    s = ev.snapshot
    print(f"BOUND {s.ticker} {s.price:g} {s.currency} provider={s.provider} price_session={s.price_session_date} "
          f"latest_completed={s.latest_completed_session_date} freshness={s.freshness_status.value} "
          f"calendar={ev.attestation.calendar_name} exchange={ev.attestation.exchange} security_key={s.security_key}")
    return 0


def main(argv=None):
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("preflight", "verify", "deliver"):  # source-of-truth tooling (atlas_ui/verify.py)
        from . import verify
        return verify.main(argv)
    ap = argparse.ArgumentParser(prog="atlas_ui")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve"); s.add_argument("--demo", action="store_true"); s.add_argument("--port", type=int, default=8770)
    s.add_argument("--board-port", type=int, default=8765)
    sub.add_parser("matrix")
    rs = sub.add_parser("research", help="SEC company facts -> evidence ledger + retained snapshot (+ Gate B price if a key is available)")
    rs.add_argument("candidate"); rs.add_argument("--env-file"); rs.add_argument("--no-price", action="store_true")
    lc = sub.add_parser("live-check", help="READ-ONLY Gate B price/identity/XNYS check; starts no Stage 7 and writes no decision")
    lc.add_argument("ticker"); lc.add_argument("--env-file", help="optional .env to read TWELVEDATA_API_KEY from (value is never printed)")
    lc.add_argument("--out", help="write the sanitized evidence JSON here")
    x = ap.parse_args(argv)
    if x.cmd == "matrix":
        print(appmod.matrix_markdown())
        return 0
    if x.cmd == "research":
        return research_cmd(x.candidate, x.env_file, x.no_price)
    if x.cmd == "live-check":
        return live_check(x.ticker, x.env_file, x.out)
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
