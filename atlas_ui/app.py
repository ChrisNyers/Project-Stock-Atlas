"""Dashboard server (stdlib, loopback only). Presentation + thin adapters only.

All pages are server-rendered and contain no JavaScript. Eligibility, hashes,
freshness and ledger facts are read from the backend; nothing is computed here.
"""
from __future__ import annotations

import json
import os
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape as e
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from operating_mvp import ledger

from . import canonical, demo, project, research
from .service import (BASELINE_COMMIT, PAPER_ACTIONS, Blocked, Rejected, Stage7Service, Workspace, read_index)

THEME = (Path(__file__).parent / "theme.css").read_text(encoding="utf-8")
EXTRA_CSS = ".rowlist div strong{display:block}.banner-demo{background:#fbeeea;border:1px solid #e3b7ad;color:#7d2f23;padding:12px 15px;border-radius:11px;font-size:12px;margin-bottom:22px}pre.rendered{background:#f5f7f7;border:1px solid #dfe6e7;border-radius:10px;padding:12px;font-size:11px;white-space:pre-wrap}.nav a{text-decoration:none}.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}.alt{border:1px solid #dce6e6;border-radius:11px;padding:13px;background:#fff}.alt b{display:block;font-size:12px}.alt .band{font-size:20px;font-weight:800;margin:6px 0}.err{border:1px solid #e3b7ad;background:#fbeeea;color:#7d2f23;padding:11px;border-radius:10px;margin-bottom:14px;font-size:12px}.okbox{border:1px solid #cfe4e0;background:#f2f8f7;color:#255a57;padding:11px;border-radius:10px;margin-bottom:14px;font-size:12px}"

NAV = [("/", "Overview"), ("/intake", "Opportunity intake"), ("/cohort", "Research cohort"), ("/stage7", "Stage 7 evidence"),
       ("/desk", "Decision desk"), ("/history", "Decision history"), ("/capabilities", "Capability matrix")]

# Project oversight is a separate sidebar section; the seven investment pages above are unchanged. With PROJECT_NAV empty the shared chrome renders as before.
NAV_PROJECT_DEFAULT = [("/project", "Project dashboard")]
PROJECT_NAV = list(NAV_PROJECT_DEFAULT)

# Single source of truth for the honest capability matrix (page + CAPABILITY_MATRIX.md).
CAPABILITIES = [
    ("A. Overview: canonical Cycle 0 portfolio/policy, pilot status, candidates", "PROVEN CANONICAL OFFLINE",
     "The latest HUMAN-APPROVED portfolio snapshot named by the authority register (docs/authority_register.jsonl), re-validated on every load (SHA-256, holding count, total); the denominator stays approximate; as-of and source shown; superseded snapshots stay loadable."),
    ("B. Intake + immutable versioned pre-Atlas stance (source provenance, no source privilege, QUICK_TEST mandatory)", "PROVEN CANONICAL OFFLINE",
     "Writes the existing append-only discovery ledger; later stance versions are labelled revisions, never edits."),
    ("C1. SEC/issuer ingestion modules (sec_adapter, xbrl_parser, identity_resolver, point-in-time)", "PROVEN CANONICAL OFFLINE",
     "Exist and are regression-tested in the repo (Phase 4A.5); NOT yet connected to the UI or the evidence ledger."),
    ("C2. SEC filings-to-evidence adapter (company facts -> point-in-time PRIMARY evidence, retained snapshot) and source-backed economics view", "PROVEN LIVE",
     "Run live against SEC EDGAR for MCD, GEV, RMD, ORCL: approved XBRL concepts, explicit annual periods, accession + filing date as known-at, units; missing/conflicting facts become UNVERIFIED questions, nothing imputed. 25/25 selected core facts re-found in the filings' own primary documents (SOURCE_VERIFICATION_001). Not an independent second data vendor."),
    ("D. Live price + XNYS session (Gate B), read-only", "PROVEN LIVE",
     "Real TwelveData binding with the independent XNYS calendar for MCD, GEV, RMD, ORCL (FRESH, USD, XNYS, identity SEC-CIK keys) and the live Gate B suite (54 passed, 1 transient provider ERROR that passed on re-run). Read-only: no Stage 7 run and no decision exists. The ELIGIBLE funded branch has never been exercised on live data."),
    ("E. Stage 7 via CapitalDecisionFacade.run_stage7, retained hashed run, side-by-side alternatives", "FIXTURE-TESTED",
     "Runs through the real facade with a FIXTURE price provider in DEMO mode and tests. No canonical run exists. MCD is PARKED until 2026-11-04. Treasury reference is human-attested; security decision is explicit; all % inputs use one unit. Retained runs are referenced workspace-relative, so a moved or extracted workspace still verifies, rehydrates and funds from its own files (traversal, symlinks and tampering are refused)."),
    ("F. Human Stage 8 (paper only): facade-enforced funded freshness, non-actions, ledger proof", "FIXTURE-TESTED",
     "Real facade + DecisionStore; funded freshness is mandatory (FundedFreshnessEvidence, frozen-control change 001) and rejected paths leave zero ledger rows. Freshness uses a sealed backend UTC clock (changes 002 and 003): a caller-supplied created_at cannot establish the time used and a created_at more than 5 minutes from it is refused; no facade attribute, subclass, patched datetime name or test-runner import can choose the clock (the pytest-presence exemption was removed). Residual: code that edits the control inside the same process (private entry, overwriting the sealed clock) is prevented operationally, not by Python."),
    ("G1. Decision history (append-only ledger) + manual linked revisit note", "PROVEN CANONICAL OFFLINE",
     "Reads the real ledger; a revisit is a dated linked note, the original record is never edited."),
    ("G2. Linked later observation (append-only, price-only) ", "PROVEN CANONICAL OFFLINE",
     "MCD: dated observation linked to the underwriting record with a price-only change (+7.9%, SECONDARY vs UNCERTIFIED originals). Benchmark comparison vs time-matched cash/Treasury and SPY adjusted total return is UNVERIFIED / NOT IMPLEMENTED; monitoring cadence is out of scope."),
    ("H. Unranked research cohort and descriptive 'attractive at the verified price?' assessment view", "PROVEN CANONICAL OFFLINE",
     "Built on live SEC + Gate B data for MCD (parked), GEV, RMD, ORCL (SURFACED, INSUFFICIENT EVIDENCE). Assessments are DRAFT_BY_RECORDER and not human-accepted; no ranks, no scores, no Stage 7 or capital control in the view. No candidate yet permitted a 'SUPPORTED' example. Saved research snapshots are referenced by a bare file name inside the research workspace and bound to their SHA-256, so an extracted ZIP loads them anywhere; a missing, tampered or mis-bound snapshot is shown as a RESEARCH EVIDENCE ERROR, never as 'no research'."),
    ("I. Source-of-truth reference, preflight, regression verification and delivery (tooling)", "PROVEN CANONICAL OFFLINE",
     "docs/CURRENT_AUTHORITY.md holds the rules; the values that change (approved state, portfolio snapshot, active work, candidate-ledger acceptance) are HUMAN-approved, hash-chained events in docs/authority_register.jsonl, resolved by `python -m atlas_ui preflight` and by the app (latest approved snapshot only; the Stage 7 and funded Stage 8 server-side gates follow the register-approved candidate status, so an unapproved promotion never opens capital comparison and any unapproved status change closes it; drafts and unapproved newer records are never followed; conflicting approved records fail closed; superseded snapshots stay loadable; a revisit date is a trigger, never a promotion). `verify` runs the suite with skips classified and an optional clean-extraction run; `deliver` builds one ZIP, one patch and one report and fails if the repository preflight, the clean-extraction preflight or either test run fails. Historical Pilot 2 / Sprint 2 instructions are marked non-governing. Tooling only: no investment logic."),
    ("J. Project oversight dashboard (/project, separate PROJECT section of the same app)", "PROVEN CANONICAL OFFLINE",
     "One page read live from the authority register (approved state, active work, MILESTONE events), git, the candidate ledger, the capability list and the Decision Log. Shows Git HEAD, the published GitHub position and the approved baseline separately; milestones by phase with counts only (no percentages); a COMPLETE milestone counts only if a human approved it and its evidence resolves; unapproved, unsupported or missing information is shown as such or as UNKNOWN. A project view, not an investment view: it reads no price, makes no assessment and writes nothing except an explicit read-only GitHub check."),
    ("K. MCD research run: reverse valuation, reference cases and SPY / Treasury-cash comparison (script and retained artifact; not an app feature)", "PROVEN CANONICAL OFFLINE",
     "atlas_ui/valuation.py (pure, unit-tested arithmetic) plus a run over live read-only inputs (SEC facts, provider closes, the keyless U.S. Treasury par-yield CSV) whose derived result and input hashes are committed; raw provider series are not (storage terms). Verified: dividend-adjustment convention, dividends tied to SEC, Treasury values reproduced. Output is descriptive, not a forecast or recommendation; no edge is demonstrated. The Treasury source is evaluated, NOT integrated (needs the human's approval). Visible on the MCD candidate page as a draft assessment and evidence."),
    ("Real trades / broker connectivity / execution", "NOT IMPLEMENTED", "By design: paper only. No order API exists."),
]


@dataclass
class App:
    ws: Workspace
    svc: Stage7Service
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
    github_live: dict | None = None  # result of the last explicit "Check GitHub now" (read-only ls-remote); never persisted

    @property
    def mode(self) -> str:
        return self.ws.mode


# ------------------------------------------------------------------ helpers
def money(x) -> str:
    return f"${float(x):,.2f}"


def pill(text: str, kind: str = "no") -> str:
    return f'<span class="pill {kind}">{e(text)}</span>'


def status_pill(status: str) -> str:
    kind = {"ELIGIBLE FOR STAGE 8": "ok", "WATCH / NO DECISION": "wait", "NOT DISTINGUISHABLE": "wait", "BLOCKED": "danger"}.get(status, "no")
    return pill(status, kind)


def page(app: App, active: str, title: str, body: str, flash: str = "", err: str = "", section: str = "", head_extra: str = "") -> str:
    nav = "".join(f'<a class="navbtn{" active" if p == active else ""}" href="{p}"><span class="number">{i + 1}</span>{e(n)}</a>'
                  for i, (p, n) in enumerate(NAV))
    if app.mode == "DEMO":
        banner = ('<div class="banner-demo"><b>DEMO MODE — FIXTURE DATA.</b> Prices come from a fixture provider labelled '
                  'FIXTURE-DEMO in an isolated workspace. Nothing here is evidence, a Stage 7 run for the pilot, or a decision.</div>')
    else:
        banner = ('<div class="warning"><strong>CONNECTED TO STOCK ATLAS — canonical records.</strong> Paper decisions only. '
                  'No real orders. Stage 7 runs only through the frozen facade; Human Stage 8 alone decides.</div>')
    proj = ""
    if PROJECT_NAV:
        proj = ('<div class="navtitle" data-group="project" style="color:#e6c27a;margin-top:18px">PROJECT</div><nav class="nav">'
                + "".join(f'<a class="navbtn{" active" if p == active else ""}" href="{p}"><span class="number">P{i + 1}</span>{e(n)}</a>' for i, (p, n) in enumerate(PROJECT_NAV)) + "</nav>")
    crumb = "PROJECT STOCK ATLAS / PROJECT OVERSIGHT" if section == "project" else "PROJECT STOCK ATLAS / CONTROLLED LIVE PILOT"
    msgs = (f'<div class="err">{e(err)}</div>' if err else "") + (f'<div class="okbox">{flash}</div>' if flash else "")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · Stock Atlas</title><style>{THEME}{EXTRA_CSS}
