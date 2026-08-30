# Temporal Architecture Amendment

**Status**: REQUIRED BEFORE LIVE VALIDATION

**Issue**: Current `known_date` (date only) is insufficient. Must support timestamp precision.

**Blocker**: A filing accepted at `2026-04-29 16:06:24` must NOT leak into queries at `2026-04-29 10:00:00` on the same calendar day.

---

## Problem Statement

### Current Implementation (INSUFFICIENT)

```python
class EvidenceRecordORM(Base):
    known_date: datetime = Column(DateTime)  # Date only, hour/minute lost
```

**Issue**: 
```
Query: get_evidence_as_of_date(knowledge_date=2026-04-29)
Before filing published: 2026-04-29 10:00:00
After filing published: 2026-04-29 16:06:24

Both queries on same calendar date would return the filing.
✗ INCORRECT: Information leaks from future on same day.
```

### Required Implementation (TIMESTAMP PRECISION)

```python
class EvidenceRecordORM(Base):
    known_at: datetime = Column(DateTime)  # Full timestamp with microseconds
    # Stores: 2026-04-29 16:06:24.000000
```

**Correct behavior**:
```
Query: get_evidence_as_of_date(query_timestamp=2026-04-29 10:00:00)
Result: [] (empty, filing not yet published)

Query: get_evidence_as_of_date(query_timestamp=2026-04-29 16:06:25)
Result: [EvidenceRecord(...)] (filing now available)

Query: get_evidence_as_of_date(query_date=2026-04-29)  # Daily mode
Result: [EvidenceRecord(...)] (end-of-day snapshot mode)

✓ CORRECT: Timestamp precision respected. No same-day leakage.
```

---

## Recommended Temporal Field Set

### Four Distinct Concepts

```python
class EvidenceRecordORM(Base):
    
    # 1. When did the economic event occur?
    effective_at: datetime  # e.g., 2026-06-30 (period end)
    
    # 2. When did the fact become PUBLICLY KNOWN?
    known_at: datetime  # e.g., 2026-07-29 16:08:01 (SEC accepted timestamp)
    
    # 3. When was the filing published by issuer?
    publication_at: datetime  # e.g., 2026-07-29 (filing date)
    
    # 4. When did Atlas retrieve it?
    retrieved_at: datetime  # e.g., 2026-07-30 08:15:22 (local retrieval)
    
    # Metadata (keep)
    filing_date: str  # "2026-07-29"
    accession: str    # "0001193125-26-323660"
```

### Usage in Queries

```python
# Point-in-time with timestamp precision
def get_evidence_as_of_timestamp(
    security_id: str,
    field_name: str,
    query_timestamp: datetime
) -> List[EvidenceRecord]:
    """Returns evidence where known_at <= query_timestamp."""
    return db.query(EvidenceRecordORM).filter(
        EvidenceRecordORM.security_id == security_id,
        EvidenceRecordORM.field_name == field_name,
        EvidenceRecordORM.known_at <= query_timestamp  # TIMESTAMP PRECISION
    ).all()

# Historical daily snapshot (end-of-day mode)
def get_evidence_as_of_date(
    security_id: str,
    field_name: str,
    query_date: date
) -> List[EvidenceRecord]:
    """Returns evidence known by end of day (00:00:00 next day)."""
    end_of_day = datetime(query_date.year, query_date.month, query_date.day, 23, 59, 59)
    return db.query(EvidenceRecordORM).filter(
        EvidenceRecordORM.security_id == security_id,
        EvidenceRecordORM.field_name == field_name,
        EvidenceRecordORM.known_at <= end_of_day  # END OF DAY BOUNDARY
    ).all()
```

---

## Required Code Changes

### 1. Database Schema

**Before:**
```python
known_date = Column(DateTime)
```

**After:**
```python
effective_at = Column(DateTime, nullable=False)    # When fact economically applies
known_at = Column(DateTime, nullable=False)        # When fact became public (SEC accepted time)
publication_at = Column(DateTime, nullable=True)   # When published (filing date + assumed time)
retrieved_at = Column(DateTime, default=utcnow)    # When Atlas fetched it

# Indexes
Index("ix_evidence_known_at", "known_at")
Index("ix_evidence_security_known_at", "security_id", "known_at")
```

### 2. Point-in-Time Service

