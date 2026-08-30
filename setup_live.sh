#!/bin/bash

################################################################################
# Stock Atlas Sprint 1 — Live Validation Setup
#
# This script prepares the Stock Atlas environment for live SEC validation.
# Run this once before running `run_live_validation.sh`
#
# Usage:
#   ./setup_live.sh
#
# Prerequisites:
#   - Python 3.10+
#   - pip
#   - Bash
################################################################################

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Stock Atlas Sprint 1 — Live Validation Setup              ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# ============================================================================
# 1. CHECK PYTHON
# ============================================================================

echo ""
echo "Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    echo "✗ FATAL: Python 3 not found"
    echo "  Please install Python 3.10+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

# Check Python 3.10+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MINOR" -lt 10 ]; then
    echo "✗ FATAL: Python 3.10+ required (you have $PYTHON_VERSION)"
    exit 1
fi

# ============================================================================
# 2. CREATE VIRTUAL ENVIRONMENT
# ============================================================================

echo ""
echo "Setting up virtual environment..."

if [ -d "venv" ]; then
    echo "  Virtual environment already exists"
    echo "  Activating existing venv..."
else
    echo "  Creating new virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate venv
source venv/bin/activate
echo "✓ Virtual environment activated"

# ============================================================================
# 3. UPGRADE PIP
# ============================================================================

echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1 || true
echo "✓ pip ready"

# ============================================================================
# 4. INSTALL REQUIREMENTS
# ============================================================================

echo ""
echo "Installing dependencies from requirements.txt..."

if [ ! -f "requirements.txt" ]; then
    echo "✗ ERROR: requirements.txt not found"
    echo "  Make sure you're in the stock-atlas project directory"
    exit 1
fi

pip install -r requirements.txt
echo "✓ All dependencies installed"

# ============================================================================
# 5. CREATE DIRECTORIES
# ============================================================================

echo ""
echo "Setting up directories..."

mkdir -p live_validation_results
echo "✓ Directory: live_validation_results/"

mkdir -p sec_archive
echo "✓ Directory: sec_archive/"

mkdir -p cache
echo "✓ Directory: cache/"

# ============================================================================
# 6. CHECK CONFIGURATION
# ============================================================================

echo ""
echo "Checking configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "  .env not found, copying from .env.example..."
        cp .env.example .env
        echo "  ⚠ WARNING: .env created from template"
        echo "  ⚠ Please edit .env and add your contact email to SEC_USER_AGENT"
        echo ""
        echo "  Edit .env and set:"
        echo "    SEC_USER_AGENT=\"Project Stock Atlas your-email@example.com\""
        echo ""
    else
        echo "✗ ERROR: Neither .env nor .env.example found"
        exit 1
    fi
else
    echo "✓ .env configuration found"
fi

# Check if SEC_USER_AGENT is set
if grep -q "SEC_USER_AGENT" .env; then
    USER_AGENT=$(grep "SEC_USER_AGENT" .env | cut -d= -f2 | xargs)
    if [ "$USER_AGENT" = "your-email@example.com" ] || [ "$USER_AGENT" = "" ]; then
        echo "  ⚠ WARNING: SEC_USER_AGENT not configured"
        echo "  Please edit .env and set your contact email"
    else
        echo "✓ SEC_USER_AGENT configured: $USER_AGENT"
    fi
fi

# ============================================================================
# 7. VERIFY KEY FILES
# ============================================================================

echo ""
echo "Verifying source files..."

REQUIRED_FILES=(
    "validation_harness_live.py"
    "sec_adapter.py"
    "database.py"
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
echo "1. Edit .env and add your contact email:"
echo "   nano .env"
echo "   # Set: SEC_USER_AGENT=\"Project Stock Atlas your-email@example.com\""
echo ""
echo "2. Run the live validation:"
echo "   ./run_live_validation.sh"
echo ""
echo "3. Results will be saved to:"
echo "   live_validation_results/"
echo ""
echo "Virtual environment activated."
echo "To deactivate later, run: deactivate"
echo ""