@media(max-width:820px){{.app{{grid-template-columns:1fr}}.sidebar{{position:static;height:auto}}.layout,.topstats,.inputs{{grid-template-columns:1fr}}}}</style>{head_extra}</head>
<body><div class="app"><aside class="sidebar"><div class="brand"><div class="mark">A</div><div><span class="brand-name">STOCK ATLAS</span>
<span class="brand-small">Decision workspace</span></div></div><div class="navtitle">WORKSPACE</div><nav class="nav">{nav}</nav>{proj}
<div class="sidebottom"><b>Frozen controls preserved</b><p>Baseline {BASELINE_COMMIT[:7]}… Stage 7 compares only. Stage 8 remains human. Paper only.</p></div></aside>
<main class="main"><div class="topbar"><span class="crumb">{crumb} · {e(app.mode)}</span><span class="version">UI integration v0.1</span></div>
{banner}{msgs}{body}<p class="footer-note">Stock Atlas — presentation and input layer over the existing engine · No real trades · Capital status: NO REAL PORTFOLIO ACTION</p></main></div></body></html>"""


def key_status(app: App) -> tuple[str, str]:
    if app.svc._key_present():
        return "PRESENT", "ok"
    return "ABSENT", "danger"


def candidate_runs(app: App, cid: str, ticker: str) -> list[dict]:
    return [r for r in app.svc.list_runs() if r["candidate_id"] == cid or r["ticker"] == ticker]


# ------------------------------------------------------------------ pages

DISPOSITION_TEXT = {"SUPPORTED": ("SUPPORTED at the verified price (research level)", "ok"),
                    "INSUFFICIENT_EVIDENCE": ("INSUFFICIENT EVIDENCE", "wait"),
                    "NOT_SUPPORTED": ("NOT SUPPORTED at the verified price (research level)", "danger"),
                    "PARKED_FOR_REVISIT": ("PARKED FOR REVISIT", "wait")}


def research_dir(app: App) -> Path:
    return app.ws.root / "research"


def research_snapshot(app: App, candidate_id: str) -> tuple[dict | None, str | None]:
    """(snapshot | None, error | None). A retained snapshot that fails verification is returned as an ERROR to display, never as 'no research'."""
    try:
        return research.latest_snapshot(research_dir(app), candidate_id), None
    except research.ResearchIntegrityError as exc:
        return None, str(exc)


def effective_disposition(c: dict) -> tuple[str, str, dict | None]:
    """Latest recorded assessment, else a lifecycle-derived default. Nothing here scores or recommends."""
    a = c["assessments"][-1] if c["assessments"] else None
    if a:
        return a["disposition"], "assessment v%d" % a["version"], a
    if c["state"] == "PARKED":
        return "PARKED_FOR_REVISIT", "lifecycle state (no assessment recorded)", None
    return "INSUFFICIENT_EVIDENCE", "default — no assessment recorded", None


def _pct(x) -> str:
    return "n/a" if x is None else f"{x * 100:.1f}%"


def _bn(x) -> str:
    return "n/a" if x is None else f"${x / 1e9:,.2f}B"


def snapshot_rows(snap: dict) -> tuple[str, dict]:
    data = snap["data"]
    ends = sorted(data["periods"], reverse=True)
    latest = ends[0]
    g = lambda e, f: (data["periods"][e].get(f) or {}).get("value")
    m = lambda e, k: data["derived_inference"].get(e, {}).get(k)
    head = "".join(f"<th>FY {e[:4]}</th>" for e in ends)
    def row(label, fn, note=""):
        return f"<tr><td>{label}</td>" + "".join(f"<td>{fn(e)}</td>" for e in ends) + f"<td class='small'>{note}</td></tr>"
    body = (row("Revenue", lambda e: _bn(g(e, "revenue")), "FACT — SEC")
            + row("Revenue growth", lambda e: _pct(m(e, "revenue_growth")), "INFERENCE — arithmetic")
            + row("Operating margin", lambda e: _pct(m(e, "operating_margin")), "INFERENCE")
            + row("Net margin", lambda e: _pct(m(e, "net_margin")), "INFERENCE")
            + row("Diluted EPS", lambda e: "n/a" if g(e, "diluted_eps") is None else f"${g(e, 'diluted_eps'):.2f}", "FACT — SEC")
            + row("EPS growth", lambda e: _pct(m(e, "eps_growth")), "INFERENCE")
            + row("Diluted share change", lambda e: _pct(m(e, "diluted_share_change")), "INFERENCE (dilution if +)")
            + row("Free cash flow (CFO − capex)", lambda e: _bn(m(e, "free_cash_flow")), "INFERENCE")
            + row("FCF ÷ net income", lambda e: _pct(m(e, "fcf_conversion_of_net_income")), "INFERENCE")
            + row("Net debt", lambda e: _bn(m(e, "net_debt")), "INFERENCE — shown only if all legs are SEC facts"))
    return f"<table><tr><th>Metric</th>{head}<th></th></tr>{body}</table>", data


def assessment_panel(app: App, c: dict) -> str:
    disp, src, a = effective_disposition(c)
    label, kind = DISPOSITION_TEXT[disp]
    lst = lambda xs, empty="none recorded": "".join(f"<li>{e(x)}</li>" for x in xs) or f"<li class='mut'>{e(empty)}</li>"
    snap, snap_err = research_snapshot(app, c["candidate_id"])
    fin, price = '<p class="subtle">No source-backed financial snapshot has been retained for this candidate (run <span class="mono">python -m atlas_ui research ' + e(c["candidate_id"]) + '</span>).</p>', ""
    if snap_err:
        fin = (f'<p class="subtle">{pill("RESEARCH EVIDENCE UNAVAILABLE", "danger")} {e(snap_err)}<br>This is an integrity failure of the retained snapshot, '
               f'not an absence of research; nothing is displayed in its place.</p>')
    if snap:
        table, data = snapshot_rows(snap)
        gaps = "".join(f"<li>{e(x)}</li>" for x in data["gaps"][:12]) + (f"<li class='mut'>… {len(data['gaps']) - 12} more UNVERIFIED items in the unresolved list</li>" if len(data["gaps"]) > 12 else "")
        fin = (f'<p class="subtle">SEC EDGAR company facts, approved XBRL concepts, annual periods, retained as <span class="mono">{e(snap["snapshot"]["sha256"][:16])}…</span> '
               f'(recorded {e(snap["recorded_at"][:10])}; each fact carries accession, filing date = known-at, period and units in the evidence ledger).</p>{table}'
               f'<h3 style="margin-top:12px">UNVERIFIED / conflicting (not imputed)</h3><ul>{gaps or "<li class=mut>none</li>"}</ul>')
        pr = data.get("price_relative_inference", {})
        if "inputs" in pr:
            i = pr["inputs"]
            try:
                from live_session_calendar import latest_completed_session
                cur = latest_completed_session(app.clock(), mic="XNYS").session_date.isoformat()
            except Exception:
                cur = "?"
            stale = "" if cur == i["price_session"] else f' {pill("PRICE SESSION OLDER THAN LATEST COMPLETED " + cur, "danger")}'
            price = (f'<h3 style="margin-top:12px">What is priced in (arithmetic on the bound price; no forecast)</h3><p>Gate B bound price <b>${i["price"]:g}</b> for session {e(i["price_session"])}.{stale}</p>'
                     f'<ul><li>P/E on FY{i["fy_end"][:4]} diluted EPS: <b>{pr.get("pe_on_latest_fy_diluted_eps", float("nan")):.1f}×</b> (earnings yield {_pct(pr.get("earnings_yield"))})</li>'
                     f'<li>FCF yield: <b>{_pct(pr.get("fcf_yield_on_weighted_diluted_shares"))}</b> — {e(pr.get("caveat_fcf_yield") or pr.get("fcf_yield_status", ""))}</li></ul>')
        else:
            price = f'<p class="subtle"><b>Price-relative view BLOCKED:</b> {e(str(pr.get("status", "no price evidence")))}</p>'
    held = ledger_holding_note(c)
    asmt = (f'<div class="rowlist"><div><strong>Research disposition</strong><span>{e(src)}</span></div>{pill(label, kind)}</div>'
            + (f'<p class="subtle">Authored by {e(a["authored_by"])} · status <b>{e(a["status"])}</b>{"" if a["status"] == "HUMAN_ACCEPTED" else " (not yet human-accepted)"} · {e(a["date"])}</p>'
               f'<h3>Priced-in view</h3><p>{e(a["priced_in_view"])}</p>'
               f'<h3>Coarse return band</h3><p>{e(a["return_band"]) + " — basis: " + e(a["return_band_basis"]) if a["return_band"] else "<i>not substantiated — none shown</i>"}</p>'
               f'<h3>Dominant drivers (≤3)</h3><ul>{lst(a["drivers"])}</ul><h3>Highest-impact risks</h3><ul>{lst(a["risks"])}</ul>'
               f'<h3>What would disprove the thesis</h3><ul>{lst(a["falsifiers"])}</ul><h3>New information that would change this assessment</h3><ul>{lst(a["what_would_change"])}</ul>'
               f'<h3>Evidence gaps</h3><ul>{lst(a["evidence_gaps"])}</ul><h3>Relevant existing holdings</h3><p>{e(a["existing_holdings_note"] or held)}</p>'
               if a else f'<p class="subtle">{e(held)}</p>'))
    obs = "".join(f'<div class="event"><strong>{e(o["observed_on"])} — linked to {e(o["linked_to"])}</strong><p>{e(o["what_changed"])}</p>'
                  + (f'<p class="small">price {o["price"]:g} ({e(o["price_session"])}, {e(o["price_grade"])}) vs original {o["original_price"]:g} ({e(o["original_price_grade"])}) = <b>{o["price_change_only"]:+.1%} price change only</b>. {e(o["price_change_note"])}</p>' if "price_change_only" in o else "")
                  + f'<p class="small">Benchmark: {e(o["benchmark"])}</p></div>' for o in c["observations"])
    return (f'<section class="panel"><h2>Opportunity assessment — descriptive research view, not a capital verdict</h2>{asmt}</section>'
            f'<section class="panel"><h2>Source-backed company economics</h2>{fin}{price}</section>'
            f'<section class="panel"><h2>Later observations (append-only, linked)</h2><div class="audit">{obs or "<p class=subtle>None recorded.</p>"}</div></section>')


def baseline_phrase() -> str:
    """Wording for the acknowledgement checkbox, taken from the currently approved snapshot (not a fixed date)."""
    try:
        c0 = canonical.current_portfolio()
        return f"dated {c0.as_of[:10]} (snapshot {c0.portfolio_snapshot_id}, defensive ≈ ${c0.defensive_approx:,.0f})"
    except canonical.CanonicalError:
        return "(UNAVAILABLE: the authority records failed validation; Stage 7 will refuse)"


def ledger_holding_note(c: dict) -> str:
    try:
        w = canonical.current_portfolio().weight(c.get("ticker") or "")
    except canonical.CanonicalError:
        return "existing holdings unavailable (canonical baseline failed validation)"
    return (f"{c['ticker']} is an existing holding at ≈{w:.2%} of the approximate identified value." if w > 0 else
            f"{c.get('ticker') or c['candidate_id']} is not among the baseline holdings; driver overlap is not assigned (human-authored at Stage 7).")


def cohort_page(app: App) -> str:
    cands = sorted((c for c in ledger.replay(app.ws.candidate_ledger).values() if c["state"] != "REJECTED"), key=lambda c: c["candidate_id"])
    rows = ""
    for c in cands:
        disp, src, a = effective_disposition(c)
        label, kind = DISPOSITION_TEXT[disp]
        snap, snap_err = research_snapshot(app, c["candidate_id"])
        price = fcf = opm = rg = pe = "n/a"
        sess = "RESEARCH EVIDENCE ERROR" if snap_err else "—"
        if snap:
            d = snap["data"]
            le = max(d["periods"])
            m = d["derived_inference"].get(le, {})
            opm, rg, fcf = _pct(m.get("operating_margin")), _pct(m.get("revenue_growth")), _pct(m.get("fcf_conversion_of_net_income"))
            pr = d.get("price_relative_inference", {})
            if "inputs" in pr:
                price, sess, pe = f"${pr['inputs']['price']:g}", pr["inputs"]["price_session"], f"{pr.get('pe_on_latest_fy_diluted_eps', 0):.1f}×"
        stance = (f"v{c['stances'][0]['version']} frozen" if c["stances"] else ("frozen record" if any("STANCE" in r for r in c["refs"]) else "none — human to supply"))
        qt = next((f for f in reversed(c["falsifications"]) if f["status"] == "ACTIVE"), None)
        qts = qt["result"] if qt else ("not run (grandfathered)" if c["grandfathered"] else "not run")
        until = f' · until {e(c["parked_until"])}' if c["parked_until"] else ""
        risk = (a["risks"][0] if a and a["risks"] else "—")
        chg = (a["what_would_change"][0] if a and a["what_would_change"] else "—")
        rows += (f'<tr><td><b><a href="/candidate/{urllib_q(c["candidate_id"])}">{e(c["candidate_id"])}</a></b><br><span class="small">{e(c["source"])}</span></td>'
                 f'<td>{pill(c["state"].replace("_", " ") + until)}<br><span class="small">stance: {e(stance)}<br>QUICK_TEST: {e(qts)}</span></td>'
                 f'<td>{pill(label, kind)}<br><span class="small">{e(src)}</span></td><td>{price}<br><span class="small">{e(sess)}</span></td><td>{pe}</td>'
                 f'<td>{rg}<br><span class="small">op margin {opm}<br>FCF/NI {fcf}</span>' + (f'<br>{pill("RESEARCH EVIDENCE ERROR", "danger")}<br><span class="small">{e(snap_err)}</span>' if snap_err else '') + '</td><td class="small">{e(risk)}</td><td class="small">{e(chg)}</td></tr>')
    alts = ("<div class='cols'>" + "".join(f"<div class='alt'><b>{t}</b><span class='subtle'>{d}</span></div>" for t, d in (
        ("SPY / beta", "Stage 7 only: needs a human-authored basis; not computed here."), ("Treasury / Cash", "Stage 7 only: needs an attested reference; not computed here."),
        ("Relevant existing holdings", "Human-assigned drivers at Stage 7; ADD-ONLY (no recycle)."), ("Do Nothing", "Always preserved."))) + "</div>")
    body = f"""<div class="view active"><p class="eyebrow">Research cohort</p><h1>Side by side — unranked</h1>
