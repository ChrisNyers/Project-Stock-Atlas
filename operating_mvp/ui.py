"""UI v0.1 — read-mostly board over the candidate ledger (stdlib only).

Shows state; records intake / state changes / notes through the ledger and
nothing else. No ranking: sections follow the state vocabulary and items are
listed oldest-in-state first. Source is shown, never used to order or filter.
"""
from __future__ import annotations

import os
import urllib.parse
from datetime import date
from html import escape as e
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import ledger

REPO = Path(__file__).resolve().parent.parent
DOC_DIR = (REPO / "docs" / "controlled_live_pilot").resolve()

SECTION_TITLES = {
    "SURFACED": "Surfaced — awaiting triage",
    "QUICK_TEST": "Quick test",
    "UNDERWRITING": "Underwriting",
    "READY_FOR_CAPITAL_COMPARISON": "Ready for capital comparison (human decides what happens next)",
    "PARKED": "Parked — waiting on evidence",
    "REJECTED": "Rejected",
}
SECTION_ORDER = ["SURFACED", "QUICK_TEST", "UNDERWRITING",
                 "READY_FOR_CAPITAL_COMPARISON", "PARKED", "REJECTED"]

CSS = """
:root{--bg:#fafaf8;--fg:#1c1c1a;--mut:#6b6b66;--card:#fff;--line:#deded8;--acc:#1f5f8b;--warn:#a15c00;--bad:#9b2c2c}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#17171a;--fg:#e8e8e4;--mut:#9a9a94;--card:#202024;--line:#33333a;--acc:#7db4dc;--warn:#e0a85a;--bad:#e08a8a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}
main{max-width:980px;margin:0 auto;padding:16px}h1{font-size:22px;margin:8px 0 4px}h2{font-size:17px;margin:28px 0 8px}
h3{font-size:15px;margin:0}a{color:var(--acc)}.mut{color:var(--mut)}.small{font-size:13px}
.banner{border:1px solid var(--line);background:var(--card);border-radius:8px;padding:10px 12px;margin:10px 0;font-size:13px}
.banner b.unc{color:var(--warn)}.card{border:1px solid var(--line);background:var(--card);border-radius:8px;padding:12px;margin:8px 0}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:baseline}.tag{font-size:12px;border:1px solid var(--line);border-radius:10px;padding:0 8px;color:var(--mut)}
.tag.due{color:var(--bad);border-color:var(--bad)}.tag.soon{color:var(--warn);border-color:var(--warn)}
nav ul{margin:6px 0;padding-left:18px}table{border-collapse:collapse;width:100%}td:first-child{white-space:nowrap}td,th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;font-size:13px;vertical-align:top}
form label{display:block;font-size:13px;margin:8px 0 2px}input,select,textarea{width:100%;padding:6px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg);font:inherit}
button{margin-top:10px;padding:6px 14px;border-radius:6px;border:1px solid var(--acc);background:transparent;color:var(--acc);font:inherit;cursor:pointer}
.err{border:1px solid var(--bad);color:var(--bad);padding:8px;border-radius:6px;margin:8px 0}details summary{cursor:pointer}
"""


def price_certification(env=None) -> tuple[str, str]:
    env = os.environ if env is None else env
    if not (env.get("TWELVEDATA_API_KEY") or "").strip():
        return ("UNCERTIFIED", "TWELVEDATA_API_KEY absent — Stage 7 live price binding is BLOCKED; "
                "any price shown elsewhere is research context only.")
    return ("UNCERTIFIED", "Key present, but this UI does not certify prices. Certification "
            "belongs to the Gate B path (ELIGIBLE branch still unproven on live data).")


def _days_to(d: str, today: date) -> int | None:
    return (date.fromisoformat(d) - today).days if d else None


def _due_tag(c: dict, today: date) -> str:
    n = _days_to(c.get("parked_until", ""), today)
    if n is None:
        return ""
    if n <= 0:
        return '<span class="tag due">REVISIT DUE</span>'
    if n <= 30:
        return f'<span class="tag soon">revisit in {n}d</span>'
    return f'<span class="tag">revisit in {n}d</span>'


