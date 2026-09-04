"""Pilot 1 Red Team closeout — Stage 8 allocation-rationale fields.

Acceptance tests A–H from the closeout work package. These prove the change is
a record/schema and validation enhancement and nothing more: no allocation
score, conviction score, sizing formula, optimizer, ranking layer, automated
recommendation, probability engine, or second capital-allocation model.

Human allocation authority is unchanged, and the historical Pilot 1 decision is
preserved without backfilled language.

Capital status: NO REAL PORTFOLIO ACTION. Every value here is a fixture.
"""

from __future__ import annotations

import inspect
from datetime import timedelta

import pytest

import allocation_rationale as ar
from allocation_rationale import (
    AllocationDecisionRecord,
    AllocationRationaleStatus,
    assert_live_capital_decision_ready,
    derive_allocation_rationale_status,
    missing_rationale_fields,
)
from capital_decision_facade import ControlFailure
from stock_atlas.models import PortfolioAction, RevisitTriggers

# Reuse the proven integration fixtures rather than re-deriving them.
from test_integration_facade import (  # noqa: E402
    NOW,
    _eligible_run,
    _facade,
    _input_versions,
)

COMPLETE = dict(
    why_this_vs_alternatives="Own versus SPY/Treasury because the modeled return "
    "opportunity remains attractive after considering the identified uncertainty.",
    why_this_size="Controlled core exposure: larger than an exploratory position but "
    "capped to prevent one security from dominating the incremental allocation.",
    allocation_wrong_if="Material spending fails to translate into operating growth, "
    "earnings, or stronger per-share economics.",
)


def _fund(facade, run, record_id, **kwargs):
    """Persist a funded INITIATE line through the single authorized path."""
    return facade.record_final_decision(
        run,
        record_id=record_id,
        human_stage8_action="INITIATE",
        human_rationale="Human accepted the comparison and funded a starter increment.",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(facade.artifact_dir.parent),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
        dominant_drivers=("enterprise IT",),
        revisit_triggers=RevisitTriggers("±25% price", NOW + timedelta(days=90)),
        starter_cap_weight=0.10,
        **kwargs,
    )


# ===========================================================================
# A. Complete funded line
# ===========================================================================


def test_a_funded_line_with_all_three_fields_is_rationale_complete(tmp_path):
    facade = _facade(tmp_path)
    record = _fund(facade, _eligible_run(facade), "ALLOC-COMPLETE-1", **COMPLETE)
    assert record.human_stage8_action is PortfolioAction.INITIATE
    assert record.allocation_rationale_status is AllocationRationaleStatus.RATIONALE_COMPLETE
    assert record.why_this_vs_alternatives == COMPLETE["why_this_vs_alternatives"]
    assert record.why_this_size == COMPLETE["why_this_size"]
    assert record.allocation_wrong_if == COMPLETE["allocation_wrong_if"]
    assert facade.verify_ledger()


def test_a_add_action_is_also_a_funded_line():
    """ADD moves capital too, so it carries the same requirement as INITIATE."""
    assert (
        derive_allocation_rationale_status(PortfolioAction.ADD, **COMPLETE)
        is AllocationRationaleStatus.RATIONALE_COMPLETE
    )


def test_a_rationale_fields_persist_into_the_ledger_and_record_hash(tmp_path):
    """The new fields are really written and really hashed, not dropped."""
    facade = _facade(tmp_path)
    record = _fund(facade, _eligible_run(facade), "ALLOC-PERSIST-1", **COMPLETE)
    text = facade.store.path.read_text()
    assert "why_this_vs_alternatives" in text
    assert "RATIONALE_COMPLETE" in text
    assert record.record_hash and len(record.record_hash) == 64
    assert facade.verify_ledger()


# ===========================================================================
# B. Paper funded line with missing rationale
# ===========================================================================


@pytest.mark.parametrize("omit", list(ar.RATIONALE_FIELDS))
def test_b_funded_paper_line_missing_any_field_is_preserved_and_flagged(tmp_path, omit):
    """The decision persists; the gap is recorded, not rejected."""
    facade = _facade(tmp_path)
    fields = {k: v for k, v in COMPLETE.items() if k != omit}
    record = _fund(facade, _eligible_run(facade), f"ALLOC-LOW-{omit}", **fields)
    assert record.allocation_rationale_status is AllocationRationaleStatus.EXPLORATORY_LOW_RATIONALE
    assert getattr(record, omit) is None
    assert facade.verify_ledger()  # persisted, not discarded


