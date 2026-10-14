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


def render_candidate(cid: str, path: Path = ledger.DEFAULT_LEDGER, *, today: date | None = None,
                     error: str = "") -> str | None:
    today = today or date.today()
    c = ledger.replay(path).get(cid)
    if c is None:
        return None
    allowed = sorted(ledger.TRANSITIONS[c["state"]])
    opts = "".join(f"<option>{s}</option>" for s in allowed)
    hist = "".join(f'<tr><td>{h["seq"]}</td><td>{e(h["date"])}</td><td>{e(h["type"])}</td>'
                   f'<td>{e(h["summary"])}</td><td>{e(h["reason"])}</td>'
                   f'<td>{"backfilled" if h["backfilled"] else ""}</td></tr>' for h in c["history"])
    notes = "".join(f'<li>{e(n["date"])} — {e(n["text"])}</li>' for n in c["notes"]) or '<li class="mut">None.</li>'
    rq = "".join(f"<li>{e(q)}</li>" for q in c["revisit_questions"])
    refs = "".join(f"<li>{_ref(r, True)}</li>" for r in c["refs"]) or '<li class="mut">None.</li>'
    forms = ""
    if allowed:
        forms = f"""<h2>Change state</h2><form method="post" action="/state"><input type="hidden" name="candidate_id" value="{e(cid)}">
<label>To state</label><select name="to_state">{opts}</select><label>Reason *</label><textarea name="reason" rows="2" required></textarea>
<label>If PARKED — waiting on (specific evidence) *</label><input name="waiting_on">
<label>If PARKED — revisit date (YYYY-MM-DD, optional)</label><input name="parked_until">
<label><input type="checkbox" name="parked_until_verified" value="1" style="width:auto"> date officially verified (company IR / filing)</label>
<label>If PARKED — revisit questions (one per line)</label><textarea name="revisit_questions" rows="3"></textarea>
<button>Record state change</button></form>
<p class="small mut">READY FOR CAPITAL COMPARISON is a label only. It starts nothing; Stage 7 and Stage 8 are separate, human-run steps.</p>"""
    forms += f"""<h2>Add note</h2><form method="post" action="/note"><input type="hidden" name="candidate_id" value="{e(cid)}">
<textarea name="text" rows="2" required></textarea><button>Record note</button></form>"""
    err = f'<div class="err">{e(error)}</div>' if error else ""
    parked = ""
    if c["state"] == "PARKED":
        ver = "officially verified" if c["parked_until_verified"] else "NOT officially verified"
        parked = (f'<h2>Parked</h2><p>Until <b>{e(c["parked_until"] or "no date")}</b> ({ver}) {_due_tag(c, today)}<br>'
                  f'Waiting on: {e(c["waiting_on"])}</p><b>Revisit questions</b><ul>{rq}</ul>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(cid)} · Atlas</title><style>{CSS}</style></head><body><main>
<p><a href="/">← Board</a></p><h1>{e(cid)} — {e(c["name"])}</h1>
<div class="row"><span class="tag">state: {e(c["state"])} since {e(c["state_since"])}</span><span class="tag">source: {e(c["source"])}</span></div>
{err}<h2>Provenance</h2><p>Source <b>{e(c["source"])}</b>{" — " + e(c["source_detail"]) if c["source_detail"] else ""}; surfaced {e(c["surfaced_on"])}.</p>
<p><b>Why it surfaced:</b> {e(c["why_surfaced"])}</p><p><b>Investment question:</b> {e(c["investment_question"])}</p>
{parked}<h2>Records</h2><ul>{refs}</ul><h2>Notes</h2><ul>{notes}</ul>
<h2>History (append-only)</h2><table><tr><th>#</th><th>Date</th><th>Type</th><th>State / text</th><th>Reason</th><th></th></tr>{hist}</table>
{forms}</main></body></html>"""


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
