# Stock Atlas Sprint 1 — Live SEC Validation

**Welcome!** This is the Stock Atlas validation package. It will test the system against real SEC data to confirm everything works correctly.

**Time required**: ~5-10 minutes  
**Internet required**: Yes (SEC EDGAR access)  
**Technical knowledge required**: Minimal  

---

## Quick Start (3 Steps)

### Step 1: Download and Extract

Download `stock-atlas-sprint1-live.zip` and extract it:

```bash
unzip stock-atlas-sprint1-live.zip
cd stock-atlas-sprint1-live
```

### Step 2: Setup Environment

Run the setup script once:

```bash
bash setup_live.sh
```

This will:
- ✓ Check Python installation
- ✓ Create a virtual environment
- ✓ Install dependencies
- ✓ Create required directories

**If setup asks you to edit .env:**

```bash
# Open .env in a text editor
nano .env
```

Find this line:
```
SEC_USER_AGENT=Project Stock Atlas contact-email@example.com
```

Replace `contact-email@example.com` with your actual email address, then save.

Example:
```
SEC_USER_AGENT=Project Stock Atlas john.doe@company.com
```

### Step 3: Run Live Validation

```bash
bash run_live_validation.sh
```

The script will:
1. ✓ Connect to SEC EDGAR
2. ✓ Download real Microsoft financial data
3. ✓ Run 8 validation tests
4. ✓ Save results to `live_validation_results/`

---

## What Gets Tested

The validation checks 8 things:

| Test | Purpose |
|------|---------|
| Live SEC Connection | Can we reach SEC? |
| MSFT Security Resolution | Is Microsoft found? |
| MSFT 10-K Ingestion | Can we download the annual report? |
| MSFT 10-Q Ingestion | Can we download the quarterly report? |
| XBRL Normalization | Are financial fields correct? |
| FCF Provenance | Can we trace every calculation back to SEC? |
| Timestamp PIT Test | Does time precision work correctly? |
| Real Restatement Test | Are corrections handled properly? |

---

## Understanding Results

### Success (All Green)

If you see:
```
LIVE SEC CONNECTION:      PASS ✓
MSFT SECURITY RESOLUTION: PASS ✓
MSFT 10-K INGESTION:      PASS ✓
MSFT 10-Q INGESTION:      PASS ✓
XBRL NORMALIZATION:       PASS ✓
FCF PROVENANCE:           PASS ✓
TIMESTAMP PIT TEST:       PASS ✓
REAL RESTATEMENT TEST:    PASS ✓

SPRINT 1 FINAL STATUS: PASS ✓
```

**Congratulations!** All tests passed. The system is ready.

### Failure (See Errors)

If you see any test marked `FAIL`, check the results file for details:

```bash
cat live_validation_results/latest_validation_results.md
```

Look for the `BLOCKING ISSUES` section and share that with the team.

---

## Where Results Are Saved

After validation runs, check:

```
live_validation_results/
  ├── YYYYMMDD_HHMMSS_validation_results.md    # Human-readable report
  ├── YYYYMMDD_HHMMSS_validation_results.json  # Machine-readable data
  └── raw_logs.txt                              # Complete output log
```

**Send the `.md` file to the team** — it has everything they need to see.

---

## Troubleshooting

### Error: "Python 3 not found"

Install Python:
- **Windows**: https://www.python.org/downloads/
- **Mac**: `brew install python3`
- **Linux**: `apt-get install python3`

### Error: "SEC connection failed"

Check your internet connection:
```bash
ping data.sec.gov
```

If that works but validation fails, SEC may be temporarily unavailable. Try again in a few minutes.

### Error: "MSFT not found"

This shouldn't happen, but if it does, share the error message with the team.

---

## Advanced: Interpreting the Report

If you're curious about the results, the markdown report includes:

- **Executive Summary** — Overall status
- **Test Details** — Each test's results and why
- **Blocking Issues** — Problems that stop the system (usually none)
- **Non-Blocking Issues** — Notes for later (usually none)
- **Recommendations** — What's next

---

## What NOT to Do

❌ Don't edit Python files  
❌ Don't modify the source code  
❌ Don't add external API keys (SEC doesn't need them)  
❌ Don't run validation twice simultaneously  

---

## What to Do if Something Goes Wrong

1. **Read the error message** in the terminal
2. **Check the results file** (see "Where Results Are Saved" above)
3. **Send the `.md` file to the team** with a note about what happened

The validation is designed to fail gracefully with clear error messages.

---

## One More Thing

This validation tests **SEC data only**. It does NOT test:
- Market prices (coming next)
- Macroeconomic data (coming next)
- Portfolio calculations (Sprint 2)
- Investment decisions (Sprint 2)

If SEC validation passes, you're good to go for the next phase.

---

## Questions?

If anything is unclear:
1. Check the troubleshooting section above
2. Review the results file
3. Contact the project team with the results file attached

---

**That's it!** Run the setup script, add your email, and run the validation. The system will do the rest.

```bash
bash setup_live.sh
# Edit .env with your email
bash run_live_validation.sh
# Check live_validation_results/
```

Good luck! 🚀