def test_b_funded_line_with_no_rationale_at_all_is_preserved(tmp_path):
    """Pilot 1's historical shape: funded, no rationale, still a valid record."""
    facade = _facade(tmp_path)
    record = _fund(facade, _eligible_run(facade), "ALLOC-LOW-NONE")
    assert record.allocation_rationale_status is AllocationRationaleStatus.EXPLORATORY_LOW_RATIONALE
    assert record.why_this_vs_alternatives is None
    assert record.why_this_size is None
    assert record.allocation_wrong_if is None
    assert facade.verify_ledger()


def test_b_blank_and_whitespace_text_does_not_count_as_supplied():
    """An empty string is not a rationale."""
    for blank in ("", "   ", "\n\t"):
        assert (
            derive_allocation_rationale_status(
                PortfolioAction.INITIATE,
                why_this_vs_alternatives=blank,
                why_this_size=blank,
                allocation_wrong_if=blank,
            )
            is AllocationRationaleStatus.EXPLORATORY_LOW_RATIONALE
        )


def test_b_missing_fields_are_named_exactly():
    assert missing_rationale_fields() == ar.RATIONALE_FIELDS
    assert missing_rationale_fields(**COMPLETE) == ()
    assert missing_rationale_fields(why_this_size="sized as ballast") == (
        "why_this_vs_alternatives",
        "allocation_wrong_if",
    )


# ===========================================================================
# C. No synthetic rationale
# ===========================================================================


def test_c_missing_rationale_is_never_generated_or_backfilled(tmp_path):
    """A historical decision with no rationale keeps None — no invented language."""
    facade = _facade(tmp_path)
    record = _fund(facade, _eligible_run(facade), "ALLOC-NOBACKFILL-1")
    for field in ar.RATIONALE_FIELDS:
        assert getattr(record, field) is None
    # And nothing resembling generated prose reached the ledger.
    import json

    row = json.loads(facade.store.path.read_text().splitlines()[0])
    for field in ar.RATIONALE_FIELDS:
        assert row["record"][field] is None


def test_c_status_derivation_returns_only_a_status_never_text():
    """The derivation reports presence; it cannot emit rationale content."""
    status = derive_allocation_rationale_status(PortfolioAction.INITIATE)
    assert isinstance(status, AllocationRationaleStatus)
    assert status is AllocationRationaleStatus.EXPLORATORY_LOW_RATIONALE


def test_c_module_exposes_no_text_generator():
    """No callable in the module produces rationale language."""
    banned = ("generate", "suggest", "autofill", "backfill", "infer", "compose", "draft")
    for name, obj in vars(ar).items():
        if callable(obj) and not name.startswith("_"):
            assert not any(b in name.lower() for b in banned), name


# ===========================================================================
# D. Unfunded finalist
# ===========================================================================


def test_d_unfunded_finalist_records_why_not_this_increment(tmp_path):
    """A $0 finalist can explain itself without being classified as rejected."""
    facade = _facade(tmp_path)
    record = facade.record_final_decision(
        _eligible_run(facade),
        record_id="ALLOC-UNFUNDED-1",
        human_stage8_action="DO NOTHING",
        human_rationale="Preferred other finalists for this increment.",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(tmp_path),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
        why_not_this_increment="Preferred Tencent and VEON for this increment; HBR remains eligible.",
    )
    assert record.why_not_this_increment
    assert "remains eligible" in record.why_not_this_increment
    assert facade.verify_ledger()


def test_d_unfunded_finalist_is_not_classified_as_rejected(tmp_path):
    """No automatic REJECTED state exists anywhere for an unfunded finalist."""
    facade = _facade(tmp_path)
    record = facade.record_final_decision(
        _eligible_run(facade),
        record_id="ALLOC-UNFUNDED-2",
        human_stage8_action="DO NOTHING",
        human_rationale="No incremental capital this round.",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(tmp_path),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
        why_not_this_increment="Preferred alternatives for this increment.",
    )
    assert "REJECT" not in facade.store.path.read_text().upper()
    # Unfunded lines carry no rationale status at all — nothing to rank.
    assert record.allocation_rationale_status is None


def test_d_no_rejection_vocabulary_in_the_schema():
    assert not any("reject" in n.lower() for n in vars(ar))
    assert not any("reject" in v.value.lower() for v in AllocationRationaleStatus)


def test_d_no_ranking_can_be_inferred_from_the_status():
    """The two statuses are labels, not an ordering."""
    assert not hasattr(AllocationRationaleStatus, "__lt__") or not isinstance(
        AllocationRationaleStatus.RATIONALE_COMPLETE, (int, float)
    )
    values = {s.value for s in AllocationRationaleStatus}
    assert values == {"RATIONALE_COMPLETE", "EXPLORATORY_LOW_RATIONALE"}


