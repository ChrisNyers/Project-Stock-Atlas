# Project Atlas: Equities — Sprint 1 File Index

## Quick Navigation

### 📋 **START HERE**
1. **README.md** — System overview, architecture, getting started
2. **SPRINT_1_COMPLETION_REPORT.md** — What was built, what wasn't, test results, recommendations
3. **METHODOLOGY_ISSUES.md** — Questions for portfolio team (8 issues, none blocking)

### 🗄️ **Data Models & Infrastructure**
4. **models.py** — Data model definitions (enums, class definitions, no ORM)
5. **database.py** — SQLAlchemy ORM models (18 tables, bitemporal architecture)

### 🔌 **External Data Adapters**
6. **sec_adapter.py** — SEC API access, rate limiting, caching, filing archive
7. **xbrl_parser.py** — XBRL parsing, concept mapping, unit normalization
8. **market_macro_adapters.py** — Provider-neutral interfaces (Massive, FRED)

### ⏰ **Query & Evidence Infrastructure**
9. **point_in_time.py** — Bitemporal query service (enforces known_date ≤ query_date)
10. **freeze_and_registry.py** — Evidence freezes (with hash), source authority registry, freshness policies
11. **formulas.py** — Formula registry (13 formulas), safe execution, metrics calculation

### 🧪 **Testing**
12. **test_atlas.py** — 23 comprehensive tests (unit, integration, golden test for MSFT)

### ⚙️ **Configuration**
13. **requirements.txt** — Python dependencies (SQLAlchemy, requests, pytest, etc)
14. **.env.example** — Environment configuration template (API keys, DB URL, paths)

---

## Core Architecture

### Separation of Concerns
```
FACT (EvidenceRecord)
  ↓
ASSUMPTION (AssumptionRecord)
  ↓
CALCULATION (FormulaRegistry + CalculationRecord)
  ↓
JUDGMENT (DataQualityAssessment, BusinessQuality in Sprint 2)
  ↓
DECISION (SecurityDecision in Sprint 2)
  ↓
PORTFOLIO_ACTION (PortfolioAction in Sprint 2)
```

### Evidence Pipeline
```
Raw Source (SEC, Market, Macro)
  ↓ [SECAdapter, MarketDataAdapter, MacroDataAdapter]
Raw Evidence (EvidenceRecord - immutable)
  ↓ [XBRL Parser, Normalization]
Normalized Evidence
  ↓ [SourceAuthorityRegistry]
Canonical Fact (CanonicalFactORM - queryable)
  ↓ [FormulaRegistry]
Calculation Output (CalculationRecord)
  ↓ [DecisionLogic in Sprint 2]
Decision & Freeze
```

### Bitemporal Architecture
```
Every material fact has TWO time concepts:

effective_date    = When fact economically applies
                    Example: Q1 ended March 31

known_date        = When Atlas could have known the fact
                    Example: Q1 earnings released April 25

On April 10: Query returns NOTHING (not yet known)
On April 26: Query returns Q1 data (now known)

Historical integrity rule: Cannot see future information
```

---

## Key Features

### Immutability
- Raw evidence never mutated
- Assumptions versioned, not overwritten
- Formulas versioned, old versions preserved
- Freezes include cryptographic hash (detect tampering)

### Data Quality
- Componentized quality scoring
- Source authority tiers (DA0-DA4)
- Verification states (UNVERIFIED → PRIMARY_VERIFIED → CONFLICTED)
- Stale data flagged; blocks investment action

### Conflict Handling
- All conflicts recorded (not silent overwrites)
- Types: SOURCE_DISAGREEMENT, PERIOD_MISMATCH, RESTATEMENT, etc.
- Resolution tracked; material conflicts block decisions

### Point-in-Time Queries
- Historical data accurate as of specific date
- Backtesting safe: cannot accidentally see future
- Restatements handled: original value in history, current value separate

### Provider Abstraction
- MarketDataAdapter interface (Massive implementation stubbed)
- MacroDataAdapter interface (FRED implementation stubbed)
- SECAdapter (fully functional)
- All replaceable; no vendor lock-in

---

## Database Tables (18)

| Layer | Table | Purpose |
|-------|-------|---------|
| Identity | security_identity | Canonical security (ticker not permanent) |
| Evidence | evidence_record | Raw, immutable evidence with bitemporal fields |
| Canonical | canonical_fact | Validated, normalized facts ready for calculations |
| Assumptions | assumption_record | Versioned investment assumptions |
| Formulas | formula_registry | Deterministic formulas (13 implemented) |
| Formulas | calculation_record | Formula outputs with input references |
| Conflicts | evidence_conflict | Recorded conflicts preventing silent overwrites |
| Quality | data_quality_assessment | Componentized quality scoring |
| Registry | source_authority_registry | Source precedence rules (queryable) |
| Registry | freshness_policy_registry | Staleness thresholds |
| Monitoring | provider_health | Provider status tracking |
| Freeze | evidence_freeze | Immutable snapshots with SHA-256 hash |
| Financial | financial_state | Financial statement view |
| Market | market_state | Market data snapshots |
| Macro | macro_data_point | Macro series with bitemporal fields |
| Research | research_event | Research foundation (Grok placeholder) |
| Versioning | atlas_version | System component versions |
| Audit | audit_trail | Important write audit records |

---

## Formulas Implemented (13)

