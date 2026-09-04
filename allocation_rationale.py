"""Stage 8 allocation-rationale fields — Pilot 1 Red Team closeout.

This is a **record/schema and validation enhancement only**. It adds
human-authored fields to the existing ``FINAL_CAPITAL_DECISION`` object so the
link between evidence and the human dollar split is explicit and auditable.

It is NOT an allocation engine. There is no score, no conviction metric, no
sizing formula, no ranking layer, no optimizer, no probability model, and no
automated recommendation. Nothing here computes, modifies, recommends or
validates a dollar amount. Human allocation authority is unchanged.

Architecture note
-----------------
``AllocationDecisionRecord`` **subclasses** the control layer's
``DecisionRecord`` rather than modifying it. That matters: ``stock_atlas/``
is byte-identical to the Red-Team-accepted archive and stays that way.
Because ``canonical_payload`` serialises with ``asdict()`` and
``DecisionStore.append`` re-hashes with ``dataclasses.replace()``, the added
fields are carried into the record hash and the append-only ledger with no
change to the frozen control layer.

The three funded-line questions
-------------------------------
``why_this_vs_alternatives``  Why own this instead of the live alternatives?
``why_this_size``             Why approximately this position size?
``allocation_wrong_if``       What observable evidence would make this wrong?

All three are **human-written**. Atlas must never generate them, and never
backfills them after the fact. A funded paper line missing any of them is
preserved and marked ``EXPLORATORY_LOW_RATIONALE`` — the decision is kept, the
gap is recorded honestly rather than papered over.

Capital status: NO REAL PORTFOLIO ACTION.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from stock_atlas.decision_store import ControlFailure
from stock_atlas.models import DecisionRecord, PortfolioAction

__all__ = [
    "AllocationRationaleStatus",
    "AllocationDecisionRecord",
    "FUNDING_ACTIONS",
    "RATIONALE_FIELDS",
    "derive_allocation_rationale_status",
    "missing_rationale_fields",
    "assert_live_capital_decision_ready",
]

#: Actions that move capital. Only these require the three rationale fields.
FUNDING_ACTIONS = frozenset({PortfolioAction.INITIATE, PortfolioAction.ADD})

#: The three human-authored funded-line questions, in record order.
RATIONALE_FIELDS = (
    "why_this_vs_alternatives",
    "why_this_size",
    "allocation_wrong_if",
)


class AllocationRationaleStatus(str, Enum):
    """Completeness of the human allocation rationale on a funded line.

    This is a statement about *what the human wrote*, not a quality judgement
    and not a score. Neither value ranks a decision against another.
    """

    RATIONALE_COMPLETE = "RATIONALE_COMPLETE"
    EXPLORATORY_LOW_RATIONALE = "EXPLORATORY_LOW_RATIONALE"


@dataclass(frozen=True)
class AllocationDecisionRecord(DecisionRecord):
    """A ``FINAL_CAPITAL_DECISION`` carrying Stage 8 allocation rationale.

    Every field below is human-authored text or a status derived purely from
    whether that text is present. None of them influences the dollar amount,
    the position weight, or any Stage 7 output.

    ``why_not_this_increment`` belongs to a finalist that reached the final
    Stage 8 opportunity set and received no incremental capital. It is **not**
    a rejection classification: the finalist remains eligible, and no ranking
    may be inferred from it.
    """

    why_this_vs_alternatives: Optional[str] = None
    why_this_size: Optional[str] = None
    allocation_wrong_if: Optional[str] = None
    allocation_rationale_status: Optional[AllocationRationaleStatus] = None
    why_not_this_increment: Optional[str] = None


def _present(value: Optional[str]) -> bool:
    """A field counts as supplied only when it holds non-blank human text."""
    return bool(value is not None and str(value).strip())


def missing_rationale_fields(
    why_this_vs_alternatives: Optional[str] = None,
    why_this_size: Optional[str] = None,
    allocation_wrong_if: Optional[str] = None,
) -> tuple[str, ...]:
    """Names of the three funded-line fields that were not supplied.

    Reports absence. It never fills, suggests, or infers the missing text.
    """
    supplied = {
        "why_this_vs_alternatives": why_this_vs_alternatives,
        "why_this_size": why_this_size,
        "allocation_wrong_if": allocation_wrong_if,
    }
    return tuple(name for name in RATIONALE_FIELDS if not _present(supplied[name]))


def derive_allocation_rationale_status(
    human_stage8_action: Optional[PortfolioAction],
    why_this_vs_alternatives: Optional[str] = None,
    why_this_size: Optional[str] = None,
    allocation_wrong_if: Optional[str] = None,
) -> Optional[AllocationRationaleStatus]:
    """Status for a line, derived only from which fields the human supplied.

    Funded lines (``INITIATE``/``ADD``) with all three fields are
    ``RATIONALE_COMPLETE``; funded lines missing any are
    ``EXPLORATORY_LOW_RATIONALE`` — preserved, not rejected, never backfilled.

    Non-funded lines return ``None``: the three questions are about deploying
    capital, so they do not apply where no capital moved. Returning ``None``
    rather than a status keeps ``HOLD CASH`` and ``DO NOTHING`` from being
    scored against funded decisions.
    """
    if human_stage8_action not in FUNDING_ACTIONS:
        return None
    missing = missing_rationale_fields(
        why_this_vs_alternatives, why_this_size, allocation_wrong_if
    )
    return (
        AllocationRationaleStatus.EXPLORATORY_LOW_RATIONALE
        if missing
        else AllocationRationaleStatus.RATIONALE_COMPLETE
    )


def assert_live_capital_decision_ready(record: DecisionRecord) -> None:
    """Gate for a FUTURE controlled live-capital pilot. Fail closed.

    Paper and shadow decisions are deliberately NOT subject to this: an
    exploratory funded line is preserved with ``EXPLORATORY_LOW_RATIONALE``.
    Only when real capital is at stake must all three rationale fields be
    present before a funded ``INITIATE``/``ADD`` counts as decision-ready.

    This does not authorise live capital and moves no money. It is the check a
    live-capital path would have to call.
    """
    action = getattr(record, "human_stage8_action", None)
    if action not in FUNDING_ACTIONS:
        return
    missing = missing_rationale_fields(
        getattr(record, "why_this_vs_alternatives", None),
        getattr(record, "why_this_size", None),
        getattr(record, "allocation_wrong_if", None),
    )
    if missing:
        raise ControlFailure(
            "Live-capital funded decision is not decision-ready; missing "
            f"human allocation rationale: {', '.join(missing)}. "
            "This text must be written by the investor and is never generated."
        )
    status = getattr(record, "allocation_rationale_status", None)
    if status != AllocationRationaleStatus.RATIONALE_COMPLETE:
        raise ControlFailure(
            "Live-capital funded decision requires allocation_rationale_status "
            f"RATIONALE_COMPLETE; record says {status!r}"
        )
