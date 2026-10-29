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
SOURCES = ("HUMAN", "SCOUT", "SUE", "NUTSTUFF", "LIQN", "OTHER")

EVIDENCE_TAGS = ("FACT", "MANAGEMENT_CLAIM", "CONTEXT", "INFERENCE", "VARIANT", "CAPITAL_IMPLICATION")
GRADES = ("PRIMARY", "SECONDARY", "UNCERTIFIED")
DIRECTIONS = ("FOR", "AGAINST", "NEUTRAL")
FALSIFICATION_RESULTS = ("SURVIVED", "INCONCLUSIVE", "FALSIFIED")

# Candidates created before the Operating MVP checkpoint keep their historical
# SURFACED -> UNDERWRITING path. Everything else must pass QUICK_TEST first.
GRANDFATHERED = frozenset({"MCD", "RPM"})

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
                revisit_questions=[], notes=[], grandfathered=cid in GRANDFATHERED,
                quick_test_visited=False, falsifications=[], evidence=[], unresolved=[], strongest={},
                stances=[], assessments=[], observations=[],
            )
        elif ev["event_type"] == "STATE_CHANGE":
            c = cands[cid]
            c.update(state=p["to_state"], state_since=ev["effective_date"], reason=p["reason"])
            c["quick_test_visited"] = c["quick_test_visited"] or p["to_state"] == "QUICK_TEST"
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
        elif ev["event_type"] == "FALSIFICATION":
            cands[cid]["falsifications"].append({**p, "seq": ev["seq"], "date": ev["effective_date"],
                                                 "backfilled": ev["backfilled"], "status": "ACTIVE"})
        elif ev["event_type"] == "EVIDENCE":
            cands[cid]["evidence"].append({**p, "seq": ev["seq"], "date": ev["effective_date"],
                                           "backfilled": ev["backfilled"], "status": "ACTIVE", "note": ""})
        elif ev["event_type"] == "UNRESOLVED":
            cands[cid]["unresolved"].append({**p, "seq": ev["seq"], "date": ev["effective_date"],
                                             "backfilled": ev["backfilled"], "status": "OPEN", "note": ""})
        elif ev["event_type"] == "RESOLVE":
            for lst in ("falsifications", "evidence", "unresolved"):
                for item in cands[cid][lst]:
                    if item["seq"] == p["target_seq"]:
                        item["status"], item["note"] = p["status"], p["note"]
        elif ev["event_type"] == "STRONGEST":
            cands[cid]["strongest"][p["direction"]] = p["target_seq"]
        elif ev["event_type"] == "ASSESSMENT":
            cands[cid]["assessments"].append({**p, "seq": ev["seq"], "date": ev["effective_date"], "backfilled": ev["backfilled"]})
        elif ev["event_type"] == "OBSERVATION":
            cands[cid]["observations"].append({**p, "seq": ev["seq"], "date": ev["effective_date"], "backfilled": ev["backfilled"]})
        elif ev["event_type"] == "STANCE":
            cands[cid]["stances"].append({**p, "seq": ev["seq"], "date": ev["effective_date"],
                                          "recorded_at": ev["recorded_at"], "backfilled": ev["backfilled"]})
        summary = ((f"{p['tag']} {p['direction']} [{p['grade']}]: {p['text']}" if ev["event_type"] == "EVIDENCE" else "")
                   or p.get("to_state") or p.get("text") or p.get("question") or p.get("test")
                   or (f"{p['status']} #{p['target_seq']}" if ev["event_type"] == "RESOLVE" else "")
                   or (f"strongest {p['direction']} = #{p['target_seq']}" if ev["event_type"] == "STRONGEST" else "")
                   or (f"stance v{p['version']}" if ev["event_type"] == "STANCE" else "")
                   or (f"assessment v{p['version']}: {p['disposition']}" if ev["event_type"] == "ASSESSMENT" else "")
                   or (f"observation: {p['what_changed'][:100]}" if ev["event_type"] == "OBSERVATION" else "")
                   or "SURFACED")
        cands[cid]["history"].append(
            {"seq": ev["seq"], "type": ev["event_type"], "date": ev["effective_date"],
             "backfilled": ev["backfilled"], "summary": summary[:160],
             "reason": p.get("reason", "") or p.get("result", "") or p.get("note", "")})
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
    if to_state == "UNDERWRITING" and not c["grandfathered"]:
        if not c["quick_test_visited"]:
            raise LedgerError("QUICK_TEST is mandatory before UNDERWRITING: move to QUICK_TEST and record "
                              "a cheapest-falsification result first")
        live = [f for f in c["falsifications"] if f["status"] == "ACTIVE"]
        if not live:
            raise LedgerError("record a cheapest-falsification test and result before UNDERWRITING")
        if live[-1]["result"] == "FALSIFIED":
            raise LedgerError("latest falsification result is FALSIFIED: PARK or REJECT, or record a new test")
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