# ===========================================================================
# E. No sizing engine
# ===========================================================================


def test_e_rationale_fields_do_not_compute_or_alter_the_allocation(tmp_path):
    """Same Stage 7 run, opposite rationale completeness, identical position."""
    fa, fb = _facade(tmp_path / "a"), _facade(tmp_path / "b")
    with_text = _fund(fa, _eligible_run(fa), "ALLOC-SIZE-A", **COMPLETE)
    without = _fund(fb, _eligible_run(fb), "ALLOC-SIZE-B")
    assert with_text.post_trade_weight == without.post_trade_weight
    assert with_text.position_classification == without.position_classification
    assert with_text.starter_cap_weight == without.starter_cap_weight


def test_e_module_computes_no_dollar_or_weight_value():
    """No function in the module returns a number that could size a position."""
    for name, obj in vars(ar).items():
        if not callable(obj) or name.startswith("_") or isinstance(obj, type):
            continue
        sig = inspect.signature(obj)
        for param in sig.parameters.values():
            assert "weight" not in param.name.lower(), f"{name}.{param.name}"
            assert "dollar" not in param.name.lower(), f"{name}.{param.name}"
            assert "amount" not in param.name.lower(), f"{name}.{param.name}"


def test_e_no_scoring_or_optimizer_surface():
    banned = ("score", "rank", "optimi", "sentiment", "probabilit", "recommend", "size_position")
    for name in vars(ar):
        assert not any(b in name.lower() for b in banned), name


# ===========================================================================
# F. Human authority
# ===========================================================================


def test_f_changing_rationale_text_cannot_change_capital_amounts(tmp_path):
    """Rewriting the text leaves every capital field untouched."""
    fa, fb = _facade(tmp_path / "a"), _facade(tmp_path / "b")
    base = _fund(fa, _eligible_run(fa), "ALLOC-AUTH-1", **COMPLETE)
    edited = dict(COMPLETE, why_this_size="Completely different sizing narrative.")
    other = _fund(fb, _eligible_run(fb), "ALLOC-AUTH-2", **edited)
    assert other.why_this_size != base.why_this_size
    assert other.post_trade_weight == base.post_trade_weight
    assert other.starter_cap_weight == base.starter_cap_weight
    assert other.position_classification == base.position_classification


def test_f_ledger_remains_append_only_and_records_are_immutable(tmp_path):
    """Rationale is captured at decision time; history cannot be rewritten."""
    facade = _facade(tmp_path)
    _fund(facade, _eligible_run(facade), "ALLOC-IMMUT-1", **COMPLETE)
    with pytest.raises(ControlFailure, match="append-only"):
        facade.store.overwrite()
    with pytest.raises(ControlFailure, match="duplicate record_id"):
        _fund(facade, _eligible_run(facade), "ALLOC-IMMUT-1", **COMPLETE)


def test_f_live_capital_gate_blocks_incomplete_but_paper_is_untouched(tmp_path):
    """The future live gate is strict; paper decisions stay preserved."""
    fa, fb = _facade(tmp_path / "a"), _facade(tmp_path / "b")
    low = _fund(fa, _eligible_run(fa), "ALLOC-LIVEGATE-1")
    assert low.allocation_rationale_status is AllocationRationaleStatus.EXPLORATORY_LOW_RATIONALE
    with pytest.raises(ControlFailure, match="not decision-ready"):
        assert_live_capital_decision_ready(low)

    complete = _fund(fb, _eligible_run(fb), "ALLOC-LIVEGATE-2", **COMPLETE)
    assert_live_capital_decision_ready(complete)  # does not raise


def test_f_live_capital_gate_ignores_non_funded_actions(tmp_path):
    """HOLD CASH / DO NOTHING are never gated on funded-line rationale."""
    facade = _facade(tmp_path)
    record = facade.record_final_decision(
        _eligible_run(facade),
        record_id="ALLOC-LIVEGATE-3",
        human_stage8_action="HOLD CASH",
        human_rationale="Refusal remains legal after an ELIGIBLE comparison.",
        alternatives_considered=("ELIG", "SPY", "Treasury/Cash", "Do Nothing"),
        input_versions=_input_versions(tmp_path),
        created_at=NOW,
        portfolio_snapshot_id="INTEGRATION",
    )
    assert_live_capital_decision_ready(record)  # not applicable, does not raise


# ===========================================================================
# G. Existing Stage 7 behavior unchanged
# ===========================================================================


