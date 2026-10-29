"""Project execution status: ONE read-only view over records that already exist. It owns no data.

Every figure comes from a structured record and is re-read each time the page is viewed:
  * Git (HEAD, the local tracking ref of the published branch, history)           * the authority register (approved state, active work, milestones)
  * the candidate ledger, as the register accepts it (states, revisit dates)       * the capability list in ``atlas_ui/app.py`` (what the matrix is generated from)
  * the approved portfolio snapshot                                               * the Stage 7 run index and the decision ledger (counts only)
  * Decision Log entry headings, dates and their Status cell, shown VERBATIM (never interpreted)

Rules: no percentage-complete figure is computed or shown (only counts of what is accepted); a milestone is COMPLETE only because a human-approved
register event says so and its evidence resolves; nothing is inferred from prose in the Master Plan or Decision Log; anything missing or unverifiable
is the literal string UNKNOWN; Git HEAD, the published GitHub HEAD and the approved state are three different things and are shown separately.
"""
from __future__ import annotations

import os
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

from operating_mvp import ledger

from . import authority
from .verify import _git, has_git

REPO = Path(__file__).resolve().parent.parent
UNKNOWN = "UNKNOWN"
EVIDENCE_KINDS = ("commit", "file", "decision-log", "register")
PUBLISHED_REF = "refs/remotes/origin/main"


