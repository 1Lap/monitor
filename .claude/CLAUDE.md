# 1Lap Monitor - Claude Instructions

## Project Overview

This is the **monitor** component of the 1Lap Race Dashboard system. It reads telemetry from Le Mans Ultimate (LMU) and publishes real-time data to the dashboard server via WebSocket.

**Architecture:** Part of 3-repository system:
- **monitor** (this repo) - Reads LMU telemetry, publishes to server
- **server** - Receives data, broadcasts to dashboards
- **dashboard-ui** - Web interface for viewing (embedded in server)

**Current Status:** MVP Implementation Phase - Repository cleaned, ready for development

## Development Philosophy

### Test-Driven Development (TDD)
- **ALWAYS write tests before code** when implementing new features
- Tests should fail first, then write code to make them pass
- Current coverage: Core components tested (telemetry, process monitor, REST API)
- If tests can't pass after trying, ask user before modifying tests

### Cross-Platform Architecture
- Develop on macOS with mocks
- Test/deploy on Windows with real LMU
- Abstract platform-specific code behind interfaces
- `src/telemetry/telemetry_interface.py` - defines `TelemetryReaderInterface`
- `src/telemetry/telemetry_mock.py` - macOS implementation (simulates telemetry)
- `src/telemetry/telemetry_real.py` - Windows implementation
- Platform detection: `sys.platform == 'win32'` → real, else → mock

## Project Architecture

### Core Components

1. **TelemetryReader** (`src/telemetry/`) ✅ COMPLETE
   - Interface-based design for cross-platform support
   - Mock reader simulates realistic racing data with lap progression
   - Real reader uses `pyRfactor2SharedMemory` (Windows only)
   - Provides 100+ telemetry fields from LMU shared memory

2. **ProcessMonitor** (`src/process_monitor.py`) ✅ COMPLETE
   - Auto-detects target process (LMU.exe on Windows, configurable on macOS)
   - Uses `psutil` for cross-platform process detection
   - Case-insensitive, partial name matching

3. **LMURestAPI** (`src/lmu_rest_api.py`) ✅ COMPLETE
   - Fetches car setup data from LMU REST API
   - Endpoint: `http://localhost:6397/rest/garage/setup`
   - Returns complete mechanical setup (suspension, aero, brakes, etc.)
   - Setup is player car only (opponent setups not available)

4. **DashboardPublisher** (`src/dashboard_publisher.py`) ⬜ TO IMPLEMENT
   - WebSocket client using `python-socketio[client]`
   - Connects to dashboard server
   - Publishes telemetry data (2Hz)
   - Publishes setup data (once per session)
   - Handles reconnection gracefully

5. **Monitor** (`monitor.py`) ⬜ TO IMPLEMENT
   - Main entry point
   - Orchestrates all components
   - Configuration management (config.json)
   - Main loop with error handling

### Data Flow

```
LMU.exe (Windows)
    ↓
Shared Memory API (100Hz) + REST API (setup)
    ↓
TelemetryReader + LMURestAPI
    ↓
Monitor (Python)
    ↓
DashboardPublisher
    ↓
WebSocket (2Hz)
    ↓
Dashboard Server
    ↓
WebSocket Broadcast
    ↓
Web Dashboard (Browser)
```

### WebSocket Events

**Monitor → Server:**
- `request_session_id` - Request new session
- `setup_data` - Publish car setup (once)
- `telemetry_update` - Publish telemetry (2Hz)

**Server → Monitor:**
- `session_id_assigned` - Receive session ID and dashboard URL

## Implementation Phases

### Phase 1: MVP (Current)

**Status:** Repository cleaned, ready for implementation

**Tasks:** See `bugs/MVP_MONITOR_TASKS.md` for complete breakdown

1. **API Exploration** (4-6 hours) ⬜
   - Explore shared memory fields on Windows
   - Explore REST API endpoints
   - Define dashboard data requirements

2. **Core Implementation** (8-12 hours) ⬜
   - Implement DashboardPublisher
   - Create monitor.py entry point
   - Add configuration system
   - Write comprehensive tests

3. **Testing & Integration** (4-6 hours) ⬜
   - Integration tests
   - Server connection testing
   - End-to-end validation
   - Performance testing

**Total Estimated Time:** 16-24 hours

### Phase 2: Polish & Enhancement (Future)

- Error recovery and reconnection
- Performance optimization
- Enhanced logging
- Deployment packaging
- Documentation polish

## Testing Requirements

### Running Tests

```bash
# All tests
pytest -v

# Specific module
pytest tests/test_dashboard_publisher.py -v

# With coverage
pytest --cov=src --cov-report=html
```

### Test Organization

- Each module has corresponding test file: `test_<module>.py`
- Use pytest fixtures for setup/teardown
- Mock time-dependent behavior when needed
- Test edge cases and error conditions

### Current Test Coverage

**Existing (Core Components):**
- `test_telemetry_mock.py` - 7 tests ✅
- `test_telemetry_real.py` - 2 tests ✅
- `test_process_monitor.py` - 5 tests ✅
- `test_lmu_rest_api.py` - existing tests ✅

