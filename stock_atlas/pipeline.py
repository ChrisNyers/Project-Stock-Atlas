from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Sequence

from .controls import evaluate_stage7_candidate, validate_stage7_language
from .freeze import freeze_payload
from .models import (
    AlternativeType,
    CandidateUnderwriting,
    ComparisonAlternative,
    FrozenInputRef,
    PortfolioSnapshot,
    PositionProposal,
    Stage7CandidateResult,
)
from .presentation import render_stage7_result


@dataclass(frozen=True)
class Stage7Run:
    """Canonical Stage 7 output plus a hashable/freezeable comparison bundle."""

    result: Stage7CandidateResult
    rendered_text: str
    artifact_ref: FrozenInputRef


def run_stage7_pipeline(
    underwriting: CandidateUnderwriting,
    portfolio: PortfolioSnapshot,
    position: PositionProposal | None,
    alternatives: Sequence[ComparisonAlternative],
    decision_time: datetime,
    *,
    human_accepts_unverified_constraints: bool = False,
    known_latest_session_date: date | None = None,
    max_reference_age_hours: float = 96.0,
    artifact_destination: str | Path | None = None,
) -> Stage7Run:
    """Authoritative Stage 7 path for the control layer.

    This function deliberately stops before any PortfolioAction is created. The
    returned bundle is hashed every time. For any final capital DecisionRecord,
    a retained artifact_destination is required so persistence can prove Stage 7
    actually ran and can re-verify the exact comparison state.
    """
    result = evaluate_stage7_candidate(
        underwriting,
        portfolio,
        position,
        alternatives,
        decision_time,
        human_accepts_unverified_constraints=human_accepts_unverified_constraints,
        known_latest_session_date=known_latest_session_date,
        max_reference_age_hours=max_reference_age_hours,
    )
    rendered = render_stage7_result(result)
    validate_stage7_language(rendered)
    treasury = next((a.market_reference for a in alternatives
                     if a.alternative_type == AlternativeType.TREASURY_CASH and a.market_reference is not None), None)
    bundle = {
        "decision_time": decision_time,
        "result": result,
        "rendered_text": rendered,
        # Frozen pricing basis (FROZEN_CONTROL_CHANGE_001): lets a later funded Stage 8 prove it is still
        # looking at the same price/reference evidence. Inside the hashed artifact the ledger already binds.
        "price_basis": {
            "price_snapshot": underwriting.price_snapshot,
            "treasury_reference": treasury,
            "known_latest_session_date": known_latest_session_date,
        },
    }
    artifact_ref = freeze_payload(bundle, version="stage7-control-v0.2", destination=artifact_destination)
    return Stage7Run(result=result, rendered_text=rendered, artifact_ref=artifact_ref)