def _clean_url(url: str | None) -> str:
    """A remote URL for display, with any embedded credentials removed."""
    return re.sub(r"//[^/@\s]+@", "//", url.strip()) if url else UNKNOWN


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------------------------------------------------------------------ git
def git_truth(repo: Path, approved: dict | None) -> dict:
    """HEAD, the published branch as last known locally, and the approved state: three separate facts, plus how they relate."""
    if not has_git(repo):
        return {"available": False, "head": None, "published": None, "approved": approved, "dirty": None, "branch": UNKNOWN, "ahead_of_approved": None,
                "published_vs_head": UNKNOWN, "remote": UNKNOWN, "note": "no git history in this tree (an extracted copy): HEAD and the published position are UNKNOWN here"}
    one = lambda *a: (_git(repo, *a) or "").strip()
    sha = one("rev-parse", "HEAD")
    head = {"sha": sha, "subject": one("log", "-1", "--format=%s"), "date": one("log", "-1", "--format=%cI")}
    pub_sha = one("rev-parse", "--verify", "-q", PUBLISHED_REF)
    ref_file = repo / ".git" / "refs" / "remotes" / "origin" / "main"
    pub_when = datetime.fromtimestamp(ref_file.stat().st_mtime, timezone.utc).isoformat(timespec="seconds") if ref_file.is_file() else UNKNOWN
    published = ({"sha": pub_sha, "subject": one("log", "-1", "--format=%s", pub_sha), "as_of": pub_when,
                  "basis": "local tracking ref origin/main: the position at the last push or fetch, NOT a live check"} if pub_sha else None)
    dirty = [ln for ln in (_git(repo, "status", "--porcelain") or "").splitlines() if ln and not ln[3:].startswith("deliverables/")]
    ahead = []
    if approved and _git(repo, "cat-file", "-e", f"{approved['commit']}^{{commit}}") is not None:
        ahead = [ln.split(" ", 1) for ln in (_git(repo, "log", "--format=%h %s", f"{approved['commit']}..HEAD") or "").splitlines() if ln]
    if not pub_sha:
        rel = UNKNOWN
    elif pub_sha == sha:
        rel = "SAME"
    else:
        n_ahead = int(one("rev-list", "--count", f"{pub_sha}..HEAD") or 0) if _git(repo, "cat-file", "-e", f"{pub_sha}^{{commit}}") is not None else None
        n_behind = int(one("rev-list", "--count", f"HEAD..{pub_sha}") or 0) if n_ahead is not None else None
        rel = (f"HEAD is {n_ahead} commit(s) ahead of the published branch (unpublished)" if n_ahead and not n_behind else
               f"published branch is {n_behind} commit(s) ahead of HEAD" if n_behind and not n_ahead else "DIVERGED" if n_ahead is not None else UNKNOWN)
    return {"available": True, "head": head, "published": published, "approved": approved, "dirty": len(dirty), "branch": one("rev-parse", "--abbrev-ref", "HEAD") or UNKNOWN,
            "ahead_of_approved": ahead, "published_vs_head": rel, "remote": _clean_url(one("remote", "get-url", "origin") or None),
            "approved_is_ancestor": (subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", approved["commit"], "HEAD"], capture_output=True).returncode == 0) if approved else None}


def check_github(repo: Path, timeout: int = 25) -> dict:
    """A live, read-only check of the published branch (``git ls-remote``). Never prompts; failure is reported as UNKNOWN, not guessed."""
    at = _iso(datetime.now(timezone.utc))
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_SSH_COMMAND": "ssh -o BatchMode=yes -o ConnectTimeout=15"}
    try:
        r = subprocess.run(["git", "-C", str(repo), "ls-remote", "origin", "refs/heads/main"], capture_output=True, text=True, timeout=timeout, env=env)
    except Exception as exc:
        return {"ok": False, "checked_at": at, "sha": None, "error": f"{type(exc).__name__}"}
    if r.returncode != 0:
        return {"ok": False, "checked_at": at, "sha": None, "error": "remote unreachable or not authorised"}
    line = r.stdout.strip().split("\n")[0].split()
    return {"ok": True, "checked_at": at, "sha": line[0] if line else None, "error": None if line else "the remote has no main branch"}


# ------------------------------------------------------------------------------------------------------------------------------ evidence
def verify_evidence(repo: Path, refs: list[str], res: authority.Resolution | None, use_git: bool = True) -> list[dict]:
    """Does each evidence reference of a milestone resolve? Formats: commit:<sha> | file:<path> | decision-log:<NAME> | register:<seq>.
    ok is True / False / None (None = cannot be checked here, e.g. a commit in a tree without git history: UNKNOWN, never a pass)."""
    out = []
    log = None
    for ref in refs:
        kind, _, val = str(ref).partition(":")
        ok, why = None, ""
        if kind == "commit":
            if use_git and has_git(repo):
                ok = _git(repo, "cat-file", "-e", f"{val}^{{commit}}") is not None
                why = "" if ok else "commit not in this repository"
            else:
                why = "no git history here"
        elif kind == "file":
            p = (repo / val)
            ok = p.is_file() and repo.resolve() in p.resolve().parents
            why = "" if ok else "file not found"
        elif kind == "decision-log":
            if log is None:
                f = repo / "docs" / "STOCK_ATLAS_DECISION_LOG.md"
                log = f.read_text(encoding="utf-8") if f.is_file() else ""
            ok = re.search(rf"^##+ {re.escape(val)}\s*$", log, re.M) is not None
            why = "" if ok else "no such Decision Log entry"
        elif kind == "register":
            ok = bool(res) and val.isdigit() and any(e.get("seq") == int(val) for e in res.events)
            why = "" if ok else "no such register event"
        else:
            ok, why = False, f"unknown evidence kind {kind!r}"
        out.append({"ref": ref, "ok": ok, "why": why})
    return out


# ------------------------------------------------------------------------------------------------------------------------------ records
def decision_log_entries(repo: Path, n: int = 8) -> list[dict]:
    """The latest Decision Log entries: heading, date and the Status cell exactly as written. Display only; nothing is read into them."""
    f = repo / "docs" / "STOCK_ATLAS_DECISION_LOG.md"
    if not f.is_file():
        return []
    text = f.read_text(encoding="utf-8")
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"^## ([A-Z0-9_]+)\s*$", text, re.M)]
    out = []
    for i, (pos, name) in enumerate(heads[-n:][::-1]):
        end = heads[heads.index((pos, name)) + 1][0] if heads.index((pos, name)) + 1 < len(heads) else len(text)
        block = text[pos:end]
        d = re.search(r"^\|\s*Date\s*\|\s*(.+?)\s*\|\s*$", block, re.M)
        s = re.search(r"^\|\s*Status\s*\|\s*(.+?)\s*\|\s*$", block, re.M)
        out.append({"name": name, "date": d.group(1) if d else UNKNOWN, "status_text": re.sub(r"\*\*", "", s.group(1)) if s else UNKNOWN})
    return out


def _file_date(repo: Path, rel: str) -> str:
    """When a source file last changed: its last commit date, else its modification time; UNKNOWN if it does not exist."""
    p = repo / rel
    if not p.is_file():
        return UNKNOWN
    d = (_git(repo, "log", "-1", "--format=%cI", "--", rel) or "").strip() if has_git(repo) else ""
    return d or datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")