def _ref(r: str, linkable: bool) -> str:
    if linkable and r.startswith("docs/controlled_live_pilot/") and r.endswith(".md"):
        return f'<a href="/doc/{e(urllib.parse.quote(Path(r).name))}">{e(r)}</a>'
    return e(r)


def _card(c: dict, today: date, linkable: bool) -> str:
    href = f"/c/{urllib.parse.quote(c['candidate_id'])}" if linkable else f"#c-{e(c['candidate_id'])}"
    parked = ""
    if c["state"] == "PARKED":
        ver = "officially verified" if c["parked_until_verified"] else "date NOT officially verified"
        until = f" until <b>{e(c['parked_until'])}</b> ({ver})" if c["parked_until"] else " (no date set)"
        parked = f'<div class="small">Waiting on{until}: {e(c["waiting_on"])}</div>'
    return (f'<div class="card" id="c-{e(c["candidate_id"])}"><div class="row">'
            f'<h3><a href="{href}">{e(c["candidate_id"])}</a> — {e(c["name"])}</h3>'
            f'<span class="tag">source: {e(c["source"])}</span>{_due_tag(c, today)}'
            f'<span class="tag">in {e(c["state"])} since {e(c["state_since"])}</span></div>'
            f'<div class="small"><b>Why it surfaced:</b> {e(c["why_surfaced"])}</div>'
            f'<div class="small"><b>Question:</b> {e(c["investment_question"])}</div>'
            f'{parked}'
            f'{"<div class=small><b>Last reason:</b> " + e(c["reason"]) + "</div>" if c["reason"] else ""}</div>')


def _intake_form() -> str:
    opts = "".join(f'<option>{s}</option>' for s in ledger.SOURCES)
    return f"""<details><summary><b>Surface a new idea</b></summary>
<form method="post" action="/surface"><label>Name *</label><input name="name" required>
<label>Ticker (optional)</label><input name="ticker">
<label>Source *</label><select name="source">{opts}</select>
<label>Source detail (required if OTHER; who/where/link)</label><input name="source_detail">
<label>Why did it surface? *</label><textarea name="why_surfaced" rows="2" required></textarea>
<label>Investment question *</label><textarea name="investment_question" rows="2" required></textarea>
<button>Record as SURFACED</button></form></details>"""


def render_board(path: Path = ledger.DEFAULT_LEDGER, *, today: date | None = None,
                 interactive: bool = True, error: str = "", env=None) -> str:
    today = today or date.today()
    cands = ledger.replay(path)
    by_state = {s: [] for s in SECTION_ORDER}
    for c in cands.values():
        by_state[c["state"]].append(c)
    for s in by_state:  # oldest in state first — not a ranking
        by_state[s].sort(key=lambda c: (c["state_since"], c["candidate_id"]))
    cert, cert_msg = price_certification(env)
    parked = [c for c in by_state["PARKED"]]
    dated = sorted((c for c in parked if c["parked_until"]), key=lambda c: c["parked_until"])
    alerts = "".join(
        f'<tr><td>{e(c["parked_until"])}</td><td><a href="{"/c/" + urllib.parse.quote(c["candidate_id"]) if interactive else "#c-" + e(c["candidate_id"])}">{e(c["candidate_id"])}</a></td>'
        f'<td>{_due_tag(c, today)}</td><td>{"official" if c["parked_until_verified"] else "unverified"}</td>'
        f'<td>{e(c["waiting_on"])}</td></tr>' for c in dated) or '<tr><td colspan=5 class="mut">No dated catalysts.</td></tr>'
    due_now = [c for c in dated if _days_to(c["parked_until"], today) <= 0]
    attention = (by_state["SURFACED"] + by_state["QUICK_TEST"] + by_state["UNDERWRITING"]
                 + by_state["READY_FOR_CAPITAL_COMPARISON"] + due_now)
    counts = " · ".join(f"{s.replace('_', ' ').title()} {len(by_state[s])}" for s in SECTION_ORDER)
    sections = []
    for s in SECTION_ORDER:
        body = "".join(_card(c, today, interactive) for c in by_state[s]) or '<p class="mut small">None.</p>'
        sections.append(f'<h2 id="{s.lower()}">{e(SECTION_TITLES[s])} ({len(by_state[s])})</h2>{body}')
    err = f'<div class="err">{e(error)}</div>' if error else ""
    attn_html = "".join(_card(c, today, interactive) for c in attention) or '<p class="mut small">Nothing needs attention now.</p>'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Atlas Operating Board</title>