<p class="intro">Candidates are listed alphabetically; no rank, score, ordering by merit or allocation is implied. “Research disposition” is descriptive and never a capital verdict.
MCD and RPM remain PARKED (dates are revisit triggers, not promotions). Admission to the 3–5 capital-decision cycles is a separate human decision.</p>
<section class="panel"><div class="table-wrap"><table><tr><th>Candidate</th><th>Lifecycle</th><th>Research disposition</th><th>Verified price</th><th>P/E</th><th>Economics (FY, SEC)</th><th>Highest-impact risk</th><th>What would change the view</th></tr>{rows}</table></div></section>
<section class="panel"><h2>Capital alternatives (kept separate; Stage 7 only)</h2>{alts}</section></div>"""
    return page(app, "/cohort", "Research cohort", body)


def overview(app: App) -> str:
    c0 = canonical.current_portfolio()
    cands = ledger.replay(app.ws.candidate_ledger)
    runs = app.svc.list_runs()
    ks, kk = key_status(app)
    try:
        ledger.verify_chain(app.ws.candidate_ledger)
        chain = pill("INTACT", "ok")
    except ledger.LedgerError as exc:
        chain = pill("BROKEN", "danger")
    s8 = pill("INTACT", "ok") if app.ws.facade.verify_ledger() else pill("BROKEN", "danger")
    ident = float(c0.identified_value)
    ordered = sorted(c0.holdings, key=lambda kv: -kv[1])
    bar = "".join(f'<span style="flex:{float(v)};background:hsl({170 + i * 7 % 60},35%,{28 + (i * 3) % 40}%)" title="{t}"></span>' for i, (t, v) in enumerate(ordered))
    rows = "".join(f'<div class="item"><span><i class="dot" style="background:#2c736e"></i>{t}</span><strong>{float(v) / ident:.2%}</strong></div>' for t, v in ordered)
    top4 = sum(float(v) for _, v in ordered[:4]) / ident
    pipe = ""
    for c in sorted(cands.values(), key=lambda c: (c["state_since"], c["candidate_id"])):
        cr = [r for r in runs if r["candidate_id"] == c["candidate_id"]]
        s7 = status_pill(cr[-1]["status"]) if cr else pill("Stage 7 NOT RUN / NOT VERIFIED", "wait")
        until = f' until {e(c["parked_until"])}' if c["parked_until"] else ""
        pipe += (f'<tr><td><b><a href="/candidate/{urllib_q(c["candidate_id"])}">{e(c["candidate_id"])}</a></b></td><td>{e(c["investment_question"][:110])}</td>'
                 f'<td>{pill(c["state"].replace("_", " ") + until, "wait" if c["state"] == "PARKED" else "no")}</td><td>{s7}</td></tr>')
    body = f"""<div class="view active"><p class="eyebrow">Portfolio and pilot</p><h1>Your investment decision workspace</h1>
<p class="intro">Canonical portfolio context, your independent judgment, verified Stage 7 results and a deliberate paper decision — through the existing Stock Atlas controls.</p>
<div class="topstats"><div class="stat"><div class="statlabel">Identified portfolio</div><div class="statvalue">≈ ${ident:,.0f}</div><div class="statsub">APPROXIMATE (defensive ≈ $59K) · HUMAN-SUPPLIED as of {e(c0.as_of)} · {(app.clock() - c0.effective_at).days} days old · not live</div></div>
<div class="stat"><div class="statlabel">{len(c0.holdings)} stocks</div><div class="statvalue">{money(c0.stocks_total)}</div><div class="statsub">exact, reconciled by the loader</div></div>
<div class="stat"><div class="statlabel">Defensive (T-bills + MM)</div><div class="statvalue">≈ {money(c0.defensive_approx)}</div><div class="statsub">approximate by design</div></div>
<div class="stat"><div class="statlabel">Funding pocket</div><div class="statvalue">$25–50K</div><div class="statsub">new outside capital · T+1 · ADD-ONLY</div></div></div>
<div class="layout"><div><section class="panel"><div class="panel-head"><h2>Frozen portfolio exposure</h2>{pill("HUMAN-SUPPLIED BASELINE","wait")}</div>
<div class="allocline">{bar}</div><div class="legend">{rows}</div><div class="thin"></div>
<p class="subtle">Top-4 names = {top4:.1%}. Policy: ADD-ONLY, no trims or recycle; reserves N/A; STARTER 1–2%. Source: <span class="mono">{e(c0.doc_path)}</span> (SHA-256 <span class="mono">{c0.doc_sha256[:16]}…</span>). The handoff's $500K sanitized snapshot of 2026-09-02 is <b>not</b> the canonical baseline.</p></section>
<section class="panel"><div class="panel-head"><h2>Candidates</h2></div><div class="table-wrap"><table><tr><th>Case</th><th>Question</th><th>State</th><th>Stage 7</th></tr>{pipe}</table></div>
<p class="subtle" style="margin-top:12px">Stage 7 can be started only for a candidate a human has moved to READY FOR CAPITAL COMPARISON. MCD and RPM are PARKED pending dated evidence.</p></section></div>
<div><section class="panel"><div class="panel-head"><h2>Operational gates</h2>{pill("GATE B CLOSED","ok")}</div>
<div class="rowlist"><div><strong>Frozen architecture</strong><span>Accepted commit {BASELINE_COMMIT[:7]}…</span></div>{pill("ANCESTOR OF HEAD","ok")}</div>
<div class="rowlist"><div><strong>TWELVEDATA_API_KEY</strong><span>server-side only; never sent to the browser</span></div>{pill(ks, kk)}</div>
<div class="rowlist"><div><strong>Live price binding</strong><span>needs the key; fixture prices are refused in canonical mode</span></div>{pill("BLOCKED" if ks == "ABSENT" else "READY TO TRY", "danger" if ks == "ABSENT" else "wait")}</div>
<div class="rowlist"><div><strong>Discovery ledger chain</strong><span>append-only, hash-chained</span></div>{chain}</div>
<div class="rowlist"><div><strong>Decision ledger</strong><span>{len(app.svc.ledger_rows())} record(s)</span></div>{s8}</div>
<div class="rowlist"><div><strong>Retained Stage 7 runs</strong><span>{len(runs)} in this workspace</span></div>{pill(str(len(runs)), "ok" if runs else "wait")}</div></section>
<section class="panel"><h2>Next permitted step</h2><p class="subtle" style="margin-top:8px">Supply <span class="mono">TWELVEDATA_API_KEY</span> in the server environment (rotate the previously exposed key), then wait for the dated evidence: MCD Q3 on 2026-11-04, RPM Investor Day on 2026-11-09. No capital action is authorized now.</p></section></div></div></div>"""
    return page(app, "/", "Overview", body)


def urllib_q(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def intake(app: App, err="", flash="") -> str:
    opts = "".join(f"<option>{s}</option>" for s in ledger.SOURCES)
    cands = ledger.replay(app.ws.candidate_ledger)
    rows = ""
    for c in sorted(cands.values(), key=lambda c: c["candidate_id"]):
        st = c["stances"][0] if c["stances"] else None
        stance = (f'v{st["version"]} {"PRE-ATLAS" if st["pre_atlas"] else "revision after analysis"} ({e(st["date"])})' if st
                  else ("frozen record: " + e(", ".join(r.split("/")[-1] for r in c["refs"] if "STANCE" in r)) if any("STANCE" in r for r in c["refs"]) else "none"))
        rows += (f'<tr><td><a href="/candidate/{urllib_q(c["candidate_id"])}">{e(c["candidate_id"])}</a></td><td>{e(c["source"])}</td>'
                 f'<td>{pill(c["state"].replace("_", " "))}</td><td>{stance}</td></tr>')
    body = f"""<div class="view active"><p class="eyebrow">Opportunity intake</p><h1>Freeze your independent view first</h1>