1. **Free Cash Flow** (F_FCF_001): CFO - Capex
2. **FCF Margin** (F_FCF_MARGIN_001): FCF / Revenue
3. **Gross Margin** (F_GROSS_MARGIN_001): Gross Profit / Revenue
4. **Operating Margin** (F_OPERATING_MARGIN_001): Operating Income / Revenue
5. **Revenue Growth** (F_REVENUE_GROWTH_001): YoY growth
6. **EPS Growth** (F_EPS_GROWTH_001): Diluted EPS YoY
7. **FCF Growth** (F_FCF_GROWTH_001): YoY growth
8. **Net Debt** (F_NET_DEBT_001): (ST Debt + LT Debt) - Cash
9. **Share Count Growth** (F_SHARE_COUNT_GROWTH_001): YoY diluted shares
10. **Share Count CAGR** (F_SHARE_COUNT_CAGR_001): Multi-year growth
11. **SBC / Revenue** (F_SBC_REVENUE_001): Stock comp as % of revenue
12. **SBC / FCF** (F_SBC_FCF_001): Stock comp as % of FCF
13. **Net Buyback Yield** (F_NET_BUYBACK_YIELD_001): (Repurchases - Dividends) / Market Cap

---

## Test Coverage (23 tests)

**Unit Tests (14)**
- Formula calculations: normal, boundary, missing input, division by zero, extremes
- Evidence immutability
- Conflict detection and recording

**Integration Tests (8)**
- Point-in-time queries: before/after known_date
- Restatement handling: original vs restated values
- SEC adapter: rate limiting, filing archive
- Provider functionality: quotes, bars, FRED series

**Golden Test (1)**
- MSFT end-to-end: CIK resolution → security creation → market data → macro data → evidence → point-in-time queries

---

## What's NOT Included (Sprint 2+)

❌ DCF valuation engine  
❌ Expected return calculations  
❌ BUY/SELL decision logic  
❌ Portfolio optimization  
❌ Grok research integration  
❌ Consensus estimates (model exists, not integrated)  
❌ Backtesting engine  

**These build on Sprint 1 foundation.**

---

## Key Constraints Enforced

1. ✅ **No Silent Overwrites** — Conflicts recorded, not overwritten
2. ✅ **No Future Information** — known_date ≤ query_date always
3. ✅ **No LLM Guessing** — Missing data → INCOMPLETE
4. ✅ **No Raw Mutation** — Evidence immutable
5. ✅ **No Assumption Overwrite** — Versioned history
6. ✅ **No Formula Drift** — Versioned, immutable
7. ✅ **No Vendor Lock-In** — Provider-neutral interfaces
8. ✅ **No Noise in Decisions** — Research claims cannot directly affect financial facts
9. ✅ **Fail Closed** — Ambiguous/stale/conflicted data blocks decisions
10. ✅ **Full Provenance** — Every fact traceable to source

---

## Getting Started

### Setup
```bash
cp .env.example .env
# Edit .env with API keys (Massive, FRED optional for Sprint 1)
pip install -r requirements.txt
```

### Initialize Database
```python
from database import init_db
init_db()  # Creates all tables
```

### Query MSFT (Golden Test)
```python
from database import SessionLocal
from sec_adapter import get_sec_adapter
from market_macro_adapters import get_market_adapter, get_macro_adapter

db = SessionLocal()
sec = get_sec_adapter()
market = get_market_adapter()
macro = get_macro_adapter()

# Resolve CIK
cik = sec.resolve_cik("MSFT")  # → "0000789019"

# Create security
security = ... # See test_atlas.py for example

# Query point-in-time
pit = PointInTimeService(db)
evidence = pit.get_evidence_as_of_date(
    security.security_id, 
    "revenue",
    datetime(2024, 4, 26)
)
```

### Run Tests
```bash
pytest test_atlas.py -v
```

---

## Methodology Questions for Portfolio Team

See **METHODOLOGY_ISSUES.md** for full details. 8 questions identified; none block Sprint 1:

1. ROIC definition (defer to Sprint 2)
2. SBC economic treatment (defer to Sprint 2)
3. TTM vs latest quarter (documented, awaiting guidance)
4. Consensus estimates (defer to Sprint 2)
5. Merger/spinoff handling (defer to Sprint 2+)
6. Stale data tolerance (await portfolio guidance)
7. Missing data policy (currently: always INCOMPLETE, no guessing)
8. Macro data vintage handling (defer to backtest sprint)

---

## Next Steps

1. **Code Review** — Portfolio and engineering team review Sprint 1 deliverables
2. **Architecture Feedback** — Adjust design based on feedback
3. **Methodology Alignment** — Resolve 8 questions in METHODOLOGY_ISSUES.md
4. **Sprint 2 Planning** — Valuation engine, business quality, decision logic
5. **API Integration** — Real Massive and FRED API calls (stubs ready)

---

## Repository Quality

✅ No monolithic files  
✅ Clear conceptual boundaries  
✅ Versioned, immutable components  
✅ Comprehensive tests (23 passing)  
✅ Full documentation  
✅ No hardcoded secrets  
✅ Provider-neutral architecture  
✅ Bitemporal integrity enforced  

**Status**: Ready for review and Sprint 2 planning.

---

**Prepared**: 2024-08-12  
**Version**: 1.0 (Sprint 1)  
**Next Review**: Sprint 1 completion meeting
