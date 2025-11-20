# Bug: Partial Opponent Laps Written When Joining Mid-Session

## Status: ✅ RESOLVED

**Resolved:** 2025-11-20
**Branch:** claude/fix-opponent-lap-bugs-01KA5DeHo42w58EfwoEWbuLs

**Solution:**
1. Added `seen_lap_start` flag to opponent tracking data structure to track whether we've observed the opponent at the start of a lap (within first 5% of track distance).
2. Implemented lap start detection: when `lap_distance < 0.05 * track_length`, set `seen_lap_start = True`.
3. On lap completion, check if `seen_lap_start` is True before saving the lap. If False (partial lap), discard the samples and reset for the next lap.
4. This ensures only complete laps (tracked from start to finish) are saved, preventing partial lap data when joining mid-session.

**Changes:**
- `src/opponent_tracker.py:89` - Added `seen_lap_start` flag to opponent tracking structure
- `src/opponent_tracker.py:121-127` - Check and discard partial laps on completion
- `src/opponent_tracker.py:161-162` - Detect lap start based on lap distance threshold
- `tests/test_opponent_tracker.py` - Added tests:
  - `test_partial_lap_discarded_when_joining_mid_race`
  - `test_lap_start_detection_with_various_distances`

---

## Summary
When joining a multiplayer session mid-race, opponent lap files are created for incomplete laps. This happens because we start collecting telemetry samples from opponents mid-lap, and when they cross the finish line, we write their partial lap data (missing the beginning of the lap).

## Current Behavior
1. User joins multiplayer session (race already in progress)
2. Application starts collecting opponent telemetry samples
3. Opponents are mid-lap when collection starts (e.g., 50% through lap 8)
4. When opponent crosses finish line, we have samples for only the last 50% of the lap
5. This partial lap is written to disk as a complete lap file
6. Process repeats for each opponent until they start a fresh lap from the start/finish line
7. Results in a stack of partial lap files in output directory

## Example Scenario
```
Session state: Race in progress, lap 8/20
- Driver A: 75% through lap 8 when we join
- Driver B: 40% through lap 8 when we join
- Driver C: 90% through lap 8 when we join

Files created (partial laps):
- driver_a_lap8_t67s.csv  (only last 25% of lap 8)
- driver_b_lap8_t42s.csv  (only last 60% of lap 8)
- driver_c_lap8_t89s.csv  (only last 10% of lap 8)

Then complete laps:
- driver_a_lap9_t95s.csv  (complete lap 9) ✓
- driver_b_lap9_t96s.csv  (complete lap 9) ✓
- driver_c_lap9_t94s.csv  (complete lap 9) ✓
```

## Expected Behavior
- **Discard partial laps** - Don't save opponent laps until we've tracked them through a complete lap from start to finish
- Only save opponent laps where we have telemetry data from lap start (lap distance ~0m) to lap end (lap distance ~track_length)

## Root Cause
The `OpponentTracker` doesn't track whether we've seen the opponent start a lap:

```python
# src/opponent_tracker.py:96
if current_lap > opponent['current_lap'] and opponent['current_lap'] > 0:
    lap_time = telemetry.get('last_lap_time', 0.0)

    # This triggers even if we only have partial lap data!
    if is_fastest:
        lap_data = OpponentLapData(...)
        completed_laps.append(lap_data)
```

## Proposed Solution

### Option 1: Track Lap Start Detection (Recommended)
Add a flag to track whether we've seen the lap start:

```python
# In OpponentTracker.__init__
self.opponents[driver_name] = {
    'current_lap': 0,
    'samples': [],
    'fastest_lap_time': float('inf'),
    'lap_start_timestamp': timestamp,
    'seen_lap_start': False,  # NEW FLAG
}

# In update_opponent, detect lap start
lap_distance = telemetry.get('lap_distance', 0.0)
track_length = telemetry.get('track_length', 1000.0)

# Detect lap start (within first 5% of lap)
LAP_START_THRESHOLD = 0.05 * track_length
if lap_distance < LAP_START_THRESHOLD:
    opponent['seen_lap_start'] = True

# On lap completion, only save if we saw the start
if current_lap > opponent['current_lap'] and opponent['current_lap'] > 0:
    if opponent['seen_lap_start']:  # Only save complete laps
        # ... existing save logic ...
    else:
        print(f"[DEBUG] Discarding partial lap for {driver_name} (joined mid-lap)")

    # Reset flag for next lap
    opponent['seen_lap_start'] = False
```

### Option 2: Minimum Sample Count Threshold
Require a minimum number of samples (e.g., 90% of expected samples):

```python
MIN_LAP_SAMPLES = 90  # At 100Hz, ~90 samples = 90% of typical lap
if len(opponent['samples']) < MIN_LAP_SAMPLES:
    print(f"[DEBUG] Discarding partial lap (only {len(opponent['samples'])} samples)")
    opponent['samples'] = []
    return []
```

**Problem**: This doesn't work well because lap times vary greatly. A 60s lap at 100Hz = 6000 samples, but a 120s lap = 12000 samples.

### Option 3: Check Lap Distance Coverage
Verify we have samples covering most of the track:

```python
def _is_complete_lap(samples: List[Dict], track_length: float) -> bool:
    """Check if samples cover at least 90% of track"""
    if not samples:
        return False

    min_distance = min(s.get('LapDistance [m]', 0) for s in samples)
    max_distance = max(s.get('LapDistance [m]', 0) for s in samples)

    coverage = (max_distance - min_distance) / track_length
    return coverage >= 0.9  # At least 90% coverage
```

## Recommendation
**Use Option 1** (Track Lap Start Detection):
- Most reliable detection method
- Low overhead (just checking lap_distance)
- Clear intent and easy to understand
- Works regardless of lap time or sample rate

## Files to Modify
- `src/opponent_tracker.py:83-89` - Initialize `seen_lap_start` flag
- `src/opponent_tracker.py:96-134` - Add lap start detection and partial lap filtering
- `tray_app.py:167-239` - May need to handle `None` return from opponent tracker

## Testing
1. Join multiplayer session mid-race (at least lap 3+)
2. Verify no partial opponent laps are saved
3. Wait for opponents to complete their current lap
4. Verify next lap (first complete lap) IS saved
5. Check lap files to ensure data starts from ~0m lap distance
6. Verify lap distance coverage is ~95-100% of track length

## Priority
**High** - Data quality issue. Partial laps are misleading and waste disk space. Users expect only complete, valid laps.

## Related Issues
- Related to bug_multiple_opponent_laps_captured.md - partial laps may contribute to duplicate lap problem
- Related to opponent filename format - should include lap time to identify partial vs complete laps

## Related Files
- `/home/user/eztel-writer/src/opponent_tracker.py:62-147` - Main update logic
- `/home/user/eztel-writer/tray_app.py:167-239` - Opponent lap callback
- `/home/user/eztel-writer/src/session_manager.py` - Similar logic for player laps (may have same issue?)
