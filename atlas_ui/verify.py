"""Source-of-truth preflight, regression verification and delivery bundle.

Tooling over records that already exist (the pin file, the Cycle 0 loader, the discovery-ledger hash chain, git, pytest). It adds no data source,
store, provider or investment logic. ``docs/CURRENT_AUTHORITY.md`` is the one reference it reads.

    python -m atlas_ui preflight [--json]
    python -m atlas_ui verify [--clean-extract]
    python -m atlas_ui deliver [--base COMMIT]
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AUTHORITY = "docs/CURRENT_AUTHORITY.md"
MILESTONE_LABELS = ("What changed and was verified", "Incomplete or potentially overlooked", "What we should do next")
CODE_PATHS = ("atlas_ui", "operating_mvp", "stock_atlas", "capital_decision_facade.py", "allocation_rationale.py",
              "live_price_binding.py", "live_session_calendar.py", "sec_adapter.py", "xbrl_parser.py", "identity_resolver.py")


@dataclass
class Check:
    name: str
    status: str  # OK | FAIL | WARN | INFO | SKIP
    detail: str = ""

    def line(self) -> str:
        return f"[{self.status:4s}] {self.name}" + (f" — {self.detail}" if self.detail else "")


# ------------------------------------------------------------------------------------------------------ helpers
def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_authority(repo: Path = REPO) -> dict:
    text = (Path(repo) / AUTHORITY).read_text(encoding="utf-8")
    m = re.search(r"```json\n(.*?)\n```", text, re.S)
    if not m:
        raise ValueError(f"{AUTHORITY} has no JSON manifest block")
    return json.loads(m.group(1))


def _git(repo: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=60)
    except Exception:
        return None
    return r.stdout if r.returncode == 0 else None


def has_git(repo: Path) -> bool:
    return (Path(repo) / ".git").exists() and _git(repo, "rev-parse", "HEAD") is not None


def _section(text: str, heading_prefix: str) -> str | None:
    """Text of the markdown section whose heading line starts with ``heading_prefix`` (up to the next heading of the same or higher level)."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(heading_prefix):
            level = len(ln) - len(ln.lstrip("#"))
            out = [ln]
            for nxt in lines[i + 1:]:
                if nxt.startswith("#") and len(nxt) - len(nxt.lstrip("#")) <= level:
                    break
                out.append(nxt)
            return "\n".join(out)
    return None


