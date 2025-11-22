# Monitor ↔ Dashboard Compatibility Report

Date: 2025-11-22

Scope
- Verify that `monitor` and `dashboard` agree on WebSocket events and payloads.
- Document the shared event schema and surface any mismatches or risks.
- Provide JSON Schemas to anchor future changes.

Summary
- Event names align: `request_session_id`, `session_id_assigned`, `setup_data`, `telemetry_update`, `join_session`.
- Payload shapes are compatible with the dashboard’s server and UI.
- Minor semantic gap: `fuel_capacity` currently maps to `fuel_at_start` from telemetry; treat as a fallback until true capacity is available.

Repositories inspected
- Monitor: `src/dashboard_publisher.py`, `monitor.py`, `src/telemetry/*`, `tools/test_server_connection.py`
- Dashboard: `app/main.py`, `app/session_manager.py`, `static/js/dashboard.js`

Event Contracts (agreed)
- Monitor → Server
  - `request_session_id`: `{}` → server replies with `session_id_assigned`.
  - `setup_data`: `{ session_id: string(UUID), timestamp: string(ISO8601), setup: object }`.
  - `telemetry_update`: `{ session_id: string(UUID), telemetry: TelemetryPayload }`.
- Server → Monitor
  - `session_id_assigned`: `{ session_id: string(UUID) }`.
- Dashboard ↔ Server
  - Dashboard `join_session`: `{ session_id: string(UUID) }`.
  - Server emits `setup_update` and `telemetry_update` to session room with same shapes as above.

Shared Telemetry Payload v1 (used by dashboard UI)
- Fields sent by monitor (filtered in `DashboardPublisher._extract_dashboard_fields`):
  - `timestamp`: string ISO8601 (UTC, `...Z`)
  - `lap`: integer
  - `position`: integer (derived from `race_position`)
  - `lap_time`: number (seconds)
  - `fuel`: number (liters)
  - `fuel_capacity`: number (liters) — currently mapped from `fuel_at_start` as fallback
  - `tire_pressures`: object `{ fl, fr, rl, rr }` numbers (PSI)
  - `tire_temps`: object `{ fl, fr, rl, rr }` numbers (°C)
  - `tire_wear`: object `{ fl, fr, rl, rr }` numbers (%)
  - `brake_temps`: object `{ fl, fr, rl, rr }` numbers (°C)
  - `engine_water_temp`: number (°C) — mapped from `engine_temp`
  - `track_temp`: number (°C)
  - `ambient_temp`: number (°C)
  - `speed`: number (km/h)
  - `gear`: integer
  - `rpm`: number
  - `player_name`: string
  - `car_name`: string
  - `track_name`: string
  - `session_type`: string

Schemas
- JSON Schemas added in `bugs/schemas/`:
  - `telemetry_update.schema.json`: Envelope + `telemetry` payload definition
  - `setup_data.schema.json`: Envelope + `setup` payload stub (opaque to server)

Potential Divergences / Risks
- Fuel semantics: `fuel_capacity` currently equals `fuel_at_start`. If/when actual capacity is available, update monitor mapping; the UI will continue to work but percent may be off in some cars.
- Optional fields: Dashboard UI tolerates missing nested tire/brake objects; no server-side validation at present. Adding schema validation would improve robustness.

Recommendations
- Server: Optionally validate incoming `setup_data` and `telemetry_update` against the provided schemas (e.g., `jsonschema`) and log warnings for violations.
- Monitor: When true tank capacity becomes available from LMU, map it to `fuel_capacity`; keep `fuel_at_start` for logging only.
- Versioning: Keep `bugs/schemas/` as the source of truth, increment `$id` and `version` field when schema changes.

Appendix: Validation Pseudocode
```python
# server/app/main.py (inside handlers)
#from jsonschema import validate, Draft202012Validator
#validate(instance=data, schema=TELEMETRY_ENVELOPE_SCHEMA)
```

Status
- As of this review, the monitor and dashboard are compatible on event names and payloads. No blocking issues found.