<style>{CSS}</style></head><body><main>
<h1>Atlas Operating Board <span class="mut small">v0.1 · {e(today.isoformat())}</span></h1>
<div class="banner"><b>Workflow support only.</b> Human Stage 8 is the sole capital authority; nothing here executes,
sizes or recommends. <b>NO REAL PORTFOLIO ACTION.</b> Candidates are listed oldest-in-state first — not ranked.
Source is provenance only.<br>Price evidence: <b class="unc">{e(cert)}</b> — {e(cert_msg)}</div>
{err}
<nav class="small"><b>Jump to:</b><ul>
<li>What deserves attention now? → <a href="#attention">Attention now</a></li>
<li>Why did they surface? → shown on every card</li>
<li>What has been rejected? → <a href="#rejected">Rejected</a></li>
<li>What is parked and waiting on evidence? → <a href="#parked">Parked</a> · <a href="#catalysts">Dated catalysts</a></li>
<li>What deserves deeper underwriting? → <a href="#quick_test">Quick test</a> · <a href="#underwriting">Underwriting</a></li></ul>
<span class="mut">{e(counts)}</span></nav>
{_intake_form() if interactive else ''}
<h2 id="attention">Attention now ({len(attention)})</h2>
<p class="small mut">Open work in SURFACED, QUICK TEST, UNDERWRITING or READY FOR CAPITAL COMPARISON, plus parked items whose revisit date has arrived.</p>
{attn_html}
<h2 id="catalysts">Dated catalysts</h2><table><tr><th>Date</th><th>Candidate</th><th>Status</th><th>Date source</th><th>Waiting on</th></tr>{alerts}</table>
{''.join(sections)}
<p class="small mut">Ledger: append-only, hash-chained ({len(ledger.read_events(path))} events). Historical cycle records keep their original disposition wording.</p>
</main></body></html>"""


TAG_LABEL = {"FACT": "FACT", "MANAGEMENT_CLAIM": "MANAGEMENT CLAIM", "CONTEXT": "CONTEXT",
             "INFERENCE": "INFERENCE", "VARIANT": "VARIANT", "CAPITAL_IMPLICATION": "CAPITAL IMPLICATION"}


def _evid_row(it: dict, strongest: dict) -> str:
    marks = "".join(f' <span class="tag">★ strongest {d}</span>' for d, q in strongest.items()
                    if q == it["seq"] and it["status"] == "ACTIVE")
    cls = ' style="text-decoration:line-through;opacity:.6"' if it["status"] == "RETRACTED" else ""
    ref = e(it["source_ref"]) if it["source_ref"] else '<i class="mut">no reference</i>'
    ka = e(it["known_at"]) if it["known_at"] else "n/a"
    back = " · backfilled" if it["backfilled"] else ""
    ret = f' — <b>RETRACTED:</b> {e(it["note"])}' if it["status"] == "RETRACTED" else ""
    return (f'<tr><td{cls}>#{it["seq"]}</td><td{cls}><span class="tag">{e(it["grade"])}</span> '
            f'<span class="tag">{e(it["direction"])}</span>{marks}</td>'
            f'<td{cls}>{e(it["text"])}</td><td class="small">{ref}<br>known {ka}{back}{ret}</td></tr>')


def _glance(c: dict, today: date) -> str:
    live_f = [f for f in c["falsifications"] if f["status"] == "ACTIVE"]
    if live_f:
        f = live_f[-1]
        qt = f'<b>{e(f["result"])}</b> ({e(f["date"])}) — {e(f["test"])}'
    elif c["grandfathered"]:
        qt = "No QUICK_TEST recorded — grandfathered historical candidate (went SURFACED → UNDERWRITING; history not rewritten)."
    else:
        qt = "Not yet run. QUICK_TEST is mandatory before UNDERWRITING."

    def strongest(d):
        q = c["strongest"].get(d)
        it = next((i for i in c["evidence"] if i["seq"] == q and i["status"] == "ACTIVE"), None)
        return (f'#{it["seq"]} <span class="tag">{e(it["grade"])}</span> {e(it["text"])}' if it
                else '<span class="mut">not designated (human designates; never computed)</span>')
    open_q = [u for u in c["unresolved"] if u["status"] == "OPEN"]
    uq = e(open_q[0]["question"]) + (f' <span class="mut">(+{len(open_q) - 1} more)</span>' if len(open_q) > 1 else "") \
        if open_q else (f'{e(c["revisit_questions"][0])} <span class="mut">(parked revisit question)</span>'
                        if c["revisit_questions"] else '<span class="mut">none recorded</span>')
    cat = '<span class="mut">n/a — not parked</span>'
    if c["state"] == "PARKED":
        ver = "officially verified" if c["parked_until_verified"] else "NOT officially verified"
        cat = (f'<b>{e(c["parked_until"] or "no date")}</b> ({ver}) {_due_tag(c, today)}<br>Waiting on: {e(c["waiting_on"])}')
    rows = [("Current state", f'<b>{e(c["state"])}</b> since {e(c["state_since"])}'),
            ("Why it surfaced", e(c["why_surfaced"])), ("Survived QUICK_TEST?", qt),
            ("Strongest evidence FOR", strongest("FOR")), ("Strongest evidence AGAINST", strongest("AGAINST")),
            ("Unresolved question", uq), ("Next dated catalyst", cat)]
    return '<div class="card"><table>' + "".join(f"<tr><th style='width:34%'>{k}</th><td>{v}</td></tr>" for k, v in rows) + "</table></div>"


def _placeholders(c: dict) -> str:
    box = lambda t, d: f'<div class="card"><b>{t}</b><div class="small mut">{d}</div></div>'
    return ('<h2>Capital comparison — placeholders only</h2>'
            '<p class="small mut">Nothing is computed or fetched here. Stage 7 (human-run, separate) does the comparison; '
            'this page never invokes it or the capital facade.</p>'
            + box("SPY", "Not populated. Advantage vs SPY must be demonstrated by evidence before any comparison.")
            + box("Treasury / Cash", "Not populated. Must be preserved as an alternative at Stage 7.")
            + box("Do Nothing", "Not populated. Must be preserved as an alternative at Stage 7.")
            + box("Relevant existing holdings", "Not assigned. Common drivers are human-assigned at Stage 7 "
                  "(see frozen Cycle 0 baseline and any driver notes in the cycle record)."))


def _forms(c: dict) -> str:
    cid = e(c["candidate_id"])
    hid = f'<input type="hidden" name="candidate_id" value="{cid}">'
    allowed = sorted(ledger.TRANSITIONS[c["state"]])
    sopts = "".join(f"<option>{s}</option>" for s in allowed)
    mk = lambda opts: "".join(f"<option>{o}</option>" for o in opts)
    grade = f'<label>Grade *</label><select name="grade">{mk(ledger.GRADES)}</select>'
    refdate = ('<label>Source / reference</label><input name="source_ref">'
               '<label>Known at (YYYY-MM-DD, optional)</label><input name="known_at">')
    active_ev = [i for i in c["evidence"] if i["status"] == "ACTIVE"]
    targets = "".join(f'<option value="{i["seq"]}">#{i["seq"]} {e(i["direction"])} {e(i["text"][:60])}</option>' for i in active_ev)
    open_items = ([(u["seq"], "Q: " + u["question"]) for u in c["unresolved"] if u["status"] == "OPEN"]
                  + [(i["seq"], "E: " + i["text"]) for i in active_ev]
                  + [(f["seq"], "T: " + f["test"]) for f in c["falsifications"] if f["status"] == "ACTIVE"])
    ropts = "".join(f'<option value="{q}">#{q} {e(t[:60])}</option>' for q, t in open_items)
    F = lambda title, action, body, btn: (f'<details><summary>{title}</summary><form method="post" action="{action}">'
                                          f'{hid}{body}<button>{btn}</button></form></details>')
    out = ['<h2>Record</h2>']
    if allowed:
        out.append(F("Change state", "/state",
            f'<label>To state</label><select name="to_state">{sopts}</select><label>Reason *</label><textarea name="reason" rows="2" required></textarea>'
            '<label>If PARKED — waiting on (specific evidence) *</label><input name="waiting_on">'
            '<label>If PARKED — revisit date (YYYY-MM-DD, optional)</label><input name="parked_until">'
            '<label><input type="checkbox" name="parked_until_verified" value="1" style="width:auto"> date officially verified (company IR / filing)</label>'
            '<label>If PARKED — revisit questions (one per line)</label><textarea name="revisit_questions" rows="3"></textarea>', "Record state change"))
    out.append(F("Record quick-test / falsification result", "/falsify",
        f'<label>Cheapest test that could kill the idea *</label><textarea name="test" rows="2" required></textarea>'
        f'<label>Result *</label><select name="result">{mk(ledger.FALSIFICATION_RESULTS)}</select>{grade}{refdate}', "Record result"))
    out.append(F("Add evidence", "/evidence",
        f'<label>Tag *</label><select name="tag">{mk(ledger.EVIDENCE_TAGS)}</select><label>Direction *</label><select name="direction">{mk(ledger.DIRECTIONS)}</select>'
        f'{grade}<label>Text *</label><textarea name="text" rows="3" required></textarea>{refdate}', "Record evidence"))
    out.append(F("Add unresolved question", "/unresolved", '<textarea name="question" rows="2" required></textarea>', "Record question"))
    if active_ev:
        out.append(F("Designate strongest evidence (human choice)", "/strongest",
            f'<label>Direction</label><select name="direction"><option>FOR</option><option>AGAINST</option></select>'
            f'<label>Evidence item (must match direction)</label><select name="target_seq">{targets}</select>', "Designate"))
    if open_items:
        out.append(F("Resolve a question / retract an entry", "/resolve",
            f'<label>Item</label><select name="target_seq">{ropts}</select><label>Status</label><select name="status"><option>RESOLVED</option><option>RETRACTED</option></select>'
            '<label>Note * (what resolved it / why retracted; the original stays in history)</label><textarea name="note" rows="2" required></textarea>', "Record"))
    out.append(F("Add note (e.g. “continue underwriting”)", "/note", '<textarea name="text" rows="2" required></textarea>', "Record note"))
    if c["state"] == "READY_FOR_CAPITAL_COMPARISON":
        out.append('<p class="small mut">READY FOR CAPITAL COMPARISON is a label only. It starts nothing.</p>')
    return "".join(out)


def render_candidate(cid: str, path: Path = ledger.DEFAULT_LEDGER, *, today: date | None = None,
                     error: str = "") -> str | None:
    today = today or date.today()
    c = ledger.replay(path).get(cid)
    if c is None:
        return None
    hist = "".join(f'<tr><td>{h["seq"]}</td><td>{e(h["date"])}</td><td>{e(h["type"])}</td>'
                   f'<td>{e(h["summary"])}</td><td>{e(h["reason"])}</td>'
                   f'<td>{"backfilled" if h["backfilled"] else ""}</td></tr>' for h in c["history"])
    refs = "".join(f"<li>{_ref(r, True)}</li>" for r in c["refs"]) or '<li class="mut">None.</li>'
    ev_head = "<tr><th>#</th><th>Grade · direction</th><th>Item</th><th>Source · known-at</th></tr>"
    groups = []
    for tag in ledger.EVIDENCE_TAGS:
        items = [i for i in c["evidence"] if i["tag"] == tag]
        body = (f'<table>{ev_head}{"".join(_evid_row(i, c["strongest"]) for i in items)}</table>' if items
                else '<p class="mut small">None recorded.</p>')
        groups.append(f"<h3>{TAG_LABEL[tag]}</h3>{body}")
    falsif = "".join(
        f'<tr><td>#{f["seq"]}</td><td><b>{e(f["result"])}</b> <span class="tag">{e(f["grade"])}</span></td><td>{e(f["test"])}</td>'
        f'<td class="small">{e(f["source_ref"]) or "<i class=mut>no reference</i>"}<br>known {e(f["known_at"]) or "n/a"}'
        f'{" · backfilled" if f["backfilled"] else ""}{" · RETRACTED: " + e(f["note"]) if f["status"] == "RETRACTED" else ""}</td></tr>'
        for f in c["falsifications"]) or '<tr><td colspan=4 class="mut small">No test recorded.</td></tr>'
    unres = "".join(f'<li{" style=opacity:.6" if u["status"] != "OPEN" else ""}>#{u["seq"]} {e(u["question"])}'
                    f'{" — <b>" + e(u["status"]) + ":</b> " + e(u["note"]) if u["status"] != "OPEN" else ""}</li>'
                    for u in c["unresolved"]) or '<li class="mut">None recorded.</li>'
    rq = "".join(f"<li>{e(q)}</li>" for q in c["revisit_questions"])
    parked_q = f"<h3>Parked — revisit questions</h3><ul>{rq}</ul>" if rq else ""
    notes = "".join(f'<li>{e(n["date"])} — {e(n["text"])}</li>' for n in c["notes"]) or '<li class="mut">None.</li>'
    err = f'<div class="err">{e(error)}</div>' if error else ""
    gf = (' <span class="tag">grandfathered</span>' if c["grandfathered"] else "")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(cid)} · Atlas</title><style>{CSS}</style></head><body><main>
<p><a href="/">← Board</a></p><h1>{e(cid)} — {e(c["name"])}</h1>
<div class="row"><span class="tag">state: {e(c["state"])}</span><span class="tag">source: {e(c["source"])}</span>{gf}</div>
{err}{_glance(c, today)}
<h2>Underwriting template</h2>
<h3>Investment question</h3><p>{e(c["investment_question"])}</p>
<h3>Cheapest falsification and result</h3><table><tr><th>#</th><th>Result</th><th>Test</th><th>Source · known-at</th></tr>{falsif}</table>
{''.join(groups)}
<h3>Unresolved questions</h3><ul>{unres}</ul>{parked_q}
<h3>Current state</h3><p><b>{e(c["state"])}</b> since {e(c["state_since"])}. {e(c["reason"])}</p>
{_placeholders(c)}
<h2>Provenance</h2><p>Source <b>{e(c["source"])}</b>{" — " + e(c["source_detail"]) if c["source_detail"] else ""}; surfaced {e(c["surfaced_on"])}.</p>
<h3>Records</h3><ul>{refs}</ul><h3>Notes</h3><ul>{notes}</ul>
{_forms(c)}
<h2>History (append-only)</h2><table><tr><th>#</th><th>Date</th><th>Type</th><th>Summary</th><th>Reason / result</th><th></th></tr>{hist}</table>
</main></body></html>"""


