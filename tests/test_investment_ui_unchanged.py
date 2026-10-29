"""The existing investment interface (``atlas_ui``, the application of record) must not change when project pages are added.

Fingerprints below were taken from the code BEFORE the Project section was added (HEAD 0398537). A change to any investment page function, the
theme, the shared stylesheet or the seven-item navigation fails here and needs a deliberate, reviewed update of this file.
The shared page chrome may add the PROJECT group and nothing else: with no project pages it must render byte-for-byte as before.
"""
import hashlib
import inspect
import types

import pytest

from atlas_ui import app as appmod
from atlas_ui.__main__ import build

from test_atlas_ui import http_app, req  # noqa: F401  (fixtures)


@pytest.fixture
def demo_app(tmp_path):
    return build(True, tmp_path / "demo")

PINS = {
    "_bn": "1b43c54829608a3a",
    "_pct": "fd5f202aa19a3bc3",
    "api_cohort": "a662c877f9088a08",
    "api_state": "9be88665da29bbb0",
    "assessment_panel": "1458a87f4e6129ad",
    "baseline_phrase": "7e2f3b1f2c004745",
    "candidate_page": "a441c61328b53b47",
    "candidate_runs": "2d1c4af03e75df22",
    "capabilities_page": "03f07ee2e237f0ee",
    "cohort_page": "ddf3e9016eaa4eff",
    "desk_page": "ca22d6cd1d34d10b",
    "effective_disposition": "f8dff7954ea43ea1",
    "history_page": "00d9bbb7614c0e97",
    "intake": "58b6454de4d470f6",
    "key_status": "917f4ff647154091",
    "ledger_holding_note": "2971aeb370643204",
    "matrix_markdown": "f974e06876eb606e",
    "money": "a34ec142b43e71b6",
    "overview": "4bc2305c546255e2",
    "pill": "cf57786194d9536e",
    "research_dir": "0950e28d260fe9f0",
    "research_snapshot": "1abc1efc358e3e40",
    "run_page": "eb74c0babaf31683",
    "snapshot_rows": "77b81e273611616b",
    "stage7_page": "b56fa1454b0a653b",
    "status_pill": "f6f62a093085c26d",
    "urllib_q": "c38a24d46148ec5c"
}

NAV_BEFORE = [("/", "Overview"), ("/intake", "Opportunity intake"), ("/cohort", "Research cohort"), ("/stage7", "Stage 7 evidence"),
              ("/desk", "Decision desk"), ("/history", "Decision history"), ("/capabilities", "Capability matrix")]
THEME_SHA16, EXTRA_CSS_SHA16 = "fbe9392b81ae94d0", "c906099f0e6c39bb"
PAGE_GOLDEN = {"DEMO": "8a00b26655f96f07a3488e714e0a303ce6d8760063191b58da6d8d55ec2143d9",
               "CANONICAL": "9df54ed89fb9be5c6766cf56bcedbeba2a8f15b342fec0b740307ded4359991a"}
EXCLUDED = {"page", "make_handler", "serve"}        # shared chrome / server wiring: covered by the byte-for-byte test and the route tests below


def sha16(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def test_every_investment_page_function_is_unchanged():
    now = {n: sha16(inspect.getsource(o)) for n, o in vars(appmod).items()
           if isinstance(o, types.FunctionType) and o.__module__ == appmod.__name__ and n not in EXCLUDED and n not in NEW_FUNCTIONS}
    assert now == PINS, sorted({k for k in set(now) | set(PINS) if now.get(k) != PINS.get(k)})


NEW_FUNCTIONS = {"project_page", "api_project", "project_data", "_when", "_unk"}      # the only functions added by the project dashboard increment


def test_the_seven_investment_pages_keep_their_navigation_order_and_the_theme_is_untouched():
    assert appmod.NAV == NAV_BEFORE
    assert sha16(appmod.THEME) == THEME_SHA16 and sha16(appmod.EXTRA_CSS) == EXTRA_CSS_SHA16


@pytest.mark.parametrize("demo", [True, False])
def test_shared_page_chrome_is_byte_identical_when_there_are_no_project_pages(tmp_path, monkeypatch, demo):
    monkeypatch.setattr(appmod, "PROJECT_NAV", [])
    app = build(demo, tmp_path / "w")
    html = appmod.page(app, "/", "Title", "<p>fixed body</p>", flash="f", err="e")
    assert hashlib.sha256(html.encode()).hexdigest() == PAGE_GOLDEN[app.mode]


def test_project_group_is_the_only_difference_the_chrome_makes(tmp_path, monkeypatch):
    app = build(True, tmp_path / "w")
    with_project = appmod.page(app, "/", "Title", "<p>fixed body</p>")
    monkeypatch.setattr(appmod, "PROJECT_NAV", [])
    without = appmod.page(app, "/", "Title", "<p>fixed body</p>")
    start = with_project.index('<div class="navtitle" data-group="project"')
    end = with_project.index("</nav>", start) + len("</nav>")
    assert with_project[:start] + with_project[end:] == without
    assert "/project" in with_project[start:end] and with_project[start:end].count('class="navbtn') == len(appmod.NAV_PROJECT_DEFAULT)


def test_all_existing_investment_routes_still_serve_and_stay_free_of_scripts(http_app):
    app, port = http_app
    for path in ("/", "/intake", "/cohort", "/stage7", "/desk", "/history", "/capabilities", "/candidate/MCD", "/candidate/DEMOCO", "/api/state", "/api/cohort", "/api/ledger"):
        st, body, hd = req(port, "GET", path)
        assert st == 200, path
        if not path.startswith("/api"):
            assert "<script" not in body.lower() and "WORKSPACE" in body, path
            for p, n in NAV_BEFORE:                                  # every investment page still links to all seven investment pages
                assert f'href="{p}"' in body and n in body, (path, p)


def test_investment_pages_do_not_mention_or_depend_on_the_project_module():
    src = {n: inspect.getsource(o) for n, o in vars(appmod).items() if isinstance(o, types.FunctionType) and n in PINS}
    assert not [n for n, s in src.items() if "project" in s.lower().replace("projects", "") and n not in ("api_state",)], "investment page code must not reach into the project view"