<p class="intro">Record the idea with its source and your own stance <b>before</b> Atlas analysis. The stance is written to the existing append-only ledger and cannot be edited; a later view becomes a new version labelled a revision. A neutral stance is valid. Source is provenance only — it earns no priority.</p>
<section class="panel"><form method="post" action="/intake"><div class="inputs">
<div><label class="field">Company or ticker *</label><input class="text" name="name" required></div>
<div><label class="field">Ticker (optional)</label><input class="text" name="ticker"></div>
<div><label class="field">Source *</label><select name="source">{opts}</select></div>
<div><label class="field">Source detail (required for OTHER)</label><input class="text" name="source_detail"></div>
<div class="full"><label class="field">Why did it surface? *</label><textarea name="why_surfaced" required></textarea></div>
<div class="full"><label class="field">Investment question *</label><textarea name="investment_question" required></textarea></div>
<div class="full"><label class="field">Your independent stance * <span class="fieldhint">e.g. “Neutral research stance — no view yet.” Do not invent conviction.</span></label><textarea name="stance_text" required></textarea></div>
<div><label class="field">Intended action (optional)</label><input class="text" name="intended_action"></div>
<div><label class="field">Amount / funding (optional)</label><input class="text" name="amount"></div>
<div><label class="field">Main concern (optional)</label><input class="text" name="concern"></div>
<div><label class="field">What would you do without Atlas? (optional)</label><input class="text" name="without_atlas"></div></div>
<div class="btn-row" style="margin-top:16px"><button class="btn primary">Record idea and freeze stance</button></div></form></section>
<section class="panel"><h2>Recorded candidates</h2><div class="table-wrap"><table><tr><th>Candidate</th><th>Source</th><th>State</th><th>Frozen stance</th></tr>{rows}</table></div></section></div>"""
    return page(app, "/intake", "Intake", body, flash=flash, err=err)


def candidate_page(app: App, cid: str, err="", flash="") -> str | None:
    c = ledger.replay(app.ws.candidate_ledger).get(cid)
    if c is None:
        return None
    st = "".join(
        f'<div class="event"><strong>Stance v{s["version"]} — {"PRE-ATLAS BASELINE" if s["pre_atlas"] else "REVISION AFTER ANALYSIS (not the pre-Atlas baseline)"}</strong>'
        f'<p>{e(s["date"])} (state when frozen: {e(s["state_when_frozen"])}){" · backfilled" if s["backfilled"] else ""}</p><p>{e(s["stance_text"])}</p>'
        f'<p class="small">Intended action: {e(s["intended_action"] or "—")} · amount/funding: {e(s["amount"] or "—")} / {e(s["funding"] or "—")} · concern: {e(s["concern"] or "—")} · without Atlas: {e(s["without_atlas"] or "—")}</p></div>'
        for s in c["stances"]) or '<p class="subtle">No ledger stance. See the frozen record(s) listed under Records for historical candidates.</p>'
    refs = "".join(f'<li class="mono">{e(r)}</li>' for r in c["refs"]) or "<li>none</li>"
    runs = candidate_runs(app, cid, c["ticker"])
    run_rows = "".join(f'<tr><td><a href="/run/{urllib_q(r["run_id"])}">{e(r["run_id"])}</a></td><td>{status_pill(r["status"])}</td><td class="mono">{r["stage7"]["sha256"][:16]}…</td><td>{pill("VERIFIED" if r["verified"] else "NOT VERIFIED", "ok" if r["verified"] else "danger")}</td></tr>' for r in runs) \
        or '<tr><td colspan="4"><span class="pill wait">NOT RUN / NOT VERIFIED</span></td></tr>'
    try:
        auth = app.ws.candidates()[cid]
        why = app.ws.capital_gate(cid, auth)
        gate = ("READY — a human marked this candidate READY FOR CAPITAL COMPARISON and the authority register approves it." if why is None
                else f"Not ready: {why}." + (" Revisit date reached: a trigger to reassess, not a promotion." if auth["revisit_due"] else ""))
    except Blocked as exc:
        gate = f"Not ready: {exc}"
    body = f"""<div class="view active"><p class="eyebrow">Candidate</p><h1>{e(cid)} — {e(c["name"])}</h1>
<div class="btn-row">{pill(c["state"].replace("_", " "))}{pill("source: " + c["source"])}{pill("grandfathered") if c["grandfathered"] else ""}</div>
<section class="panel" style="margin-top:16px"><h2>Why it surfaced</h2><p>{e(c["why_surfaced"])}</p><div class="thin"></div><h3>Investment question</h3><p>{e(c["investment_question"])}</p>
<p class="subtle" style="margin-top:10px">Provenance: {e(c["source"])}{" — " + e(c["source_detail"]) if c["source_detail"] else ""}; surfaced {e(c["surfaced_on"])}.</p></section>
<section class="panel"><h2>Frozen independent stance</h2><div class="audit">{st}</div></section>
{assessment_panel(app, c)}
<section class="panel"><h2>Stage 7 status</h2><p class="subtle">{e(gate)}</p><div class="table-wrap"><table><tr><th>Run</th><th>Status</th><th>Hash</th><th>Retained artifacts</th></tr>{run_rows}</table></div></section>
<section class="panel"><h2>Records</h2><ul>{refs}</ul><p class="subtle">Evidence ledger, falsification and state changes are edited on the Discovery board (same ledger): <span class="mono">python -m atlas_ui serve</span> also starts it on its own port.</p></section></div>"""
    return page(app, "/", f"{cid}", body, flash=flash, err=err)


def stage7_page(app: App, err="", flash="", market: str = "") -> str:
    try:
        ready = [c for c in app.ws.candidates().values() if app.ws.capital_gate(c["candidate_id"], c) is None]      # only candidates the register approves as READY
    except Blocked:
        ready = []
    runs = app.svc.list_runs()
    rr = "".join(f'<tr><td><a href="/run/{urllib_q(r["run_id"])}">{e(r["run_id"])}</a></td><td>{e(r["ticker"])}</td><td>{status_pill(r["status"])}</td><td class="mono">{r["stage7"]["sha256"][:16]}…</td><td>{pill("VERIFIED" if r["verified"] else "NOT VERIFIED", "ok" if r["verified"] else "danger")}</td></tr>' for r in runs) \
        or '<tr><td colspan="5"><span class="pill wait">NOT RUN / NOT VERIFIED — no retained Stage 7 run</span></td></tr>'
    if ready:
        opts = "".join(f'<option value="{e(c["candidate_id"])}">{e(c["candidate_id"])} — {e(c["ticker"] or "NO TICKER RECORDED")}</option>' for c in ready)
        F = lambda n, lab, hint="", ph="": f'<div><label class="field">{lab}<span class="fieldhint">{hint}</span></label><input class="text" name="{n}" placeholder="{ph}"></div>'
        T = lambda n, lab, hint="": f'<div class="full"><label class="field">{lab}<span class="fieldhint">{hint}</span></label><textarea name="{n}"></textarea></div>'
        S = lambda n, lab, vals: f'<div><label class="field">{lab}</label><select name="{n}">' + "".join(f"<option>{v}</option>" for v in vals) + "</select></div>"
        form = f"""<form method="post" action="/stage7/run"><div class="inputs"><div><label class="field">Candidate (READY only)</label><select name="cand">{opts}</select></div>
{F("increment","Increment dollars *","within $25,000–$50,000; weights are recomputed server-side")}
<div class="full"><div class="callout warn">Every field marked % is a PERCENT: type <b>1</b> for 1%, <b>0.5</b> for 0.5%, <b>12</b> for 12%. There is no other unit and nothing is guessed.</div></div>
{S("decision","Security decision * (explicit; never defaulted)",["","BUY","HOLD","WATCH","REDUCE","EXIT","REJECT","NO DECISION"])}
{F("decision_basis","Evidence basis for that decision *","cite the underwriting record, e.g. the evidence-ledger items")}
{F("horizon_years","Horizon years *")}{F("ret_low","Candidate return band low % *","human-authored, coarse")}{F("ret_high","Candidate return band high % *")}
{F("req_low","Required-return band low % *")}{F("req_high","Required-return band high % *")}
{F("spy_low","SPY/beta band low % *","with basis notes below")}{F("spy_high","SPY/beta band high % *")}
{F("tsy_low","Treasury/Cash band low % *")}{F("tsy_high","Treasury/Cash band high % *")}
{F("tsy_ref_key","Treasury reference key","e.g. UST-13W")}{F("tsy_ref_value","Treasury reference yield % *","e.g. 3.9 for 3.9%")}{F("tsy_ref_date","Treasury reference date YYYY-MM-DD *")}
{F("tsy_source_ref","Treasury source reference *","e.g. the home.treasury.gov page you read")}
<div class="full"><label class="field"><input type="checkbox" name="tsy_attest" value="1" style="width:auto"> I retrieved this rate from the U.S. Treasury primary source on the date shown. <span class="fieldhint">Atlas does NOT verify a typed rate; a recent date is not verification. It is recorded as HUMAN-ATTESTED.</span></label></div>
{S("tsy_duration","Treasury duration match",["UNVERIFIED","VERIFIED"])}
{T("spy_notes","SPY basis notes *","one per line")}{T("tsy_notes","Treasury duration/reinvestment notes *","one per line")}
{T("regime","Observable priced-in regime *")}{T("regime_evidence","Regime evidence *","one per line")}
{T("variant","Atlas variant *")}{T("variant_evidence","Variant evidence *","one per line")}
{T("band_basis","Return-band basis *","one per line")}{T("provenance","Underwriting provenance *","one per line")}
{T("uncertainties","Typed uncertainties *","TYPE | description | YES/NO (blocking); one per line")}{T("drivers","Dominant drivers (1–3) *","one per line")}
{F("revisit_price","Price revisit trigger *")}{F("revisit_date","Time revisit date YYYY-MM-DD *")}{F("revisit_thesis","Thesis revisit trigger")}
{S("gate","Underwriting gate",["UNVERIFIED","CLEAR","MARGINAL","FAIL"])}{S("capacity","Candidate capacity",["UNVERIFIED","AVAILABLE","CONSTRAINED"])}{F("remaining_capacity","Remaining capacity % of post-trade portfolio")}
{S("classification","Position classification (human)",["STARTER","OTHER","ADD"])}
{S("tax","Tax constraint (human-attested)",["UNVERIFIED","VERIFIED"])}{S("liquidity","Liquidity (human-attested)",["UNVERIFIED","VERIFIED"])}{S("execution","Execution (human-attested)",["UNVERIFIED","VERIFIED"])}
<div class="full"><label class="field"><input type="checkbox" name="baseline_ack" value="1" style="width:auto"> I acknowledge the portfolio baseline is the approved human-supplied record {e(baseline_phrase())} (holdings are NOT live) and the denominator is approximate. *</label></div>
<div class="full"><label class="field"><input type="checkbox" name="accept_unverified" value="1" style="width:auto"> Proceed to Stage 7 with UNVERIFIED constraints (a funded Stage 8 will still fail closed)</label></div></div>
<div class="btn-row" style="margin-top:16px"><button class="btn primary">Bind market data and run Stage 7 via the facade</button></div></form>"""
    else:
        form = '<p class="subtle">No candidate is READY FOR CAPITAL COMPARISON. Stage 7 cannot be started (MCD and RPM are PARKED pending dated evidence). Nothing is enabled and nothing is inferred.</p>'
    ks, _ = key_status(app)
    mk = f'<div class="okbox">{market}</div>' if market else ""
    body = f"""<div class="view active"><p class="eyebrow">Stage 7 evidence</p><h1>Verified comparison — no recommendation</h1>
