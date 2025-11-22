1Lap Monitor — AGENTS Guide

Purpose
- Monitors LMU telemetry and publishes real-time data to the Dashboard Server via WebSocket.
- Works cross‑platform: mock telemetry on macOS, real LMU on Windows.

Repo Relationships
- monitor: this repo (collector/publisher)
- dashboard: Flask server + web UI in `dashboard/` (separate repo colocated here)

Quick Start
- Create venv and install: `pip install -r requirements.txt -r requirements-dev.txt`
- Windows extras (on Windows): `pip install -r requirements-windows.txt`
- Run tests: `pytest -v` (see Current Tests below)
- Run monitor (to server): `python monitor.py`
- Log-only mode (no server): `python monitor.py --log-only`
- Server connect check: `python tools/test_server_connection.py`

Key Files
- `monitor.py`: main orchestration entry
- `src/telemetry/telemetry_interface.py`: `TelemetryReaderInterface`
- `src/telemetry/telemetry_mock.py`: macOS/mock implementation
- `src/telemetry/telemetry_real.py`: Windows/LMU implementation
- `src/process_monitor.py`: process detection
- `src/lmu_rest_api.py`: car setup REST API client
- `src/dashboard_publisher.py`: WebSocket client to dashboard server
- `config.json.example` → copy to `config.json` to run

Configuration
- `config.json` fields:
  - `server_url`: dashboard server URL (e.g., `http://localhost:5000`)
  - `session_id`: `auto` or explicit ID
  - `update_rate_hz`: telemetry publish rate (default 2)
  - `poll_interval`: telemetry read interval (default 0.01s)
  - `target_process`: process name to detect (default `"LMU.exe"`)

WebSocket Contract
- Outbound events (Monitor → Server):
  - `request_session_id`: ask server to assign a session
  - `setup_data`: car setup payload (once per session)
  - `telemetry_update`: telemetry payload (2Hz)
- Inbound events (Server → Monitor):
  - `session_id_assigned`: receive `session_id` and dashboard URL

Development Workflow (TDD)
- Write tests first; make them fail; implement to green; refactor.
- Prefer interface‑based code; keep Windows specifics behind abstractions.
- Keep code cross‑platform; mock on macOS, real on Windows.
- Don’t weaken tests to make code pass without strong rationale.

Current Tests (indicative; keep green)
- `test_telemetry_mock.py`, `test_telemetry_real.py`
- `test_process_monitor.py`, `test_lmu_rest_api.py`
- `test_dashboard_publisher.py` (comprehensive)
- `test_monitor.py` (entry orchestration)

Common Tasks
- Add telemetry field:
  1) Extend interface/types; 2) update mock + real readers; 3) adapt publisher; 4) add tests; 5) document.
- Adjust publish cadence:
  1) Change config + monitor loop; 2) update tests for timing; 3) verify log-only mode output.
- Improve reconnection:
  1) Add retry/backoff in publisher; 2) simulate disconnects in tests; 3) ensure idempotent session handling.

Guardrails
- This is a live publisher, not a CSV logger—avoid reintroducing file logging (archived in `_archive/`).
- Keep platform detection simple: `sys.platform == 'win32'` → real; else → mock.
- Ask before adding heavy/new dependencies or changing core architecture.

Troubleshooting
- Tests fail: ensure venv active; reinstall deps; run targeted tests.
- Process not detected: adjust `target_process` in config; verify process name.
- Server connect issues: validate `server_url`; use `tools/test_server_connection.py`; check firewall.

Status & Next Steps
- MVP Core complete; ready for server integration.
- Pending: Windows-with-LMU validation, server integration tests, performance checks.

References
- See `.claude/CLAUDE.md` (this repo) and `RACE_DASHBOARD_PLAN.md` for deeper context.

