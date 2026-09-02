from __future__ import annotations

from .controls import STAGE7_HEADER, validate_stage7_language
from .models import Stage7CandidateResult


def render_stage7_result(result: Stage7CandidateResult) -> str:
    reasons = "; ".join(result.reasons) if result.reasons else "none stated"
    overlap = result.overlap_status.value if result.overlap_status is not None else "NOT APPLICABLE / NOT PRESENT"
    text = (
        f"{STAGE7_HEADER}\n"
        f"Security: {result.ticker} ({result.security_key})\n"
        f"Treatment: {result.status}\n"
        f"Constraint verification: {result.constraint_state.value}\n"
        f"ETF overlap status: {overlap}\n"
        f"Reasons: {reasons}\n"
        "Action status: HUMAN STAGE 8 ONLY.\n"
        "No portfolio action is authorized by this comparison.\n"
        "Treasury/Cash and Do Nothing remain live alternatives."
    )
    validate_stage7_language(text)
    return text