**Before:**
```python
def get_evidence_as_of_date(self, security_id, field_name, knowledge_date):
    return db.query(EvidenceRecordORM).filter(
        EvidenceRecordORM.known_date <= knowledge_date
    ).all()
```

**After:**
```python
def get_evidence_as_of_timestamp(self, security_id, field_name, query_timestamp):
    """Query with full timestamp precision."""
    return db.query(EvidenceRecordORM).filter(
        EvidenceRecordORM.security_id == security_id,
        EvidenceRecordORM.field_name == field_name,
        EvidenceRecordORM.known_at <= query_timestamp  # TIMESTAMP
    ).all()

def get_evidence_as_of_date(self, security_id, field_name, query_date):
    """Query for end-of-day snapshot."""
    end_of_day = datetime(
        query_date.year, query_date.month, query_date.day,
        23, 59, 59, 999999
    )
    return db.query(EvidenceRecordORM).filter(
        EvidenceRecordORM.security_id == security_id,
        EvidenceRecordORM.field_name == field_name,
        EvidenceRecordORM.known_at <= end_of_day  # END OF DAY BOUNDARY
    ).all()
```

### 3. SEC Adapter

**Capture SEC accepted timestamp:**
```python
def archive_filing(
    self,
    cik: str,
    accession: str,
    form_type: str,
    filed_date: str,
    period_end: str,
    content: str,
    sec_accepted_timestamp: datetime  # NEW
) -> Dict:
    """Archive filing with SEC accepted timestamp."""
    
    metadata = {
        "cik": cik,
        "accession_number": accession,
        "form_type": form_type,
        "filed_date": filed_date,
        "period_end": period_end,
        "sec_accepted_timestamp": sec_accepted_timestamp.isoformat(),  # PRESERVED
        "retrieved_at": datetime.utcnow().isoformat(),
        "parser_version": "1.0"
    }
```

### 4. Evidence Creation

**When creating EvidenceRecord from SEC filing:**
```python
evidence = EvidenceRecordORM(
    security_id=security_id,
    field_name="revenue",
    raw_value="245122",
    normalized_value=245122000000,
    unit="USD",
    
    # Temporal
    effective_at=datetime(2026, 6, 30),           # Period end
    known_at=datetime(2026, 7, 29, 16, 8, 1),    # SEC accepted timestamp
    publication_at=datetime(2026, 7, 29),        # Filing date
    retrieved_at=datetime.utcnow(),              # Atlas retrieval time
    
    source_type="SEC",
    source_name="SEC",
    source_identifier="0001193125-26-323660",
    evidence_class=EvidenceClass.REPORTED_FACT,
    verification_status=VerificationStatus.PRIMARY_VERIFIED,
    parser_version="1.0",
    schema_version="1.0"
)
```

---

## Validation Tests

### Test 1: Intra-Day Timestamp Precision

```python
def test_same_day_timestamp_precision():
    """Filing at 16:06:24 must NOT leak into 10:00:00 same day."""
    
    # Filing accepted: 2026-04-29 16:06:24
    evidence = EvidenceRecordORM(
        known_at=datetime(2026, 4, 29, 16, 6, 24),
        ...
    )
    db.add(evidence)
    db.commit()
    
    pit_service = PointInTimeService(db)
    
    # Query BEFORE filing published (same day)
    result_before = pit_service.get_evidence_as_of_timestamp(
        security_id="SEC_MSFT",
        field_name="revenue",
        query_timestamp=datetime(2026, 4, 29, 10, 0, 0)  # 6 hours BEFORE
    )
    assert len(result_before) == 0  # ✓ CORRECT: Not yet available
    
    # Query AFTER filing published (same day)
    result_after = pit_service.get_evidence_as_of_timestamp(
        security_id="SEC_MSFT",
        field_name="revenue",
        query_timestamp=datetime(2026, 4, 29, 16, 6, 25)  # 1 second AFTER
    )
    assert len(result_after) == 1  # ✓ CORRECT: Now available
```

### Test 2: Daily Snapshot Mode

