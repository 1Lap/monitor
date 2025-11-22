# Feature: Explore LMU REST API

**Type:** Investigation / Test Script
**Priority:** High
**Phase:** MVP - Phase 1
**Estimated Time:** 1-2 hours

---

## Overview

Create a test script to explore the LMU REST API (localhost:6397) and validate which setup/garage data is available. This will confirm we can fetch car setup details to display on the dashboard.

## Objective

Build a simple Python script that queries the LMU REST API and logs all available endpoints and data to help us:
1. Validate the REST API is accessible
2. Identify actual setup data structure
3. Confirm vehicle metadata format
4. Document the response schema

## Requirements

### Must Have

1. **Script: `tools/explore_rest_api.py`**
   - Use existing `LMURestAPI` class (from `src/lmu_rest_api.py`)
   - Query `/rest/garage/setup` endpoint
   - Query `/rest/sessions/getAllVehicles` endpoint
   - Pretty-print the responses

2. **Output Format**
   - JSON or formatted text showing endpoint responses
   - Include full data structure
   - Note any errors or missing endpoints

3. **Documentation**
   - Save sample output to `docs/rest_api_responses.txt`
   - Include actual setup structure
   - Note any differences from expected format

### Nice to Have

- Export to JSON file for easy parsing
- Test multiple endpoints (if other endpoints exist)
- Validate data types and units
- Compare with shared memory data for consistency

## Dashboard Data Needs

Based on `RACE_DASHBOARD_PLAN.md`, we need to validate these setup fields exist:

### Critical Setup Fields (from `/rest/garage/setup`)
- **Suspension:** Springs, dampers, ARBs, ride height
- **Aerodynamics:** Wing angles, downforce levels
- **Gearing:** Gear ratios
- **Differential:** Settings
- **Brakes:** Brake balance, bias
- **Tires:** Base tire pressures (cold)

### Vehicle Metadata (from `/rest/sessions/getAllVehicles`)
- Vehicle make/model
- Team name
- Car class
- Number

## Implementation Steps

1. Create `tools/` directory if it doesn't exist
2. Write `explore_rest_api.py`:
   ```python
   """
   Explore LMU REST API endpoints
   Run with LMU active to see available data
   """
   import json
   from src.lmu_rest_api import LMURestAPI

   def main():
       api = LMURestAPI()

       if not api.is_available():
           print("ERROR: LMU REST API not available")
           print("Make sure LMU is running and API is enabled")
           return

       print("LMU REST API detected!")
       print("=" * 60)

       # Test /rest/garage/setup
       print("\n[1] Fetching setup data...")
       setup = api.fetch_setup_data()
       if setup:
           print(json.dumps(setup, indent=2))
       else:
           print("  No setup data available")

       # Test /rest/sessions/getAllVehicles (if implemented)
       print("\n" + "=" * 60)
       print("[2] Fetching vehicle metadata...")
       try:
           vehicles = api.fetch_vehicles()  # May not be implemented yet
           if vehicles:
               print(json.dumps(vehicles, indent=2))
           else:
               print("  No vehicle data available")
       except AttributeError:
           print("  Not implemented yet (add to lmu_rest_api.py)")

       print("\n" + "=" * 60)
       print("Exploration complete!")

   if __name__ == '__main__':
       main()
   ```

3. Run with LMU active (Windows only)
4. Capture output and save to `docs/rest_api_responses.txt`
5. Review and validate structure

## Expected Outcome

- ✅ Confirmed connection to LMU REST API
- ✅ Complete setup data structure documented
- ✅ Vehicle metadata format validated
- ✅ Identification of any missing endpoints

## Testing

1. Run script without LMU → should display error
2. Run script with LMU active but not in session → test behavior
3. Run script during active session → should display full setup
4. Test in garage vs. on track

## Dependencies

- `requests` library (HTTP client)
- Existing `LMURestAPI` class
- LMU running with REST API enabled

## Notes

- This is **Windows-only** testing (requires LMU)
- REST API must be enabled in LMU settings
- User will need to run this manually when LMU is available
- Setup data is player car only (opponents not available)

## LMU REST API Configuration

According to plan, the API should be at:
- **Base URL:** `http://localhost:6397`
- **Endpoints:**
  - `/rest/garage/setup` - Car setup (once per session)
  - `/rest/sessions/getAllVehicles` - Vehicle metadata

If these don't work, we may need to:
- Check LMU settings for API port
- Verify API is enabled
- Test alternative endpoints

## Related Files

- `src/lmu_rest_api.py` - REST API client
- `tests/test_lmu_rest_api.py` - Existing tests
- `RACE_DASHBOARD_PLAN.md` - Dashboard requirements

---

**Next Steps:** After completing this, we'll know exactly which setup data is available and can design the dashboard setup display accordingly.

## Status

✅ **COMPLETE** - Tested 2025-11-22

**What was tested:**
- Tool: `tools/explore_rest_api.py` created and tested
- Platform: Windows + Le Mans Ultimate
- Endpoint: `/rest/garage/setup`

**Key Findings:**

**Setup Data Structure:**
- **172 setup parameters** available when in garage with setup loaded
- Structure: `carSetup.garageValues` contains all parameters
- Each parameter includes: `key`, `value`, `stringValue`, `minValue`, `maxValue`, `available`

**Setup Parameters Include:**
- ✅ Brake balance: `VM_BRAKE_BALANCE`
- ✅ Brake ducts: `VM_BRAKE_DUCTS`, `VM_BRAKE_DUCTS_REAR`
- ✅ Brake migration: `VM_BRAKE_MIGRATION`
- ✅ Brake pressure: `VM_BRAKE_PRESSURE`
- ✅ Springs, dampers, ARBs (all suspension components)
- ✅ Aerodynamics settings
- ✅ Gearing ratios
- ✅ Differential settings
- ✅ And 160+ more parameters!

**Endpoint Behavior:**
- When **not in garage:** Returns list of available setup names
- When **in garage with setup:** Returns full setup data with 172 parameters
- Endpoint path: `GET http://localhost:6397/rest/garage/setup`

**Actions Taken:**
1. Created `tools/explore_rest_api.py`
2. Tested in multiple contexts (menu, garage)
3. Updated `lmu_rest_api.py` to handle both list and dict responses
4. Added fallback to `/rest/garage/UIScreen/CarSetupOverview` endpoint

**Code Updates:**
- `src/lmu_rest_api.py`:
  - Now tries `/rest/garage/UIScreen/CarSetupOverview` first
  - Falls back to `/rest/garage/setup`
  - Detects and handles list vs dict responses
  - Returns empty dict when setup not loaded

**Test Results:**
- ✅ API accessible at `http://localhost:6397`
- ✅ Setup data structure documented in `explore_rest_api.log`
- ✅ All critical setup categories present

**Next Steps:**
- ✅ REST API integration complete
- Ready for setup data publishing to dashboard
- Server integration testing pending
