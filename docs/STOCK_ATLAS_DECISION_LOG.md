# Stock Atlas — Decision Log

Architecture decisions, appended only. Entries are never edited; a superseded
decision gets a new entry that names the one it replaces.

---

## `ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE`

| | |
|---|---|
| Date | 2026-09-03 |
| Status | **ACCEPTED** |
| Context | Pilot 1 Red Team closeout |

### Decision

Stage 8 allocation reasoning is captured through **human-authored fields within
the existing final capital decision record**. No separate allocation engine,
scoring model, ranking layer, or optimizer is introduced.

### Reason

Pilot 1 demonstrated strong research and process coherence but **insufficient
explicit linkage between the evidence and the human dollar split**. The gap was
in what got recorded, not in the machinery — so the fix belongs in the record,
not in a new engine.

### What was added

Five fields on the `FINAL_CAPITAL_DECISION` object:

- `why_this_vs_alternatives` — why own this instead of the live alternatives
- `why_this_size` — why approximately this position size (qualitative)
- `allocation_wrong_if` — what observable evidence would weaken it
- `allocation_rationale_status` — `RATIONALE_COMPLETE` or `EXPLORATORY_LOW_RATIONALE`
- `why_not_this_increment` — for a finalist that received no capital

### Consequences

- Funded paper lines missing rationale are **preserved** and flagged
  `EXPLORATORY_LOW_RATIONALE`. Nothing is backfilled.
- A future controlled live-capital pilot requires all three funded-line fields
  before a funded `INITIATE`/`ADD` is decision-ready.
- Unfunded finalists are **never** auto-classified as rejected, and no ranking
  may be inferred from any field.
- Human allocation authority is unchanged. Rationale text cannot alter a dollar
  amount or a position weight.

### Implementation note

`AllocationDecisionRecord` **subclasses** the control layer's `DecisionRecord`
rather than modifying it, so `stock_atlas/` remains byte-identical to the
Red-Team-accepted archive. The added fields still flow into the record hash and
the append-only ledger, because `canonical_payload` serialises via `asdict()`
and `append` re-hashes via `dataclasses.replace()`.

### Explicitly not built

Allocation score · conviction score · sentiment score · sizing formula ·
optimization routine · ranking layer · automated recommendation · probability
engine · new Stage 8 module · second capital-allocation model.

---

## `PILOT1_DECISION_RECORD_SCOPE_CLARIFICATION`

| | |
|---|---|
| Date | 2026-09-03 |
| Status | **ACCEPTED** |
| Context | Records-scope clarification following Pilot 1 closeout |

### Decision

The **September 1 Treasury/Cash decision is the canonical Pilot 1 Stage 8
record.** The September 3 allocation is a **separate post-Pilot-1 paper
calibration decision.** Neither supersedes the other.

### Reason

The two decisions used different dates, different opportunity universes, and
different purposes. Preserving this distinction prevents hindsight
contamination and incorrect Pilot 1 outcome attribution.

### The two records

| | Canonical Pilot 1 Stage 8 | Post-Pilot-1 calibration |
|---|---|---|
| Date | September 1, 2026 | September 3, 2026 |
| Universe | Frozen Pilot 1 33-stock discovery process / resulting Opportunity Set | HBR / Tencent / VEON / CRM plus SPY / Treasury / Do Nothing |
| Decision | $50,000 → Treasury/Cash Sleeve | Tencent $25k · VEON $10k · SPY $10k · 1-Yr Treasury $5k |
| Artifact | `pilot1/PILOT1_STAGE8_HUMAN_DECISION_001.md` | `pilot1/PILOT1_SEPT3_ALLOCATION_RECORD_001.md` |
| Authority | **Authoritative Pilot 1 Stage 8 decision** | Calibration exercise only |

`PILOT1_STAGE8_HUMAN_DECISION_001.md` is not superseded, rewritten, or
reconciled with the September 3 decision.

### Filename provenance note

`PILOT1_SEPT3_ALLOCATION_RECORD_001.md` was initially labeled within Pilot 1
during closeout. Historical review established that the underlying September 3
allocation was a separate post-Pilot-1 paper decision using a different
opportunity universe. **The artifact remains unchanged for provenance**, but it
must not be interpreted as superseding or replacing the September 1 Pilot 1
Stage 8 decision.

Its filename and path therefore under-describe its scope by accident of
sequencing. Renaming it would destroy provenance; this entry is the correction
of record. The artifact's own "Relationship to
`PILOT1_STAGE8_HUMAN_DECISION_001.md`" section predates this clarification and
is superseded **by this entry only** — the artifact text itself stays as
committed.

### Why the September 3 decision still matters

It exposed the Stage 8 rationale gap that produced
`ALLOCATION_BRIDGE_AS_FIELDS_NOT_ENGINE`. It remains a valid historical test
case for missing-rationale behaviour, `EXPLORATORY_LOW_RATIONALE`, absence of
synthetic rationale, and human allocation authority — but it is not the
canonical Pilot 1 Stage 8 decision, and test fixtures name it accordingly
(`POST_PILOT1_SEPT3_ALLOCATION`).

### Scope

Records-scope clarification only. Not an architecture reopening. Pilot 1
remains `FROZEN / COMPLETE`.
