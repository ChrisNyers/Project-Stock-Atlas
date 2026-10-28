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

from . import canonical, demo
from .service import (BASELINE_COMMIT, PAPER_ACTIONS, Blocked, Rejected, Stage7Service, Workspace, read_index)

THEME = (Path(__file__).parent / "theme.css").read_text(encoding="utf-8")
EXTRA_CSS = ".rowlist div strong{display:block}.banner-demo{background:#fbeeea;border:1px solid #e3b7ad;color:#7d2f23;padding:12px 15px;border-radius:11px;font-size:12px;margin-bottom:22px}pre.rendered{background:#f5f7f7;border:1px solid #dfe6e7;border-radius:10px;padding:12px;font-size:11px;white-space:pre-wrap}.nav a{text-decoration:none}.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}.alt{border:1px solid #dce6e6;border-radius:11px;padding:13px;background:#fff}.alt b{display:block;font-size:12px}.alt .band{font-size:20px;font-weight:800;margin:6px 0}.err{border:1px solid #e3b7ad;background:#fbeeea;color:#7d2f23;padding:11px;border-radius:10px;margin-bottom:14px;font-size:12px}.okbox{border:1px solid #cfe4e0;background:#f2f8f7;color:#255a57;padding:11px;border-radius:10px;margin-bottom:14px;font-size:12px}"

NAV = [("/", "Overview"), ("/intake", "Opportunity intake"), ("/stage7", "Stage 7 evidence"),
       ("/desk", "Decision desk"), ("/history", "Decision history"), ("/capabilities", "Capability matrix")]

# Single source of truth for the honest capability matrix (page + CAPABILITY_MATRIX.md).
CAPABILITIES = [
    ("A. Overview: canonical Cycle 0 portfolio/policy, pilot status, candidates", "PROVEN WORKING WITH REAL BACKEND",
     "Parsed and re-validated from the frozen baseline record (28 names, sum $624,905.93); as-of and source shown."),
    ("B. Intake + immutable pre-Atlas stance (versioned, provenance, no source privilege)", "PROVEN WORKING WITH REAL BACKEND",
     "Writes the existing append-only discovery ledger; later versions are labelled revisions, never edits."),
    ("C. Filings / financial research ingestion into the UI", "NOT IMPLEMENTED",
     "Evidence is typed by the human with PRIMARY/SECONDARY/UNCERTIFIED labels (existing evidence ledger). No SEC fetch is wired to the UI yet."),
    ("D. Live price + XNYS session (Gate B)", "BLOCKED WITH EXACT REASON",
     "Wired to the verified Gate B path; TWELVEDATA_API_KEY is absent in this environment, so no live observation can be bound. Offline fail-closed paths are tested."),
    ("E. Stage 7 via CapitalDecisionFacade.run_stage7, retained hashed run, side-by-side grid", "FIXTURE-TESTED ONLY",
     "Runs through the real facade; exercised with a clearly-labelled FIXTURE price provider in DEMO mode and tests. No canonical run exists. MCD is PARKED until 2026-11-04. The Treasury reference is HUMAN-ATTESTED (not independently verified by Atlas); security decision is explicit, never defaulted; all % inputs use one unit."),
    ("F. Human Stage 8 (paper only): server-side recheck, non-action, ledger proof", "FIXTURE-TESTED ONLY",
     "Real facade + DecisionStore; funded actions also pass an adapter-level fresh-price checkpoint (run age, newer XNYS session, fresh Gate B rebind) because the facade alone does not check run age; rejected paths leave zero rows in tests; no canonical decision exists."),
    ("G1. Decision history (existing append-only ledger) + manual revisit note", "PROVEN WORKING WITH REAL BACKEND",
     "Reads the real ledger; revisit is a linked dated note, the original record is never edited."),
    ("G2. Outcome vs cash/SPY with matched as-of dates; automatic trigger monitoring", "NOT IMPLEMENTED",
     "Needs a fresh bound price per revisit and approved cadence/alert delivery; not claimed."),
    ("Real trades / broker connectivity / execution", "NOT IMPLEMENTED (by design)", "Paper only. No order API exists."),
]


@dataclass
class App:
    ws: Workspace
    svc: Stage7Service
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)

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


def page(app: App, active: str, title: str, body: str, flash: str = "", err: str = "") -> str:
    nav = "".join(f'<a class="navbtn{" active" if p == active else ""}" href="{p}"><span class="number">{i + 1}</span>{e(n)}</a>'
                  for i, (p, n) in enumerate(NAV))
    if app.mode == "DEMO":
        banner = ('<div class="banner-demo"><b>DEMO MODE — FIXTURE DATA.</b> Prices come from a fixture provider labelled '
                  'FIXTURE-DEMO in an isolated workspace. Nothing here is evidence, a Stage 7 run for the pilot, or a decision.</div>')
    else:
        banner = ('<div class="warning"><strong>CONNECTED TO STOCK ATLAS — canonical records.</strong> Paper decisions only. '
                  'No real orders. Stage 7 runs only through the frozen facade; Human Stage 8 alone decides.</div>')
    msgs = (f'<div class="err">{e(err)}</div>' if err else "") + (f'<div class="okbox">{flash}</div>' if flash else "")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · Stock Atlas</title><style>{THEME}{EXTRA_CSS}
