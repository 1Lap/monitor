# Feature: Define Dashboard Data Requirements

**Type:** Planning / Documentation
**Priority:** High
**Phase:** MVP - Phase 1
**Estimated Time:** 1 hour

---

## Overview

Document exactly what data the dashboard needs from the monitor, based on the race dashboard plan and API exploration results. This will define the contract between monitor and server.

## Objective

Create a clear specification of:
1. Which telemetry fields to publish (2Hz updates)
2. Which setup fields to publish (once per session)
3. Data format and units
4. Update frequency for each category

## Requirements

### Must Have

1. **Document: `docs/DASHBOARD_DATA_SPEC.md`**
   - List all telemetry fields to publish
   - List all setup fields to publish
   - Define data types and units
   - Specify update frequencies

2. **Data Selection Criteria**
   - Only include fields needed by dashboard UI
   - Minimize bandwidth (2Hz updates)
   - Ensure cross-platform compatibility (mock + real)

3. **Validation**
   - Compare with API exploration results
   - Confirm all fields are available in shared memory
   - Verify setup fields exist in REST API

### Nice to Have

- Example JSON payloads for reference
- Field priority (critical vs. nice-to-have)
- Future enhancement fields (for Phase 3)
- Data transformation notes (unit conversions, etc.)

## Dashboard Requirements

Based on `RACE_DASHBOARD_PLAN.md`, the dashboard UI needs:

### Session Info (display once, update rarely)
- `player_name` - Driver name
- `car_name` - Car model
- `track_name` - Track name
- `session_type` - Race/Practice/Qualifying

### Live Telemetry (2Hz updates)
- `lap` - Current lap number
- `position` - Race position
- `lap_time` - Current lap time

### Fuel Management
- `fuel` - Current fuel (L)
- `fuel_capacity` - Tank capacity (L)
- Calculated: `fuel_percent` - Fuel remaining %
- Calculated: `laps_remaining` - Estimated laps left

### Tire Data
- `tire_pressures` - Object: {fl, fr, rl, rr} in PSI
- `tire_temps` - Object: {fl, fr, rl, rr} in °C
- `tire_wear` - Object: {fl, fr, rl, rr} in %

### Brake Data
- `brake_temps` - Object: {fl, fr, rl, rr} in °C

### Engine & Weather
- `engine_water_temp` - Engine coolant temp (°C)
- `track_temp` - Track surface temp (°C)
- `ambient_temp` - Air temp (°C)

### Driving Info (optional)
- `speed` - Current speed (km/h)
- `gear` - Current gear
- `rpm` - Engine RPM

### Car Setup (once per session)
- Full setup object from REST API
- Display as JSON or structured format
- Categories: Suspension, Aero, Brakes, Gearing, Diff, Tires

## Data Format Specification

### Telemetry Update Payload
```json
{
  "session_id": "abc-def-ghi-jkl",
  "telemetry": {
    "timestamp": "2025-11-22T14:30:22.567Z",
    "lap": 45,
    "position": 3,
    "lap_time": 123.456,
    "fuel": 42.3,
    "fuel_capacity": 90.0,
    "tire_pressures": {
      "fl": 25.1,
      "fr": 24.9,
      "rl": 25.3,
      "rr": 25.0
    },
    "tire_temps": {
      "fl": 75.2,
      "fr": 73.8,
      "rl": 78.1,
      "rr": 76.5
    },
    "tire_wear": {
      "fl": 14.5,
      "fr": 13.2,
      "rl": 15.8,
      "rr": 12.1
    },
    "brake_temps": {
      "fl": 480.0,
      "fr": 485.0,
      "rl": 612.0,
      "rr": 615.0
    },
    "engine_water_temp": 109.5,
    "track_temp": 41.8,
    "ambient_temp": 24.0,
    "speed": 256.3,
    "gear": 6,
    "rpm": 7267.0,
    "player_name": "Driver Name",
    "car_name": "Toyota GR010",
    "track_name": "Bahrain International Circuit",
    "session_type": "Race"
  }
}
```

### Setup Data Payload
```json
{
  "session_id": "abc-def-ghi-jkl",
  "timestamp": "2025-11-22T14:30:22.123Z",
  "setup": {
    "suspension": { ... },
    "aerodynamics": { ... },
    "brakes": { ... },
    "gearing": { ... },
    "differential": { ... },
    "tires": { ... }
  }
}
```

## Field Mapping

### From Shared Memory → Dashboard

| Shared Memory Field | Dashboard Field | Transform |
|---------------------|-----------------|-----------|
| `fuel_remaining` | `fuel` | None |
| `fuel_at_start` | `fuel_capacity` | None |
| `tyre_pressure` | `tire_pressures` | None (already PSI) |
| `tyre_temp` | `tire_temps` | None (already °C) |
| `tyre_wear` | `tire_wear` | None (already %) |
| `brake_temp` | `brake_temps` | None (already °C) |
| `engine_temp` | `engine_water_temp` | None |
| `track_temp` | `track_temp` | None |
| `ambient_temp` | `ambient_temp` | None |
| `speed` | `speed` | None (already km/h) |
| `rpm` | `rpm` | None |
| `gear` | `gear` | None |
| `lap` | `lap` | None |
| `race_position` | `position` | None |
| `lap_time` | `lap_time` | None |
| `player_name` | `player_name` | None |
| `car_name` | `car_name` | None |
| `track_name` | `track_name` | None |
| `session_type` | `session_type` | None |

## Implementation Steps

1. Run API exploration scripts (see related bugs)
2. Validate all fields are available
3. Create `docs/DASHBOARD_DATA_SPEC.md` with:
   - Complete field list
   - Data types and units
   - Example payloads
   - Field mapping table
4. Review with plan to ensure completeness
5. Use spec to implement `DashboardPublisher`

## Validation Checklist

- [ ] All dashboard UI fields have data source
- [ ] All fields available in shared memory
- [ ] Setup data available in REST API
- [ ] Data types compatible with JSON
- [ ] Units are consistent (°C, PSI, km/h, etc.)
- [ ] No redundant fields (minimize bandwidth)
- [ ] Cross-platform compatible (mock + real)

## Dependencies

- API exploration scripts must be run first
- Dashboard UI design (from RACE_DASHBOARD_PLAN.md)
- Shared memory field validation
- REST API endpoint validation

## Notes

- Keep payload small (2Hz updates = bandwidth)
- Only send fields that change (future optimization)
- Consider delta compression (future enhancement)
- Plan for missing data (null/undefined handling)

## Related Files

- `RACE_DASHBOARD_PLAN.md` - Dashboard requirements
- `bugs/api_exploration_shared_memory.md` - Field validation
- `bugs/api_exploration_rest_api.md` - Setup validation
- `docs/shared_memory_fields.txt` - API exploration results
- `docs/rest_api_responses.txt` - API exploration results

---

**Next Steps:** Use this spec to implement `DashboardPublisher.publish_telemetry()` and `publish_setup()` methods.