def _int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        raise ledger.LedgerError("invalid item number")


# ------------------------------------------------------------------ server
class Handler(BaseHTTPRequestHandler):
    ledger_path: Path = ledger.DEFAULT_LEDGER
    server_version = "AtlasBoard/0.1"

    def log_message(self, *a):  # quiet
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
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, "forbidden", "text/plain")
        p = urllib.parse.urlparse(self.path).path
        if p == "/":
            return self._send(200, render_board(self.ledger_path))
        if p.startswith("/c/"):
            html = render_candidate(urllib.parse.unquote(p[3:]), self.ledger_path)
            return self._send(200, html) if html else self._send(404, "not found", "text/plain")
        if p.startswith("/doc/"):  # read-only, allowlisted to the pilot record folder
            f = (DOC_DIR / urllib.parse.unquote(p[5:])).resolve()
            if f.parent == DOC_DIR and f.suffix == ".md" and f.is_file():
                return self._send(200, f.read_text(encoding="utf-8"), "text/plain; charset=utf-8")
        return self._send(404, "not found", "text/plain")

    def do_POST(self):
        if not self._host_ok():
            return self._send(403, "forbidden", "text/plain")
        n = int(self.headers.get("Content-Length") or 0)
        if n > 100_000:
            return self._send(413, "too large", "text/plain")
        f = {k: v[0] for k, v in urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8")).items()}
        p = urllib.parse.urlparse(self.path).path
        lines = lambda s: [x for x in (s or "").splitlines() if x.strip()]
        try:
            if p == "/surface":
                ev = ledger.surface(self.ledger_path, name=f.get("name", ""), ticker=f.get("ticker", ""),
                                    source=f.get("source", ""), source_detail=f.get("source_detail", ""),
                                    why_surfaced=f.get("why_surfaced", ""),
                                    investment_question=f.get("investment_question", ""))
                dest = "/c/" + urllib.parse.quote(ev["candidate_id"])
            elif p == "/state":
                ledger.change_state(self.ledger_path, candidate_id=f.get("candidate_id", ""),
                                    to_state=f.get("to_state", ""), reason=f.get("reason", ""),
                                    waiting_on=f.get("waiting_on", ""), parked_until=f.get("parked_until", ""),
                                    parked_until_verified=f.get("parked_until_verified") == "1",
                                    revisit_questions=lines(f.get("revisit_questions")))
                dest = "/c/" + urllib.parse.quote(f.get("candidate_id", ""))
            elif p == "/falsify":
                ledger.record_falsification(self.ledger_path, candidate_id=f.get("candidate_id", ""), test=f.get("test", ""),
                                            result=f.get("result", ""), grade=f.get("grade", ""),
                                            source_ref=f.get("source_ref", ""), known_at=f.get("known_at", ""))
                dest = "/c/" + urllib.parse.quote(f.get("candidate_id", ""))
            elif p == "/evidence":
                ledger.add_evidence(self.ledger_path, candidate_id=f.get("candidate_id", ""), tag=f.get("tag", ""),
                                    direction=f.get("direction", ""), grade=f.get("grade", ""), text=f.get("text", ""),
                                    source_ref=f.get("source_ref", ""), known_at=f.get("known_at", ""))
                dest = "/c/" + urllib.parse.quote(f.get("candidate_id", ""))
            elif p == "/unresolved":
                ledger.add_unresolved(self.ledger_path, candidate_id=f.get("candidate_id", ""), question=f.get("question", ""))
                dest = "/c/" + urllib.parse.quote(f.get("candidate_id", ""))
            elif p == "/strongest":
                ledger.set_strongest(self.ledger_path, candidate_id=f.get("candidate_id", ""),
                                     direction=f.get("direction", ""), target_seq=_int(f.get("target_seq")))
                dest = "/c/" + urllib.parse.quote(f.get("candidate_id", ""))
            elif p == "/resolve":
                ledger.resolve_item(self.ledger_path, candidate_id=f.get("candidate_id", ""),
                                    target_seq=_int(f.get("target_seq")), status=f.get("status", ""), note=f.get("note", ""))
                dest = "/c/" + urllib.parse.quote(f.get("candidate_id", ""))
            elif p == "/note":
                ledger.add_note(self.ledger_path, candidate_id=f.get("candidate_id", ""), text=f.get("text", ""))
                dest = "/c/" + urllib.parse.quote(f.get("candidate_id", ""))
            else:
                return self._send(404, "not found", "text/plain")
        except ledger.LedgerError as exc:
            if p == "/surface":
                return self._send(400, render_board(self.ledger_path, error=str(exc)))
            html = render_candidate(f.get("candidate_id", ""), self.ledger_path, error=str(exc))
            return self._send(400, html or "bad request", "text/html; charset=utf-8" if html else "text/plain")
        self._send(303, "", "text/plain", {"Location": dest})


def serve(port: int = 8765, path: Path = ledger.DEFAULT_LEDGER) -> None:
    Handler.ledger_path = Path(path)
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)  # loopback only
    print(f"Atlas Operating Board on http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
