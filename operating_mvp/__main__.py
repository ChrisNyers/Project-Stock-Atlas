"""CLI: python -m operating_mvp {seed|serve|render|verify|surface|state|note}"""
import argparse
import sys
from pathlib import Path

from . import ledger, seed, ui


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="operating_mvp")
    ap.add_argument("--ledger", default=str(ledger.DEFAULT_LEDGER))
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed", help="backfill MCD and RPM into an empty ledger")
    sub.add_parser("seed-evidence", help="append MCD/RPM template + evidence entries (backfilled)")
    sub.add_parser("verify", help="verify the hash chain")
    s = sub.add_parser("serve"); s.add_argument("--port", type=int, default=8765)
    r = sub.add_parser("render", help="write a static, non-interactive board"); r.add_argument("out")
    a = sub.add_parser("surface")
    a.add_argument("--name", required=True); a.add_argument("--ticker", default="")
    a.add_argument("--source", required=True, choices=ledger.SOURCES); a.add_argument("--source-detail", default="")
    a.add_argument("--why", required=True); a.add_argument("--question", required=True)
    t = sub.add_parser("state")
    t.add_argument("candidate_id"); t.add_argument("to_state", choices=ledger.STATES); t.add_argument("--reason", required=True)
    t.add_argument("--waiting-on", default=""); t.add_argument("--until", default="")
    t.add_argument("--verified", action="store_true"); t.add_argument("--revisit-question", action="append", default=[])
    q = sub.add_parser("falsify"); q.add_argument("candidate_id"); q.add_argument("--test", required=True)
    q.add_argument("--result", required=True, choices=ledger.FALSIFICATION_RESULTS)
    q.add_argument("--grade", required=True, choices=ledger.GRADES); q.add_argument("--ref", default=""); q.add_argument("--known-at", default="")
    v = sub.add_parser("evidence"); v.add_argument("candidate_id"); v.add_argument("--tag", required=True, choices=ledger.EVIDENCE_TAGS)
    v.add_argument("--direction", required=True, choices=ledger.DIRECTIONS); v.add_argument("--grade", required=True, choices=ledger.GRADES)
    v.add_argument("--text", required=True); v.add_argument("--ref", default=""); v.add_argument("--known-at", default="")
    u = sub.add_parser("unresolved"); u.add_argument("candidate_id"); u.add_argument("question")
    rs = sub.add_parser("resolve"); rs.add_argument("candidate_id"); rs.add_argument("target_seq", type=int)
    rs.add_argument("status", choices=("RESOLVED", "RETRACTED")); rs.add_argument("--note", required=True)
    st = sub.add_parser("strongest"); st.add_argument("candidate_id"); st.add_argument("direction", choices=("FOR", "AGAINST")); st.add_argument("target_seq", type=int)
    n = sub.add_parser("note"); n.add_argument("candidate_id"); n.add_argument("text")
    x = ap.parse_args(argv)
    path = Path(x.ledger)
    try:
        if x.cmd == "seed":
            print(f"seeded {seed.seed(path)} events")
        elif x.cmd == "seed-evidence":
            print(f"appended {seed.seed_evidence(path)} events")
        elif x.cmd == "verify":
            ledger.verify_chain(path); print("ledger chain OK")
        elif x.cmd == "serve":
            ui.serve(x.port, path)
        elif x.cmd == "render":
            Path(x.out).write_text(ui.render_board(path, interactive=False), encoding="utf-8"); print(x.out)
        elif x.cmd == "surface":
            ev = ledger.surface(path, name=x.name, ticker=x.ticker, source=x.source, source_detail=x.source_detail,
                                why_surfaced=x.why, investment_question=x.question)
            print("surfaced", ev["candidate_id"])
        elif x.cmd == "state":
            ledger.change_state(path, candidate_id=x.candidate_id, to_state=x.to_state, reason=x.reason,
                                waiting_on=x.waiting_on, parked_until=x.until or None,
                                parked_until_verified=x.verified, revisit_questions=x.revisit_question)
            print("recorded")
        elif x.cmd == "falsify":
            ledger.record_falsification(path, candidate_id=x.candidate_id, test=x.test, result=x.result,
                                        grade=x.grade, source_ref=x.ref, known_at=x.known_at); print("recorded")
        elif x.cmd == "evidence":
            ledger.add_evidence(path, candidate_id=x.candidate_id, tag=x.tag, direction=x.direction, grade=x.grade,
                                text=x.text, source_ref=x.ref, known_at=x.known_at); print("recorded")
        elif x.cmd == "unresolved":
            ledger.add_unresolved(path, candidate_id=x.candidate_id, question=x.question); print("recorded")
        elif x.cmd == "resolve":
            ledger.resolve_item(path, candidate_id=x.candidate_id, target_seq=x.target_seq, status=x.status, note=x.note); print("recorded")
        elif x.cmd == "strongest":
            ledger.set_strongest(path, candidate_id=x.candidate_id, direction=x.direction, target_seq=x.target_seq); print("recorded")
        elif x.cmd == "note":
            ledger.add_note(path, candidate_id=x.candidate_id, text=x.text); print("recorded")
    except ledger.LedgerError as exc:
        print(f"error: {exc}", file=sys.stderr); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
