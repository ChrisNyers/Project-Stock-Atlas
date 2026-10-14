"""Discovery Loop v0.1 — append-only candidate ledger.

One vocabulary:  SURFACED -> QUICK_TEST -> UNDERWRITING
                 -> PARKED / REJECTED / READY_FOR_CAPITAL_COMPARISON
"Continue underwriting" is remaining in UNDERWRITING, recorded as a NOTE.

Source is recorded for provenance. It is never used to order, filter, weight
or gate anything. READY_FOR_CAPITAL_COMPARISON is a label only: it triggers no
Stage 7, no Stage 8 and no capital action (Human Stage 8 is the sole authority).
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

GENESIS_HASH = "0" * 64
DEFAULT_LEDGER = Path(__file__).parent / "data" / "candidate_ledger.jsonl"

STATES = (
    "SURFACED",
    "QUICK_TEST",
    "UNDERWRITING",
    "PARKED",
    "REJECTED",
    "READY_FOR_CAPITAL_COMPARISON",
)
SOURCES = ("HUMAN", "SCOUT", "SUE", "NUTSTUFF", "OTHER")

# Workflow edges. SURFACED -> UNDERWRITING is allowed because the human may
# order underwriting directly (Cycles 1-2 did); QUICK_TEST is optional.
TRANSITIONS = {
    "SURFACED": {"QUICK_TEST", "UNDERWRITING", "PARKED", "REJECTED"},
    "QUICK_TEST": {"UNDERWRITING", "PARKED", "REJECTED"},
    "UNDERWRITING": {"PARKED", "REJECTED", "READY_FOR_CAPITAL_COMPARISON"},
    "PARKED": {"QUICK_TEST", "UNDERWRITING", "REJECTED"},
    "REJECTED": {"SURFACED"},  # re-open only with a stated reason
    "READY_FOR_CAPITAL_COMPARISON": {"UNDERWRITING", "PARKED", "REJECTED"},
}


class LedgerError(ValueError):
    pass


def _hash(prev: str, body: dict) -> str:
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((prev + blob).encode("utf-8")).hexdigest()


def read_events(path: Path = DEFAULT_LEDGER) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def verify_chain(path: Path = DEFAULT_LEDGER) -> None:
    """Raise LedgerError if any recorded event was edited, removed or reordered."""
    prev = GENESIS_HASH
    for i, ev in enumerate(read_events(path), start=1):
        body = {k: v for k, v in ev.items() if k not in ("prev_hash", "event_hash")}
        if ev.get("seq") != i or ev.get("prev_hash") != prev or ev.get("event_hash") != _hash(prev, body):
            raise LedgerError(f"ledger integrity failure at event {i}")
        prev = ev["event_hash"]


def _append(path: Path, event_type: str, candidate_id: str, effective_date: str,
            payload: dict, backfilled: bool = False) -> dict:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        existing = [json.loads(l) for l in fh.read().splitlines() if l.strip()]
        prev = existing[-1]["event_hash"] if existing else GENESIS_HASH
        body = {
            "seq": len(existing) + 1,
            "event_type": event_type,
            "candidate_id": candidate_id,
            "effective_date": effective_date,
            "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "backfilled": backfilled,
            "payload": payload,
        }
        ev = {**body, "prev_hash": prev, "event_hash": _hash(prev, body)}
        fh.seek(0, 2)
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev


def _clean(text) -> str:
    return (text or "").strip()


def _iso(d) -> str:
    if isinstance(d, date):
        return d.isoformat()
    try:
        return date.fromisoformat(_clean(d)).isoformat()
    except ValueError:
        raise LedgerError(f"invalid date: {d!r} (use YYYY-MM-DD)")


def _slug(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-")


def replay(path: Path = DEFAULT_LEDGER) -> dict[str, dict]:
    """Derive current candidate state by replaying the event log."""
    cands: dict[str, dict] = {}
    for ev in read_events(path):
        cid, p = ev["candidate_id"], ev["payload"]
        if ev["event_type"] == "SURFACED":
            c = cands.setdefault(cid, {"candidate_id": cid, "history": []})
            c.update(
                ticker=p.get("ticker", ""), name=p["name"], source=p["source"],
                source_detail=p.get("source_detail", ""), why_surfaced=p["why_surfaced"],
                investment_question=p["investment_question"], surfaced_on=ev["effective_date"],
                refs=list(p.get("refs", [])), state="SURFACED", state_since=ev["effective_date"],
                reason="", waiting_on="", parked_until="", parked_until_verified=False,
                revisit_questions=[], notes=[],
            )
        elif ev["event_type"] == "STATE_CHANGE":
            c = cands[cid]
            c.update(state=p["to_state"], state_since=ev["effective_date"], reason=p["reason"])
            if p["to_state"] == "PARKED":
                c.update(waiting_on=p["waiting_on"], parked_until=p.get("parked_until", ""),
                         parked_until_verified=bool(p.get("parked_until_verified")),
                         revisit_questions=list(p.get("revisit_questions", [])))
            else:
                c.update(waiting_on="", parked_until="", parked_until_verified=False,
                         revisit_questions=[])
            c["refs"] = c["refs"] + [r for r in p.get("refs", []) if r not in c["refs"]]
        elif ev["event_type"] == "NOTE":
            cands[cid]["notes"].append({"date": ev["effective_date"], "text": p["text"]})
            cands[cid]["refs"] += [r for r in p.get("refs", []) if r not in cands[cid]["refs"]]
        cands[cid]["history"].append(
            {"seq": ev["seq"], "type": ev["event_type"], "date": ev["effective_date"],
             "backfilled": ev["backfilled"],
             "summary": p.get("to_state") or p.get("text") or "SURFACED",
             "reason": p.get("reason", "")})
    return cands


def surface(path: Path = DEFAULT_LEDGER, *, name: str, source: str, why_surfaced: str,
            investment_question: str, ticker: str = "", source_detail: str = "",
            refs: list[str] | None = None, effective_date=None, backfilled: bool = False) -> dict:
    """Intake a new SURFACED idea. Source is provenance only."""
    name, ticker = _clean(name), _clean(ticker).upper()
    source = _clean(source).upper()
    if source not in SOURCES:
        raise LedgerError(f"source must be one of {SOURCES}")
    if source == "OTHER" and not _clean(source_detail):
        raise LedgerError("source OTHER requires source_detail")
    for label, val in (("name", name), ("why_surfaced", why_surfaced),
                       ("investment_question", investment_question)):
        if not _clean(val):
            raise LedgerError(f"{label} is required")
    cid = ticker or _slug(name)
    if not cid:
        raise LedgerError("name must contain letters or digits")
    existing = replay(path).get(cid)
    if existing and existing["state"] != "REJECTED":
        raise LedgerError(f"{cid} is already tracked (state {existing['state']}); "
                          "add a note or change its state instead of duplicating it")
    if existing:
        raise LedgerError(f"{cid} was REJECTED; re-open it with a state change to SURFACED and a reason")
    return _append(path, "SURFACED", cid, _iso(effective_date or date.today()), {
        "ticker": ticker, "name": name, "source": source, "source_detail": _clean(source_detail),
        "why_surfaced": _clean(why_surfaced), "investment_question": _clean(investment_question),
        "refs": [_clean(r) for r in (refs or []) if _clean(r)]}, backfilled)


def change_state(path: Path = DEFAULT_LEDGER, *, candidate_id: str, to_state: str, reason: str,
                 waiting_on: str = "", parked_until=None, parked_until_verified: bool = False,
                 revisit_questions: list[str] | None = None, refs: list[str] | None = None,
                 effective_date=None, backfilled: bool = False) -> dict:
    cands = replay(path)
    c = cands.get(candidate_id)
    if c is None:
        raise LedgerError(f"unknown candidate {candidate_id!r}")
    to_state = _clean(to_state).upper()
    if to_state not in STATES:
        raise LedgerError(f"state must be one of {STATES}")
    if to_state not in TRANSITIONS[c["state"]]:
        raise LedgerError(f"{c['state']} -> {to_state} is not an allowed transition "
                          f"(allowed: {sorted(TRANSITIONS[c['state']]) or 'none'})")
    if not _clean(reason):
        raise LedgerError("reason is required")
    payload = {"to_state": to_state, "reason": _clean(reason),
               "refs": [_clean(r) for r in (refs or []) if _clean(r)]}
    if to_state == "PARKED":
        if not _clean(waiting_on):
            raise LedgerError("PARKED requires waiting_on (the specific evidence awaited)")
        payload.update(waiting_on=_clean(waiting_on),
                       parked_until=_iso(parked_until) if _clean(str(parked_until or "")) else "",
                       parked_until_verified=bool(parked_until_verified),
                       revisit_questions=[_clean(q) for q in (revisit_questions or []) if _clean(q)])
        if payload["parked_until_verified"] and not payload["parked_until"]:
            raise LedgerError("parked_until_verified requires parked_until")
    return _append(path, "STATE_CHANGE", candidate_id, _iso(effective_date or date.today()),
                   payload, backfilled)


def add_note(path: Path = DEFAULT_LEDGER, *, candidate_id: str, text: str,
             refs: list[str] | None = None, effective_date=None, backfilled: bool = False) -> dict:
    if candidate_id not in replay(path):
        raise LedgerError(f"unknown candidate {candidate_id!r}")
    if not _clean(text):
        raise LedgerError("text is required")
    return _append(path, "NOTE", candidate_id, _iso(effective_date or date.today()),
                   {"text": _clean(text), "refs": [_clean(r) for r in (refs or []) if _clean(r)]},
                   backfilled)
