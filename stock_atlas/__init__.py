"""Stock Atlas validated control layer.

The package root deliberately exposes only the canonical comparison pipeline,
append-only decision persistence, and ControlFailure. Lower-level models and
helpers remain available from their explicit modules for tests/integration work,
but are not advertised as application entry points.
"""

from .controls import ControlFailure
from .decision_store import DecisionStore
from .pipeline import Stage7Run, run_stage7_pipeline

__all__ = ["ControlFailure", "DecisionStore", "Stage7Run", "run_stage7_pipeline"]
__version__ = "0.2.0"
