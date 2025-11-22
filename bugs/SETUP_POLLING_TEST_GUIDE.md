# Setup Polling Test Guide

**Purpose:** Test if LMU REST API is available on-track and reflects HUD changes

**Tools Created:**
- `tools/test_setup_polling.py` - Continuous monitoring (detects changes in real-time)
- `tools/test_setup_snapshot.py` - Single snapshots (compare garage vs. on-track)

---

## Prerequisites

1. **Windows machine** with LMU installed
2. **LMU REST API enabled** (should be by default on port 6397)
3. **Monitor repository** cloned and Python environment set up
4. **Car and track** loaded in LMU

---

## Test 1: Continuous Monitoring (Recommended)

**This is the easiest way to see changes in real-time.**

### Steps

1. **Start LMU and load a car/track**

2. **Go to GARAGE and load a setup**

3. **In Windows terminal, navigate to monitor directory:**
   ```cmd
   cd C:\path\to\monitor
   venv\Scripts\activate
   ```

4. **Run the continuous polling tool:**
   ```cmd
   python tools/test_setup_polling.py --interval 2
   ```

5. **Verify garage behavior:**
   ```
   Expected output:
   ✅ REST API available
   ✅ Setup data received
   📊 Adjustable Parameters (X found):
     • VM_TRACTION_CONTROL: 7 (7.00)
     • VM_BRAKE_BALANCE: 56.5% (0.565)
     ...
   ```

6. **Start a session and go ON-TRACK**
   - Leave the script running
   - Watch the output

7. **Check on-track availability:**
   ```
   Question: Does script still show setup values?
   ✅ YES = REST API works on-track
   ❌ NO  = REST API only works in garage
   ```

8. **Change traction control via in-game HUD:**
   - Use in-game controls to change TC from 7 → 4
   - Watch the script output

9. **Check if change detected:**
   ```
   Expected if API reflects changes:
   🔄 VM_TRACTION_CONTROL
       OLD: 7 (7.00)
       NEW: 4 (4.00) ⬅️ CHANGED!
   ```

10. **Try other HUD changes:**
    - Brake bias
    - ABS settings
    - Fuel mixture (if adjustable)
    - Watch for changes in script output

11. **Press Ctrl+C to stop when done**

### What We Learn

- ✅ **Script shows values on-track** → API available on-track
- ❌ **Script shows "No setup data" on-track** → API only works in garage
- ✅ **Script detects HUD changes** → API reflects real-time changes
- ❌ **Script doesn't detect HUD changes** → API shows stale data

---

## Test 2: Snapshot Comparison (Alternative)

**Use this if you want to compare files side-by-side.**

### Steps

1. **Start LMU, load car/track**

2. **In GARAGE, load a setup**

3. **Take garage snapshot:**
   ```cmd
   python tools/test_setup_snapshot.py --output garage.json
   ```

4. **Start a session, go ON-TRACK**

5. **Take on-track snapshot (before HUD changes):**
   ```cmd
   python tools/test_setup_snapshot.py --output ontrack_before.json
   ```

6. **Change TC via HUD (e.g., 7 → 4)**

7. **Take on-track snapshot (after HUD change):**
   ```cmd
   python tools/test_setup_snapshot.py --output ontrack_after.json
   ```

8. **Compare files:**
   ```cmd
   # Check if on-track works
   diff garage.json ontrack_before.json

   # Check if HUD changes are detected
   diff ontrack_before.json ontrack_after.json
   ```

### What We Learn

- **`ontrack_before.json` exists** → API works on-track ✅
- **`ontrack_before.json` empty/error** → API doesn't work on-track ❌
- **Diff shows TC changed from 7 to 4** → API reflects HUD changes ✅
- **Diff shows no changes** → API doesn't reflect HUD changes ❌

---

## Expected Results

### Scenario A: Full Support ✅ (Best Case)

**On-track availability:** ✅ YES
**Reflects HUD changes:** ✅ YES

**Conclusion:** We can implement periodic polling. Changes made via HUD will be detected and published to dashboard.

**Next steps:** Implement periodic polling (5-10s interval) with change detection.

---

### Scenario B: On-track available, but stale data ⚠️

**On-track availability:** ✅ YES
**Reflects HUD changes:** ❌ NO

**Conclusion:** API works on-track but shows garage values, not live changes.

**Implications:**
- Polling will show initial setup but not HUD adjustments
- Dashboard will show incorrect TC/brake bias if changed on-track
- May need to warn users that HUD changes aren't synced

**Next steps:**
- Document limitation
- Consider showing setup with disclaimer
- Maybe add "last updated in garage" timestamp

---

### Scenario C: Garage-only API ❌

**On-track availability:** ❌ NO
**Reflects HUD changes:** N/A (can't test if API unavailable)

**Conclusion:** REST API only works in garage, not during sessions.

**Implications:**
- Can't poll during race
- Setup only available at session start
- Can't detect HUD changes

**Next steps:**
- Keep current behavior (one-time fetch at session start)
- Document that HUD changes won't sync
- Consider alternative data sources (shared memory?)

---

## Reporting Results

After testing, please report:

1. **Which test you ran** (continuous monitoring or snapshots)
2. **On-track availability** (did API work while on-track?)
3. **HUD change detection** (did TC change from 7→4 get detected?)
4. **Any error messages** (if things didn't work)
5. **LMU version** (which version are you running?)

**Report format:**
```
Test: Continuous monitoring (test_setup_polling.py)
LMU Version: 1.1.4.0

On-track availability: YES/NO
HUD change detection: YES/NO

Details:
- In garage: Saw 172 parameters including TC=7
- On-track: [Still saw parameters / Got "no setup data" error]
- After HUD change (TC 7→4): [Detected change / No change detected]

Notes: [Any other observations]
```

---

## Troubleshooting

### "REST API not available"

**Causes:**
- LMU not running
- REST API disabled in LMU settings
- Wrong port (not 6397)

**Fix:**
1. Verify LMU is running
2. Check LMU settings → Plugins → REST API enabled
3. Try accessing http://localhost:6397/rest/sessions in browser

### "No setup data returned"

**Possible reasons:**
- No setup loaded (go to garage, load a setup)
- On-track and API doesn't work during sessions (this is what we're testing!)
- API endpoint changed in newer LMU version

### Script crashes

**Report the error with:**
- Full error message
- LMU version
- What you were doing (garage, on-track, etc.)

---

## Next Steps After Testing

Based on test results:

1. **Report findings** in bug file or to developer
2. **Update `periodic_setup_updates.md`** with findings
3. **Decide implementation approach:**
   - Full support → Periodic polling
   - Partial support → Documented limitations
   - No support → Keep current behavior
4. **Implement solution** (if feasible)

---

## Questions These Tests Answer

- ✅ Can we poll setup data during a race?
- ✅ Do HUD changes update the REST API values?
- ✅ Which parameters are adjustable on-track?
- ✅ How fast does the API reflect changes? (polling interval test)
- ✅ Is there any performance impact from polling?

---

**Ready to test?** Run Test 1 (Continuous Monitoring) - it's the easiest and gives real-time feedback!
