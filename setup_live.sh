#!/bin/bash

################################################################################
# Stock Atlas Sprint 1 — Live Validation Setup
#
# Prepares the Stock Atlas environment for live SEC validation.
# Run this once before running `run_live_validation.sh`.
#
# Usage:
#   ./setup_live.sh
#
# Baseline (Phase 4A.5.0) standard:
#   - Python 3.11 (required)
#   - Virtual environment lives in ./.venv  (NOT ./venv)
#   - Dependencies pinned in requirements.txt (do not float versions)
################################################################################

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Stock Atlas Sprint 1 — Live Validation Setup              ║"
echo "╚════════════════════════════════════════════════════════════════╝"

VENV_DIR=".venv"

# ============================================================================
# 1. LOCATE PYTHON 3.11
# ============================================================================

echo ""
echo "Locating Python 3.11..."

PYTHON_BIN=""
for candidate in python3.11 python3; do
    if command -v "$candidate" &> /dev/null; then
        ver=$("$candidate" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "")
        if [ "$ver" = "3.11" ]; then
            PYTHON_BIN=$(command -v "$candidate")
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "✗ FATAL: Python 3.11 not found."
    echo "  This baseline standardizes on Python 3.11. Install it and retry."
    echo "  (e.g. 'uv python install 3.11' or 'brew install python@3.11')"
    exit 1
fi

echo "✓ Using: $PYTHON_BIN ($($PYTHON_BIN --version))"

# ============================================================================
# 2. CREATE VIRTUAL ENVIRONMENT (.venv)
# ============================================================================

echo ""
echo "Setting up virtual environment in $VENV_DIR ..."

if [ -d "$VENV_DIR" ]; then
    existing_ver=$("$VENV_DIR/bin/python" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "")
    if [ "$existing_ver" = "3.11" ]; then
        echo "  Existing $VENV_DIR (Python $existing_ver) — reusing."
    else
        echo "  Existing $VENV_DIR is Python '$existing_ver', not 3.11 — recreating."
        rm -rf "$VENV_DIR"
        "$PYTHON_BIN" -m venv "$VENV_DIR"
    fi
else
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
fi

PY="$VENV_DIR/bin/python"

# ============================================================================
# 3. UPGRADE PIP
# ============================================================================

echo ""
echo "Upgrading pip..."
"$PY" -m pip install --upgrade pip > /dev/null 2>&1 || true
echo "✓ pip ready"

# ============================================================================
# 4. INSTALL REQUIREMENTS (pinned)
# ============================================================================

echo ""
echo "Installing dependencies from requirements.txt..."

if [ ! -f "requirements.txt" ]; then
    echo "✗ ERROR: requirements.txt not found (run from the project directory)"
    exit 1
fi

"$PY" -m pip install -r requirements.txt
echo "✓ All dependencies installed"

"$PY" -m pip check || echo "  ⚠ pip reported dependency warnings (see above)"

# ============================================================================
# 5. CREATE DIRECTORIES
# ============================================================================

echo ""
echo "Setting up directories..."
mkdir -p live_validation_results
echo "✓ Directory: live_validation_results/"

# ============================================================================
# 6. CHECK CONFIGURATION
# ============================================================================

echo ""
echo "Checking configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "  .env not found, copying from .env.example..."
        cp .env.example .env
        echo "  ⚠ WARNING: .env created from template."
        echo "  ⚠ Edit .env and set SEC_USER_AGENT to a real contact, e.g.:"
        echo '      SEC_USER_AGENT="Project Stock Atlas you@example.com"'
    else
        echo "✗ ERROR: Neither .env nor .env.example found"
        exit 1
    fi
else
    echo "✓ .env configuration found"
fi

if grep -q "^SEC_USER_AGENT=" .env; then
    UA=$(grep "^SEC_USER_AGENT=" .env | cut -d= -f2- | tr -d '"' | xargs)
    case "$UA" in
        ""|*"example.com"*|*"your-email"*)
            echo "  ⚠ WARNING: SEC_USER_AGENT still a placeholder ('$UA')."
            echo "    SEC EDGAR requires a genuine contact; live gates will 403 otherwise." ;;
        *)
            echo "✓ SEC_USER_AGENT configured" ;;
    esac
fi

# ============================================================================
# 7. VERIFY KEY FILES
# ============================================================================

echo ""
echo "Verifying source files..."

REQUIRED_FILES=(
    "validation_harness_live_v3.py"   # active live harness
    "sec_adapter.py"
    "database.py"
    "models.py"
    "point_in_time.py"
    "formulas.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ MISSING: $file"
    fi
done

# ============================================================================
# 8. SUMMARY
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    SETUP COMPLETE                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "  1. Ensure .env has a real SEC_USER_AGENT contact."
echo "  2. Run the live validation:   ./run_live_validation.sh"
echo "  3. Results are written to:     live_validation_results/"
echo ""
echo "The runner uses $VENV_DIR/bin/python directly; no manual activation needed."
echo "To work interactively:  source $VENV_DIR/bin/activate"
echo ""