<p class="intro">Stage 7 compares only; it emits no action. This page starts the canonical run and lists retained runs. Browser values never decide eligibility.</p>
<section class="panel"><h2>Market data and session (Gate B)</h2><p class="subtle">Price and exchange session are bound server-side; TwelveData key {pill(ks, "ok" if ks == "PRESENT" else "danger")}. Freshness comes from the XNYS calendar, never from the provider or the browser clock.</p>
<form method="get" action="/stage7" class="btn-row" style="margin-top:12px"><input class="text" style="max-width:180px" name="ticker" placeholder="ticker"><button class="btn">Check binding</button></form>{mk}</section>
<section class="panel"><h2>Retained Stage 7 runs</h2><div class="table-wrap"><table><tr><th>Run</th><th>Ticker</th><th>Status</th><th>Artifact SHA-256</th><th>Integrity</th></tr>{rr}</table></div></section>
<section class="panel"><h2>Run Stage 7</h2>{form}</section></div>"""
    return page(app, "/stage7", "Stage 7", body, flash=flash, err=err)


def run_page(app: App, run_id: str, err="", flash="") -> str | None:
    try:
        run, versions, entry = app.svc.load_run(run_id)
    except Blocked as exc:
        if not any(r["run_id"] == run_id for r in read_index(app.ws.index_path)):
            return None
        return page(app, "/stage7", run_id, f'<div class="view active"><h1>{e(run_id)}</h1><div class="err"><b>NOT VERIFIED.</b> {e(str(exc))}</div><p class="subtle">Stage 8 is disabled for this run.</p></div>')
    req = json.loads(Path(app.ws.ref(entry["inputs"]["scenario_model"]).artifact_path).read_text())["request"]
    evd = json.loads(Path(app.ws.ref(entry["inputs"]["evidence_set"]).artifact_path).read_text())
    pb = evd["price_binding"]["price_binding"]
    r = run.result
    pos = r.position
    ret = lambda lo, hi: f'{float(lo):g}% – {float(hi):g}%'
    tsy = next((x for x in [req] if x), req)
    grid = f"""<div class="cols">
<div class="alt"><b>{e(r.ticker)} (candidate)</b><div class="band">{ret(req["ret_low"], req["ret_high"])}</div><span class="subtle">coarse band over {e(str(req["horizon_years"]))}y · human-authored · not a forecast midpoint</span></div>
<div class="alt"><b>SPY / beta</b><div class="band">{ret(req["spy_low"], req["spy_high"])}</div><span class="subtle">overlap UNMEASURED — no diversification credit</span></div>
<div class="alt"><b>Treasury</b><div class="band">{ret(req["tsy_low"], req["tsy_high"])}</div><span class="subtle">ref {e(req["tsy_ref_key"])} = {e(req["tsy_ref_value"])}% on {e(req["tsy_ref_date"])} · <b>HUMAN-ATTESTED, not independently verified</b></span></div>
<div class="alt"><b>Cash</b><div class="band">—</div><span class="subtle">compared together with Treasury (single frozen alternative)</span></div>
<div class="alt"><b>Existing holdings / recycle</b><div class="band">Not permitted</div><span class="subtle">ADD-ONLY policy: no trim or recycle comparison. Driver overlap UNASSIGNED; not described as diversification.</span></div>
<div class="alt"><b>Do Nothing</b><div class="band">—</div><span class="subtle">always preserved</span></div></div>
<p class="subtle" style="margin-top:10px">Overlapping bands cannot be ordered on return alone. No score, ranking or forced allocation is shown.</p>"""
    funded_ok = r.status == "ELIGIBLE FOR STAGE 8" and r.constraint_state.value == "VERIFIED"
    existing = next((x for x in app.svc.ledger_rows() if x["record"]["record_id"] == f"S8-{run_id}"), None)
    if existing:
        rec = existing["record"]
        s8 = f"""<section class="panel"><h2>Human Stage 8 — recorded</h2><div class="okbox"><b>{e(rec["human_stage8_action"])}</b> (paper) · record <span class="mono">{e(rec["record_id"])}</span> · entry hash <span class="mono">{e(existing["entry_hash"][:24])}…</span></div><p>{e(rec["human_rationale"] or "")}</p></section>"""
    else:
        chips = "".join(f'<label class="radiochip"><input type="radio" name="action" value="{a}" {"checked" if a == "DO NOTHING" else ""}><span>{a}{"" if a in ("HOLD CASH", "DO NOTHING") or funded_ok else " — blocked"}</span></label>' for a in PAPER_ACTIONS)
        why = ("" if funded_ok else f'<div class="callout warn">INITIATE/ADD are blocked: Stage 7 is <b>{e(r.status)}</b>, constraints <b>{e(r.constraint_state.value)}</b>. HOLD CASH and DO NOTHING stay available. The backend re-checks this on submit.</div>')
        s8 = f"""<section class="panel"><h2>Human Stage 8 — paper decision</h2>{why}
<form method="post" action="/stage8"><input type="hidden" name="run_id" value="{e(run_id)}"><div class="radrow" style="margin:12px 0">{chips}</div>
<div class="inputs"><div class="full"><label class="field">Your rationale *</label><textarea name="rationale" required></textarea></div>
<div class="full"><label class="field">Why this vs the alternatives (funded only)</label><textarea name="why_vs"></textarea></div>
<div><label class="field">Why this size (funded only)</label><textarea name="why_size"></textarea></div><div><label class="field">Allocation is wrong if… (funded only)</label><textarea name="wrong_if"></textarea></div>
<div><label class="field">Cluster note (if shared drivers)</label><input class="text" name="cluster_note"></div><div><label class="field">Prior record id (linked revisit)</label><input class="text" name="prior_record_id"></div></div>
<div class="callout warn" style="margin-top:12px"><b>Funded actions only (INITIATE/ADD):</b> re-confirm the Treasury reference from the primary source today. It must equal the Stage 7 reference exactly, or Stage 7 must be re-run. A fresh price bind must also reproduce the frozen Stage 7 price exactly.</div>
<div class="inputs" style="margin-top:12px"><div><label class="field">Treasury yield % (re-attested)</label><input class="text" name="tsy_ref_value"></div>
<div><label class="field">Treasury reference date YYYY-MM-DD</label><input class="text" name="tsy_ref_date"></div>
<div><label class="field">Treasury source reference</label><input class="text" name="tsy_source_ref"></div>
<div><label class="field"><input type="checkbox" name="tsy_attest" value="1" style="width:auto"> I re-confirmed this from the Treasury primary source today.</label></div></div>
<div class="callout" style="margin-top:12px">Confirm before submit — candidate <b>{e(r.ticker)}</b>, increment <b>{money(entry["increment_dollars"])}</b>, funding <b>new outside capital</b>, run <span class="mono">{e(run_id)}</span>, Stage 7 SHA-256 <span class="mono">{e(entry["stage7"]["sha256"][:24])}…</span>, constraints <b>{e(r.constraint_state.value)}</b>.
<br><label><input type="checkbox" name="confirm" value="1" style="width:auto"> This is a PAPER decision. No order will be placed.</label></div>
<div class="btn-row" style="margin-top:12px"><button class="btn primary">Record paper decision</button></div></form></section>"""
    unc = "".join(f"<li>{e(l)}</li>" for l in req["uncertainties"].splitlines() if l.strip())
    body = f"""<div class="view active"><p class="eyebrow">Stage 7 run</p><h1>{e(run_id)}</h1><div class="btn-row">{status_pill(r.status)}{pill("mode: " + entry["mode"], "danger" if entry["mode"] == "DEMO" else "ok")}{pill("integrity VERIFIED","ok")}</div>
<section class="panel" style="margin-top:16px"><h2>Retained artifact</h2><div class="rowlist"><div><strong>Stage 7 SHA-256</strong><span class="mono">{e(entry["stage7"]["sha256"])}</span></div></div>
<div class="rowlist"><div><strong>Baseline</strong><span>valuation as of <b>{e(entry.get("baseline_as_of", "2026-10-07")[:10])}</b> (human-supplied, not live); evaluated {e(entry["created_at"][:19])} · denominator approximate · <span class="mono">{e(entry["baseline_doc_sha256"][:24])}…</span></span></div></div>
<div class="rowlist"><div><strong>Priced session</strong><span>{e(entry.get("priced_session", "n/a"))} (XNYS). A funded Stage 8 must pass a fresh-price check against the current session.</span></div></div>
<div class="rowlist"><div><strong>Gating result</strong><span>{e("; ".join(r.reasons))}</span></div></div>
<div class="rowlist"><div><strong>Position</strong><span>{"" if pos is None else f"increment {money(pos.proposed_increment_dollars)} · post-trade weight {pos.post_trade_weight:.2%} · {e(pos.classification.value)} · capacity {e(pos.capacity_status.value)}"}</span></div></div>
<p class="subtle"><a href="/artifact/{urllib_q(run_id)}/stage7.json">stage7.json</a> · <a href="/artifact/{urllib_q(run_id)}/evidence_set.json">evidence_set.json</a> · <a href="/artifact/{urllib_q(run_id)}/scenario_model.json">scenario_model.json</a></p></section>
<section class="panel"><h2>Side-by-side alternatives</h2>{grid}</section>
<section class="panel"><h2>Evidence used</h2><div class="rowlist"><div><strong>Bound price</strong><span>{e(pb["ticker"])} {pb["price"]:g} {e(pb["currency"])} · provider {e(pb["provider"])} · session {e(pb["price_session_date"])} · freshness {e(pb["freshness_status"])} · basis: {e(pb["freshness_basis"])}</span></div></div>
<div class="rowlist"><div><strong>Session authority</strong><span>{e(evd["price_binding"]["session_attestation"]["calendar_name"])} · {e(evd["price_binding"]["session_attestation"]["exchange"])} · {e(evd["price_binding"]["session_attestation"]["authority"])}</span></div></div>
<h3 style="margin-top:12px">Typed uncertainties</h3><ul>{unc}</ul><h3>Dominant drivers</h3><p>{e(req["drivers"].replace(chr(10), " · "))}</p><h3>Revisit triggers</h3><p>{e(req["revisit_price"])} · by {e(req["revisit_date"])}</p></section>
<section class="panel"><h2>Rendered Stage 7 output</h2><pre class="rendered">{e(run.rendered_text)}</pre></section>{s8}</div>"""
    return page(app, "/stage7", run_id, body, flash=flash, err=err)


def desk_page(app: App) -> str:
    runs = app.svc.list_runs()
    done = {r["record"]["record_id"] for r in app.svc.ledger_rows()}
    rows = "".join(f'<tr><td><a href="/run/{urllib_q(r["run_id"])}">{e(r["run_id"])}</a></td><td>{status_pill(r["status"])}</td><td>{pill("decided","ok") if "S8-" + r["run_id"] in done else pill("awaiting human","wait")}</td></tr>' for r in runs) \
        or '<tr><td colspan="3"><span class="pill wait">No retained Stage 7 run — nothing to decide. Do Nothing is the default.</span></td></tr>'
    body = f"""<div class="view active"><p class="eyebrow">Decision desk</p><h1>Human Stage 8 — paper only</h1>
