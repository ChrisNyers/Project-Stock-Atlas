"""Approval register: the latest HUMAN-APPROVED records, resolved from data, never from code.

Operating values that legitimately change (the approved state, the portfolio snapshot, the active work, a candidate's restriction) are not
written into software or into ``docs/CURRENT_AUTHORITY.md``. They are append-only events in ``docs/authority_register.jsonl`` (hash-chained,
like the candidate and decision ledgers). Rules, enforced by ``resolve``:

* Only an event carrying a valid HUMAN approval (who, date, a record that exists, a quote) is authoritative. An event without one is a DRAFT: kept,
  listed, never followed. Approval is recorded by the human's instruction; software can check it is present and consistent, not that it is genuine.
* A newer record supersedes an older one only by naming it (``supersedes``). Exactly one approved head per family. Two heads, two roots, a duplicate,
  an unknown or draft predecessor, a non-increasing date or a hash mismatch is a CONFLICT and the resolver raises: callers fail closed.
* Nothing is rewritten. Superseded snapshots and states stay in the register and stay loadable (``chain``), so any past decision can be reconstructed.
* A revisit date is a trigger to reassess (``revisit_due``). It never changes a candidate's state.
* Candidate status: a STATE_CHANGE in the candidate ledger is authoritative once the register accepts it (a bulk ``LEDGER_ACCEPTED_THROUGH`` for
  the history, or one ``CANDIDATE_STATUS_APPROVED`` per later change). Later unapproved changes are listed as ``pending`` and not followed.

Adding a record is data (``python -m atlas_ui authority append ...``); no software change.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTER = "docs/authority_register.jsonl"
GENESIS = "0" * 64
# family -> (key field, required payload fields)
FAMILIES = {
    "APPROVED_STATE": ("commit", ("commit", "status")),
    "PORTFOLIO_SNAPSHOT": ("snapshot_id", ("snapshot_id", "doc", "doc_sha256", "table_marker", "as_of", "holdings", "stocks_total", "defensive_approx")),
    "ACTIVE_WORK": ("work_id", ("work_id", "plan_heading_prefix", "summary", "state")),
}
MILESTONE_STATUSES = ("COMPLETE", "IN_PROGRESS", "BLOCKED", "UPCOMING")
MILESTONE_FIELDS = ("milestone_id", "phase", "phase_order", "title", "status", "evidence")     # optional: depends_on, target_date, blocker, notes
CANDIDATE_TYPES = {
    "LEDGER_ACCEPTED_THROUGH": ("through_seq", "through_event_hash"),
    "CANDIDATE_STATUS_APPROVED": ("ledger_seq", "ledger_event_hash"),
}
ALL_TYPES = {**{k: v[1] for k, v in FAMILIES.items()}, **CANDIDATE_TYPES, "MILESTONE": MILESTONE_FIELDS}


class AuthorityError(Exception):
    """The register is unreadable, tampered or malformed."""


class AuthorityConflict(AuthorityError):
    """Approved records disagree. Nothing may be resolved from them."""


def _hash(prev: str, body: dict) -> str:
    return hashlib.sha256((prev + json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)).encode("utf-8")).hexdigest()


def _iso(s) -> date:
    try:
        return date.fromisoformat(str(s))
    except ValueError:
        raise AuthorityError(f"invalid date {s!r} (use YYYY-MM-DD)")


def read_register(path: Path) -> list[dict]:
    path = Path(path)
    if not path.is_file():
        raise AuthorityError(f"authority register missing: {path}")
    try:
        events = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except ValueError as exc:
        raise AuthorityError(f"authority register unreadable: {exc}")
    prev = GENESIS
    for i, ev in enumerate(events, start=1):
        try:
            body = {k: v for k, v in ev.items() if k not in ("prev_hash", "event_hash")}
            good = ev.get("seq") == i and ev.get("prev_hash") == prev and ev.get("event_hash") == _hash(prev, body)
        except Exception:
            good = False
        if not good:
            raise AuthorityError(f"authority register integrity failure at event {i}: an event was edited, removed or reordered")
        prev = ev["event_hash"]
    return events


def approved(ev: dict) -> bool:
    """A valid HUMAN approval: who is HUMAN, a date, a quote, and a record naming where the approval is kept. Anything else is a draft."""
    a = ev.get("approval")
    if not isinstance(a, dict) or a.get("by") != "HUMAN":
        return False
    try:
        date.fromisoformat(str(a.get("date")))
    except ValueError:
        return False
    return all(isinstance(a.get(k), str) and a[k].strip() for k in ("record", "quote"))


# --------------------------------------------------------------------------------------------------------------------- resolution
@dataclass
class Resolution:
    events: list[dict]
    chains: dict[str, list[dict]] = field(default_factory=dict)      # family -> approved events, oldest first
    drafts: list[dict] = field(default_factory=list)                  # events without a valid HUMAN approval: never followed
    ledger_through: tuple[int, str] | None = None
    status_approvals: dict[int, str] = field(default_factory=dict)    # candidate ledger seq -> event_hash approved one by one
    milestones: dict[str, dict] = field(default_factory=dict)         # milestone_id -> {current, proposed, history}; see _milestones

    def head(self, family: str) -> dict | None:
        c = self.chains.get(family) or []
        return c[-1] if c else None

    @property
    def approved_state(self) -> dict | None:
        h = self.head("APPROVED_STATE")
        return {**h["payload"], "approval": h["approval"], "register_seq": h["seq"]} if h else None

    @property
    def active_work(self) -> dict | None:
        h = self.head("ACTIVE_WORK")
        return {**h["payload"], "approval": h["approval"], "register_seq": h["seq"]} if h else None

    @property
    def snapshots(self) -> list[dict]:
        """Approved snapshot specs, oldest first. The last is current; the rest are history and stay loadable."""
        return [{**e["payload"], "approval": e["approval"], "register_seq": e["seq"]} for e in self.chains.get("PORTFOLIO_SNAPSHOT", [])]

    @property
    def current_snapshot(self) -> dict | None:
        s = self.snapshots
        return s[-1] if s else None

    def snapshot_as_of(self, on: str | date) -> dict | None:
        """The snapshot in force on a date (the latest approved one whose as_of is not after it) — how a past analysis is reconstructed."""
        d = _iso(on) if not isinstance(on, date) else on
        ok = [s for s in self.snapshots if _iso(s["as_of"]) <= d]
        return ok[-1] if ok else None


def _chain(family: str, evs: list[dict]) -> list[dict]:
    key = FAMILIES[family][0]
    by_key: dict[str, dict] = {}
    for e in evs:
        k = e["payload"][key]
        if k in by_key:
            raise AuthorityConflict(f"{family}: two approved records share the id {k!r}")
        by_key[k] = e
    successors: dict[str | None, list[dict]] = {}
    for e in evs:
        sup = e["payload"].get("supersedes")
        if sup is not None and sup not in by_key:
            raise AuthorityConflict(f"{family} {e['payload'][key]!r} supersedes {sup!r}, which is not an approved record (a draft or unknown id cannot be superseded)")
        if sup is not None and by_key[sup]["seq"] >= e["seq"]:
            raise AuthorityConflict(f"{family} {e['payload'][key]!r} supersedes a record that was not yet in the register")
        successors.setdefault(sup, []).append(e)
    forks = {s: [x["payload"][key] for x in v] for s, v in successors.items() if len(v) > 1}
    if forks:
        raise AuthorityConflict(f"{family}: conflicting approved records — more than one supersedes {next(iter(forks))!r}: {next(iter(forks.values()))}")
    out, cur = [], (successors.get(None) or [None])[0]
    while cur is not None:
        out.append(cur)
        cur = (successors.get(cur["payload"][key]) or [None])[0]
    if len(out) != len(evs):
        raise AuthorityConflict(f"{family}: approved records do not form one chain")
    if family == "PORTFOLIO_SNAPSHOT":
        for a, b in zip(out, out[1:]):
            if _iso(b["payload"]["as_of"]) <= _iso(a["payload"]["as_of"]):
                raise AuthorityConflict(f"PORTFOLIO_SNAPSHOT {b['payload']['snapshot_id']!r} is dated {b['payload']['as_of']}, not after the snapshot it supersedes ({a['payload']['as_of']})")
    return out


def _milestones(events: list[dict]) -> dict[str, dict]:
    """Milestone status from MILESTONE events only (never from prose). ``current`` = the latest HUMAN-APPROVED event for the id (a COMPLETE counts only
    because a human approved it); ``proposed`` = a later event without a valid approval, shown as awaiting acceptance and never followed;
    ``history`` = every event, oldest first. Append-only: a status change is a new event."""
    out: dict[str, dict] = {}
    for ev in events:
        if ev.get("type") != "MILESTONE":
            continue
        p = ev["payload"]
        if p["status"] not in MILESTONE_STATUSES or not isinstance(p["evidence"], list) or not isinstance(p["phase_order"], int):
            raise AuthorityError(f"register event {ev['seq']} (MILESTONE {p.get('milestone_id')!r}): status must be one of {MILESTONE_STATUSES}, evidence a list, phase_order an integer")
        m = out.setdefault(p["milestone_id"], {"current": None, "proposed": None, "history": []})
        m["history"].append(ev)
        if approved(ev):
            m["current"] = ev
    for m in out.values():
        cur = m["current"]["seq"] if m["current"] else 0
        later = [e for e in m["history"] if not approved(e) and e["seq"] > cur]
        m["proposed"] = later[-1] if later else None
    return out


def resolve(register: Path) -> Resolution:
    events = read_register(register)
    res = Resolution(events)
    by_family: dict[str, list[dict]] = {f: [] for f in FAMILIES}
    for ev in events:
        t, p = ev.get("type"), ev.get("payload")
        if t not in ALL_TYPES or not isinstance(p, dict):
            raise AuthorityError(f"register event {ev.get('seq')}: unknown type {t!r}")
        missing = [k for k in ALL_TYPES[t] if k not in p]
        if missing:
            raise AuthorityError(f"register event {ev['seq']} ({t}) lacks {missing}")
        if not approved(ev):
            res.drafts.append(ev)
            continue
        if t in FAMILIES:
            by_family[t].append(ev)
        elif t == "MILESTONE":
            pass                                                             # resolved by _milestones below
        elif t == "LEDGER_ACCEPTED_THROUGH":
            if res.ledger_through is None or p["through_seq"] > res.ledger_through[0]:
                res.ledger_through = (int(p["through_seq"]), p["through_event_hash"])
        else:
            prior = res.status_approvals.get(int(p["ledger_seq"]))
            if prior is not None and prior != p["ledger_event_hash"]:
                raise AuthorityConflict(f"candidate ledger event {p['ledger_seq']} is approved under two different hashes")
            res.status_approvals[int(p["ledger_seq"])] = p["ledger_event_hash"]
    for fam, evs in by_family.items():
        res.chains[fam] = _chain(fam, evs)
    res.milestones = _milestones(events)
    return res


# --------------------------------------------------------------------------------------------------------------------- candidates
def resolve_candidates(res: Resolution, ledger_path: Path, today: date | None = None) -> dict[str, dict]:
    """Current candidate status under the register. Each record is the ledger's full replay (history stays complete) with the status fields taken
    only from approved STATE_CHANGEs, plus ``pending`` (later changes the register has not approved) and ``revisit_due``."""
    from operating_mvp import ledger as L
    evs = L.read_events(ledger_path)
    L.verify_chain(ledger_path)
    by_seq = {e["seq"]: e for e in evs}
    claims = {**{s: h for s, h in res.status_approvals.items()}}
    for seq, h in claims.items():
        e = by_seq.get(seq)
        if e is None or e["event_type"] != "STATE_CHANGE" or e["event_hash"] != h:
            raise AuthorityConflict(f"the register approves candidate ledger event {seq} as {h[:12]}…, which the ledger does not contain as a STATE_CHANGE")
    through = res.ledger_through
    if through is not None:
        e = by_seq.get(through[0])
        if e is None or e["event_hash"] != through[1]:
            raise AuthorityConflict(f"the register accepts the candidate ledger through event {through[0]}, which the ledger does not contain (or contains differently)")

    def ok(e):
        return e["event_type"] != "STATE_CHANGE" or (through is not None and e["seq"] <= through[0]) or e["seq"] in claims

    full = L.replay_events(evs)
    auth = L.replay_events([e for e in evs if ok(e)])
    today = today or date.today()
    out = {}
    for cid, c in full.items():
        a = auth.get(cid, c)
        pending = [{"seq": e["seq"], "to_state": e["payload"]["to_state"], "effective_date": e["effective_date"]}
                   for e in evs if e["candidate_id"] == cid and not ok(e)]
        rec = {**c, **{k: a[k] for k in ("state", "state_since", "reason", "waiting_on", "parked_until", "parked_until_verified", "revisit_questions")}}
        rec["pending"] = pending
        rec["revisit_due"] = bool(rec["state"] == "PARKED" and rec["parked_until"] and _iso(rec["parked_until"]) <= today)
        out[cid] = rec
    return out


# --------------------------------------------------------------------------------------------------------------------- writing
def append(register: Path, type_: str, payload: dict, *, approval: dict | None = None, recorded_on: str | None = None, check_record=None) -> dict:
    """Append one event. The resulting register must still resolve (a conflicting event is refused before anything is written).
    Without ``approval`` the event is a DRAFT. Never edits or removes an existing line."""
    register = Path(register)
    if type_ not in ALL_TYPES:
        raise AuthorityError(f"unknown type {type_!r}; one of {sorted(ALL_TYPES)}")
    missing = [k for k in ALL_TYPES[type_] if k not in payload]
    if missing:
        raise AuthorityError(f"{type_} requires {missing}")
    existing = read_register(register) if register.exists() else []
    prev = existing[-1]["event_hash"] if existing else GENESIS
    body = {"seq": len(existing) + 1, "type": type_, "recorded_on": recorded_on or date.today().isoformat(), "payload": payload, "approval": approval}
    ev = {**body, "prev_hash": prev, "event_hash": _hash(prev, body)}
    if approval is not None and not approved(ev):
        raise AuthorityError("approval must be {by: 'HUMAN', date: YYYY-MM-DD, record: <where it is kept>, quote: <the human's words>}; omit it to record a draft")
    if approval is not None and check_record is not None and not check_record(approval["record"]):
        raise AuthorityError(f"approval record {approval['record']!r} does not resolve to a repository record")
    tmp = register.with_suffix(".check")
    try:
        tmp.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in [*existing, ev]), encoding="utf-8")
        resolve(tmp)                      # raises AuthorityConflict / AuthorityError: nothing is written to the real register
    finally:
        if tmp.exists():
            os.unlink(tmp)
    with open(register, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def accept_ledger_tail(register: Path, ledger_path: Path, approval: dict) -> dict:
    """Accept the candidate ledger as it stands (one LEDGER_ACCEPTED_THROUGH event). Used to seed a DEMO workspace and by tests acting as the human;
    nothing in the app or the services calls it for the repository's register."""
    from operating_mvp import ledger as L
    last = L.read_events(ledger_path)[-1]
    return append(register, "LEDGER_ACCEPTED_THROUGH", {"through_seq": last["seq"], "through_event_hash": last["event_hash"]}, approval=approval)


def record_exists(repo: Path, ref: str) -> bool:
    """An approval's ``record`` resolves to a repository file, or to a heading in the Decision Log ("Decision Log: NAME")."""
    ref = ref.strip()
    if ref.startswith("Decision Log:"):
        name = ref.split(":", 1)[1].strip()
        log = Path(repo) / "docs" / "STOCK_ATLAS_DECISION_LOG.md"
        return log.is_file() and re.search(rf"^##+ {re.escape(name)}\s*$", log.read_text(encoding="utf-8"), re.M) is not None
    path = Path(repo) / ref.split("#", 1)[0]
    return path.is_file() and (Path(repo).resolve() in path.resolve().parents)