# ---------------------------------------------------------------- template / evidence
def _check_candidate(path, candidate_id):
    c = replay(path).get(candidate_id)
    if c is None:
        raise LedgerError(f"unknown candidate {candidate_id!r}")
    return c


def _known_at(v) -> str:
    return _iso(v) if _clean(str(v or "")) else ""


def _grade(g) -> str:
    g = _clean(g).upper()
    if g not in GRADES:
        raise LedgerError(f"grade must be one of {GRADES}")
    return g


def record_falsification(path: Path = DEFAULT_LEDGER, *, candidate_id: str, test: str, result: str,
                         grade: str, source_ref: str = "", known_at=None, effective_date=None,
                         backfilled: bool = False) -> dict:
    """The cheapest test that could kill the idea, and what happened."""
    c = _check_candidate(path, candidate_id)
    if c["state"] == "SURFACED":
        raise LedgerError("move the candidate to QUICK_TEST before recording its falsification result")
    result = _clean(result).upper()
    if result not in FALSIFICATION_RESULTS:
        raise LedgerError(f"result must be one of {FALSIFICATION_RESULTS}")
    if not _clean(test):
        raise LedgerError("test is required")
    return _append(path, "FALSIFICATION", candidate_id, _iso(effective_date or date.today()), {
        "test": _clean(test), "result": result, "grade": _grade(grade),
        "source_ref": _clean(source_ref), "known_at": _known_at(known_at)}, backfilled)


def add_evidence(path: Path = DEFAULT_LEDGER, *, candidate_id: str, tag: str, direction: str, grade: str,
                 text: str, source_ref: str = "", known_at=None, effective_date=None,
                 backfilled: bool = False) -> dict:
    _check_candidate(path, candidate_id)
    tag, direction = _clean(tag).upper(), _clean(direction).upper()
    if tag not in EVIDENCE_TAGS:
        raise LedgerError(f"tag must be one of {EVIDENCE_TAGS}")
    if direction not in DIRECTIONS:
        raise LedgerError(f"direction must be one of {DIRECTIONS}")
    if not _clean(text):
        raise LedgerError("text is required")
    return _append(path, "EVIDENCE", candidate_id, _iso(effective_date or date.today()), {
        "tag": tag, "direction": direction, "grade": _grade(grade), "text": _clean(text),
        "source_ref": _clean(source_ref), "known_at": _known_at(known_at)}, backfilled)


def add_unresolved(path: Path = DEFAULT_LEDGER, *, candidate_id: str, question: str,
                   effective_date=None, backfilled: bool = False) -> dict:
    _check_candidate(path, candidate_id)
    if not _clean(question):
        raise LedgerError("question is required")
    return _append(path, "UNRESOLVED", candidate_id, _iso(effective_date or date.today()),
                   {"question": _clean(question)}, backfilled)