# ------------------------------------------------------------------------------------------------------ preflight
def preflight(repo: Path = REPO, *, use_git: bool = True) -> list[Check]:
    repo = Path(repo)
    cs: list[Check] = []
    add = lambda name, status, detail="": cs.append(Check(name, status, detail))

    try:
        a = load_authority(repo)
    except Exception as exc:
        add("authority reference", "FAIL", f"{AUTHORITY} unreadable: {exc}")
        return cs
    add("authority reference", "OK", AUTHORITY)

    # --- referenced documents exist
    missing = [p for p in [*a["documents"].values(), a["portfolio_baseline"]["doc"], a["controls"]["pin_file"], a["candidates"]["ledger"],
                           *(c["record"] for c in a["controls"]["authorized_changes"])] if not (repo / p).is_file()]
    add("referenced records exist", "FAIL" if missing else "OK", f"missing: {missing}" if missing else f"{len(a['documents'])} governing documents, baseline, pin, ledger, change records")

    # --- frozen controls
    pin_path = repo / a["controls"]["pin_file"]
    if pin_path.is_file():
        pins = [ln.split() for ln in pin_path.read_text().splitlines() if ln.strip()]
        bad = [rel for digest, rel in pins if not (repo / rel).is_file() or _sha(repo / rel) != digest]
        if len(pins) != a["controls"]["files"]:
            add("frozen controls pinned", "FAIL", f"{len(pins)} pinned files, authority expects {a['controls']['files']}")
        elif bad:
            add("frozen controls pinned", "FAIL", f"differ from the pin: {bad}")
        else:
            add("frozen controls pinned", "OK", f"{len(pins)} control files match {a['controls']['pin_file']}")
        if _sha(pin_path) != a["controls"]["pin_file_sha256"]:
            add("pin file matches authority", "FAIL", "the pin file changed without updating controls.pin_file_sha256 and its change record in the authority reference")
        else:
            add("pin file matches authority", "OK", "authorized changes " + ", ".join(c["id"] for c in a["controls"]["authorized_changes"]))
    else:
        add("frozen controls pinned", "FAIL", "pin file missing")

    # --- portfolio baseline (reuses the canonical loader's own validation)
    b = a["portfolio_baseline"]
    try:
        sys.path.insert(0, str(repo)) if str(repo) not in sys.path else None
        from atlas_ui import canonical
        c0 = canonical.load_cycle0(repo / b["doc"])
        ok = (len(c0.holdings) == b["holdings"] and str(c0.stocks_total) == b["stocks_total"] and str(c0.identified_value) == b["identified_value_approx"]
              and c0.doc_sha256 == b["sha256"])
        add("portfolio baseline (Cycle 0 Correction 002)", "OK" if ok else "FAIL",
            f"{len(c0.holdings)} holdings, stocks ${c0.stocks_total}, identified ≈${c0.identified_value}" if ok else "baseline record or its totals differ from the authority reference")
    except Exception as exc:
        add("portfolio baseline (Cycle 0 Correction 002)", "FAIL", str(exc))

    # --- candidate restrictions
    try:
        from operating_mvp import ledger
        ledger.verify_chain(repo / a["candidates"]["ledger"])
        cands = ledger.replay(repo / a["candidates"]["ledger"])
        bad, notes = [], []
        for t, until in a["candidates"]["parked"].items():
            c = cands.get(t)
            if not c or c["state"] != "PARKED" or c["parked_until"] != until:
                bad.append(f"{t}: {None if not c else (c['state'], c['parked_until'])} != PARKED until {until}")
            elif date.fromisoformat(until) <= date.today():
                notes.append(f"{t} revisit date {until} reached (a trigger to review, not a promotion)")
        add("candidate ledger chain + parked restrictions", "FAIL" if bad else "OK",
            "; ".join(bad) if bad else ", ".join(f"{t} PARKED until {u}" for t, u in a["candidates"]["parked"].items()))
        for n in notes:
            add("revisit trigger", "INFO", n)
    except Exception as exc:
        add("candidate ledger chain + parked restrictions", "FAIL", str(exc))

    # --- capital status
    dl = repo / a["capital"]["decision_ledger"]
    rows = sum(1 for ln in dl.read_text().splitlines() if ln.strip()) if dl.is_file() else 0
    add("canonical decision ledger", "OK" if rows == a["capital"]["canonical_decision_rows"] else "WARN",
        f"{rows} rows (authority expects {a['capital']['canonical_decision_rows']}); {a['capital']['status']}")

    # --- master plan / decision log structure and "historical never governs"
    docs = a["documents"]
    plan = (repo / docs["master_plan"]).read_text(encoding="utf-8")
    pm = a["plan_markers"]
    top = "\n".join(plan.splitlines()[:90])
    add("master plan points to the authority reference", "OK" if pm["top_pointer"] in top else "FAIL", pm["top_pointer"] if pm["top_pointer"] in top else "no pointer near the top of the Master Plan")
    i = plan.find(pm["immediate_next_actions_heading"])
    sup = plan.find(pm["immediate_next_actions_superseded"], i) if i >= 0 else -1
    add("outdated Pilot 2 work list marked superseded", "OK" if (i >= 0 and sup > i) or i < 0 else "FAIL",
        "the 'Immediate Next Actions' section is marked as not governing" if (i >= 0 and sup > i) else "'Immediate Next Actions' is not marked superseded; its Pilot 2 instructions could read as active")
    aw = _section(plan, a["active_work"]["plan_heading_prefix"])
    add("active work is a Master Plan entry", "OK" if aw else "FAIL", a["active_work"]["plan_heading_prefix"].lstrip("# ") if aw else "heading not found")
    mr = _section(plan, a["last_milestone_review"]["plan_heading"])
    if mr is None:
        add("latest milestone review present", "FAIL", f"'{a['last_milestone_review']['plan_heading']}' not found in the Master Plan")
    else:
        lacking = [lbl for lbl in MILESTONE_LABELS if lbl.lower() not in mr.lower()]
        add("latest milestone review present", "FAIL" if lacking else "OK", f"missing sections: {lacking}" if lacking else "has changed/verified, incomplete/overlooked, next")
    hist = a["historical_not_governing"]
    found = 0
    for h in hist:
        globs = h.get("glob")
        globs = [globs] if isinstance(globs, str) else (globs or [])
        found += sum(1 for g in globs if list(repo.glob(g)))
    add("historical material declared", "OK", f"{len(hist)} entries; {found} matching path patterns present in this tree")

    # --- git: newest commit vs approved state, append-only, controls since approval
    if not use_git or not has_git(repo):
        add("git position / append-only / controls since approval", "SKIP", "no git history in this tree (extracted ZIP): not checkable here — run from the repository")
        return cs
    approved, head = a["approved_state"]["commit"], _git(repo, "rev-parse", "HEAD").strip()
    if _git(repo, "cat-file", "-e", f"{approved}^{{commit}}") is None:
        add("approved state in history", "FAIL", f"approved commit {approved[:12]} not found in this repository")
        return cs
    is_anc = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", approved, "HEAD"], capture_output=True).returncode == 0
    if not is_anc:
        add("approved state is an ancestor of HEAD", "FAIL", f"{approved[:12]} is not an ancestor of {head[:12]} (wrong branch or rewritten history)")
        return cs
    ahead = [ln for ln in (_git(repo, "log", "--oneline", f"{approved}..HEAD") or "").splitlines() if ln]
    if head == approved:
        add("newest commit vs approved state", "OK", f"HEAD {head[:12]} IS the approved state")
    else:
        add("newest commit vs approved state", "INFO",
            f"NEWEST COMMIT {head[:12]} is {len(ahead)} commit(s) ahead of the LATEST APPROVED STATE {approved[:12]}; those commits are unapproved until the human accepts them: "
            + " | ".join(ln[:70] for ln in ahead[:6]) + (" | …" if len(ahead) > 6 else ""))
    # governed files changed since approval
    changed_ctrl = []
    if pin_path.is_file():
        for digest, rel in [ln.split() for ln in pin_path.read_text().splitlines() if ln.strip()]:
            old = _git(repo, "show", f"{approved}:{rel}")
            if old is not None and hashlib.sha256(old.encode("utf-8")).hexdigest() != _sha(repo / rel):
                changed_ctrl.append(rel)
    add("frozen controls changed since the approved state", "WARN" if changed_ctrl else "OK",
        (f"{changed_ctrl}: confirm an authorization record covers them" if changed_ctrl else "none: control files are byte-identical to the approved state"))
    stat = _git(repo, "diff", "--numstat", approved, "--", *a["append_only"]) or ""
    removed = [(p, int(d)) for ad, d, p in (ln.split("\t") for ln in stat.splitlines() if ln.count("\t") == 2) if d.isdigit() and int(d) > 0]
    add("append-only records since the approved state", "FAIL" if removed else "OK",
        f"lines removed or edited in {removed}" if removed else "Master Plan and Decision Log have additions only")
    dirty = [ln for ln in (_git(repo, "status", "--porcelain") or "").splitlines() if ln and not ln[3:].startswith("deliverables/")]
    add("working tree", "WARN" if dirty else "OK", f"{len(dirty)} uncommitted change(s)" if dirty else "clean")
    rc = a["last_milestone_review"]["reviewed_commit"]
    if rc and rc != "PENDING" and _git(repo, "cat-file", "-e", f"{rc}^{{commit}}") is not None:
        since = [ln for ln in (_git(repo, "log", "--oneline", f"{rc}..HEAD", "--", *CODE_PATHS) or "").splitlines() if ln]
        add("code commits since the last milestone review", "INFO", f"{len(since)}" + (" — a review is due after the next major improvement" if since else ""))
    return cs


