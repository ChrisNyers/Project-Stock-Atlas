> **Historical (Sprint 1 era).** This document does not govern current work, including any “Sprint 2” instruction in it. The current authority is [`docs/CURRENT_AUTHORITY.md`](docs/CURRENT_AUTHORITY.md) (`python -m atlas_ui preflight`).

# Project Atlas: Equities — Sprint 1

**Status**: Sprint 1 Implementation

## Overview

Atlas is a deterministic portfolio-management operating system that evaluates securities within the context of an investor's entire portfolio. Sprint 1 builds the trustworthy infrastructure upon which investment decisions can later be calculated.

At the end of Sprint 1, Atlas can:
1. Identify a U.S. public company (e.g., Microsoft)
2. Retrieve authoritative financial evidence from the SEC
3. Normalize and preserve that evidence point-in-time
4. Retrieve market state and macro data
5. Calculate deterministic derived financial metrics
6. Create an immutable evidence freeze
7. Trace any fact back to its source

**Atlas does NOT yet:**
- Perform DCF valuation
- Generate BUY/SELL decisions
- Optimize portfolio allocation
- Integrate live Grok research

## Architecture Principles

### Separation of Concerns
- **FACT**: What happened economically (e.g., Q1 revenue = $100B)
- **ASSUMPTION**: Future expectations (e.g., revenue growth = 8%)
- **CALCULATION**: Deterministic formula output (e.g., year-5 revenue = $146.9B)
- **JUDGMENT**: Quality assessment (e.g., BusinessQuality = HIGH)
- **DECISION**: Security action (e.g., BUY, HOLD, WATCH)
- **PORTFOLIO_ACTION**: Capital allocation (e.g., INITIATE, ADD, HOLD, TRIM)

### Evidence Pipeline
```
RAW_SOURCE
    ↓
RAW_EVIDENCE (immutable)
    ↓
NORMALIZED_EVIDENCE
    ↓
CANONICAL_FACT
    ↓
ASSUMPTION / CALCULATION
    ↓
DECISION
    ↓
FREEZE (immutable)
```

### Bitemporal Architecture
Every material financial fact supports two time concepts:
- **Effective Time**: When the fact economically applies (e.g., quarter end = March 31)
- **Knowledge Time**: When Atlas could have known the fact (e.g., earnings released = April 25)

On April 10, Atlas cannot return Q1 results (not yet known).

## Repository Structure

```
stock-atlas/
├── atlas_core/              # Core infrastructure
│   ├── config/              # Configuration
│   ├── versioning/          # Version management
│   ├── provenance/          # Data lineage tracking
│   ├── formulas/            # Formula registry and execution
│   ├── freeze/              # Immutable freeze infrastructure
│   └── audit/               # Audit trail
├── securities/              # Security identity and reference
│   ├── identity/            # SecurityIdentity model
│   ├── reference/           # Reference data
│   └── corporate_actions/   # Corporate actions foundation
├── evidence/                # Evidence management
│   ├── raw/                 # Raw evidence ingestion
│   ├── normalized/          # Normalized evidence
│   ├── canonical/           # Canonical facts
│   ├── conflicts/           # Conflict detection/resolution
│   └── quality/             # Data quality assessment
├── financials/              # Financial statements
│   ├── ingestion/           # SEC/provider ingestion
│   ├── normalization/       # XBRL/field normalization
│   ├── statements/          # FinancialState models
│   ├── metrics/             # Derived metrics
│   └── xbrl/                # XBRL mapping
├── market/                  # Market data
│   ├── adapters/            # Provider-neutral interface
│   ├── models/              # MarketState
│   └── services/            # Market data service
├── macro/                   # Macroeconomic data
│   ├── adapters/            # FRED/macro adapters
│   ├── models/              # Macro state
│   └── services/            # Macro data service
├── providers/               # External provider adapters
│   ├── sec/                 # SEC adapter
│   ├── massive/             # Massive (market data) adapter
│   ├── fred/                # FRED adapter
│   └── base/                # Base adapter interface
├── research/                # Research events (Grok placeholder)
├── backtesting/             # Point-in-time query infrastructure
├── api/                     # Service layer / API
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── fixtures/            # Test data and mocks
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project configuration
└── METHODOLOGY_ISSUES.md    # Methodology questions log
```

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL (recommended)
- API keys: MASSIVE_API_KEY, FRED_API_KEY