def resolve_item(path: Path = DEFAULT_LEDGER, *, candidate_id: str, target_seq: int, status: str,
                 note: str, effective_date=None, backfilled: bool = False) -> dict:
    """Close an unresolved question, or retract an evidence/falsification entry.
    The original event stays in the ledger; nothing is edited or deleted."""
    c = _check_candidate(path, candidate_id)
    status = _clean(status).upper()
    if status not in ("RESOLVED", "RETRACTED"):
        raise LedgerError("status must be RESOLVED or RETRACTED")
    if not _clean(note):
        raise LedgerError("note is required (what resolved it / why it was retracted)")
    target = next((i for lst in ("falsifications", "evidence", "unresolved") for i in c[lst]
                   if i["seq"] == int(target_seq)), None)
    if target is None:
        raise LedgerError(f"no item #{target_seq} on {candidate_id}")
    if target["status"] != ("OPEN" if "question" in target else "ACTIVE"):
        raise LedgerError(f"item #{target_seq} is already {target['status']}")
    if status == "RESOLVED" and "question" not in target:
        raise LedgerError("only unresolved questions can be RESOLVED; retract evidence instead")
    return _append(path, "RESOLVE", candidate_id, _iso(effective_date or date.today()),
                   {"target_seq": int(target_seq), "status": status, "note": _clean(note)}, backfilled)


def set_strongest(path: Path = DEFAULT_LEDGER, *, candidate_id: str, direction: str, target_seq: int,
                  effective_date=None, backfilled: bool = False) -> dict:
    """Human designation of the strongest evidence FOR or AGAINST. Never computed."""
    c = _check_candidate(path, candidate_id)
    direction = _clean(direction).upper()
    if direction not in ("FOR", "AGAINST"):
        raise LedgerError("direction must be FOR or AGAINST")
    ev = next((i for i in c["evidence"] if i["seq"] == int(target_seq)), None)
    if ev is None or ev["status"] != "ACTIVE" or ev["direction"] != direction:
        raise LedgerError(f"item #{target_seq} must be active evidence marked {direction}")
    return _append(path, "STRONGEST", candidate_id, _iso(effective_date or date.today()),
                   {"direction": direction, "target_seq": int(target_seq)}, backfilled)


def freeze_stance(path: Path = DEFAULT_LEDGER, *, candidate_id: str, stance_text: str,
                  intended_action: str = "", amount: str = "", funding: str = "", concern: str = "",
                  without_atlas: str = "", effective_date=None, backfilled: bool = False) -> dict:
    """Freeze the human's independent view as an immutable, versioned event.

    Never edited: a later view is a NEW version. Only a version recorded while the
    candidate is still SURFACED or QUICK_TEST (and is the first) is the pre-Atlas
    baseline; later versions are labelled as revisions after analysis. A neutral
    stance ("no view") is a valid stance; nothing is inferred if fields are blank.
    """
    c = _check_candidate(path, candidate_id)
    if not _clean(stance_text):
        raise LedgerError("stance_text is required (a neutral stance is a valid stance)")
    version = len(c["stances"]) + 1
    pre_atlas = version == 1 and c["state"] in ("SURFACED", "QUICK_TEST")
    return _append(path, "STANCE", candidate_id, _iso(effective_date or date.today()), {
        "version": version, "pre_atlas": pre_atlas, "stance_text": _clean(stance_text),
        "intended_action": _clean(intended_action), "amount": _clean(amount), "funding": _clean(funding),
        "concern": _clean(concern), "without_atlas": _clean(without_atlas),
        "state_when_frozen": c["state"]}, backfilled)


# ---------------------------------------------------------------- research-level assessment & later observations
ASSESSMENT_DISPOSITIONS = ("SUPPORTED", "INSUFFICIENT_EVIDENCE", "NOT_SUPPORTED", "PARKED_FOR_REVISIT")
ASSESSMENT_STATUSES = ("DRAFT_BY_RECORDER", "HUMAN_ACCEPTED")