def render(checks: list[Check]) -> str:
    c = Counter(x.status for x in checks)
    verdict = "PREFLIGHT FAIL" if c["FAIL"] else "PREFLIGHT PASS"
    return "\n".join(x.line() for x in checks) + f"\n{verdict} ({c['OK']} ok, {c['FAIL']} fail, {c['WARN']} warn, {c['INFO']} info, {c['SKIP']} skipped)"


# ------------------------------------------------------------------------------------------------------ test runs
_HIDE_PLUGIN = '''"""pytest plugin: opening any project file under the ORIGINAL tree (outside .venv/__pycache__) is an error, so a clean copy cannot be rescued by it."""
import os, sys
ORIG = os.environ["ATLAS_ORIGINAL_ROOT"]
def _hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.fsdecode(args[0])
        if p.startswith(ORIG) and not p.startswith(ORIG + "/.venv") and "/__pycache__/" not in p:
            raise PermissionError("ORIGINAL TREE READ BLOCKED: " + p)
sys.addaudithook(_hook)
'''


def classify_skip(reason: str) -> str:
    r = reason.lower()
    if "api_key absent" in r or "blocked" in r:
        return "BLOCKED — live credential absent (not a pass)"
    if "not present in this checkout" in r or ".git" in r:
        return "ENVIRONMENT — needs git history"
    return "OTHER — investigate"