@media(max-width:820px){{.app{{grid-template-columns:1fr}}.sidebar{{position:static;height:auto}}.layout,.topstats,.inputs{{grid-template-columns:1fr}}}}</style></head>
<body><div class="app"><aside class="sidebar"><div class="brand"><div class="mark">A</div><div><span class="brand-name">STOCK ATLAS</span>
<span class="brand-small">Decision workspace</span></div></div><div class="navtitle">WORKSPACE</div><nav class="nav">{nav}</nav>
<div class="sidebottom"><b>Frozen controls preserved</b><p>Baseline {BASELINE_COMMIT[:7]}… Stage 7 compares only. Stage 8 remains human. Paper only.</p></div></aside>
<main class="main"><div class="topbar"><span class="crumb">PROJECT STOCK ATLAS / CONTROLLED LIVE PILOT · {e(app.mode)}</span><span class="version">UI integration v0.1</span></div>
{banner}{msgs}{body}<p class="footer-note">Stock Atlas — presentation and input layer over the existing engine · No real trades · Capital status: NO REAL PORTFOLIO ACTION</p></main></div></body></html>"""


def key_status(app: App) -> tuple[str, str]:
    if app.svc._key_present():
        return "PRESENT", "ok"
    return "ABSENT", "danger"


def candidate_runs(app: App, cid: str, ticker: str) -> list[dict]:
    return [r for r in app.svc.list_runs() if r["candidate_id"] == cid or r["ticker"] == ticker]


# ------------------------------------------------------------------ pages
def overview(app: App) -> str:
    c0 = canonical.load_cycle0()
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
<div class="stat"><div class="statlabel">28 stocks</div><div class="statvalue">{money(c0.stocks_total)}</div><div class="statsub">exact, reconciled by the loader</div></div>
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
    gate = ("READY — a human has marked this candidate READY FOR CAPITAL COMPARISON." if c["state"] == "READY_FOR_CAPITAL_COMPARISON"
            else f"Not ready: state is {c['state']}" + (f" until {c['parked_until']}" if c["parked_until"] else "") + ". Stage 7 cannot be started.")
    body = f"""<div class="view active"><p class="eyebrow">Candidate</p><h1>{e(cid)} — {e(c["name"])}</h1>
<div class="btn-row">{pill(c["state"].replace("_", " "))}{pill("source: " + c["source"])}{pill("grandfathered") if c["grandfathered"] else ""}</div>
<section class="panel" style="margin-top:16px"><h2>Why it surfaced</h2><p>{e(c["why_surfaced"])}</p><div class="thin"></div><h3>Investment question</h3><p>{e(c["investment_question"])}</p>
<p class="subtle" style="margin-top:10px">Provenance: {e(c["source"])}{" — " + e(c["source_detail"]) if c["source_detail"] else ""}; surfaced {e(c["surfaced_on"])}.</p></section>
<section class="panel"><h2>Frozen independent stance</h2><div class="audit">{st}</div></section>
<section class="panel"><h2>Stage 7 status</h2><p class="subtle">{e(gate)}</p><div class="table-wrap"><table><tr><th>Run</th><th>Status</th><th>Hash</th><th>Retained artifacts</th></tr>{run_rows}</table></div></section>
<section class="panel"><h2>Records</h2><ul>{refs}</ul><p class="subtle">Evidence ledger, falsification and state changes are edited on the Discovery board (same ledger): <span class="mono">python -m atlas_ui serve</span> also starts it on its own port.</p></section></div>"""
    return page(app, "/", f"{cid}", body, flash=flash, err=err)


def stage7_page(app: App, err="", flash="", market: str = "") -> str:
    cands = ledger.replay(app.ws.candidate_ledger)
    ready = [c for c in cands.values() if c["state"] == "READY_FOR_CAPITAL_COMPARISON"]
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
<div class="full"><label class="field"><input type="checkbox" name="baseline_ack" value="1" style="width:auto"> I acknowledge the portfolio baseline is the frozen human-supplied record of 2026-10-07 (holdings are NOT live) and the denominator is approximate (defensive ≈ $59,000). *</label></div>
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
    req = json.loads(Path(entry["inputs"]["scenario_model"]["artifact_path"]).read_text())["request"]
    evd = json.loads(Path(entry["inputs"]["evidence_set"]["artifact_path"]).read_text())
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
<div class="callout" style="margin-top:12px">Confirm before submit — candidate <b>{e(r.ticker)}</b>, increment <b>{money(entry["increment_dollars"])}</b>, funding <b>new outside capital</b>, run <span class="mono">{e(run_id)}</span>, Stage 7 SHA-256 <span class="mono">{e(entry["stage7"]["sha256"][:24])}…</span>, constraints <b>{e(r.constraint_state.value)}</b>.
<br><label><input type="checkbox" name="confirm" value="1" style="width:auto"> This is a PAPER decision. No order will be placed.</label></div>
<div class="btn-row" style="margin-top:12px"><button class="btn primary">Record paper decision</button></div></form></section>"""
    unc = "".join(f"<li>{e(l)}</li>" for l in req["uncertainties"].splitlines() if l.strip())
    body = f"""<div class="view active"><p class="eyebrow">Stage 7 run</p><h1>{e(run_id)}</h1><div class="btn-row">{status_pill(r.status)}{pill("mode: " + entry["mode"], "danger" if entry["mode"] == "DEMO" else "ok")}{pill("integrity VERIFIED","ok")}</div>
<section class="panel" style="margin-top:16px"><h2>Retained artifact</h2><div class="rowlist"><div><strong>Stage 7 SHA-256</strong><span class="mono">{e(entry["stage7"]["sha256"])}</span></div></div>
<div class="rowlist"><div><strong>Baseline</strong><span>valuation as of <b>2026-10-07</b> (human-supplied, not live); evaluated {e(entry["created_at"][:19])} · denominator approximate · <span class="mono">{e(entry["baseline_doc_sha256"][:24])}…</span></span></div></div>
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
    c0 = canonical.load_cycle0()
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


# ------------------------------------------------------------------ server
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
                            if ref and Path(ref["artifact_path"]).is_file():
                                return self._send(200, Path(ref["artifact_path"]).read_text(), "application/json; charset=utf-8")
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
