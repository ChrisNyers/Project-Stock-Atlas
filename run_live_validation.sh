#!/bin/bash

################################################################################
# Stock Atlas Sprint 1 — Run Live SEC Validation
#
# This script executes the live SEC validation harness and saves results.
#
# Usage:
#   ./run_live_validation.sh
#
# Output:
#   live_validation_results/
#     - TIMESTAMP_validation_results.txt
################################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Stock Atlas Sprint 1 — Live SEC Validation                ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# ============================================================================
# 1. VERIFY ENVIRONMENT
# ============================================================================

echo ""
echo "Verifying environment..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "✗ ERROR: Virtual environment not activated"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup_live.sh"
    echo ""
    echo "Then activate the virtual environment:"
    echo "  source venv/bin/activate"
    exit 1
fi

echo "✓ Virtual environment activated: $VIRTUAL_ENV"

# Check .env
if [ ! -f ".env" ]; then
    echo "✗ ERROR: .env not found"
    exit 1
fi

echo "✓ Configuration found (.env)"

# Check SEC_USER_AGENT is set
SEC_USER_AGENT=$(grep "^SEC_USER_AGENT=" .env | cut -d'=' -f2 | tr -d '"')
if [ -z "$SEC_USER_AGENT" ]; then
    echo "✗ ERROR: SEC_USER_AGENT not configured in .env"
    echo "   Please set SEC_USER_AGENT in .env before running"
    exit 1
fi

echo "✓ SEC_USER_AGENT configured"

# Check validation harness
if [ ! -f "validation_harness_live.py" ]; then
    echo "✗ ERROR: validation_harness_live.py not found"
    exit 1
fi

echo "✓ Validation harness found"

# ============================================================================
# 2. CREATE RESULTS DIRECTORY
# ============================================================================

echo ""
echo "Preparing results directory..."

mkdir -p live_validation_results

echo "✓ Results directory ready: live_validation_results/"

# ============================================================================
# 3. RUN VALIDATION HARNESS
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║            LIVE SEC VALIDATION STARTING                       ║"
echo "║            Connecting to SEC EDGAR...                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""

# Run the validation harness
python3 validation_harness_live.py

VALIDATION_EXIT_CODE=$?

# ============================================================================
# 4. RESULTS SUMMARY
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    VALIDATION COMPLETE                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "Results saved to: live_validation_results/"
echo ""
echo "View results:"
echo "  ls -la live_validation_results/"
echo ""

if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests completed successfully"
else
    echo "⚠ Some tests did not pass (exit code: $VALIDATION_EXIT_CODE)"
fi

echo ""

exit $VALIDATION_EXIT_CODE
