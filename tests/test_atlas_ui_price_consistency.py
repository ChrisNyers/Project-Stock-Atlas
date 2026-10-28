"""Review of d2df7af: Stage 8 must reproduce the FROZEN Stage 7 price/reference evidence, not merely a fresh same-session bind.

Real facade / DecisionStore / Gate B code; FIXTURE provider only; paper only. Every rejected funded path asserts the
decision ledger is byte-identical afterwards. There is deliberately NO price tolerance: any change means re-run Stage 7.
"""
import ast
from pathlib import Path

import pytest

from atlas_ui import demo
from atlas_ui.__main__ import build
from atlas_ui.service import Rejected, Stage7Service
from test_atlas_ui import NOW, good_req, s8  # noqa: F401
from test_atlas_ui_remediation import ledger_bytes

OTHER_PROVIDER = "FIXTURE-OTHER"


@pytest.fixture
def demo_app(tmp_path):
    return build(True, tmp_path / "demo")


def svc_with(app, **fixture_kw):
    """A service over the SAME workspace whose provider differs from the one that priced Stage 7."""
    return Stage7Service(app.ws, provider_factory=lambda: demo.FixtureProvider(**fixture_kw), identity_fn=lambda t: demo.DEMO_KEY,
                         allowed_providers={demo.DEMO_PROVIDER, OTHER_PROVIDER}, key_present=lambda: True)


def eligible_run(app, price=100.0):
    svc = svc_with(app, price=price)
    e = svc.run(good_req(), NOW)
    assert e["status"] == "ELIGIBLE FOR STAGE 8"
    return e


def assert_rejected_with_zero_rows(app, svc, run_id, form, needle):
    before = ledger_bytes(app)
    with pytest.raises(Rejected, match=needle) as ei:
        svc.record_stage8(run_id, form, NOW)
    assert (ei.value.rows_before, ei.value.rows_after) == (0, 0)
    assert ledger_bytes(app) == before and app.svc.ledger_rows() == [] and app.ws.facade.verify_ledger()


# ---- (a) the reviewer's reproduction: $100 -> $130, same session, same security ------------------------
def test_a_100_to_130_same_session_funded_action_is_rejected(demo_app):
    e = eligible_run(demo_app, 100.0)
    for action in ("INITIATE", "ADD"):
        assert_rejected_with_zero_rows(demo_app, svc_with(demo_app, price=130.0), e["run_id"], s8(action=action),
                                       "does NOT reproduce the frozen Stage 7 price evidence")


def test_a_message_names_the_changed_field_and_demands_a_rerun(demo_app):
    e = eligible_run(demo_app, 100.0)
    with pytest.raises(Rejected) as ei:
        svc_with(demo_app, price=130.0).record_stage8(e["run_id"], s8(), NOW)
    assert "price: Stage 7 100.0 vs now 130.0" in str(ei.value) and "re-run Stage 7" in str(ei.value)


@pytest.mark.parametrize("fresh_price", [100.01, 99.99, 100.5, 70.0])
def test_a_there_is_no_price_tolerance(demo_app, fresh_price):
    e = eligible_run(demo_app, 100.0)
    assert_rejected_with_zero_rows(demo_app, svc_with(demo_app, price=fresh_price), e["run_id"], s8(), "price")


# ---- (b) identical evidence + all other gates -> allowed ----------------------------------------------
def test_b_identical_price_session_and_references_allows_the_paper_action_and_logs_both_sides(demo_app):
    e = eligible_run(demo_app, 100.0)
    out = svc_with(demo_app, price=100.0).record_stage8(e["run_id"], s8(), NOW)
    assert out["rows_after"] == 1 and out["paper_only"]
    import json
    chk = json.loads((demo_app.ws.root / "stage8_price_checks.jsonl").read_text().splitlines()[-1])
    assert chk["frozen_price_binding"] == chk["fresh_price_binding"] and chk["result"] == "REPRODUCED"


def test_b_other_gates_still_apply_even_when_the_price_reproduces(demo_app):
    e = demo_app.svc.run(good_req(tax="UNVERIFIED", accept_unverified="1"), NOW)
    assert_rejected_with_zero_rows(demo_app, demo_app.svc, e["run_id"], s8(), "VERIFIED")