def summarize_pytest(out: str) -> dict:
    counts = {k: 0 for k in ("passed", "failed", "skipped", "error", "xfailed", "xpassed", "warnings")}
    last = next((ln for ln in reversed(out.splitlines()) if re.search(r"\d+ (passed|failed|skipped|error)", ln)), "")
    for n, word in re.findall(r"(\d+) (passed|failed|skipped|errors?|xfailed|xpassed|warnings?)", last):
        counts["error" if word.startswith("error") else "warnings" if word.startswith("warning") else word] += int(n)
    skips: Counter = Counter()
    for m in re.finditer(r"^SKIPPED \[(\d+)\] (.+?): (.*)$", out, re.M):
        skips[classify_skip(m.group(3))] += int(m.group(1))
    return {**counts, "skip_classes": dict(skips), "summary_line": last.strip(), "failed_tests": re.findall(r"^FAILED (\S+)", out, re.M)}


def run_pytest(cwd: Path, *, hide_original: Path | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST") and k != "PYTHONPATH"}
    cmd = [sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider", "--tb=short"]
    tmp = None
    if hide_original is not None:
        tmp = Path(tempfile.mkdtemp(prefix="atlas_plugin_"))
        (tmp / "hide_original_tree.py").write_text(_HIDE_PLUGIN)
        env.update(PYTHONPATH=str(tmp), ATLAS_ORIGINAL_ROOT=str(hide_original))
        cmd += ["-p", "hide_original_tree"]
    try:
        r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=1800)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    return {**summarize_pytest(r.stdout + r.stderr), "returncode": r.returncode, "tail": (r.stdout + r.stderr)[-700:]}


def tests_clean(s: dict | None) -> bool:
    """A run counts only if pytest exited 0, produced a summary, passed something, and nothing failed or errored. An empty or unparseable run is NOT clean."""
    return bool(s) and s["returncode"] == 0 and bool(s["summary_line"]) and s["passed"] > 0 and s["failed"] == 0 and s["error"] == 0


def render_tests(label: str, s: dict) -> str:
    if not s["summary_line"]:
        return f"{label}: **NO PYTEST SUMMARY** (exit code {s.get('returncode')}) — treat as FAILED. Output tail:\n{s.get('tail', '')}"
    skips = "; ".join(f"{n} {k}" for k, n in s["skip_classes"].items()) or "none"
    return (f"{label}: {s['passed']} passed, {s['failed']} failed, {s['error']} errors, {s['skipped']} skipped, {s['warnings']} warning(s)\n"
            f"  skipped by class: {skips}" + (f"\n  FAILED: {s['failed_tests']}" if s["failed_tests"] else ""))


def extract_clean(repo: Path, dest: Path, *, commit: str = "HEAD") -> Path:
    """A clean copy of the committed tree (what a ZIP contains) at ``dest/stock-atlas``."""
    zpath = dest / "clean.zip"
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(repo), "archive", "--format=zip", "--prefix=stock-atlas/", "-o", str(zpath), commit], check=True)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(dest)
    zpath.unlink()
    return dest / "stock-atlas"


