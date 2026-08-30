# Project Atlas: Equities — Methodology Issues Log

**Purpose**: Track investment methodology questions and ambiguities discovered during implementation.

Technical recommendations are provided. Financial policy decisions require explicit approval before implementation.

---

## ISSUE #M001: ROIC Definition

**Status**: PENDING_DECISION

**Specification Reference**: Section 29 - Initial Formula Set

**Ambiguity**:
The specification mentions ROIC (Return on Invested Capital) may be implemented if the canonical invested-capital definition is unambiguous. Currently, there are multiple ways to define invested capital:

1. **Sum of Debt + Equity**: Simple but includes cash (economically incorrect)
2. **Debt + Equity - Cash**: Removes cash but may miss other adjustments
3. **Adjusted Invested Capital**: Adds back various intangibles, operating leases, etc.

Different schools of investment thought prefer different definitions.

**Why Implementation Depends On It**:
- ROIC is a primary capital efficiency metric
- Multiple ROIC values for same company possible with different definitions
- Canonical Fact system requires ONE truth per field
- DecisionFreeeze logic (Sprint 2) will reference ROIC
- If we implement ROIC, we must ensure every Atlas output references identical definition

**Possible Choices**:

A. **Defer ROIC to Sprint 2+**
   - Cleaner: Sprint 1 doesn't implement it
   - Safe: Can establish consensus by then
   - Cost: Delays ROIC availability

B. **Use Debt + Equity - Cash (Simplest)**
   - Advantage: Widely used, relatively unambiguous
   - Disadvantage: Omits some nuances
   - Risk: May not satisfy sophisticated users

C. **Use Vendor ROIC (Sharadar, FactSet, etc)**
   - Advantage: Outsource definition
   - Disadvantage: Creates vendor dependency
   - Contradicts architecture principle: "Do not make data provider inseparable from Atlas"

**Technical Recommendation**:
Defer to Sprint 2. By then, Grok research context may surface preferred definitions. No ROIC formula implemented in Sprint 1.

**Action**: Awaiting explicit decision before Sprint 2 implementation.

---

## ISSUE #M002: Stock-Based Compensation Treatment

**Status**: ACKNOWLEDGED

**Specification Reference**: Section 31 - Stock-Based Compensation

**Ambiguity**:
SBC is economically a cost. But treatment varies:

1. **SBC as Direct Cost**: Reduces FCF, increases employee expense
2. **SBC as Dilution Only**: FCF unchanged, impacts share count
3. **SBC as Both**: Full cost + dilution

Current implementation: Stores both `sbc_dollars` and tracks share dilution. But portfolio decisions (Sprint 2) need clarity on whether SBC should reduce Expected Return calculations.

**Why Implementation Depends On It**:
- Expected Return engine will need to know how to account for SBC
- Scenario modeling (Sprint 2) depends on assumption
- High-SBC companies (tech) could have very different returns depending on SBC treatment

**Possible Choices**:

A. **Economic Cost Model**: SBC reduces FCF and expected return
   - Most intellectually consistent
   - Most conservative
   - May undervalue tech companies relative to market

B. **Dilution-Only Model**: SBC noted but doesn't reduce FCF
   - More lenient to SBC
   - Share dilution captured separately
   - May overvalue tech companies

C. **Dual-Track**: Store both, let portfolio manager choose
   - Maximum flexibility
   - Adds complexity
   - Violates determinism principle

**Technical Recommendation**:
Implement A (Economic Cost Model) as canonical. This is clearest, most conservative, most defensible.

**Action**: Awaiting explicit decision.

---

## ISSUE #M003: TTM vs Latest Quarter Precedence

**Status**: ACKNOWLEDGED

**Specification Reference**: Section 42 - Financial Time Types

**Ambiguity**:
Current architecture supports QUARTER, TTM, and FISCAL_YEAR periods. But when most recent data is:

- Latest Q1 results (3 months known)
- Prior quarters + TTM available (12 months known)

Which should canonical Revenue be? Q1 alone or TTM?

**Why Implementation Depends On It**:
- Revenue Growth calculations need base
- Margin calculations need denominator
- If Atlas uses TTM when Q1 more recent, we're mixing time periods
- If Atlas uses Q1, margins look volatile

**Possible Choices**:

A. **Latest Quarter Always**: Most current, least lag
   - Pro: Freshest information
   - Con: Quarterly volatility, seasonal effects

B. **TTM When Available**: Smooths seasonality
   - Pro: Better trends
   - Con: Lags 9-12 months behind latest quarter

C. **Both Canonical**: Store and choose context-dependent
   - Pro: No information loss
   - Con: Violates canonical fact unity

**Technical Recommendation**:
Current implementation stores all three separately. Recommend explicit rule: "When choosing between Q and TTM, prefer TTM when calculating trend metrics, Q when calculating growth rates." Different formulas use different periods explicitly.

**Action**: Awaiting explicit decision.

---

## ISSUE #M004: Consensus Estimate Integration

**Status**: NOT_YET_ENCOUNTERED

**Specification Reference**: Section 87 - Sprint 2 Preview

**Ambiguity**:
Sprint 2 will add consensus estimates. But consensus varies wildly:

- By analyst count (3 analysts vs 20)
- By recency (estimates updated weekly or quarterly)
- By publication (Bloomberg vs FactSet vs StreetAccount)

How should Atlas integrate consensus?

