#!/bin/bash

################################################################################
# Stock Atlas Sprint 1 — Run Live SEC Validation
#
# Executes the ACTIVE live SEC validation harness (v3) and saves results.
#
#   Active harness:   validation_harness_live_v3.py
#   Predecessors:     validation_harness_live.py    (v1, historical)
#                     validation_harness_live_v2.py (v2, historical)
#   v1/v2 are retained for audit/history only and are NOT run by this script.
#
# Usage:
#   ./run_live_validation.sh
#
# Output (written by the harness):
#   live_validation_results/<UTC-timestamp>_gate_results.json   (machine-readable)
#   live_validation_results/<UTC-timestamp>_gate_results.md     (human-readable)
################################################################################

set -u

VENV_DIR=".venv"
HARNESS="validation_harness_live_v3.py"
PY="$VENV_DIR/bin/python"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Stock Atlas Sprint 1 — Live SEC Validation (v3)           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Verifying environment..."

# --- Python / venv -----------------------------------------------------------
if [ ! -x "$PY" ]; then
    echo "✗ ERROR: $PY not found. Run ./setup_live.sh first."
    exit 1
fi

PY_VER=$("$PY" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')
case "$PY_VER" in
    3.11.*) echo "✓ Python $PY_VER ($VENV_DIR)" ;;
    *) echo "✗ ERROR: baseline requires Python 3.11, $VENV_DIR is $PY_VER. Re-run ./setup_live.sh." ; exit 1 ;;
esac

# --- .env -------------------------------------------------------------------
if [ ! -f ".env" ]; then
    echo "✗ ERROR: .env not found"
    exit 1
fi
echo "✓ Configuration found (.env)"

SEC_UA=$(grep "^SEC_USER_AGENT=" .env | cut -d'=' -f2- | tr -d '"')
if [ -z "$SEC_UA" ]; then
    echo "✗ ERROR: SEC_USER_AGENT not configured in .env"
    exit 1
fi
echo "✓ SEC_USER_AGENT configured"

# --- harness ---------------------------------------------------------------
if [ ! -f "$HARNESS" ]; then
    echo "✗ ERROR: $HARNESS not found"
    exit 1
fi
echo "✓ Active harness: $HARNESS"

mkdir -p live_validation_results

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║            LIVE SEC VALIDATION STARTING                       ║"
echo "║            Connecting to SEC EDGAR...                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Do not let a nonzero harness exit abort before we print the summary.
set +e
"$PY" "$HARNESS"
VALIDATION_EXIT_CODE=$?
set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    VALIDATION COMPLETE                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Result artifacts:"
ls -1t live_validation_results/*_gate_results.* 2>/dev/null | head -4 || echo "  (none written — check harness output above)"
echo ""

if [ "$VALIDATION_EXIT_CODE" -eq 0 ]; then
    echo "✓ Harness completed; all gates PASS or acceptably BLOCKED."
else
    echo "⚠ Harness completed with non-PASS gates (exit code: $VALIDATION_EXIT_CODE)."
    echo "  See the .md artifact for the per-gate breakdown."
fi
echo ""

exit $VALIDATION_EXIT_CODE
