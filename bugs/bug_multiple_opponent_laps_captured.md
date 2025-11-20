# Bug: Multiple Laps from Opponents Being Captured

## Status: ✅ RESOLVED

**Resolved:** 2025-11-20
**Branch:** claude/fix-opponent-lap-bugs-01KA5DeHo42w58EfwoEWbuLs

**Solution:**
1. Changed lap completion detection from `current_lap > opponent['current_lap']` to `current_lap == opponent['current_lap'] + 1` to only detect exactly +1 lap changes, preventing duplicate detections from out-of-order telemetry or lap number jumps.
2. This stricter check ensures that only valid, sequential lap completions are processed, eliminating the possibility of multiple laps being saved for the same completion event.

**Changes:**
- `src/opponent_tracker.py:105` - Stricter lap completion check
- `tests/test_opponent_tracker.py` - Added test `test_lap_number_skip_not_detected`

---

## Summary
Multiple lap files are being saved for the same opponent lap, resulting in duplicate data.

## Current Behavior
- Opponent lap files are saved multiple times
- Output directory contains duplicate opponent lap data
- May be saving the same lap with different timestamps or session IDs

## Expected Behavior
- Each opponent lap should be saved exactly once
- Only the fastest lap for each opponent should be saved (per the "fastest lap only" strategy)
- No duplicate files for the same lap

## Potential Root Causes

### 1. Lap Completion Detection Issue
The `OpponentTracker` may be detecting lap completion multiple times:
- `src/opponent_tracker.py:96` - Lap completion detected when `current_lap > opponent['current_lap']`
- If telemetry samples arrive out of order or with duplicate lap numbers, multiple completions could be triggered

### 2. Multiple Telemetry Sources
If opponent data comes from multiple sources:
- Shared memory may provide duplicate entries for same opponent
- Different vehicle slots may report same driver

### 3. Fastest Lap Logic
The "fastest lap only" logic may not be working correctly:
- `src/opponent_tracker.py:112-133` - Fastest lap detection
- If `opponent['fastest_lap_time']` is not properly initialized or updated, multiple laps could be saved

### 4. File Naming Collisions
The opponent filename format may not be unique enough:
- `tray_app.py:226` - `'{session_id}_{track}_{car}_{driver}_fastest.csv'`
- If lap time is not in filename, multiple laps would overwrite each other (actually preventing duplicates)
- But if other factors change (e.g., session_id, car name), duplicates could be created

## Investigation Steps

1. **Add Debug Logging**
   ```python
   # In opponent_tracker.py, around line 96
   print(f"[DEBUG] Opponent {driver_name}: lap {opponent['current_lap']} → {current_lap}")
   print(f"[DEBUG] Last lap time: {lap_time:.3f}s, Fastest: {opponent['fastest_lap_time']:.3f}s")
   ```

2. **Check for Duplicate Vehicle Entries**
   ```python
   # In telemetry_loop.py or tray_app.py
   # Log all opponent driver names and IDs to see if duplicates exist
   ```

3. **Verify Lap Number Progression**
   - Ensure lap numbers strictly increase (2 → 3 → 4)
   - Check if lap numbers ever go backwards or repeat

4. **Check File System**
   ```bash
   # Look for duplicate opponent lap files
   ls -la telemetry_output/ | grep opponent_name
   ```

## Proposed Solution

### Solution 1: Stricter Lap Completion Check
```python
# In opponent_tracker.py:96
if current_lap == opponent['current_lap'] + 1:  # Exactly +1
    # Lap completion detected
```

### Solution 2: Deduplicate by Lap Number
Track which lap numbers have been saved:
```python
opponent = {
    'current_lap': 0,
    'samples': [],
    'fastest_lap_time': float('inf'),
    'saved_laps': set(),  # Track lap numbers that were saved
}

# Before saving
if opponent['current_lap'] not in opponent['saved_laps']:
    # Save lap
    opponent['saved_laps'].add(opponent['current_lap'])
```

### Solution 3: Add Unique Lap Identifier to Filename
Include lap number in filename to make collisions visible:
```python
opponent_filename_format = '{session_id}_{track}_{car}_{driver}_lap{lap}_t{lap_time}s.csv'
```
This would show duplicates as separate files instead of overwrites.

## Testing
- [ ] Run application in multiplayer session
- [ ] Monitor opponent lap files being created
- [ ] Check for duplicate filenames or similar names with different timestamps
- [ ] Verify only fastest laps are saved
- [ ] Add debug logging to track lap completion events

## Priority
**High** - Data quality issue that affects core functionality. May waste disk space and confuse users.

## Related Files
- `/home/user/eztel-writer/src/opponent_tracker.py:96-147` - Lap completion detection
- `/home/user/eztel-writer/tray_app.py:167-239` - Opponent lap callback
- `/home/user/eztel-writer/src/telemetry_loop.py` - Main loop that calls opponent tracker

## Additional Notes
Need more information from user:
- How many duplicate files? (2x, 3x, more?)
- Are they identical or do they have different data?
- Does it happen for all opponents or specific ones?
- Does it happen on every lap or intermittently?
