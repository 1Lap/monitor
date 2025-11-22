# Feature: Explore LMU Shared Memory API

**Type:** Investigation / Test Script
**Priority:** High
**Phase:** MVP - Phase 1
**Estimated Time:** 1-2 hours

---

## Overview

Create a test script to explore the LMU shared memory API and validate which telemetry fields are available. This will help us confirm what data we can read and ensure it matches our dashboard requirements.

## Objective

Build a simple Python script that connects to LMU shared memory and logs all available fields to help us:
1. Validate the shared memory connection works
2. Identify actual field names and data types
3. Confirm update rates (50-100Hz as documented)
4. Document the structure for dashboard use

## Requirements

### Must Have

1. **Script: `tools/explore_shared_memory.py`**
   - Use existing `TelemetryReader` interface
   - Read telemetry data at 100Hz
   - Log all fields to console for 5-10 seconds
   - Pretty-print the data structure

2. **Output Format**
   - JSON or formatted text showing field names, values, types
   - Sample data for each field
   - Update frequency measurement

3. **Documentation**
   - Save sample output to `docs/shared_memory_fields.txt`
   - Include actual field names (not just mock data)
   - Note any differences from expected fields

### Nice to Have

- Export to JSON file for easy parsing
- Filter by category (telemetry, pit menu, session, scoring)
- Highlight critical fields for dashboard
- Compare mock vs. real data structure

## Dashboard Data Needs

Based on `RACE_DASHBOARD_PLAN.md`, we need to validate these fields exist:

### Critical Fields
- **Fuel:** `fuel_remaining`, `fuel_at_start`
- **Tires:** `tyre_pressure` (FL/FR/RL/RR), `tyre_temp`, `tyre_wear`
- **Brakes:** `brake_temp` (FL/FR/RL/RR)
- **Engine:** `engine_temp` (water temperature)
- **Weather:** `track_temp`, `ambient_temp`
- **Position:** `race_position`, `lap`, `lap_time`
- **Speed/RPM:** `speed`, `rpm`, `gear`
- **Session:** `player_name`, `car_name`, `track_name`, `session_type`

### Bonus Fields (if available)
- **Pit Menu:** Current pit options, planned fuel, tire selections
- **Driver Assists:** TC, ABS, stability, auto-shift
- **Sector Times:** Sector 1/2/3 times

## Implementation Steps

1. Create `tools/` directory if it doesn't exist
2. Write `explore_shared_memory.py`:
   ```python
   """
   Explore LMU shared memory API
   Run with LMU active to see available fields
   """
   import time
   import json
   from src.telemetry.telemetry_interface import get_telemetry_reader

   def main():
       reader = get_telemetry_reader()

       if not reader.is_available():
           print("ERROR: LMU not detected. Start LMU first.")
           return

       print("LMU detected! Reading telemetry...")
       print("=" * 60)

       samples = []
       for i in range(100):  # ~1 second at 100Hz
           data = reader.read()
           if data:
               samples.append(data)
           time.sleep(0.01)

       if samples:
           # Show first sample structure
           first = samples[0]
           print(json.dumps(first, indent=2))

           # Show field summary
           print("\n" + "=" * 60)
           print("Available fields:")
           for key in sorted(first.keys()):
               print(f"  - {key}: {type(first[key]).__name__}")

   if __name__ == '__main__':
       main()
   ```

3. Run with LMU active (Windows only)
4. Capture output and save to `docs/shared_memory_fields.txt`
5. Review and compare with mock implementation

## Expected Outcome

- ✅ Confirmed connection to LMU shared memory
- ✅ List of all available fields with sample values
- ✅ Validation that dashboard requirements can be met
- ✅ Documentation for future reference

## Testing

1. Run script without LMU → should display error
2. Run script with LMU active → should display telemetry
3. Run during different session types (practice, race, etc.)
4. Verify fields match mock data structure

## Dependencies

- `pyRfactor2SharedMemory` (Windows only)
- Existing `TelemetryReader` interface
- LMU running on Windows

## Notes

- This is **Windows-only** testing (requires LMU)
- User will need to run this manually when LMU is available
- Results will inform dashboard data selection
- Compare with mock data to ensure cross-platform compatibility

## Related Files

- `src/telemetry/telemetry_real.py` - Real telemetry reader
- `src/telemetry/telemetry_mock.py` - Mock implementation
- `RACE_DASHBOARD_PLAN.md` - Dashboard requirements

---

**Next Steps:** After completing this, we can validate which fields to publish to the dashboard and create the `DashboardPublisher` implementation.

## Status

✅ **COMPLETE** - Tested 2025-11-22

**What was tested:**
- Tool: `tools/explore_shared_memory.py` created and tested
- Platform: Windows + Le Mans Ultimate
- Results: Successfully read telemetry at 94.9 Hz

**Key Findings:**
- **55 telemetry fields** available from shared memory
- **Update rate:** 94.9 Hz (within expected 50-100 Hz range)
- **Field naming:** Uses British spelling (`tyre_*` not `tire_*`)
- **All critical dashboard fields present:**
  - ✅ Fuel: `fuel`, `fuel_capacity`
  - ✅ Tires: `tyre_pressure`, `tyre_temp`, `tyre_wear`
  - ✅ Brakes: `brake_temp`
  - ✅ Engine: `engine_temp`
  - ✅ Weather: `track_temp`, `ambient_temp`
  - ✅ Position: `lap`, `lap_time`
  - ✅ Speed/RPM: `speed`, `rpm`, `gear`
  - ✅ Session: `player_name`, `car_name`, `track_name`, `session_type`

**Field Mapping Issues Found & Fixed:**
- ❌ Missing `race_position` → ✅ Added (uses `scor.mPlace`)
- ✅ Tire fields already using British spelling (correct)

**Actions Taken:**
1. Created `tools/explore_shared_memory.py`
2. Tested with real LMU (Autodromo Enzo e Dino Ferrari, Practice session)
3. Updated `telemetry_real.py` to add missing `race_position` field
4. Updated `dashboard_publisher.py` to handle field name variations

**Test Results Saved:**
- Console output captured
- All 55 fields documented
- Sample data collected

**Next Steps:**
- ✅ Field mappings updated
- ✅ Monitor tested and working
- Ready for server integration testing