def milestone_view(res: authority.Resolution, repo: Path, use_git: bool = True) -> dict:
    """Phases and milestones from MILESTONE register events. Counts only: no percentage is computed anywhere."""
    phases: dict[int, dict] = {}
    ids = set(res.milestones)
    for mid, m in res.milestones.items():
        ev = m["current"] or m["proposed"]
        p = ev["payload"]
        ph = phases.setdefault(p["phase_order"], {"phase": p["phase"], "order": p["phase_order"], "items": []})
        cur = m["current"]
        cp = cur["payload"] if cur else None
        prop = m["proposed"]["payload"] if m["proposed"] else None
        evid = verify_evidence(repo, (cp or p)["evidence"], res, use_git)
        unverified = [x for x in evid if x["ok"] is not True]
        status = cp["status"] if cp else "NOT APPROVED"
        item = {"id": mid, "title": p["title"], "status": status, "approved": bool(cur), "approved_on": cur["approval"]["date"] if cur else None,
                "register_seq": cur["seq"] if cur else None, "evidence": evid, "evidence_ok": bool(evid) and not unverified,
                "depends_on": (cp or p).get("depends_on", []), "target_date": (cp or p).get("target_date"), "blocker": (cp or p).get("blocker"),
                "notes": (cp or p).get("notes"),
                "proposed": ({"status": prop["status"], "register_seq": m["proposed"]["seq"], "recorded_on": m["proposed"]["recorded_on"]} if prop else None),
                "unknown_dependencies": [d for d in (cp or p).get("depends_on", []) if d not in ids]}
        # COMPLETE counts only when approved AND its evidence resolves. Approved-but-unverifiable is shown as such, not counted.
        item["counts_as_complete"] = status == "COMPLETE" and item["evidence_ok"]
        ph["items"].append(item)
    out = []
    for order in sorted(phases):
        ph = phases[order]
        ph["items"].sort(key=lambda i: i["id"])
        ph["counts"] = {"complete": sum(i["counts_as_complete"] for i in ph["items"]), "total": len(ph["items"]),
                        "awaiting_acceptance": sum(1 for i in ph["items"] if i["proposed"] and i["proposed"]["status"] == "COMPLETE"),
                        "in_progress": sum(1 for i in ph["items"] if i["status"] == "IN_PROGRESS"), "blocked": sum(1 for i in ph["items"] if i["status"] == "BLOCKED"),
                        "upcoming": sum(1 for i in ph["items"] if i["status"] == "UPCOMING")}
        out.append(ph)
    allitems = [i for ph in out for i in ph["items"]]
    return {"phases": out, "totals": {"milestones": len(allitems), "complete": sum(i["counts_as_complete"] for i in allitems),
                                      "awaiting_acceptance": sum(1 for i in allitems if i["proposed"] and i["proposed"]["status"] == "COMPLETE"),
                                      "in_progress": sum(1 for i in allitems if i["status"] == "IN_PROGRESS"), "blocked": sum(1 for i in allitems if i["status"] == "BLOCKED"),
                                      "upcoming": sum(1 for i in allitems if i["status"] == "UPCOMING"),
                                      "complete_but_evidence_unverified": sum(1 for i in allitems if i["status"] == "COMPLETE" and not i["evidence_ok"])}}


