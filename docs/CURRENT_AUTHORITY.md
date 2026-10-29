# Stock Atlas — current authority

**One reference for what governs current work.** Everything else is evidence or history. It does not replace the Master Plan; it says which Master Plan state, which controls, which baseline and which restrictions are *currently approved*, and it is **verified by machine**:

```bash
python -m atlas_ui preflight        # run before any major assignment (fails on control, baseline, restriction or append-only drift)
python -m atlas_ui verify           # preflight + the offline regression suite, with skips classified (add --clean-extract to prove a clean copy)
python -m atlas_ui deliver          # one ZIP + patch + DELIVERY.md for the current HEAD, verified from the extracted ZIP
```

**Rules**
1. *Newest commit is not approved state.* `approved_state.commit` is the last state the human accepted. `preflight` always prints how far HEAD is ahead of it and which governed files changed since. Only the human moves it.
2. *Later approved records supersede older handoffs; older files stay intact.* Anything under `historical_not_governing` cannot direct current work, however it is worded ("NEXT", "active task", "Sprint 2").
3. *Controls change only through a change record* (`controls.authorized_changes`); the pin file, this block and the change record move together.
4. *After each major improvement* add one dated **Milestone review** section to the Master Plan (what changed and was verified / incomplete or potentially overlooked / next) and update the capability matrix. Minor fixes do not need one. Nothing else is created.
5. Paper only. No real trades. No new provider, agent, ML or architecture without explicit authorization.

<!-- The block below is parsed by `atlas_ui/verify.py`. Edit it deliberately; a bad edit fails preflight. -->
```json
{
  "schema": 1,
  "mission": {
    "doc": "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md",
    "section": "## Governing Mission"
  },
  "approved_state": {
    "commit": "8cbcb37c82ac6367415d517f2938cf2d0c50e2d5",
    "status": "WORKING BASELINE: the human directed on 2026-10-29 that work proceed from this commit; independent acceptance of it has not been reported",
    "update_rule": "Changed only by an explicit human acceptance, quoted in the Decision Log. A commit existing, or its tests passing, never approves it."
  },
  "documents": {
    "master_plan": "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md",
    "decision_log": "docs/STOCK_ATLAS_DECISION_LOG.md",
    "doctrine": "docs/STOCK_ATLAS_ONE_PAGE_DOCTRINE_001.md",
    "capability_matrix": "atlas_ui/CAPABILITY_MATRIX.md"
  },
  "append_only": [
    "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md",
    "docs/STOCK_ATLAS_DECISION_LOG.md"
  ],
  "plan_markers": {
    "top_pointer": "docs/CURRENT_AUTHORITY.md",
    "immediate_next_actions_heading": "## Immediate Next Actions",
    "immediate_next_actions_superseded": "SUPERSEDED AS THE ACTIVE WORK LIST (2026-10-29)"
  },
  "portfolio_baseline": {
    "doc": "docs/controlled_live_pilot/CYCLE0_BASELINE_001.md",
    "canonical": "Cycle 0 Correction 002 (2026-10-07)",
    "sha256": "ef35534d5e04f8d49f1f4043bbf01d85e630c661707e49938131487ef38a0f5e",
    "holdings": 28,
    "stocks_total": "624905.93",
    "identified_value_approx": "683905.93",
    "policy": "ADD-ONLY; $25-50K outside capital T+1; defensive assets about $59K (approximate)",
    "historical_not_current": "the September 2026 $500,000 eight-stock handoff snapshot"
  },
  "controls": {
    "pin_file": "atlas_ui/FROZEN_CONTROL_SHA256.txt",
    "pin_file_sha256": "1865b8feb46dd4f0d6a2d809cf4672de5b6415c7508d4d26a16a0a5e0108eec1",
    "files": 12,
    "authorized_changes": [
      {
        "id": "001",
        "record": "docs/controlled_live_pilot/FROZEN_CONTROL_CHANGE_001.md"
      },
      {
        "id": "002",
        "record": "docs/controlled_live_pilot/FROZEN_CONTROL_CHANGE_002_PROPOSED.md"
      },
      {
        "id": "003",
        "record": "docs/controlled_live_pilot/FROZEN_CONTROL_CHANGE_003.md"
      }
    ],
    "rule": "A control file may change only with a pre-change record and explicit human authorization; the pin file and this entry are then updated in the same commit."
  },
  "candidates": {
    "ledger": "operating_mvp/data/candidate_ledger.jsonl",
    "parked": {
      "MCD": "2026-11-04",
      "RPM": "2026-11-09"
    },
    "rule": "Parked dates are revisit triggers, never promotions."
  },
  "capital": {
    "status": "NO REAL PORTFOLIO ACTION",
    "decision_ledger": "atlas_ui/data/live/decisions.jsonl",
    "canonical_decision_rows": 0
  },
  "active_work": {
    "plan_heading_prefix": "### October 28, 2026 — Backend-first completion to an evidence-based opportunity UI",
    "summary": "Backend-first completion: Priority 0 latest-source discipline, 1 funded-decision safety, 2 primary-source research to underwriting, 3 unranked multi-candidate research view, 4 outcome learning; sequential release gates 1-5.",
    "state": "Gate 1 safety remediated (changes 001-003) and awaiting independent acceptance; gate 2 passed read-only; gate 3 reached with limits; gate 4 view only; gate 5 partial. Stop points: independent review after each delivery."
  },
  "last_milestone_review": {
    "plan_heading": "### October 29, 2026 — Milestone review",
    "reviewed_commit": "18f44d7be6e9df512a0880c9532e35186fac4def"
  },
  "historical_not_governing": [
    {
      "where": "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md",
      "section": "## Immediate Next Actions",
      "reason": "The Pilot 2 work list ('Current active task: EXECUTE PILOT 2'). Pilot 2 and the pilots after it are closed; active_work above governs."
    },
    {
      "where": "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md",
      "section": "Pilot 1-5, Post-Pilot-1 and Control Validation sections",
      "reason": "Completed pilot records, kept for provenance."
    },
    {
      "glob": "docs/pilot*",
      "reason": "Pilot 1-5 working records."
    },
    {
      "glob": "docs/manual_pilot_v0_1",
      "reason": "Manual pilot v0.1 records."
    },
    {
      "glob": [
        "README.md",
        "INDEX.md",
        "SPRINT_1_*.md",
        "DELIVERY_SUMMARY.md",
        "V2_CRITICAL_CORRECTIONS.md",
        "V3_DELIVERY.md",
        "V3_STATIC_AUDIT.md",
        "LIVE_EXECUTION_GUIDE.md",
        "LIVE_RUN_README.md",
        "LIVE_VALIDATION_CORRECTIONS.md",
        "METHODOLOGY_ISSUES.md",
        "PACKAGE_MANIFEST.md",
        "CORRECTIONS_SUMMARY.txt"
      ],
      "reason": "Sprint 1-era handoffs. Their 'Sprint 2' instructions (DCF/valuation, 'approve Sprint 2') were never made active by the approved plan and do not govern current work."
    },
    {
      "glob": "deliverables",
      "reason": "Local review packages (untracked); each is superseded by the commit it describes."
    }
  ]
}
```
