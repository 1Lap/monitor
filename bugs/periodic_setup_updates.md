# Periodic Setup Updates

**Status:** 🔍 Investigation Needed
**Priority:** Medium
**Created:** 2025-11-22

## Problem

Dashboard does not update when car setup is changed during a session.

**User Report:**
> Changed traction control from "7" to "4" using in-game HUD while on-track. Dashboard did not reflect the change.

## Current Behavior

- Setup data is fetched **ONCE** when LMU process is detected
- Published to dashboard via WebSocket (`setup_data` event)
- Never updated again until monitor/LMU restarts
- `self.setup_sent = True` flag prevents re-fetching

**Code locations:**
- `monitor.py:186-188` - Initial setup fetch on LMU detection
- `monitor.py:272-286` - `_send_setup()` method with one-time flag
- `src/dashboard_publisher.py:87-107` - `publish_setup()` method

## Expected Behavior

Dashboard should reflect setup changes made during a session, either:
1. **Real-time updates** when setup changes (if detectable)
2. **Periodic polling** every few seconds (e.g., 5-10s)

## Investigation Needed

Before implementing, we need to answer:

### 1. Is REST API available while on-track? ✅ TESTED

**Test Results (2025-11-22):**
- ✅ REST API works in garage with setup loaded
- ❌ REST API returns "No setup data" when car loads onto track
- ❌ REST API NOT available during on-track sessions

**Conclusion:** REST API is **GARAGE-ONLY**, not available while on-track.

**Test output:**
```
[18:23:33] Poll #22
✅ REST API available
⚠️  No setup data returned
   - On-track? API may not be available during session
```

**Impact:** Cannot poll setup changes during race sessions via REST API.

### 2. Does REST API reflect HUD changes? ❌ CANNOT TEST

**Cannot test:** REST API doesn't work on-track, so we cannot test if it would reflect HUD changes.

**Original question:** Does API show new TC value after HUD change?
**Answer:** N/A - API not available on-track to poll for changes.

### 3. What fields can change on-track vs. garage?

**Likely changeable on-track via HUD:**
- Traction control (TC)
- Anti-lock brakes (ABS)
- Brake bias
- Fuel mixture
- Engine map

**Likely garage-only:**
- Spring rates
- Dampers
- Aero settings
- Gear ratios

**Question:** Do we need to track which fields are "live-adjustable" vs. "garage-only"?

## Proposed Solutions

### Option A: Periodic Polling (Simpler)

Poll REST API every 5-10 seconds, republish if data changed.

**Pros:**
- Simple to implement
- Catches all changes regardless of how they're made
- Works even if LMU doesn't expose change events

**Cons:**
- Constant polling may be wasteful
- 5-10s delay before dashboard updates
- Sends full setup blob even for single field change

**Implementation:**
```python
# In monitor.py main loop
SETUP_UPDATE_INTERVAL = 5.0  # seconds
last_setup_update = 0

while self.running:
    # ... existing telemetry code ...

    # Periodically re-fetch setup
    if current_time - last_setup_update >= SETUP_UPDATE_INTERVAL:
        if self.process_monitor.is_running():
            self._send_setup(force=True)
        last_setup_update = current_time
```

**Questions:**
- What polling interval? (5s, 10s, 30s?)
- Should we diff the setup and only publish if changed?
- Send full setup or just changed fields?

### Option B: Change Detection (More Efficient)

Only republish if setup data has changed from last fetch.

**Pros:**
- Reduces bandwidth (only publish when actually changed)
- Dashboard only processes updates when needed

**Cons:**
- Requires setup diffing logic
- Still need to poll to detect changes

**Implementation:**
```python
class Monitor:
    def __init__(self, ...):
        # ...
        self.last_setup_hash = None  # Track changes

    def _send_setup(self, force=False):
        """Fetch and send setup if changed"""
        setup = self.rest_api.fetch_setup_data()
        if not setup:
            return

        # Calculate hash to detect changes
        import hashlib
        setup_json = json.dumps(setup, sort_keys=True)
        current_hash = hashlib.md5(setup_json.encode()).hexdigest()

        # Only publish if changed (or forced)
        if force or current_hash != self.last_setup_hash:
            self.publisher.publish_setup(setup)
            self.last_setup_hash = current_hash
            print(f"[Monitor] Setup updated ({current_hash[:8]})")
```

### Option C: Field-Level Updates (Most Efficient)

Send only changed fields instead of full setup blob.