# ---- (c) other validity-affecting changes ----------------------------------------------------------------
@pytest.mark.parametrize("kw,needle", [
    ({"provider": OTHER_PROVIDER}, "provider"),                       # provider/source changed
    ({"quote_offset_s": 60}, "price_as_of"),                          # same-session price correction / re-quote
    ({"name": "Demo Co Class B"}, "quoted_instrument"),               # instrument/class label changed
    ({"mic": "XNAS"}, "fresh-price check failed"),                    # venue changed (Gate B stops it)
    ({"currency": "EUR"}, "fresh-price check failed"),                # currency / FX basis changed (Gate B stops it)
    ({"key": "DEMO-FIXTURE:0000000:DEMOCO-B"}, "fresh-price check failed"),  # security class/identity changed
])
def test_c_any_validity_affecting_change_rejects_funding(demo_app, kw, needle):
    e = eligible_run(demo_app, 100.0)
    assert_rejected_with_zero_rows(demo_app, svc_with(demo_app, price=100.0, **kw), e["run_id"], s8(), needle)


def test_c_treasury_value_date_source_and_attestation_must_match_or_be_reattested(demo_app):
    e = eligible_run(demo_app)
    svc = svc_with(demo_app, price=100.0)
    for over, needle in [({"tsy_ref_value": "4.1"}, "Treasury reference changed"),
                         ({"tsy_ref_value": "3.9000001"}, "Treasury reference changed"),
                         ({"tsy_ref_date": "2020-01-01"}, "older than the 96h"),
                         ({"tsy_ref_value": ""}, "re-attestation"), ({"tsy_ref_value": "nan"}, "re-attestation"),
                         ({"tsy_attest": ""}, "re-attested"), ({"tsy_source_ref": " "}, "re-attested"),
                         ({"tsy_ref_date": "soon"}, "YYYY-MM-DD")]:
        assert_rejected_with_zero_rows(demo_app, svc, e["run_id"], s8(**over), needle)


def test_c_treasury_date_differing_from_the_frozen_one_is_a_change(demo_app):
    from datetime import timedelta
    e = eligible_run(demo_app)
    yesterday = (NOW - timedelta(days=1)).date().isoformat()
    assert_rejected_with_zero_rows(demo_app, svc_with(demo_app, price=100.0), e["run_id"], s8(tsy_ref_date=yesterday), "Treasury reference changed")


def test_c_non_usd_runs_are_not_supported_so_no_fx_is_silently_assumed(demo_app):
    # a currency other than USD can never reach a funded decision: Gate B refuses it at Stage 7 (expected USD)
    from atlas_ui.service import Blocked
    with pytest.raises(Blocked):
        svc_with(demo_app, price=100.0, currency="EUR").run(good_req(), NOW)


# ---- (d) non-actions remain possible -----------------------------------------------------------------------
def test_d_non_actions_stay_available_after_every_kind_of_change(demo_app):
    e = eligible_run(demo_app)
    changed = svc_with(demo_app, price=130.0)
    out = changed.record_stage8(e["run_id"], s8(action="DO NOTHING", tsy_ref_value="", tsy_attest=""), NOW)
    assert out["rows_after"] == 1


# ---- direct-facade bypass: prove every OPERATIONAL Stage 8 writer is the guarded service ---------------------
def test_only_the_guarded_service_writes_final_decisions_in_production_code():
    repo = Path(__file__).resolve().parent.parent
    skip = {".venv", "tests", "deliverables", "__pycache__", ".git", "docs", "live_validation_results", "control_layer_provenance"}
    callers, store_writers = [], []
    for f in repo.rglob("*.py"):
        if skip & set(f.relative_to(repo).parts):
            continue
        tree = ast.parse(f.read_text())
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and n.attr == "record_final_decision" and f.name != "capital_decision_facade.py":
                callers.append(f.relative_to(repo).as_posix())
            if isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) == "DecisionStore":
                store_writers.append(f.relative_to(repo).as_posix())
    assert callers == ["atlas_ui/service.py"], callers          # the only operational caller
    assert set(store_writers) <= {"capital_decision_facade.py"}, store_writers  # nothing else opens the ledger for writing