def verify(repo: Path = REPO, *, clean_extract: bool = False) -> int:
    checks = preflight(repo)
    print(render(checks))
    if any(c.status == "FAIL" for c in checks):
        print("Not running tests: fix the failing source-of-truth checks first.")
        return 2
    res = run_pytest(repo)
    print(render_tests("repository, full offline suite", res))
    rc = res["returncode"]
    if clean_extract:
        if not has_git(repo):
            print("clean extraction: SKIP (needs the git repository to build the copy)")
        else:
            tmp = Path(tempfile.mkdtemp(prefix="atlas_clean_"))
            try:
                tree = extract_clean(repo, tmp)
                cres = run_pytest(tree, hide_original=repo)
                print(render_tests(f"clean extraction of HEAD in {tree.parent}, original tree blocked", cres))
                rc = rc or cres["returncode"]
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    return rc


# ------------------------------------------------------------------------------------------------------ delivery
def _frozen_table(repo: Path, base: str, head: str, a: dict) -> list[str]:
    rows = []
    for digest, rel in [ln.split() for ln in (repo / a["controls"]["pin_file"]).read_text().splitlines() if ln.strip()]:
        b = _git(repo, "show", f"{base}:{rel}")
        h = _git(repo, "show", f"{head}:{rel}")
        same = b is not None and h is not None and b == h
        rows.append(f"| `{rel}` | {'identical' if same else '**CHANGED**'} | {hashlib.sha256((h or '').encode()).hexdigest()[:12]} |")
    return rows