<p class="intro">A decision can be recorded only against a retained, hash-verified Stage 7 run. The browser button is never the control: the backend rechecks the run, status and constraints on submit.</p>
<section class="panel"><table><tr><th>Run</th><th>Stage 7</th><th>Stage 8</th></tr>{rows}</table></section></div>"""
    return page(app, "/desk", "Decision desk", body)


def history_page(app: App, err="", flash="") -> str:
    rows = app.svc.ledger_rows()
    ver = pill("LEDGER VERIFIED", "ok") if app.ws.facade.verify_ledger() else pill("LEDGER BROKEN", "danger")
    tr = "".join(
        f'<tr><td><b>{e(x["record"]["record_id"])}</b></td><td>{e(x["record"]["created_at"][:10])}</td><td>{e(x["record"].get("human_stage8_action") or x["record"]["review_event_type"])}</td>'
        f'<td>{e(x["record"]["stage7_status"])}</td><td>{e(x["record"].get("candidate_security_key") or "—")}</td><td class="mono">{e(x["entry_hash"][:16])}…</td><td>{e(x["record"].get("prior_record_id") or "")}</td></tr>' for x in rows) \
        or '<tr><td colspan="7" class="subtle">Zero rows. No paper decision has been recorded in this workspace.</td></tr>'
    notes = []
    for c in ledger.replay(app.ws.candidate_ledger).values():
        for n in c["notes"]:
            if n["text"].startswith("REVISIT of "):
                notes.append(f'<div class="event"><strong>{e(c["candidate_id"])} — {e(n["date"])}</strong><p>{e(n["text"])}</p></div>')
    opts = "".join(f'<option>{e(x["record"]["record_id"])}</option>' for x in rows)
    cands = "".join(f'<option>{e(c)}</option>' for c in sorted(ledger.replay(app.ws.candidate_ledger)))
    form = (f'<form method="post" action="/revisit"><div class="inputs"><div><label class="field">Candidate</label><select name="candidate_id">{cands}</select></div>'
            f'<div><label class="field">Linked decision record</label><select name="record_id">{opts}</select></div>'
            f'<div class="full"><label class="field">Revisit note * <span class="fieldhint">Appended as a dated linked event; the original record is never edited. A new capital decision needs a fresh Stage 7 run.</span></label><textarea name="note" required></textarea></div></div>'
            '<div class="btn-row" style="margin-top:12px"><button class="btn">Record revisit</button></div></form>') if rows else '<p class="subtle">Revisit becomes available once a decision record exists.</p>'
    body = f"""<div class="view active"><p class="eyebrow">Decision history</p><h1>Append-only record</h1><div class="btn-row">{ver}{pill(str(len(rows)) + " record(s)")}</div>