### Installation

```bash
git clone https://github.com/your-org/stock-atlas.git
cd stock-atlas
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your API keys and database URL
```

### Database Setup

```bash
python -m atlas_core.db.init
```

### Run Tests

```bash
pytest tests/ -v
```

## Core Concepts

### SecurityIdentity
Canonical security representation. Ticker changes are tracked as security relationship changes, not identity changes. Status must be VERIFIED before any investment action proceeds.

### EvidenceRecord
Immutable record of raw evidence with:
- Source (SEC, market provider, macro provider, etc.)
- Source authority tier (DA0-DA4)
- Raw and normalized values
- Effective date (when economically applies)
- Known date (when Atlas learned of it)
- Verification status

### CanonicalFact
Validated, normalized fact available to calculations. Produced by applying SourceAuthorityRegistry. Never silently overwrites conflicting evidence.

### EvidenceConflict
When two Tier-1 sources disagree, a conflict is recorded. Investigation required before resolving. If critical input has unresolved material conflict, DataQuality = UNUSABLE.

### SourceAuthorityRegistry
Defines for each field:
- Primary source tier (SEC, company, market provider, etc.)
- Minimum decision authority required
- Verification requirement
- Point-in-time requirement
- Normalization rule

**Not hardcoded.** Queryable registry.

### FormulaRegistry
Every deterministic formula has:
- Unique ID and version
- Explicit inputs
- Expression
- Output unit

Formulas are immutable. New methodology = new version.

### Freeze Infrastructure
Creates immutable snapshot of:
- SecurityIdentity version
- Evidence manifest
- Canonical facts
- Formula versions
- Source authority version
- Timestamp
- Atlas version

Includes deterministic hash for mutation detection.

## Key Constraints

### No Silent Overwrites
If SEC reports $100B and vendor reports $105B, both are stored. Conflict is recorded. SourceAuthorityRegistry determines canonical fact. No guessing.

### No Future Information
Historical query for date T can only use evidence with known_date ≤ T. Enforced at query layer. Backtests cannot accidentally see future information.

### No LLM Financial Facts
Narrative claims, research events, and external text processing cannot directly populate FinancialState, ValuationState, or SecurityDecision. These are research only (Grok integration comes later). Noise firewall is enforced in code.

### No Missing Data Guessing
Missing required data follows this sequence:
1. Primary source
2. Approved secondary source
3. Explicitly authorized derivation
4. INCOMPLETE / MANUAL_REVIEW

Never LLM guess.

### Fail Closed on Uncertainty
If a number's provenance is ambiguous or data conflicts are unresolved, the system returns:
- `INCOMPLETE`
- `CONFLICTED`
- `STALE`
- `MANUAL_REVIEW`

Not plausible-looking approximations.

## Golden Security: Microsoft (MSFT)

Sprint 1 validation uses Microsoft Corporation (ticker: MSFT, CIK: 0000789019).

**Why MSFT?**
- Long filing history
- Multiple segments
- Strong cash flow and capex
- Significant SBC and buybacks
- Debt and cash positions
- Reliable market history

**What Sprint 1 Produces for MSFT:**
- Current market price with timestamp and source
- Latest 10-K and 10-Q filings archived
- Normalized financial state (Revenue, FCF, SBC, shares, etc.)
- Derived metrics (FCF margin, revenue growth, SBC/revenue, etc.)
- Current macro indicators (treasury, fed funds)
- Evidence freeze with cryptographic hash
- Full provenance chain for every number

## Methodology Issues

See `METHODOLOGY_ISSUES.md` for questions requiring portfolio/investment-policy decisions. Implementation team may flag issues; solutions require explicit approval.

## Next Steps

**Sprint 2** will add:
- Full FinancialState history
- BusinessQuality assessment
- DCF valuation engine
- Scenario modeling
- ExpectedReturnProfile
- ValuationState
- Required-return calculations
- ActionPrice
- SecurityDecision logic

**Do not implement** until Sprint 1 passes review.

## Contact & Questions

For technical questions about implementation, refer to the architecture documentation in each module.

For investment methodology questions, see METHODOLOGY_ISSUES.md.