def deliver(repo: Path = REPO, *, base: str | None = None, out: Path | None = None, run_tests: bool = True) -> Path:
    """One ZIP of the committed tree, one patch, and one DELIVERY.md of mechanical facts — everything verified from the extracted ZIP."""
    repo = Path(repo)
    if not has_git(repo):
        raise SystemExit("deliver needs the git repository")
    dirty = [ln for ln in (_git(repo, "status", "--porcelain") or "").splitlines() if ln and not ln[3:].startswith("deliverables/")]
    if dirty:
        raise SystemExit("working tree has uncommitted changes; commit first so the ZIP, diff and tests describe one commit:\n" + "\n".join(dirty[:10]))
    a = load_authority(repo)
    head = _git(repo, "rev-parse", "HEAD").strip()
    short = head[:7]
    base = _git(repo, "rev-parse", base or a["approved_state"]["commit"]).strip()
    out = Path(out or repo / "deliverables" / f"delivery_{short}")
    out.mkdir(parents=True, exist_ok=True)
    zname = f"Stock_Atlas_{short}_full_source.zip"
    subprocess.run(["git", "-C", str(repo), "archive", "--format=zip", "--prefix=stock-atlas/", "-o", str(out / zname), head], check=True)
    patch = out / f"SOURCE_DIFF_{base[:7]}_to_{short}.patch"
    patch.write_text(_git(repo, "diff", base, head) or "")
    scratch = Path(tempfile.mkdtemp(prefix="atlas_deliver_"))     # outside the repo: the repo suite must not collect it, and the original-tree block must not cover it
    with zipfile.ZipFile(out / zname) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        z.extractall(scratch)
    tree = scratch / "stock-atlas"
    try:
        secrets = [n for n in names if re.search(r"(^|/)\.env($|\.(?!example))", n)]
        key = ""
        envf = repo / ".env"
        if envf.is_file():
            key = dict(ln.strip().partition("=")[::2] for ln in envf.read_text().splitlines() if "=" in ln).get("TWELVEDATA_API_KEY", "").strip("\"' ")
        leaked = bool(key) and any(key in (tree / n.split("/", 1)[1]).read_text(errors="ignore") for n in names if (tree / n.split("/", 1)[1]).is_file())
        repo_tests = run_pytest(repo) if run_tests else None
        clean_tests = run_pytest(tree, hide_original=repo) if run_tests else None
        pre = render(preflight(repo))
        pre_zip = render(preflight(tree, use_git=False))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    tests_ok = (not run_tests) or (tests_clean(repo_tests) and tests_clean(clean_tests))
    log = _git(repo, "log", "--oneline", f"{base}..{head}") or ""
    stat = _git(repo, "diff", "--stat", base, head) or ""
    zsha = hashlib.sha256((out / zname).read_bytes()).hexdigest()
    md = f"""# Delivery — HEAD `{short}`

- **Commit:** `{head}` · **Base for the diff (latest approved state):** `{base}`
- **ZIP:** `{zname}` · SHA-256 `{zsha}` · {len(names)} files · `.env` members: {secrets or 'none'} · API key present in any ZIP file: {'**YES**' if leaked else 'no'}
- **Patch:** `{patch.name}` ({len(patch.read_text().splitlines())} lines)
- **Tests:** {'**NOT RUN**' if not run_tests else ('PASS (both runs clean)' if tests_ok else '**FAILED OR INCOMPLETE — do not accept this delivery**')}

## Commits since the approved state
```
{log.rstrip() or '(none)'}
```
## Diff summary
```
{stat.rstrip()}
```
## Frozen controls (base → HEAD, files in `{a['controls']['pin_file']}`)
| File | Status | SHA-256 (HEAD) |
|---|---|---|
{chr(10).join(_frozen_table(repo, base, head, a))}

## Tests (skips are classified; a skip is never a pass)
```
{render_tests('repository, full offline suite', repo_tests) if repo_tests else 'repository suite: NOT RUN (run_tests=False)'}
{render_tests('clean extraction of the ZIP in another directory, original tree blocked', clean_tests) if clean_tests else 'clean extraction suite: NOT RUN (run_tests=False)'}
```
## Source-of-truth preflight
```
{pre}
```
Same check on the extracted ZIP (no git history there):
```
{pre_zip}
```
Milestone review: Master Plan, section "{a['last_milestone_review']['plan_heading'].lstrip('# ')}". Capability matrix: `{a['documents']['capability_matrix']}`.
"""
    (out / "DELIVERY.md").write_text(md, encoding="utf-8")
    if not tests_ok:
        raise SystemExit(f"DELIVERY NOT CLEAN: the test runs failed or produced no results; see {out / 'DELIVERY.md'}")
    return out


def main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="atlas_ui")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight"); p.add_argument("--json", action="store_true")
    v = sub.add_parser("verify"); v.add_argument("--clean-extract", action="store_true")
    d = sub.add_parser("deliver"); d.add_argument("--base"); d.add_argument("--out")
    x = ap.parse_args(argv)
    if x.cmd == "preflight":
        cs = preflight()
        print(json.dumps([c.__dict__ for c in cs], indent=1) if x.json else render(cs))
        return 1 if any(c.status == "FAIL" for c in cs) else 0
    if x.cmd == "verify":
        return verify(clean_extract=x.clean_extract)
    out = deliver(base=x.base, out=x.out)
    print(f"delivery written to {out}")
    return 0