<section class="panel" style="margin-top:16px"><table><tr><th>Record</th><th>Date</th><th>Action</th><th>Stage 7</th><th>Security</th><th>Entry hash</th><th>Prior</th></tr>{tr}</table></section>
<section class="panel"><h2>Manual revisits</h2><div class="audit">{"".join(notes) or '<p class="subtle">None recorded.</p>'}</div><div class="thin"></div>{form}
<p class="subtle" style="margin-top:12px">Outcome versus cash/SPY with matched as-of dates and automatic trigger monitoring are NOT IMPLEMENTED (see the capability matrix).</p></section></div>"""
    return page(app, "/history", "History", body, flash=flash, err=err)


def capabilities_page(app: App) -> str:
    kind = lambda s: "ok" if s.startswith("PROVEN") else ("wait" if s.startswith("FIXTURE") else "danger")
    rows = "".join(f'<tr><td>{e(a)}</td><td>{pill(b, kind(b))}</td><td>{e(c)}</td></tr>' for a, b, c in CAPABILITIES)
    return page(app, "/capabilities", "Capabilities", f'<div class="view active"><p class="eyebrow">Honest status</p><h1>Capability matrix</h1><section class="panel"><table><tr><th>Capability</th><th>Status</th><th>Detail</th></tr>{rows}</table></section></div>')


def matrix_markdown() -> str:
    out = ["| Capability | Status | Detail |", "|---|---|---|"]
    out += [f"| {a} | **{b}** | {c} |" for a, b, c in CAPABILITIES]
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ API (JSON)
def api_state(app: App) -> dict:
    c0 = canonical.current_portfolio()
    return {"mode": app.mode, "paper_only": True,
            "baseline": {"as_of": c0.as_of, "source": c0.doc_path, "sha256": c0.doc_sha256, "label": c0.label,
                         "identified_value": str(c0.identified_value), "stocks_total": str(c0.stocks_total),
                         "defensive_approx": str(c0.defensive_approx), "holdings": [(t, str(v)) for t, v in c0.holdings]},
            "policy": {"add_only": True, "trims": False, "funding": "EXTERNAL_NEW_CAPITAL $25,000–$50,000 T+1", "starter_cap": canonical.STARTER_CAP_WEIGHT},
            "twelvedata_key": key_status(app)[0],
            "candidates": [{"id": c["candidate_id"], "state": c["state"], "parked_until": c["parked_until"], "source": c["source"]}
                           for c in ledger.replay(app.ws.candidate_ledger).values()],
            "stage7_runs": [{k: r[k] for k in ("run_id", "ticker", "status", "verified", "mode")} | {"sha256": r["stage7"]["sha256"]} for r in app.svc.list_runs()],
            "decision_rows": len(app.svc.ledger_rows()), "decision_ledger_verified": app.ws.facade.verify_ledger()}


def api_cohort(app: App) -> list[dict]:
    out = []
    for c in sorted(ledger.replay(app.ws.candidate_ledger).values(), key=lambda c: c["candidate_id"]):
        disp, src, a = effective_disposition(c)
        snap, snap_err = research_snapshot(app, c["candidate_id"])
        out.append({"candidate_id": c["candidate_id"], "state": c["state"], "parked_until": c["parked_until"], "source": c["source"],
                    "research_disposition": disp, "disposition_source": src, "rank": None,
                    "snapshot_sha256": snap["snapshot"]["sha256"] if snap else None, "research_error": snap_err,
                    "price_relative": snap["data"].get("price_relative_inference") if snap else None})
    return out


# ------------------------------------------------------------------ server
# ------------------------------------------------------------------ project oversight (separate PROJECT section; reads records, writes nothing)
PROJECT_CSS = """<style>
.proj .g4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:18px}
.proj .g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.proj .g2{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:17px}
.proj .tbox{background:#f6f9f9;border:1px solid #e1eaea;border-radius:10px;padding:13px 14px;min-width:0}
.proj .tbox .k{font-size:10px;letter-spacing:.9px;text-transform:uppercase;color:#61737d;font-weight:700}
.proj .tbox .v{font-size:22px;font-weight:800;letter-spacing:-.4px;margin:4px 0 2px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.proj details{border:1px solid #e1eaea;border-radius:10px;margin-bottom:9px;background:#fff}
.proj summary{cursor:pointer;padding:12px 14px;display:flex;justify-content:space-between;gap:12px;align-items:center;font-weight:700;font-size:13px;list-style:none}
.proj summary::-webkit-details-marker{display:none}
.proj summary>span:last-child{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.proj summary>span:first-of-type{flex:1}
.proj .nw{white-space:nowrap;word-break:normal}
.proj summary:before{content:"\\25B8";color:#76868e;margin-right:8px;display:inline-block;transition:none}
.proj details[open]>summary:before{content:"\\25BE"}
.proj details .inner{padding:2px 14px 12px}
.proj .toolbar{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:0 0 18px}
.proj .unk{color:#8a5a14;font-weight:700}
.proj .att{display:flex;gap:10px;align-items:flex-start;padding:9px 0;border-bottom:1px solid #edf1f2;font-size:12px}
.proj .att:last-child{border-bottom:0}
.proj .crit{background:#fdeeee;border:1px solid #e9bcbc;color:#7d2f23;padding:12px 15px;border-radius:11px;font-size:12px;margin-bottom:17px}
@media(max-width:1150px){.proj .g4{grid-template-columns:repeat(2,1fr)}.proj .g2{grid-template-columns:1fr}}
@media(max-width:760px){.proj .g3{grid-template-columns:1fr}}
</style>"""
MS_PILL = {"COMPLETE": "ok", "IN_PROGRESS": "wait", "BLOCKED": "danger", "UPCOMING": "no", "NOT APPROVED": "no"}


def _when(ts) -> str:
    """A timestamp for people: UTC minute precision. A plain date stays a date; anything else is shown as recorded."""
    if not ts or ts == project.UNKNOWN:
        return project.UNKNOWN
    try:
        return datetime.fromisoformat(str(ts)).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if "T" in str(ts) else str(ts)
    except ValueError:
        return str(ts)


def _unk(v) -> str:
    return '<span class="unk">UNKNOWN</span>' if v in (None, "", project.UNKNOWN) else e(str(v))


def project_data(app: App) -> dict:
    """The dashboard's data: re-read from the records on every call (nothing cached)."""
    return project.status(project.REPO, now=app.clock(), ws=app.ws, svc=app.svc, research=lambda cid: research_snapshot(app, cid),
                          capabilities=CAPABILITIES, github_live=app.github_live)


def api_project(app: App) -> dict:
    return project_data(app)


def project_page(app: App, auto: int = 0, flash: str = "", err: str = "") -> str:
    d = project_data(app)
    t, ms, act = d["truth"], d["milestones"], d["active"]
    approved, head, pub = t.get("approved"), t.get("head"), t.get("published")
    sha7 = lambda x: e((x or "")[:7]) if x else '<span class="unk">UNKNOWN</span>'
    pf = d["preflight"] or {}
    health = (pill("source-of-truth checks: PASS", "ok") if pf and not pf["fail"] and pf["ok"] is not None else
              pill("source-of-truth checks: FAIL", "danger") if pf and pf["fail"] else pill("source-of-truth checks: UNKNOWN", "no"))
    refresh = (f'<a class="btn" href="/project">Refresh now</a>' + (f'<a class="btn ghost" href="/project">Stop auto-refresh</a>' if auto else '<a class="btn ghost" href="/project?auto=60">Auto-refresh every 60 s</a>'))
    banner = ""
    if not d["authority"]["ok"]:
        banner = f'<div class="crit"><b>AUTHORITY RECORDS DO NOT RESOLVE.</b> Approved state, active work and milestones are UNKNOWN until this is fixed (fail closed): {e(d["authority"]["error"])}</div>'

    # ---- headline numbers (counts only; no percentage anywhere)
    tt = ms["totals"] if ms else None
    card = lambda label, value, sub: f'<div class="stat"><div class="statlabel">{label}</div><div class="statvalue">{value}</div><div class="statsub">{sub}</div></div>'
    if tt:
        cards = (card("Milestones accepted", f'{tt["complete"]} of {tt["milestones"]}', f'{tt["awaiting_acceptance"]} awaiting your acceptance' + (f' · {tt["complete_but_evidence_unverified"]} approved but evidence unverified' if tt["complete_but_evidence_unverified"] else ""))
                 + card("In progress", str(tt["in_progress"]), "approved status")
                 + card("Blocked", str(tt["blocked"]), "reasons listed below")
                 + card("Upcoming", str(tt["upcoming"]), "not started"))
    else:
        cards = "".join(card(l, '<span class="unk">UNKNOWN</span>', "authority records unavailable") for l in ("Milestones accepted", "In progress", "Blocked", "Upcoming"))

    # ---- three different things
    live = t.get("github_live")
    live_txt = ("not checked in this session" if not live else
                f'live check {_when(live["checked_at"])}: ' + (f'<b class="mono">{sha7(live["sha"])}</b> · ' + ("matches HEAD" if t.get("live_vs_head") == "SAME" else "DIFFERS from HEAD") if live["ok"] and live["sha"] else
                                                                  f'UNKNOWN ({e(live.get("error") or "no answer")})'))
    ahead = t.get("ahead_of_approved") or []
    rel_head_approved = ("HEAD is the approved baseline" if t.get("head_is_approved") else
                         (f'HEAD is {len(ahead)} commit(s) ahead of the approved baseline: those commits are unapproved until you accept them' if t.get("available") and ahead is not None and approved else "UNKNOWN"))
    truth = f"""<section class="panel" id="truth"><div class="panel-head"><div><h2>Code, published copy and approved baseline are three different things</h2>
<p class="subtle">The newest commit is never assumed to be approved.</p></div>
<form method="post" action="/project/check-github"><button class="btn">Check GitHub now</button></form></div>
<div class="g3">
<div class="tbox"><div class="k">Git HEAD (this Mac)</div><div class="v">{sha7(head and head["sha"])}</div><div class="small">{e(head["subject"]) if head else "UNKNOWN"}<br>{_when(head["date"]) if head else ""} · branch {e(t.get("branch") or "UNKNOWN")} · {"UNKNOWN" if t.get("dirty") is None else str(t["dirty"]) + " uncommitted change(s)"}</div></div>
<div class="tbox"><div class="k">Published on GitHub</div><div class="v">{sha7(pub and pub["sha"])}</div><div class="small">{("last push or fetch " + _when(pub["as_of"]) + " (local tracking ref, not a live check)") if pub else "UNKNOWN: no published position recorded locally"}<br>{live_txt}</div></div>
<div class="tbox"><div class="k">Approved baseline (human)</div><div class="v">{sha7(approved and approved["commit"])}</div><div class="small">{("approved " + e(approved["approved_on"]) + " · register event #" + str(approved["register_seq"])) if approved else "UNKNOWN: the register holds no approved state"}</div></div></div>
<p class="small" style="margin-top:12px"><b>HEAD vs published:</b> {e(t.get("published_vs_head") or "UNKNOWN")} &nbsp;·&nbsp; <b>HEAD vs approved:</b> {e(rel_head_approved)} &nbsp;·&nbsp; remote {e(t.get("remote") or "UNKNOWN")}</p>
{('<details style="margin-top:10px"><summary>Commits after the approved baseline (' + str(len(ahead)) + ')</summary><div class="inner">' + "".join(f'<div class="small"><span class="mono">{e(c[0])}</span> {e(c[1])}</div>' for c in ahead) + '</div></details>') if ahead else ""}</section>"""

    # ---- active assignment
    if act:
        assign = f"""<section class="panel"><h2>Active assignment</h2><p style="margin:8px 0 4px"><b>{e(act["plan_heading"])}</b></p><p class="subtle">{e(act["summary"])}</p><div class="thin"></div>
<div class="rowlist"><div><strong>State</strong><span>{e(act["state"])}</span></div></div>
<div class="rowlist"><div><strong>Owner</strong><span>{_unk(act["owner"])}</span></div></div>
<div class="rowlist"><div><strong>Next action</strong><span>{_unk(act["next_action"])}</span></div></div>
<div class="rowlist"><div><strong>Dependencies</strong><span>{_unk(act["dependencies"])}</span></div></div>
<p class="small" style="margin-top:8px">Approved by the human {e(act["approved_on"])} · register event #{act["register_seq"]} · work id <span class="mono">{e(act["work_id"])}</span></p></section>"""
    else:
        assign = '<section class="panel"><h2>Active assignment</h2><p class="unk">UNKNOWN — the register holds no approved active-work record.</p></section>'

    # ---- upcoming
    rows = "".join(f'<tr><td class="mono nw">{e(u["date"])}</td><td>{("in " + str(u["days"]) + " d") if u["days"] > 0 else ("today" if u["days"] == 0 else str(-u["days"]) + " d ago")}</td><td>{e(u["what"])}<br><span class="small subtle">{e(u["kind"])} — {e(u["note"])}</span></td></tr>' for u in d["upcoming"])
    upcoming = f'<section class="panel"><h2>Upcoming dates</h2><div class="table-wrap"><table><tr><th>Date</th><th>When</th><th>What</th></tr>{rows or "<tr><td colspan=3><span class=unk>UNKNOWN</span> — no dated item is recorded</td></tr>"}</table></div><p class="small subtle" style="margin-top:8px">A revisit date is a trigger to reassess. It never promotes a candidate or authorizes an investment.</p></section>'

    # ---- needs attention (derived only from structured records)
    att = []
    if ms:
        for ph in ms["phases"]:
            for it in ph["items"]:
                if it["status"] == "BLOCKED":
                    att.append(("danger", "BLOCKED", f'{it["id"]} {it["title"]}', it["blocker"] or "no reason recorded"))
                if it["proposed"] and it["proposed"]["status"] == "COMPLETE":
                    att.append(("wait", "AWAITING ACCEPTANCE", f'{it["id"]} {it["title"]}', f'proposed COMPLETE (register event #{it["proposed"]["register_seq"]}); not counted until you approve it'))
                elif it["proposed"] and not it["approved"]:
                    att.append(("no", "NOT APPROVED", f'{it["id"]} {it["title"]}', f'a {it["proposed"]["status"]} status was proposed but nobody has approved it (register event #{it["proposed"]["register_seq"]})'))
                if it["status"] == "COMPLETE" and not it["evidence_ok"]:
                    att.append(("danger", "EVIDENCE UNVERIFIED", f'{it["id"]} {it["title"]}', "approved COMPLETE, but at least one evidence reference does not resolve here; not counted"))
                if it["unknown_dependencies"]:
                    att.append(("no", "UNKNOWN DEPENDENCY", f'{it["id"]}', "depends on " + ", ".join(it["unknown_dependencies"]) + ", which is not a recorded milestone"))
    for c in d["pipeline"]:
        if c["pending"]:
            att.append(("wait", "PENDING APPROVAL", f'{c["candidate_id"]} status', f'ledger change(s) {c["pending"]} are not approved in the register; capital comparison stays closed'))
        if c["revisit_due"]:
            att.append(("wait", "REVISIT DATE REACHED", f'{c["candidate_id"]}', "a trigger to reassess, not a promotion"))
    for f in pf.get("fail", []):
        att.append(("danger", "CHECK FAILED", "source-of-truth preflight", f))
    for w in pf.get("warn", []):
        att.append(("wait", "CHECK WARNING", "source-of-truth preflight", w))
    attention = ('<section class="panel"><h2>Needs attention</h2>' + ("".join(f'<div class="att">{pill(k, c)}<div><b>{e(w)}</b><br><span class="subtle">{e(x)}</span></div></div>' for c, k, w, x in att)
                 if att else '<p class="subtle">No blocker, proposal, pending approval or failed check is recorded.</p>') + '</section>')

    # ---- milestones by phase
    if ms and ms["phases"]:
        blocks = ""
        for ph in ms["phases"]:
            c = ph["counts"]
            op = " open" if (c["in_progress"] or c["blocked"] or c["awaiting_acceptance"]) else ""
            trs = ""
            for it in ph["items"]:
                n_ok = sum(1 for x in it["evidence"] if x["ok"] is True)
                ev = (pill(f'evidence {n_ok}/{len(it["evidence"])} resolves', "ok") if it["evidence"] and n_ok == len(it["evidence"]) else pill(f'evidence {n_ok}/{len(it["evidence"])} resolves', "wait") if it["evidence"] else pill("no evidence cited", "no"))
                ev_list = "".join(f'<div class="small mono">{"✓" if x["ok"] is True else "?" if x["ok"] is None else "✗"} {e(x["ref"])}{(" — " + e(x["why"])) if x["why"] else ""}</div>' for x in it["evidence"])
                extra = "".join(f'<div class="small subtle">{lbl}: {e(str(v))}</div>' for lbl, v in (("blocker", it["blocker"]), ("depends on", ", ".join(it["depends_on"]) if it["depends_on"] else None), ("target", it["target_date"]), ("note", it["notes"])) if v)
                prop = (f'<div class="small" style="color:#8a5a14">proposed: {e(it["proposed"]["status"].replace("_", " "))} — not approved</div>' if it["proposed"] else "")
                appr = (f'approved {e(it["approved_on"])} · #{it["register_seq"]}' if it["approved"] else '<span class="unk">NOT APPROVED</span>')
                trs += (f'<tr><td class="mono nw"><b>{e(it["id"])}</b></td><td>{e(it["title"])}{extra}{prop}</td><td>{pill(it["status"].replace("_", " "), MS_PILL.get(it["status"], "no"))}</td>'
                        f'<td><details style="border:0;margin:0"><summary style="padding:0;font-weight:400">{ev}</summary><div class="inner" style="padding:6px 0 0">{ev_list}</div></details></td><td class="small">{appr}</td></tr>')
            acc = str(c["complete"]) + " of " + str(c["total"]) + " accepted"
            blocks += (f'<details{op}><summary><span>{e(ph["phase"])}</span><span>{pill(acc, "ok" if c["complete"] == c["total"] else "no")}'
                       + (pill(f'{c["in_progress"]} in progress', "wait") if c["in_progress"] else "") + (pill(f'{c["blocked"]} blocked', "danger") if c["blocked"] else "")
                       + (pill(f'{c["awaiting_acceptance"]} awaiting acceptance', "wait") if c["awaiting_acceptance"] else "") + '</span></summary>'
                       f'<div class="inner"><div class="table-wrap"><table><tr><th>ID</th><th>Milestone</th><th>Status</th><th>Evidence</th><th>Approval</th></tr>{trs}</table></div></div></details>')
        milestones = f'<section class="panel"><div class="panel-head"><h2>Milestones by phase</h2><span class="subtle">counts only · COMPLETE needs your approval and evidence that resolves</span></div>{blocks}</section>'
    else:
        milestones = '<section class="panel"><h2>Milestones by phase</h2><p class="unk">UNKNOWN — no milestone is recorded in the register.</p></section>'

    # ---- capabilities, pipeline, loop status
    cap = d["capabilities"]
    cap_html = (" ".join(pill(f"{k}: {n}", "ok" if k == "PROVEN LIVE" else "wait" if k in ("BLOCKED", "FIXTURE-TESTED") else "no") for k, n in cap["counts"].items())
                + '<details style="margin-top:10px"><summary>All capabilities</summary><div class="inner">' + "".join(f'<div class="rowlist"><div><strong>{e(r["name"][:78])}</strong></div><span>{e(r["status"])}</span></div>' for r in cap["rows"]) + '</div></details>') if cap else '<span class="unk">UNKNOWN</span>'
    capab = f'<section class="panel"><div class="panel-head"><h2>Verified capabilities</h2><a class="btn ghost" href="/capabilities">Full matrix</a></div>{cap_html}<p class="small subtle" style="margin-top:8px">PROVEN LIVE means read-only market data and SEC retrieval only. FIXTURE-TESTED means never run on live data.</p></section>'
    prow = "".join(f'<tr><td><a href="/candidate/{urllib_q(c["candidate_id"])}"><b>{e(c["candidate_id"])}</b></a></td><td>{pill(c["state"].replace("_", " ") + (" until " + c["parked_until"] if c["parked_until"] else ""), "wait" if c["state"] == "PARKED" else "no")}</td>'
                   f'<td class="small">{e(c["assessment"])}</td><td class="small">{c["open_questions"]} open · {c["evidence"]} evidence · {c["stances"]} stance(s)</td><td class="small">{_when(c["research_snapshot"]) if c["research_snapshot"][:1].isdigit() else e(c["research_snapshot"])}</td></tr>' for c in d["pipeline"])
    pipe = f'<section class="panel"><div class="panel-head"><h2>Research pipeline</h2><a class="btn ghost" href="/cohort">Research cohort</a></div><div class="table-wrap"><table><tr><th>Candidate</th><th>Status</th><th>Assessment</th><th>Record</th><th>Research snapshot</th></tr>{prow or "<tr><td colspan=5><span class=unk>UNKNOWN</span></td></tr>"}</table></div><p class="small subtle" style="margin-top:8px">Status only. Analysis lives in the investment pages.</p></section>'
    s78, ol, pf_ = d["stage78"], d["outcomes"], d["portfolio"]
    port = (f'<div class="rowlist"><div><strong>Portfolio snapshot</strong><span>{e(pf_["snapshot_id"])} · valuation {e(pf_["as_of"])} · <b>{pf_["age_days"]} days old</b> · {pf_["holdings"]} holdings · approximate, not a live balance</span></div></div>' if pf_ else '<div class="rowlist"><div><strong>Portfolio snapshot</strong><span class="unk">UNKNOWN</span></div></div>')
    loop = (port + f'<div class="rowlist"><div><strong>Stage 7 runs</strong><span>{_unk(s78["runs"])}' + (f' ({e(", ".join(f"{k}: {v}" for k, v in s78["by_status"].items()))})' if s78.get("by_status") else "") + f' · workspace {e(app.mode)}</span></div></div>'
            f'<div class="rowlist"><div><strong>Stage 8 decisions recorded</strong><span>{_unk(s78["decisions"])} · decision ledger verified: {_unk(s78["ledger_verified"])}</span></div></div>'
            f'<div class="rowlist"><div><strong>Outcome learning</strong><span>{_unk(ol["observations"])} dated observation(s) · decisions to measure: {_unk(ol["decisions_to_measure"])} · matched SPY / Treasury comparison: not yet built</span></div></div>')
    loopp = f'<section class="panel"><h2>Portfolio freshness, Stage 7/8 and outcome learning</h2>{loop}</section>'

    # ---- recent change
    cm = "".join(f'<tr><td class="mono nw">{e(c["sha"])}</td><td class="small">{_when(c["date"])}</td><td>{e(c["subject"])}</td><td>{pill("approved baseline or earlier", "ok") if c["approved"] else pill("unapproved", "wait")}</td></tr>' for c in d["recent"]["commits"])
    dl = "".join(f'<tr><td class="mono small">{e(x["name"])}</td><td class="small">{e(x["date"])}</td><td class="small">{e(x["status_text"])}</td></tr>' for x in d["recent"]["decisions"])
    recent = (f'<section class="panel"><h2>Recent changes</h2><details open><summary>Latest commits</summary><div class="inner"><div class="table-wrap"><table><tr><th>Commit</th><th>Date</th><th>Subject</th><th>Baseline</th></tr>{cm or "<tr><td colspan=4><span class=unk>UNKNOWN</span> — no git history here</td></tr>"}</table></div></div></details>'
              f'<details><summary>Latest Decision Log entries (Status shown exactly as written)</summary><div class="inner"><div class="table-wrap"><table><tr><th>Entry</th><th>Date</th><th>Status as recorded</th></tr>{dl or "<tr><td colspan=3><span class=unk>UNKNOWN</span></td></tr>"}</table></div></div></details></section>')

    # ---- sources and timestamps
    srcs = "".join(f'<tr><td>{e(x["name"])}</td><td class="small">{_when(x["last_changed"])}</td><td class="small subtle">{e(x["detail"])}</td></tr>' for x in d["sources"])
    sources = (f'<section class="panel"><h2>Sources and when each last changed</h2><div class="table-wrap"><table><tr><th>Record</th><th>Last changed</th><th>Detail</th></tr>{srcs}</table></div>'
               f'<p class="small subtle" style="margin-top:8px">This page was rendered {_when(d["generated_at"])} and re-reads every record each time it is viewed. {d["working_tree_dirty"] if d["working_tree_dirty"] is not None else "UNKNOWN"} uncommitted change(s) in the working tree are included in what you see.</p></section>')

    body = (PROJECT_CSS + f"""<div class="view active proj"><p class="eyebrow">Project oversight</p><h1>Where the project stands</h1>
<p class="intro">Read live from the authority register, git and the project's own records. Nothing here is investment analysis or a recommendation; that lives in the Workspace pages.</p>
<div class="toolbar">{refresh}{health}<span class="subtle small">Rendered {_when(d["generated_at"])}{" · refreshing every 60 s" if auto else ""}</span></div>{banner}
<div class="g4">{cards}</div>{truth}{attention}<div class="g2">{assign}{upcoming}</div>{milestones}<div class="g2">{pipe}{capab}</div>{loopp}{recent}{sources}</div>""")
    head = f'<meta http-equiv="refresh" content="{auto}">' if auto else ""
    return page(app, "/project", "Project dashboard", body, flash=flash, err=err, section="project", head_extra=head)



def make_handler(app: App):
    class H(BaseHTTPRequestHandler):
        server_version = "AtlasUI/0.1"

        def log_message(self, *a):
            pass

        def _host_ok(self) -> bool:
            host = (self.headers.get("Host") or "").split(":")[0]
            origin = self.headers.get("Origin")
            if host not in ("127.0.0.1", "localhost"):
                return False
            return origin is None or urllib.parse.urlparse(origin).hostname in ("127.0.0.1", "localhost")

        def _send(self, code, body, ctype="text/html; charset=utf-8", headers=None):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def _json(self, obj, code=200):
            from stock_atlas.freeze import canonical_json_bytes
            self._send(code, json.dumps(json.loads(canonical_json_bytes(obj)), indent=2), "application/json; charset=utf-8")

        def do_GET(self):
            if not self._host_ok():
                return self._send(403, "forbidden", "text/plain")
            u = urllib.parse.urlparse(self.path)
            p, q = u.path, urllib.parse.parse_qs(u.query)
            try:
                if p == "/":
                    return self._send(200, overview(app))
                if p == "/project":
                    a = (q.get("auto") or [""])[0]
                    return self._send(200, project_page(app, auto=int(a) if a.isdigit() and 10 <= int(a) <= 600 else 0))
                if p == "/api/project":
                    return self._json(api_project(app))
                if p == "/intake":
                    return self._send(200, intake(app))
                if p == "/stage7":
                    mk = ""
                    if q.get("ticker"):
                        t = q["ticker"][0].strip().upper()
                        try:
                            ev = app.svc.bind_price(t, app.clock())
                            s = ev.snapshot
                            mk = (f"<b>BOUND</b> {e(s.ticker)} {s.price:g} {e(s.currency)} · provider {e(s.provider)} · session {s.price_session_date} · "
                                  f"freshness {e(s.freshness_status.value)} · attested by {e(ev.attestation.calendar_name)} (independent of provider)")
                        except Blocked as exc:
                            return self._send(200, stage7_page(app, err=f"BLOCKED — {exc}"))
                    return self._send(200, stage7_page(app, market=mk))
                if p == "/cohort":
                    return self._send(200, cohort_page(app))
                if p == "/api/cohort":
                    return self._json(api_cohort(app))
                if p == "/desk":
                    return self._send(200, desk_page(app))
                if p == "/history":
                    return self._send(200, history_page(app))
                if p == "/capabilities":
                    return self._send(200, capabilities_page(app))
                if p.startswith("/candidate/"):
                    h = candidate_page(app, urllib.parse.unquote(p[11:]))
                    return self._send(200, h) if h else self._send(404, "not found", "text/plain")
                if p.startswith("/run/"):
                    h = run_page(app, urllib.parse.unquote(p[5:]))
                    return self._send(200, h) if h else self._send(404, "not found", "text/plain")
                if p.startswith("/artifact/"):  # read-only; allow-listed names inside retained dirs
                    parts = p.split("/")
                    if len(parts) == 4 and parts[3].endswith(".json"):
                        rid, name = urllib.parse.unquote(parts[2]), parts[3]
                        entry = next((x for x in read_index(app.ws.index_path) if x["run_id"] == rid), None)
                        if entry and not app.svc.verify_entry(entry)[0]:
                            return self._send(409, "NOT VERIFIED: retained artifact does not match its recorded SHA-256", "text/plain")
                        if entry:
                            ref = entry["stage7"] if name == "stage7.json" else entry["inputs"].get(name[:-5])
                            path = Path(app.ws.ref(ref).artifact_path) if ref else None
                            if path and path.is_file():
                                return self._send(200, path.read_text(), "application/json; charset=utf-8")
                    return self._send(404, "not found", "text/plain")
                if p == "/api/state":
                    return self._json(api_state(app))
                if p == "/api/runs":
                    return self._json(app.svc.list_runs())
                if p.startswith("/api/runs/"):
                    try:
                        run, _v, entry = app.svc.load_run(urllib.parse.unquote(p[10:]))
                        return self._json({"entry": entry, "result": run.result, "rendered_text": run.rendered_text})
                    except Blocked as exc:
                        return self._json({"verified": False, "error": str(exc)}, 404)
                if p == "/api/ledger":
                    return self._json({"verified": app.ws.facade.verify_ledger(), "rows": app.svc.ledger_rows()})
            except canonical.CanonicalError as exc:
                return self._send(500, page(app, "/", "Error", f'<div class="err"><b>Canonical record failed validation (fail-closed):</b> {e(str(exc))}</div>'))
            return self._send(404, "not found", "text/plain")

        def do_POST(self):
            if not self._host_ok():
                return self._send(403, "forbidden", "text/plain")
            n = int(self.headers.get("Content-Length") or 0)
            if n > 200_000:
                return self._send(413, "too large", "text/plain")
            f = {k: v[0] for k, v in urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8"), keep_blank_values=True).items()}
            p = urllib.parse.urlparse(self.path).path
            try:
                if p == "/project/check-github":
                    app.github_live = project.check_github(project.REPO)        # explicit, read-only (git ls-remote); the result lives in memory only
                    return self._redirect("/project#truth")
                if p == "/intake":
                    ev = ledger.surface(app.ws.candidate_ledger, name=f.get("name", ""), ticker=f.get("ticker", ""),
                                        source=f.get("source", ""), source_detail=f.get("source_detail", ""),
                                        why_surfaced=f.get("why_surfaced", ""), investment_question=f.get("investment_question", ""))
                    ledger.freeze_stance(app.ws.candidate_ledger, candidate_id=ev["candidate_id"], stance_text=f.get("stance_text", ""),
                                         intended_action=f.get("intended_action", ""), amount=f.get("amount", ""),
                                         concern=f.get("concern", ""), without_atlas=f.get("without_atlas", ""))
                    return self._redirect("/candidate/" + urllib_q(ev["candidate_id"]))
                if p == "/stage7/run":
                    entry = app.svc.run({**f, "candidate_id": f.get("cand") or f.get("candidate_id", "")}, app.clock())
                    return self._redirect("/run/" + urllib_q(entry["run_id"]))
                if p == "/stage8":
                    res = app.svc.record_stage8(f.get("run_id", ""), f, app.clock())
                    return self._redirect("/run/" + urllib_q(f.get("run_id", "")))
                if p == "/revisit":
                    ledger.add_note(app.ws.candidate_ledger, candidate_id=f.get("candidate_id", ""),
                                    text=f"REVISIT of {f.get('record_id', '')}: {f.get('note', '')}")
                    return self._redirect("/history")
            except Rejected as exc:
                rid = f.get("run_id", "")
                html = run_page(app, rid, err=f"REJECTED — {exc}. Ledger rows before/after: {exc.rows_before}/{exc.rows_after} (zero rows written).")
                return self._send(400, html or "rejected", "text/html; charset=utf-8" if html else "text/plain")
            except (Blocked, ledger.LedgerError, ValueError, KeyError) as exc:
                if p == "/intake":
                    return self._send(400, intake(app, err=str(exc)))
                if p == "/stage7/run":
                    return self._send(400, stage7_page(app, err=f"BLOCKED — {exc}"))
                if p == "/revisit":
                    return self._send(400, history_page(app, err=str(exc)))
                return self._send(400, str(exc), "text/plain")
            return self._send(404, "not found", "text/plain")

        def _redirect(self, to):
            self._send(303, "", "text/plain", {"Location": to})

    return H


def serve(app: App, port: int = 8770) -> None:
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))  # loopback only
    print(f"Stock Atlas dashboard [{app.mode}] on http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