def test_g_stage7_emits_no_portfolio_action_and_no_ranking(tmp_path):
    facade = _facade(tmp_path)
    run = _eligible_run(facade)
    assert not hasattr(run.result, "human_stage8_action")
    assert not hasattr(run.result, "rank")
    assert not hasattr(run.result, "score")
    assert "NO PORTFOLIO ACTION" in run.result.comparison_header


def test_g_stage7_does_not_see_allocation_rationale(tmp_path):
    """Rationale is a Stage 8 artifact; Stage 7 has no such parameter."""
    facade = _facade(tmp_path)
    params = inspect.signature(facade.run_stage7).parameters
    for field in ar.RATIONALE_FIELDS + ("why_not_this_increment",):
        assert field not in params


def test_g_control_layer_record_is_untouched_by_the_subclass():
    """AllocationDecisionRecord extends the accepted record; it replaces nothing."""
    from stock_atlas.models import DecisionRecord

    assert issubclass(AllocationDecisionRecord, DecisionRecord)
    for field in ar.RATIONALE_FIELDS:
        assert field not in DecisionRecord.__dataclass_fields__
        assert field in AllocationDecisionRecord.__dataclass_fields__


# ===========================================================================
# H. Fresh-price control unchanged
# ===========================================================================


def test_h_fresh_price_checkpoint_still_blocks_a_stale_snapshot(tmp_path):
    """The rationale change does not touch price freshness enforcement."""
    from dataclasses import replace as dc_replace
    from datetime import date, timezone

    from stock_atlas.controls import validate_price_snapshot
    from stock_atlas.models import FreshnessStatus

    from test_integration_facade import _price, _underwriting
    from stock_atlas.models import ReturnBand

    uw = _underwriting("SEC:ELIG", "ELIG", rb=ReturnBand(0.12, 0.18))
    stale = dc_replace(uw.price_snapshot, freshness_status=FreshnessStatus.STALE)
    with pytest.raises(ControlFailure, match="STALE"):
        validate_price_snapshot(dc_replace(uw, price_snapshot=stale), NOW)


def test_h_attested_session_binding_still_enforced():
    """The Gate B calendar attestation path is unaffected."""
    from dataclasses import replace as dc_replace
    from datetime import date

    from stock_atlas.controls import validate_price_snapshot
    from stock_atlas.models import ReturnBand

    from test_integration_facade import _underwriting

    uw = _underwriting("SEC:ELIG", "ELIG", rb=ReturnBand(0.12, 0.18))
    with pytest.raises(ControlFailure, match="attested latest trading session"):
        validate_price_snapshot(uw, NOW, known_latest_session_date=date(2026, 9, 2))


# ===========================================================================
# Pilot 1 historical decision — schema behaviour, no backfilled language
# ===========================================================================

#: The September 3, 2026 paper allocation, exactly as recorded. $50,000 total.
PILOT1_SEPT3_ALLOCATION = (
    ("Tencent", 25_000, "INITIATE"),
    ("VEON", 10_000, "INITIATE"),
    ("SPY", 10_000, "INITIATE"),
    ("1-Year Treasury", 5_000, "INITIATE"),
    ("HBR", 0, "DO NOTHING"),
    ("CRM", 0, "DO NOTHING"),
)


def test_pilot1_sept3_allocation_totals_fifty_thousand():
    assert sum(amount for _, amount, _ in PILOT1_SEPT3_ALLOCATION) == 50_000


def test_pilot1_funded_lines_are_exploratory_low_rationale():
    """Chris supplied 'Taking a stab in the dark' and MEDIUM confidence only.

    No security-specific rationale existed, so every funded line must land on
    EXPLORATORY_LOW_RATIONALE — preserved, never backfilled.
    """
    for name, amount, action in PILOT1_SEPT3_ALLOCATION:
        if amount <= 0:
            continue
        status = derive_allocation_rationale_status(PortfolioAction(action))
        assert status is AllocationRationaleStatus.EXPLORATORY_LOW_RATIONALE, name


def test_pilot1_unfunded_finalists_are_not_rejected():
    """HBR and CRM received no capital and remain eligible."""
    unfunded = [n for n, amt, _ in PILOT1_SEPT3_ALLOCATION if amt == 0]
    assert unfunded == ["HBR", "CRM"]
    for name in unfunded:
        assert derive_allocation_rationale_status(PortfolioAction.DO_NOTHING) is None


def test_pilot1_worked_example_is_fixture_text_not_historical_rationale():
    """The Tencent example is documentation only and must not be attributed."""
    assert "stab in the dark" not in COMPLETE["why_this_vs_alternatives"]
    assert derive_allocation_rationale_status(
        PortfolioAction.INITIATE, **COMPLETE
    ) is AllocationRationaleStatus.RATIONALE_COMPLETE
