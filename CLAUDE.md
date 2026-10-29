# Stock Atlas — standing instructions for Claude Code sessions

**Authority.** `docs/CURRENT_AUTHORITY.md` is the single reference for what governs current work (approved Master Plan state, portfolio baseline, frozen controls, candidate restrictions, active work). Older handoffs, Pilot 1–5 material, and "Sprint 1/2" documents are historical and never direct current work; the newest commit is not the approved state.

**Before any major assignment** run `python -m atlas_ui preflight` (use `.venv/bin/python` if `python` is not on PATH). If it reports FAIL, stop and report; do not work around it.

**Rules that do not change** (details in the authority reference and the Master Plan): paper only, no real trades; Human Stage 8 is sole capital authority; append-only records; no change to a frozen control without a pre-change record and explicit authorization; no new provider, agent, ML or architecture; fix demonstrated problems, keep a regression test for each; never print or store credentials; label price evidence uncertified when the key is absent.

**After each major improvement** add one dated "Milestone review" section to the Master Plan (what changed and was verified / incomplete or potentially overlooked / what to do next), update `atlas_ui/CAPABILITY_MATRIX.md` (via `atlas_ui/app.py:CAPABILITIES`), and run `python -m atlas_ui verify --clean-extract`. Deliver with `python -m atlas_ui deliver` (one ZIP, one patch, one DELIVERY.md), then stop for independent review. Minor bug fixes need none of this.
