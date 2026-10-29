# Stock Atlas — current authority

**One reference for what governs current work.** Everything else is evidence or history. It does not replace the Master Plan; it says which Master Plan state, which controls, which baseline and which restrictions are *currently approved*, and it is **verified by machine**:

```bash
python -m atlas_ui preflight        # run before any major assignment (fails on control, baseline, restriction or append-only drift)
python -m atlas_ui verify           # preflight + the offline regression suite, with skips classified (add --clean-extract to prove a clean copy)
python -m atlas_ui deliver          # one ZIP + patch + DELIVERY.md for the current HEAD; FAILS if either preflight or either test run fails
python -m atlas_ui authority show   # the resolved approved state, portfolio snapshot, active work and candidate status
```

**Rules**
1. *Newest commit is not approved state.* The approved state is the latest HUMAN-approved `APPROVED_STATE` event in `docs/authority_register.jsonl` (the last state the human accepted). `preflight` prints how far HEAD is ahead of it and which governed files changed since. Only the human moves it, by instructing that an event be appended with their words.
2. *Operating values are records, not code or text in this file.* The approved state, portfolio snapshot, active work and candidate-ledger acceptance live in the register: append-only, hash-chained, never edited. The latest **approved** record governs; a record without a valid HUMAN approval is a draft and is never followed; a newer record supersedes only by naming its predecessor; conflicting approved records fail closed. Superseded records stay loadable, so any past analysis can be reconstructed. A new snapshot or a candidate status change is a data append, not a software change (`python -m atlas_ui authority show | append`).
3. *A revisit date is a trigger to reassess, never an authorization or a promotion.*
4. *Later approved records supersede older handoffs; older files stay intact.* Anything under `historical_not_governing` cannot direct current work, however it is worded ("NEXT", "active task", "Sprint 2").
5. *Controls change only through a change record* (`controls.authorized_changes`); the pin file, this block and the change record move together. Controls are not operating values and are deliberately pinned here.
6. *After each major improvement* add one dated **Milestone review** section to the Master Plan (what changed and was verified / incomplete or potentially overlooked / next) and update the capability matrix. Minor fixes do not need one. Nothing else is created.
7. Paper only. No real trades. No new provider, agent, ML or architecture without explicit authorization.
8. *Publishing.* The private GitHub repository `ChrisNyers/Project-Stock-Atlas` (`origin`, branch `main`) is the shared copy for Claude and ChatGPT. Push only after the human has independently reviewed and accepted a major milestone (and asked for it to be published); a new commit is never published automatically. Never force-push or rewrite history. Before any push: `preflight` passes, and no `.env`, key, credential or `deliverables/` content is tracked. GitHub `main` can be ahead of the approved state: the approved state is the register's latest approved `APPROVED_STATE`, never the branch tip. After a push, confirm `git ls-remote origin` equals local `HEAD`.

<!-- The block below is parsed by `atlas_ui/verify.py`. Edit it deliberately; a bad edit fails preflight. -->
```json
{
  "schema": 1,
  "mission": {
    "doc": "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md",
    "section": "## Governing Mission"
  },
  "register": "docs/authority_register.jsonl",
  "documents": {
    "master_plan": "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md",
    "decision_log": "docs/STOCK_ATLAS_DECISION_LOG.md",
    "doctrine": "docs/STOCK_ATLAS_ONE_PAGE_DOCTRINE_001.md",
    "capability_matrix": "atlas_ui/CAPABILITY_MATRIX.md"
  },
  "append_only": [
    "docs/STOCK_ATLAS_MASTER_PROJECT_PLAN.md",
    "docs/STOCK_ATLAS_DECISION_LOG.md",
    "docs/authority_register.jsonl"
  ],
  "plan_markers": {
    "top_pointer": "docs/CURRENT_AUTHORITY.md",
    "immediate_next_actions_heading": "## Immediate Next Actions",
    "immediate_next_actions_superseded": "SUPERSEDED AS THE ACTIVE WORK LIST (2026-10-29)"
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
    "rule": "Status is read from the candidate ledger as the register accepts it. A revisit date is a trigger to reassess, never a promotion."
  },
  "capital": {
    "decision_ledger": "atlas_ui/data/live/decisions.jsonl"
  },
  "milestone_review_marker": "Milestone review",
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