**To Add (New Components):**
- `test_dashboard_publisher.py` - 8+ tests ⬜
- `test_monitor_integration.py` - 10+ tests ⬜

**Target:** High test coverage for all new components

## Common Commands

### Development

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Windows-specific dependencies (when on Windows)
pip install -r requirements-windows.txt

# Run tests
pytest -v

# Run monitor (once implemented)
python monitor.py

# Run monitor in logging mode (console output, no server)
python monitor.py --log-only
```

### Git Workflow

```bash
# Check status
git status

# Run tests before committing
pytest -v

# Commit with tests passing
git add -A
git commit -m "descriptive message"

# Push to feature branch
git push -u origin <branch-name>
```

## Important Files & References

### Key Files

- **`RACE_DASHBOARD_PLAN.md`** - Master plan for 3-repo dashboard system
- **`MONITOR_PLAN.md`** - Monitor-specific implementation plan (to be created)
- **`bugs/MVP_MONITOR_TASKS.md`** - MVP task breakdown and roadmap
- **`monitor.py`** - Main entry point (to be created)
- **`config.json`** - Configuration (to be created)

### Configuration Format

**`config.json`** (to be created):
```json
{
  "server_url": "http://localhost:5000",
  "session_id": "auto",
  "update_rate_hz": 2,
  "poll_interval": 0.01,
  "target_process": "LMU.exe"
}
```

**Configuration Fields:**
- `server_url` - Dashboard server URL (local or cloud)
- `session_id` - Session ID or "auto" to request from server
- `update_rate_hz` - Telemetry publish rate (default: 2Hz)
- `poll_interval` - Telemetry read interval (default: 0.01s = 100Hz)
- `target_process` - Process to monitor (default: "LMU.exe")

### Data Published to Dashboard

**Telemetry Fields (2Hz updates):**
- Session info: lap, position, lap_time, player_name, car_name, track_name
- Fuel: fuel_remaining, fuel_capacity
- Tires: tire_pressures (FL/FR/RL/RR), tire_temps, tire_wear
- Brakes: brake_temps (FL/FR/RL/RR)
- Engine: engine_water_temp
- Weather: track_temp, ambient_temp
- Driving: speed, gear, rpm

**Setup Data (once per session):**
- Complete car setup from REST API
- Suspension, aerodynamics, brakes, gearing, differential, etc.

See `bugs/dashboard_data_requirements.md` for complete field mapping.

## Code Style & Conventions

- **Docstrings:** All functions/classes have Google-style docstrings
- **Type hints:** Use when helpful, especially for function signatures
- **Imports:** Group by stdlib, third-party, local
- **Naming:**
  - snake_case for functions/variables
  - PascalCase for classes
  - UPPER_CASE for constants
- **Line length:** Keep reasonable (~100 chars when possible)

## Troubleshooting

### Tests failing?
1. Check virtual environment is activated
2. Ensure all dependencies installed
3. Read test output carefully - tests are descriptive
4. Run single test file to isolate issue

### Monitor not detecting process?
- macOS: Change `target_process` to a running process (e.g., 'python', 'Chrome')
- Windows: Ensure LMU.exe is running

### Can't connect to server?
- Check server is running at configured URL
- Verify `server_url` in config.json
- Use `python tools/test_server_connection.py` to debug
- Check firewall settings for local network

### API exploration failing?
- Shared memory: Requires LMU running on Windows
- REST API: Check LMU REST API is enabled (localhost:6397)
- Use logging mode to debug: `python monitor.py --log-only`

## Archive

Old writer project code (CSV telemetry logger) has been archived to `_archive/` for reference.

**Why archived?** Monitor publishes to server via WebSocket, doesn't write CSV files.

**What's archived?**
- CSV formatting and file management
- Session/lap tracking (too complex for monitor)
- Tray UI and settings dialog
- Auto-update system

See `_archive/README.md` for details on archived components.

---

## Next Session Checklist

When continuing development:

1. Pull latest code from git
2. Activate virtual environment
3. Run tests to verify everything works (`pytest -v`)
4. Read this file for context
5. Check `bugs/MVP_MONITOR_TASKS.md` for current tasks
6. Review `RACE_DASHBOARD_PLAN.md` for architecture

## Questions to Ask User

Before making significant changes:
- **Adding new dependencies?** → Ask first
- **Changing test behavior?** → Only if tests can't pass after thorough attempts
- **Modifying core architecture?** → Discuss rationale
- **Platform-specific code?** → Ensure cross-platform compatibility maintained

## Success Criteria

### MVP Complete When:

- ✅ All core components implemented
- ✅ Monitor connects to server
- ✅ Telemetry published at 2Hz
- ✅ Setup data published once per session
- ✅ All tests passing (unit + integration)
- ✅ Manual testing checklist complete
- ✅ Works on Windows with LMU
- ✅ Works on macOS with mock data
- ✅ Documentation updated

---

**Remember**: This is a **dashboard monitor**, not a CSV logger. We publish real-time data to a server, we don't save files locally.