def record_assessment(path: Path = DEFAULT_LEDGER, *, candidate_id: str, disposition: str, priced_in_view: str,
                      return_band: str = "", return_band_basis: str = "", drivers: list[str] | None = None,
                      risks: list[str] | None = None, falsifiers: list[str] | None = None, what_would_change: list[str] | None = None,
                      evidence_gaps: list[str] | None = None, existing_holdings_note: str = "", authored_by: str = "",
                      status: str = "DRAFT_BY_RECORDER", effective_date=None, backfilled: bool = False) -> dict:
    """A versioned, descriptive RESEARCH-level answer to "attractive at the verified price?". Never a capital verdict,
    score or rank; Atlas does not compute the disposition. A return band needs its basis; otherwise it must stay blank
    (the UI then says "not substantiated")."""
    c = _check_candidate(path, candidate_id)
    disposition = _clean(disposition).upper()
    if disposition not in ASSESSMENT_DISPOSITIONS:
        raise LedgerError(f"disposition must be one of {ASSESSMENT_DISPOSITIONS}")
    if status not in ASSESSMENT_STATUSES:
        raise LedgerError(f"status must be one of {ASSESSMENT_STATUSES}")
    if not _clean(priced_in_view):
        raise LedgerError("priced_in_view is required (state 'not established' if it is)")
    if not _clean(authored_by):
        raise LedgerError("authored_by is required")
    if _clean(return_band) and not _clean(return_band_basis):
        raise LedgerError("a return band requires its basis; leave both blank if it is not substantiated")
    drivers = [_clean(x) for x in (drivers or []) if _clean(x)]
    if len(drivers) > 3:
        raise LedgerError("at most 3 dominant drivers")
    if disposition == "PARKED_FOR_REVISIT" and c["state"] != "PARKED":
        raise LedgerError("PARKED_FOR_REVISIT requires the candidate lifecycle state PARKED")
    return _append(path, "ASSESSMENT", candidate_id, _iso(effective_date or date.today()), {
        "version": len(c["assessments"]) + 1, "disposition": disposition, "priced_in_view": _clean(priced_in_view),
        "return_band": _clean(return_band), "return_band_basis": _clean(return_band_basis), "drivers": drivers,
        "risks": [_clean(x) for x in (risks or []) if _clean(x)], "falsifiers": [_clean(x) for x in (falsifiers or []) if _clean(x)],
        "what_would_change": [_clean(x) for x in (what_would_change or []) if _clean(x)],
        "evidence_gaps": [_clean(x) for x in (evidence_gaps or []) if _clean(x)],
        "existing_holdings_note": _clean(existing_holdings_note), "authored_by": _clean(authored_by), "status": status}, backfilled)


def record_observation(path: Path = DEFAULT_LEDGER, *, candidate_id: str, observed_on, linked_to: str, what_changed: str,
                       price: float | None = None, price_session: str = "", price_source_ref: str = "", price_grade: str = "SECONDARY",
                       original_price: float | None = None, original_price_ref: str = "", original_price_grade: str = "UNCERTIFIED",
                       benchmark_note: str = "", effective_date=None, backfilled: bool = False) -> dict:
    """A NEW dated observation linked to an earlier record. The original evidence is never edited or backfilled as if known then.
    Only a PRICE change is stated (never a total return); benchmark comparison stays UNVERIFIED unless matched adjusted
    total-return and Treasury evidence is supplied in ``benchmark_note``."""
    _check_candidate(path, candidate_id)
    if not _clean(linked_to) or not _clean(what_changed):
        raise LedgerError("linked_to (the original record) and what_changed are required")
    out = {"linked_to": _clean(linked_to), "what_changed": _clean(what_changed), "observed_on": _iso(observed_on),
           "benchmark": _clean(benchmark_note) or "UNVERIFIED — no matched adjusted total-return / Treasury evidence supplied"}
    if price is not None:
        if not _clean(price_session) or not _clean(price_source_ref):
            raise LedgerError("an observed price needs its session and source reference")
        out.update(price=float(price), price_session=_iso(price_session), price_source_ref=_clean(price_source_ref), price_grade=_grade(price_grade))
        if original_price is not None:
            if not _clean(original_price_ref):
                raise LedgerError("the original price needs its source reference")
            out.update(original_price=float(original_price), original_price_ref=_clean(original_price_ref),
                       original_price_grade=_grade(original_price_grade),
                       price_change_only=float(price) / float(original_price) - 1.0,
                       price_change_note="PRICE change only (no dividends/adjustments); not a total return; the two prices may come from different sources")
    return _append(path, "OBSERVATION", candidate_id, _iso(effective_date or date.today()), out, backfilled)
