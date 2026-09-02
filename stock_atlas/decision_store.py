from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime
from enum import Enum
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any
import fcntl

from .models import (
    DecisionRecord,
    FrozenInputRef,
    PortfolioAction,
    PositionClassification,
    ReviewEventType,
    VerificationStatus,
)
from .controls import ControlFailure
from .freeze import verify_frozen_ref_file

GENESIS_HASH = "0" * 64


def validate_decision_record(record: DecisionRecord) -> None:
    if not record.record_id.strip():
        raise ControlFailure("record_id is required")
    if not record.portfolio_snapshot_id.strip():
        raise ControlFailure("portfolio_snapshot_id is required")
    if not record.stage7_status.strip():
        raise ControlFailure("stage7_status is required")

    if record.review_event_type == ReviewEventType.FINAL_CAPITAL_DECISION:
        if record.human_stage8_action is None:
            raise ControlFailure("Final capital decision requires an explicit human Stage 8 action")
        if not (record.human_rationale and record.human_rationale.strip()):
            raise ControlFailure("Final capital decision requires human rationale")
        if not record.alternatives_considered:
            raise ControlFailure("Final capital decision requires alternatives_considered")
        labels = {x.strip().lower() for x in record.alternatives_considered if x.strip()}
        if not any("treasury" in x or "cash" in x for x in labels):
            raise ControlFailure("Final capital decision must preserve Treasury/Cash as an alternative considered")
        if not any("do nothing" in x for x in labels):
            raise ControlFailure("Final capital decision must preserve Do Nothing as an alternative considered")
        if record.stage7_artifact is None:
            raise ControlFailure("Final capital decision requires a retained Stage 7 artifact")

        if record.human_stage8_action in {PortfolioAction.INITIATE, PortfolioAction.ADD}:
            if record.stage7_status != "ELIGIBLE FOR STAGE 8":
                raise ControlFailure("INITIATE/ADD requires stage7_status == ELIGIBLE FOR STAGE 8")
            if not record.candidate_security_key:
                raise ControlFailure("INITIATE/ADD final decision requires candidate_security_key")
            if record.revisit_triggers is None:
                raise ControlFailure("INITIATE/ADD final decision requires revisit triggers")
            if record.constraint_state != VerificationStatus.VERIFIED:
                raise ControlFailure("INITIATE/ADD requires VERIFIED tax/liquidity/execution constraints")
            if not 1 <= len(record.dominant_drivers) <= 3 or not all(x.strip() for x in record.dominant_drivers):
                raise ControlFailure("INITIATE/ADD requires 1–3 dominant drivers")
            if record.position_classification is None:
                raise ControlFailure("INITIATE/ADD requires position_classification")
            if record.post_trade_weight is None or record.post_trade_weight <= 0:
                raise ControlFailure("INITIATE/ADD requires positive post_trade_weight")
            if record.position_classification == PositionClassification.STARTER:
                if record.starter_cap_weight is None:
                    raise ControlFailure("STARTER decision requires starter_cap_weight from investor policy")
                if record.post_trade_weight > record.starter_cap_weight + 1e-12:
                    raise ControlFailure("STARTER decision exceeds supplied STARTER cap")
    elif record.human_stage8_action is not None:
        raise ControlFailure("Non-final review records cannot contain a human portfolio action")


def _jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    return value


def canonical_payload(record: DecisionRecord, include_hash: bool = False) -> dict:
    data = _jsonable(asdict(record))
    if not include_hash:
        data.pop("record_hash", None)
    return data


