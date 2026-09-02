from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .models import FrozenInputRef
from .controls import ControlFailure


def _jsonable(v: Any):
    if is_dataclass(v):
        return _jsonable(asdict(v))
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, dict):
        return {str(k): _jsonable(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, float) and not math.isfinite(v):
        raise ControlFailure("Frozen payload contains non-finite numeric value")
    return v


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def freeze_payload(payload: Any, *, version: str, destination: str | Path | None = None) -> FrozenInputRef:
    data = canonical_json_bytes(payload)
    digest = hashlib.sha256(data).hexdigest()
    if destination is not None:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("xb") as f:
                f.write(data)
                f.flush()
        except FileExistsError:
            existing = path.read_bytes()
            if existing != data:
                raise ControlFailure("Frozen input path already exists with different content")
    return FrozenInputRef(version=version, sha256=digest, artifact_path=str(path) if destination is not None else None)


def verify_frozen_payload(payload: Any, ref: FrozenInputRef) -> bool:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest() == ref.sha256


def verify_frozen_ref_file(ref: FrozenInputRef) -> bool:
    """Verify that a retained frozen artifact exists and still matches its hash."""
    if not ref.artifact_path:
        return False
    path = Path(ref.artifact_path)
    if not path.is_file():
        return False
    return hashlib.sha256(path.read_bytes()).hexdigest() == ref.sha256