# ------------------------------------------------------------------------------------------------------------------------------ the view model
def status(repo: Path = REPO, *, now: datetime | None = None, ws=None, svc=None, research=None, capabilities=(), github_live: dict | None = None,
           use_git: bool = True, run_preflight: bool = True) -> dict:
    """Everything the Project page shows, re-read from the records now. ``ws``/``svc``/``research`` are optional so the same function works
    on a bare repository; whatever cannot be established is UNKNOWN."""
    repo = Path(repo)
    now = now or datetime.now(timezone.utc)
    reg_path = repo / authority.REGISTER
    d: dict = {"generated_at": _iso(now), "repo": str(repo)}
    try:
        res = authority.resolve(reg_path)
        d["authority"] = {"ok": True, "error": None, "events": len(res.events), "drafts": len(res.drafts)}
    except authority.AuthorityError as exc:
        res = None
        d["authority"] = {"ok": False, "error": str(exc), "events": None, "drafts": None}

    approved = None
    if res is not None and res.approved_state:
        a = res.approved_state
        approved = {"commit": a["commit"], "status": a["status"], "approved_on": a["approval"]["date"], "register_seq": a["register_seq"], "quote": a["approval"]["quote"]}
    d["truth"] = git_truth(repo, approved) if use_git else git_truth(repo / "__no_git__", approved)
    d["truth"]["approved"] = approved
    d["truth"]["github_live"] = github_live
    if github_live and github_live.get("ok") and d["truth"].get("head"):
        d["truth"]["live_vs_head"] = "SAME" if github_live["sha"] == d["truth"]["head"]["sha"] else "DIFFERENT"
    d["truth"]["head_is_approved"] = bool(approved and d["truth"].get("head") and d["truth"]["head"]["sha"] == approved["commit"])

    # --- active assignment (the approved ACTIVE_WORK record; owner / next action / dependencies are shown only if that record carries them)
    aw = res.active_work if res else None
    d["active"] = ({"work_id": aw["work_id"], "summary": aw["summary"], "state": aw["state"], "approved_on": aw["approval"]["date"], "register_seq": aw["register_seq"],
                    "quote": aw["approval"]["quote"], "plan_heading": aw["plan_heading_prefix"].lstrip("# "),
                    "owner": aw.get("owner") or UNKNOWN, "next_action": aw.get("next_action") or UNKNOWN,
                    "dependencies": aw.get("dependencies") or UNKNOWN} if aw else None)

    d["milestones"] = milestone_view(res, repo, use_git and has_git(repo)) if res is not None else None
    d["milestone_drafts"] = [{"seq": e["seq"], "milestone_id": e["payload"]["milestone_id"], "status": e["payload"]["status"]} for e in (res.drafts if res else []) if e["type"] == "MILESTONE"]

    # --- recent change
    commits = []
    if has_git(repo) and use_git:
        unapproved = set()
        if approved and _git(repo, "cat-file", "-e", f"{approved['commit']}^{{commit}}") is not None:
            unapproved = {ln.split()[0] for ln in (_git(repo, "log", "--format=%h", f"{approved['commit']}..HEAD") or "").splitlines() if ln}
        for ln in (_git(repo, "log", "-n", "10", "--format=%h|%cI|%s") or "").splitlines():
            h, when, subj = ln.split("|", 2)
            commits.append({"sha": h, "date": when, "subject": subj, "approved": h not in unapproved})
    d["recent"] = {"commits": commits, "decisions": decision_log_entries(repo)}

    # --- candidates, as the register accepts them
    cands = {}
    if res is not None:
        try:
            cands = authority.resolve_candidates(res, repo / "operating_mvp" / "data" / "candidate_ledger.jsonl", now.date())
        except Exception as exc:
            d["candidates_error"] = str(exc)
    if ws is not None and not cands:
        try:
            cands = ws.candidates()
        except Exception as exc:
            d["candidates_error"] = str(exc)
    pipeline = []
    for cid, c in sorted(cands.items()):
        snap, snap_err = (research(cid) if research else (None, None))
        asm = c["assessments"][-1] if c.get("assessments") else None
        pipeline.append({"candidate_id": cid, "ticker": c.get("ticker") or UNKNOWN, "state": c["state"], "parked_until": c["parked_until"] or None, "revisit_due": c["revisit_due"],
                         "pending": [p["seq"] for p in c["pending"]], "stances": len(c.get("stances", [])), "evidence": len(c.get("evidence", [])),
                         "open_questions": sum(1 for u in c.get("unresolved", []) if u["status"] == "OPEN"),
                         "assessment": (f"v{asm['version']} {asm['disposition']} ({asm['status']})" if asm else UNKNOWN),
                         "research_snapshot": ((snap.get("recorded_at") or "PRESENT") if snap else (f"ERROR: {snap_err}" if snap_err else "NONE")),
                         "observations": len(c.get("observations", []))})
    d["pipeline"] = pipeline

    # --- upcoming dates and revisit triggers
    up = []
    for c in pipeline:
        if c["parked_until"]:
            days = (date.fromisoformat(c["parked_until"]) - now.date()).days
            up.append({"date": c["parked_until"], "days": days, "kind": "candidate revisit trigger", "what": f"{c['candidate_id']} PARKED until {c['parked_until']}",
                       "note": "REACHED: a trigger to reassess, not a promotion" if days <= 0 else "a trigger to reassess, not a promotion; the candidate stays PARKED"})
    if d["milestones"]:
        for ph in d["milestones"]["phases"]:
            for it in ph["items"]:
                if it["target_date"] and it["status"] != "COMPLETE":
                    days = (date.fromisoformat(it["target_date"]) - now.date()).days
                    up.append({"date": it["target_date"], "days": days, "kind": "milestone target", "what": f"{it['id']} {it['title']}",
                               "note": "depends on the information being available" if it["status"] in ("UPCOMING", "BLOCKED") else ""})
    d["upcoming"] = sorted(up, key=lambda x: x["date"])

    # --- capabilities (from the same list the capability matrix is generated from)
    caps = list(capabilities)
    counts: dict[str, int] = {}
    for _n, s, _d in caps:
        counts[s.split(" (")[0]] = counts.get(s.split(" (")[0], 0) + 1
    d["capabilities"] = {"counts": counts, "rows": [{"name": n, "status": s.split(" (")[0], "detail": dt} for n, s, dt in caps]} if caps else None

    # --- portfolio snapshot freshness
    snap = res.current_snapshot if res else None
    if snap:
        age = (now.date() - date.fromisoformat(snap["as_of"])).days
        d["portfolio"] = {"snapshot_id": snap["snapshot_id"], "as_of": snap["as_of"], "age_days": age, "holdings": snap["holdings"], "stocks_total": snap["stocks_total"],
                          "defensive_approx": snap["defensive_approx"], "doc": snap["doc"], "sha256": snap["doc_sha256"], "approved_on": snap["approval"]["date"],
                          "label": "human-supplied, approximate, NOT a live balance; no refresh policy is recorded, so freshness is shown as age only"}
    else:
        d["portfolio"] = None

    # --- Stage 7 / 8 and outcome learning
    s78 = {"runs": UNKNOWN, "by_status": {}, "decisions": UNKNOWN, "ledger_verified": UNKNOWN}
    if svc is not None and ws is not None:
        try:
            runs = svc.list_runs()
            s78["mode"] = ws.mode
            s78["runs"] = len(runs)
            for r in runs:
                s78["by_status"][r["status"]] = s78["by_status"].get(r["status"], 0) + 1
            s78["verified_runs"] = sum(1 for r in runs if r["verified"])
            s78["decisions"] = len(svc.ledger_rows())
            s78["ledger_verified"] = bool(ws.facade.verify_ledger())
        except Exception as exc:
            s78["error"] = type(exc).__name__
    d["stage78"] = s78
    obs = [{"candidate_id": c["candidate_id"], "n": c["observations"]} for c in pipeline if c["observations"]]
    g2 = next((r for r in d["capabilities"]["rows"] if r["name"].startswith("G2")), None) if d["capabilities"] else None
    d["outcomes"] = {"observations": sum(o["n"] for o in obs) if pipeline else UNKNOWN, "by_candidate": obs,
                     "decisions_to_measure": s78["decisions"],
                     "benchmark_comparison": (g2["detail"] if g2 else UNKNOWN)}

    # --- sources and when each was last changed (so a stale page is visible)
    try:
        lev = max((e["recorded_at"] for e in ledger.read_events(repo / "operating_mvp" / "data" / "candidate_ledger.jsonl")), default=UNKNOWN)
    except Exception:
        lev = UNKNOWN
    src = [("Git HEAD", d["truth"]["head"]["date"] if d["truth"].get("head") else UNKNOWN, "git log"),
           ("Authority register", (_file_date(repo, authority.REGISTER)), f"{d['authority']['events']} events" if d["authority"]["ok"] else "DOES NOT RESOLVE"),
           ("Master Plan", _file_date(repo, "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md"), "last commit touching the file"),
           ("Decision Log", _file_date(repo, "docs/STOCK_ATLAS_DECISION_LOG.md"), "last commit touching the file"),
           ("Candidate ledger", lev, "last recorded event"),
           ("Capability matrix", _file_date(repo, "atlas_ui/CAPABILITY_MATRIX.md"), "generated from the capability list"),
           ("Portfolio snapshot", (snap["as_of"] + " (valuation date)") if snap else UNKNOWN, "approved snapshot")]
    d["sources"] = [{"name": n, "last_changed": w, "detail": x} for n, w, x in src]
    d["working_tree_dirty"] = d["truth"].get("dirty")

    # --- authority health (the preflight, summarized)
    if run_preflight:
        try:
            from .verify import preflight
            cs = preflight(repo, use_git=use_git)
            d["preflight"] = {"ok": sum(c.status == "OK" for c in cs), "fail": [c.line() for c in cs if c.status == "FAIL"], "warn": [c.line() for c in cs if c.status == "WARN"],
                              "info": sum(c.status == "INFO" for c in cs), "skipped": sum(c.status == "SKIP" for c in cs)}
        except Exception as exc:
            d["preflight"] = {"ok": None, "fail": [f"preflight raised {type(exc).__name__}"], "warn": [], "info": None, "skipped": None}
    else:
        d["preflight"] = None
    return d