def compute_record_hash(record: DecisionRecord) -> str:
    blob = json.dumps(canonical_payload(record), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def compute_entry_hash(record_payload: dict, previous_entry_hash: str) -> str:
    envelope = {"record": record_payload, "previous_entry_hash": previous_entry_hash}
    blob = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _required_input_refs(record: DecisionRecord) -> tuple[tuple[str, FrozenInputRef], ...]:
    v = record.input_versions
    return (
        ("portfolio_snapshot", v.portfolio_snapshot),
        ("scenario_model", v.scenario_model),
        ("exposure_map", v.exposure_map),
        ("evidence_set", v.evidence_set),
        ("control_contract", v.control_contract),
    )


def _verify_final_artifacts(record: DecisionRecord) -> dict:
    for label, ref in _required_input_refs(record):
        if not ref.artifact_path:
            raise ControlFailure(f"Final capital decision requires retained {label} artifact")
        if not verify_frozen_ref_file(ref):
            raise ControlFailure(f"Frozen {label} artifact is missing or hash-mismatched")
    if record.stage7_artifact is None or not record.stage7_artifact.artifact_path:
        raise ControlFailure("Final capital decision requires retained Stage 7 artifact")
    if not verify_frozen_ref_file(record.stage7_artifact):
        raise ControlFailure("Frozen Stage 7 artifact is missing or hash-mismatched")
    try:
        payload = json.loads(Path(record.stage7_artifact.artifact_path).read_text(encoding="utf-8"))
    except Exception as exc:
        raise ControlFailure("Frozen Stage 7 artifact cannot be parsed") from exc
    result = payload.get("result")
    if not isinstance(result, dict):
        raise ControlFailure("Frozen Stage 7 artifact lacks structured result")
    if result.get("status") != record.stage7_status:
        raise ControlFailure("DecisionRecord stage7_status does not match frozen Stage 7 artifact")
    if record.candidate_security_key and result.get("security_key") != record.candidate_security_key:
        raise ControlFailure("DecisionRecord candidate does not match frozen Stage 7 artifact")
    return result


def _normalize_drivers(items: list[str] | tuple[str, ...]) -> set[str]:
    return {" ".join(str(x).lower().split()) for x in items if str(x).strip()}


class DecisionStore:
    """Application-layer append-only JSONL store with file locking and hash chaining.

    This protects against accidental mutation and concurrent application writes.
    It is not a substitute for external immutable/WORM storage or an externally
    anchored digest.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    @staticmethod
    def _parse_lines(text: str) -> list[dict]:
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def _load_raw(self) -> list[dict]:
        return self._parse_lines(self.path.read_text(encoding="utf-8"))

    @staticmethod
    def _verify_rows(rows: list[dict]) -> bool:
        prev = GENESIS_HASH
        for row in rows:
            if row.get("previous_entry_hash") != prev:
                return False
            record = row.get("record", {})
            stored_record_hash = record.get("record_hash")
            if not stored_record_hash:
                return False
            record_without_hash = dict(record)
            record_without_hash.pop("record_hash", None)
            blob = json.dumps(record_without_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            if hashlib.sha256(blob.encode("utf-8")).hexdigest() != stored_record_hash:
                return False
            expected_entry = compute_entry_hash(record, prev)
            if row.get("entry_hash") != expected_entry:
                return False
            prev = row["entry_hash"]
        return True

    @staticmethod
    def _latest_open_state(rows: list[dict]) -> dict[str, dict]:
        latest: dict[str, dict] = {}
        for row in rows:
            rec = row.get("record", {})
            if rec.get("review_event_type") != ReviewEventType.FINAL_CAPITAL_DECISION.value:
                continue
            key = rec.get("candidate_security_key")
            if not key:
                continue
            action = rec.get("human_stage8_action")
            if action == PortfolioAction.EXIT.value:
                latest[key] = {**rec, "post_trade_weight": 0.0}
            elif rec.get("post_trade_weight") is not None:
                latest[key] = rec
        return latest

    @staticmethod
    def _validate_stage7_binding(record: DecisionRecord, stage7_result: dict, rows: list[dict]) -> None:
        if record.human_stage8_action not in {PortfolioAction.INITIATE, PortfolioAction.ADD}:
            return
        if stage7_result.get("status") != "ELIGIBLE FOR STAGE 8":
            raise ControlFailure("INITIATE/ADD is not bound to a passing Stage 7 result")
        if stage7_result.get("constraint_state") != VerificationStatus.VERIFIED.value:
            raise ControlFailure("INITIATE/ADD frozen Stage 7 bundle has UNVERIFIED constraints")
        pos = stage7_result.get("position")
        if not isinstance(pos, dict):
            raise ControlFailure("INITIATE/ADD frozen Stage 7 bundle lacks position proposal")
        if record.position_classification is None or pos.get("classification") != record.position_classification.value:
            raise ControlFailure("DecisionRecord position classification does not match frozen Stage 7 bundle")
        if record.post_trade_weight is None or not math.isclose(
            float(pos.get("post_trade_weight")), record.post_trade_weight, rel_tol=0.0, abs_tol=1e-9
        ):
            raise ControlFailure("DecisionRecord post-trade weight does not match frozen Stage 7 bundle")

        latest = DecisionStore._latest_open_state(rows)
        previous = latest.get(record.candidate_security_key or "")
        previous_weight = float(previous.get("post_trade_weight", 0.0)) if previous else 0.0
        current_weight = float(pos.get("current_weight", -1.0))
        if not math.isclose(current_weight, previous_weight, rel_tol=0.0, abs_tol=1e-6):
            raise ControlFailure("Stage 7 current weight does not reconcile to prior decision history")
        if record.human_stage8_action == PortfolioAction.INITIATE and previous_weight > 1e-9:
            raise ControlFailure("INITIATE cannot be used when an open position already exists; use ADD")
        if record.human_stage8_action == PortfolioAction.ADD and previous_weight <= 1e-9:
            raise ControlFailure("ADD requires an existing open position")

        new_drivers = _normalize_drivers(record.dominant_drivers)
        shared: set[str] = set()
        for key, prior in latest.items():
            if key == record.candidate_security_key or float(prior.get("post_trade_weight", 0.0) or 0.0) <= 1e-9:
                continue
            shared |= new_drivers & _normalize_drivers(prior.get("dominant_drivers") or [])
        if shared and not (record.cluster_note and record.cluster_note.strip()):
            raise ControlFailure("Shared economic drivers with an open funded position require cluster_note")

    def append(self, record: DecisionRecord) -> DecisionRecord:
        validate_decision_record(record)
        with self.path.open("a+", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                rows = self._parse_lines(f.read())
                if not self._verify_rows(rows):
                    raise ControlFailure("Existing decision history failed integrity verification; append blocked")
                existing_ids = {row.get("record", {}).get("record_id") for row in rows}
                if record.record_id in existing_ids:
                    raise ControlFailure("Decision records are append-only; duplicate record_id rejected")
                if record.prior_record_id and record.prior_record_id not in existing_ids:
                    raise ControlFailure("prior_record_id does not exist in append-only history")

                if record.review_event_type == ReviewEventType.FINAL_CAPITAL_DECISION:
                    stage7_result = _verify_final_artifacts(record)
                    self._validate_stage7_binding(record, stage7_result, rows)

                hashed = replace(record, record_hash=compute_record_hash(record))
                record_payload = canonical_payload(hashed, include_hash=True)
                previous_entry_hash = rows[-1]["entry_hash"] if rows else GENESIS_HASH
                entry_hash = compute_entry_hash(record_payload, previous_entry_hash)
                envelope = {
                    "record": record_payload,
                    "previous_entry_hash": previous_entry_hash,
                    "entry_hash": entry_hash,
                }
                f.seek(0, os.SEEK_END)
                f.write(json.dumps(envelope, sort_keys=True, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
                return hashed
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def verify_integrity(self) -> bool:
        return self._verify_rows(self._load_raw())

    def manifest_hash(self) -> str:
        """Digest of the entire current store for external anchoring/snapshotting."""
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def overwrite(self, *_args, **_kwargs):
        raise ControlFailure("Decision history is append-only; overwrite is prohibited")