**Why Implementation Depends On It**:
- Expected Return depends on revenue/earnings assumptions
- If using consensus, which source of truth?
- Can consensus conflict with company guidance?
- What happens when consensus contradicts SEC filings?

**Current Placeholder**:
Architecture supports `MARKET_EXPECTATION` evidence class and `ResearchEvent` for consensus. But precedence rule undefined.

**Possible Choices**:

A. **Company Guidance First**: Use management guidance if available, else consensus
   - Pro: Most direct from company
   - Con: Guidance often vague or absent

B. **Consensus First**: Use consensus, flag company guidance separately
   - Pro: Market view
   - Con: Consensus can be manipulated

C. **Consensus with Confidence Weighting**: Higher confidence if 15+ analysts, lower if <5
   - Pro: Accounts for consensus size
   - Con: Adds complexity

**Technical Recommendation**:
Defer full implementation to Sprint 2. Current architecture supports all three. Recommend conversation with portfolio team on preferences before committing.

**Action**: Awaiting explicit decision.

---

## ISSUE #M005: Corporate Action Handling - Mergers & Spinoffs

**Status**: DEFERRED

**Specification Reference**: Section 47 - Corporate Actions Foundation

**Ambiguity**:
Sprint 1 created foundation for corporate actions but didn't implement full handling. What happens when security undergoes merger or spinoff?

- Historical financials: Adjust or keep as-reported?
- Security identity: New identity or continuation?
- Portfolio: Mark position as closed or converted?
- Backtest: Replay historical with new structure?

**Why Implementation Depends On It**:
- If MSFT acquired LinkedIn, should pre-2016 metrics reflect integration?
- If spin-off occurs, are parent and spinoff separate investments?
- Backtesting through merger requires clear rules

**Current Implementation**:
Corporate actions tracked separately. Not integrated into financial state or identity.

**Technical Recommendation**:
Keep deferred to Sprint 2+. Current foundation adequate for Phase 1.

**Action**: Awaiting explicit decision when needed.

---

## ISSUE #M006: Data Freshness vs Investment Action

**Status**: ACKNOWLEDGED

**Specification Reference**: Section 49 - Market Fallback

**Ambiguity**:
If market price stale (>24 hours) but price available, should Atlas proceed with decision or wait for fresh data?

- Recent decision: BUY at $100 when last price was $100 yesterday
- Today: Price might be $95 or $110
- Should portfolio action proceed or wait?

**Why Implementation Depends On It**:
- Defines "good enough" for investment readiness
- Affects portfolio action status (REVIEW, NO_ACTION, etc)
- Different for different decision types (BUY vs HOLD)

**Current Implementation**:
FreshnessPolicyRegistry tracks maximum and acceptable ages. But investment readiness logic not yet implemented.

**Technical Recommendation**:
Current architecture: If price stale, mark MarketState.status = STALE. DecisionFreeeze (Sprint 2) should refuse to upgrade DECISION to portfolio action if underlying data stale. Let portfolio manager manually override if needed.

**Action**: Awaiting explicit decision for Sprint 2.

---

## ISSUE #M007: Missing Financial Data - Estimation vs Rejection

**Status**: ACKNOWLEDGED

**Specification Reference**: Section 26 - Missing Data Policy

**Ambiguity**:
When required field (e.g., diluted shares) unavailable:
- Estimate from basic shares + options model?
- Estimate from peer average?
- Mark as INCOMPLETE and refuse decision?

**Why Implementation Depends On It**:
- EPS calculation needs diluted shares
- Many small/foreign companies have incomplete data
- If we always estimate, we lose data quality signal
- If we always reject, we exclude many companies

**Current Implementation**:
Hard rule: No estimation. INCOMPLETE status if missing. This is conservative.

**Technical Recommendation**:
Keep current rule (no estimation). This is safest for capital allocation. If later business case requires estimation, can add explicit approval workflow.

**Action**: Current implementation stands.

---

## ISSUE #M008: Macro Data Vintage Handling

**Status**: DEFERRED

**Specification Reference**: Section 52 - ALFRED Compatibility

**Ambiguity**:
FRED publishes data with revisions. Example:
- Initial GDP: 2.5% growth
- Revised GDP: 2.4% growth (published 1 week later)

Should Atlas use initial or final? And for backtesting through revision date?

**Why Implementation Depends On It**:
- BacktestDate(March 1, 2024) may not know June revision
- If we always use "latest revised," historical is inaccurate
- If we use vintage, ALFRED integration needed (complex)

**Current Implementation**:
Architecture supports it but ALFRED integration deferred.

**Technical Recommendation**:
Current approach (use latest available) acceptable for Sprint 1. Proper ALFRED implementation can be added later if backtesting becomes critical use case.

**Action**: Deferred to backtest sprint.

---

## OPEN QUESTIONS FOR PORTFOLIO TEAM

1. **ROIC Definition**: Which definition preferred?
2. **SBC Treatment**: Economic cost or dilution-only?
3. **Consensus Estimates**: How should they rank vs company guidance?
4. **Stale Data Tolerance**: How stale before investment action blocked?
5. **Missing Data Policy**: Ever acceptable to estimate, or always reject?

---

## COMPLETED DECISIONS

None yet. Awaiting team review of Sprint 1 foundation.

---

**Last Updated**: 2024-08-12
**Next Review**: After Sprint 1 team review