```python
def test_daily_snapshot_mode():
    """End-of-day queries should include all facts known by EOD."""
    
    evidence = EvidenceRecordORM(
        known_at=datetime(2026, 4, 29, 16, 6, 24),
        ...
    )
    db.add(evidence)
    db.commit()
    
    pit_service = PointInTimeService(db)
    
    # Query for date 2026-04-28 (day before)
    result_28th = pit_service.get_evidence_as_of_date(
        security_id="SEC_MSFT",
        field_name="revenue",
        query_date=date(2026, 4, 28)
    )
    assert len(result_28th) == 0  # ✓ Filing not yet published
    
    # Query for date 2026-04-29 (filing day, end-of-day)
    result_29th = pit_service.get_evidence_as_of_date(
        security_id="SEC_MSFT",
        field_name="revenue",
        query_date=date(2026, 4, 29)
    )
    assert len(result_29th) == 1  # ✓ Filing published during day
```

---

## Migration Path

### Step 1: Add New Columns (Backward Compatible)

```sql
ALTER TABLE evidence_record
ADD COLUMN effective_at DATETIME;
ADD COLUMN known_at DATETIME;
ADD COLUMN publication_at DATETIME;
ADD COLUMN retrieved_at DATETIME;
```

### Step 2: Populate from Existing Data

```python
# For existing records, migrate known_date to known_at
# Assume SEC filings are published at assumed time (e.g., 16:00 UTC)
evidence = db.query(EvidenceRecordORM).all()
for record in evidence:
    record.known_at = record.known_date.replace(hour=16, minute=0, second=0)
    record.effective_at = record.period_end if record.period_end else record.known_date
    record.publication_at = record.publication_date if hasattr(record, 'publication_date') else record.known_date
```

### Step 3: Update Queries Gradually

```python
# Old queries still work (backward compatible)
def get_evidence_as_of_date(self, security_id, field_name, knowledge_date):
    # Internally uses known_at with end-of-day boundary
    end_of_day = datetime(
        knowledge_date.year, knowledge_date.month, knowledge_date.day,
        23, 59, 59
    )
    return db.query(EvidenceRecordORM).filter(
        EvidenceRecordORM.known_at <= end_of_day
    ).all()
```

### Step 4: New Timestamp-Precise Queries

```python
# New code can use timestamp precision
def get_evidence_as_of_timestamp(self, security_id, field_name, query_timestamp):
    return db.query(EvidenceRecordORM).filter(
        EvidenceRecordORM.known_at <= query_timestamp
    ).all()
```

---

## UTC Normalization

**All timestamps stored in UTC internally.**

```python
from datetime import datetime, timezone

# When receiving SEC accepted timestamp
sec_accepted_string = "2026-07-29 16:08:01"  # Assumed UTC
sec_accepted = datetime.fromisoformat(sec_accepted_string).replace(tzinfo=timezone.utc)

# Store in database (UTC)
evidence.known_at = sec_accepted

# Query (compare in UTC)
def get_evidence_as_of_timestamp(query_timestamp):
    query_timestamp_utc = query_timestamp.replace(tzinfo=timezone.utc)
    return db.query(...).filter(
        EvidenceRecordORM.known_at <= query_timestamp_utc
    ).all()
```

---

## Summary of Changes

| Concept | Before | After |
|---------|--------|-------|
| Temporal Field | `known_date` (date only) | `known_at` (timestamp with microseconds) |
| Query Precision | Date boundary | Timestamp boundary (second precision) |
| Same-Day Leakage | POSSIBLE | PREVENTED |
| Daily Mode | Implicit | Explicit end-of-day boundary |
| SEC Timestamp | Lost | Preserved |
| UTC Normalization | Not specified | Required for all |
| Backward Compatibility | N/A | Maintained via date mode |

---

## Impact on Validation Harness

The validation harness must now:

1. **Capture SEC accepted timestamp** from filing metadata
2. **Test timestamp precision** with intra-day scenarios
3. **Verify same-day non-leakage** explicitly
4. **Use real accessions with real timestamps**:
   - FY2026 Q3 10-Q: `2026-04-29 16:06:24`
   - FY2026 10-K: `2026-07-29 16:08:01`

---

## Status

✅ **Amendment identified** — Current schema insufficient  
⏳ **Code changes required** — Before live validation  
⏳ **Test cases required** — Same-day timestamp precision  
⏳ **Live validation** — Use real SEC timestamps  

---

**Do not proceed with live validation until timestamp precision is implemented.**