**Pros:**
- Minimal bandwidth
- Dashboard can animate/highlight changed values
- More granular change tracking

**Cons:**
- Requires new WebSocket event (`setup_update` vs `setup_data`)
- Dashboard must handle partial updates
- More complex implementation on both sides

**Implementation:**
```python
# New WebSocket event in DashboardPublisher
def publish_setup_update(self, changed_fields: Dict[str, Any]):
    """Publish partial setup update (changed fields only)"""
    self.sio.emit('setup_update', {
        'session_id': self.session_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'changes': changed_fields
    })
```

## Recommended Approach

**Start with Option B (Periodic Polling + Change Detection):**

1. Poll REST API every 5-10 seconds while LMU running
2. Diff against previous setup (hash comparison)
3. Only publish if setup actually changed
4. Send full setup blob (reuse existing `setup_data` event)

**Advantages:**
- Simple to implement (minimal code changes)
- Works with existing dashboard server
- Efficient (only publishes when changed)
- Good balance of simplicity and efficiency

**Future enhancement:** If field-level granularity is needed, add Option C later.

## Configuration

Add to `config.json`:
```json
{
  "setup_update_interval": 5,  // seconds, 0 to disable
}
```

## Testing Plan

1. **API availability test:** Check if REST API works on-track
2. **HUD change test:** Verify API reflects HUD changes
3. **Polling test:** Run monitor with periodic updates, change TC via HUD
4. **Change detection test:** Verify we don't spam unchanged setup
5. **Dashboard test:** Confirm dashboard UI updates when setup changes

## Files to Modify

- `monitor.py` - Add periodic setup polling in main loop
- `config.json.example` - Add `setup_update_interval` config
- `tests/test_monitor.py` - Add tests for periodic updates
- `CLAUDE.md` - Update documentation

## Open Questions

1. **What polling interval?** 5s, 10s, or user-configurable?
2. **Garage vs. on-track availability?** Need to test API behavior
3. **Full blob vs. field updates?** Start with full, optimize later?
4. **Handle API errors gracefully?** What if API unavailable mid-session?

## Next Steps

1. ✅ Create this bug file
2. ✅ Test REST API availability on-track vs. garage
3. ❌ Test if HUD changes are reflected in REST API (cannot test - API unavailable on-track)
4. ⏳ Investigate alternative data sources for on-track setup changes
5. ⏳ Decide on implementation approach based on findings
6. ⏳ Document limitations if no solution found

---

## Conclusion (Updated 2025-11-22)

**Test Results:**
- ✅ REST API works perfectly in garage
- ❌ REST API does NOT work on-track (returns empty/no data)
- ❌ Cannot poll for setup changes during race sessions

**Root Cause:**
User reported TC change (7→4) not appearing on dashboard because REST API only provides data in garage, not during active sessions.

**Impact:**
- Current behavior is CORRECT - we can only fetch setup once at session start
- HUD changes made on-track cannot be detected via REST API
- Dashboard will show stale setup values if driver changes TC/brake bias on-track

**Alternative Approaches to Investigate:**

### Option 1: Accept Limitation (Simplest)
Document that dashboard shows garage setup only, not on-track HUD adjustments.

**Pros:** No code changes needed
**Cons:** Dashboard shows incorrect values if user changes setup on-track

### Option 2: Shared Memory Investigation
Check if shared memory exposes TC/brake bias/ABS values.

**Research needed:**
```bash
python tools/explore_shared_memory.py
# Look for fields like:
# - mTractionControl
# - mABS
# - mBrakeBias
```

**If found in shared memory:**
- Could read current values during telemetry polling
- Would show live adjustments
- More reliable than REST API

### Option 3: Periodic Garage Polling
Poll REST API when back in garage (between sessions).

**Use case:** Practice → Garage → Adjust setup → Dashboard updates
**Limitation:** Still won't detect on-track HUD changes

### Option 4: Disclaimer/Warning
Show setup data but add warning: "Setup shown is from garage. On-track adjustments (TC, brake bias) may differ."

---

**Recommended Next Steps:**

1. **Investigate shared memory** - Check if TC/ABS/brake bias available
2. **If in shared memory:** Use live telemetry values instead of REST API
3. **If NOT in shared memory:** Document limitation and add disclaimer

**Status:** BLOCKED - Need to investigate shared memory as alternative data source

---

**Dependencies:** None (isolated feature)
**Blocked by:** Need to check shared memory for setup values
