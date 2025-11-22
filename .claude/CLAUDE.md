# 1Lap Monitor - Claude Instructions

## Project Overview

This is the **monitor** component of the 1Lap Race Dashboard system. It reads telemetry from Le Mans Ultimate (LMU) and publishes real-time data to the dashboard server via WebSocket.

**Architecture:** Part of 3-repository system:
- **monitor** (this repo) - Reads LMU telemetry, publishes to server
- **server** - Receives data, broadcasts to dashboards
- **dashboard-ui** - Web interface for viewing (embedded in server)

**Current Status:** ✅ MVP CORE COMPLETE (2025-11-22) - Ready for Server Integration

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

1. **TelemetryReader** (`src/telemetry/`) ✅ COMPLETE & TESTED
   - Interface-based design for cross-platform support
   - Mock reader simulates realistic racing data with lap progression
   - Real reader uses `pyRfactor2SharedMemory` (Windows only)
   - Provides 55 telemetry fields from LMU shared memory at 95 Hz
   - Tested on Windows with real LMU (2025-11-22)
   - Exploration tool: `tools/explore_shared_memory.py`

2. **ProcessMonitor** (`src/process_monitor.py`) ✅ COMPLETE & TESTED
   - Auto-detects target process ("Le Mans Ultimate.exe" on Windows, configurable on macOS)
   - Uses `psutil` for cross-platform process detection
   - Case-insensitive, partial name matching
   - Diagnostic tool: `tools/test_process_detection.py`

3. **LMURestAPI** (`src/lmu_rest_api.py`) ✅ COMPLETE & TESTED
   - Fetches car setup data from LMU REST API
   - Primary: `http://localhost:6397/rest/garage/UIScreen/CarSetupOverview`
   - Fallback: `http://localhost:6397/rest/garage/setup`
   - Returns 172 setup parameters when in garage with setup loaded
   - Complete mechanical setup (suspension, aero, brakes, gearing, differential, etc.)
   - Setup is player car only (opponent setups not available)
   - Tested on Windows with real LMU (2025-11-22)
   - Exploration tool: `tools/explore_rest_api.py`

4. **DashboardPublisher** (`src/dashboard_publisher.py`) ✅ COMPLETE
   - WebSocket client using `python-socketio[client]`
   - Connects to dashboard server
   - Publishes telemetry data (2Hz)
   - Publishes setup data (once per session)
   - Handles reconnection gracefully
   - 22 comprehensive tests

5. **Monitor** (`monitor.py`) ✅ COMPLETE
   - Main entry point
   - Orchestrates all components
   - Configuration management (config.json)
   - Main loop with error handling
   - --log-only mode for console debugging
   - Signal handlers for graceful shutdown
   - 15 comprehensive tests

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

### Phase 1: MVP Core ✅ COMPLETE (2025-11-22)

**Status:** Core implementation complete, ready for server integration

**Tasks:** See `bugs/MVP_MONITOR_TASKS.md` for complete breakdown

1. **API Exploration** ✅ COMPLETE (2025-11-22)
   - ✅ Explored shared memory fields on Windows (55 fields @ 95 Hz)
   - ✅ Explored REST API endpoints (172 setup parameters)
   - ✅ Validated dashboard data requirements
   - ✅ Fixed field mapping issues (race_position, fuel fields)
   - ✅ Created exploration tools (explore_shared_memory.py, explore_rest_api.py)

2. **Core Implementation** ✅ COMPLETE
   - ✅ Implement DashboardPublisher (22 tests)
   - ✅ Create monitor.py entry point (15 tests)
   - ✅ Add configuration system (config.json)
   - ✅ Write comprehensive tests (51 total)
   - ✅ Server connection test utility

3. **Testing & Integration** ⏳ IN PROGRESS
   - ✅ Manual testing on Windows with real LMU
   - ✅ Process detection verified
   - ✅ Telemetry reading verified (2 Hz publishing)
   - ✅ Field mappings validated and fixed
   - ⏳ Integration tests with server (requires server)
   - ⏳ End-to-end validation (requires server)
   - ⏳ Extended performance testing (30+ min runs)

**Progress:** 11/12 tasks complete (92%) - Only server integration testing remains

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

**All Components Tested (51 tests total):**
- `test_telemetry_mock.py` - 7 tests ✅
- `test_telemetry_real.py` - 2 tests ✅
- `test_process_monitor.py` - 5 tests ✅
- `test_lmu_rest_api.py` - existing tests ✅
- `test_dashboard_publisher.py` - 22 tests ✅
- `test_monitor.py` - 15 tests ✅

**Coverage:** Excellent - All core components have comprehensive test coverage

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

# Run monitor (connects to server)
python monitor.py

# Run monitor in logging mode (console output, no server needed)
python monitor.py --log-only

# Diagnostic Tools (for testing/troubleshooting)
python tools/test_server_connection.py      # Test WebSocket server connection
python tools/test_process_detection.py      # Verify LMU process detection
python tools/explore_shared_memory.py       # Explore telemetry fields (Windows+LMU)
python tools/explore_rest_api.py            # Explore setup data (Windows+LMU)
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
- **`bugs/MVP_MONITOR_TASKS.md`** - MVP task breakdown and roadmap (11/12 complete)
- **`MANUAL_TESTING_GUIDE.md`** - Comprehensive manual testing guide (14 tests) ✅
- **`monitor.py`** - Main entry point ✅
- **`config.json.example`** - Configuration template ✅
- **`config.json`** - User configuration (copy from .example)

**Diagnostic Tools:**
- **`tools/test_server_connection.py`** - WebSocket server connection test ✅
- **`tools/test_process_detection.py`** - Process detection diagnostic ✅
- **`tools/explore_shared_memory.py`** - Telemetry API explorer ✅
- **`tools/explore_rest_api.py`** - Setup API explorer ✅

### Configuration Format

**`config.json`** (copy from config.json.example):
```json
{
  "server_url": "http://localhost:5000",
  "session_id": "auto",
  "update_rate_hz": 2,
  "poll_interval": 0.01,
  "target_process": "Le Mans Ultimate"
}
```

**Configuration Fields:**
- `server_url` - Dashboard server URL (local or cloud)
- `session_id` - Session ID or "auto" to request from server
- `update_rate_hz` - Telemetry publish rate (default: 2Hz)
- `poll_interval` - Telemetry read interval (default: 0.01s = 100Hz)
- `target_process` - Process to monitor (default: "Le Mans Ultimate" on Windows, "python" for testing on macOS)

### Data Published to Dashboard

**Telemetry Fields (2Hz updates):**
- Session info: lap, race_position, lap_time, player_name, car_name, track_name, session_type
- Fuel: fuel, fuel_capacity
- Tires: tyre_pressure (FL/FR/RL/RR), tyre_temp, tyre_wear (British spelling)
- Brakes: brake_temp (FL/FR/RL/RR)
- Engine: engine_temp
- Weather: track_temp, ambient_temp
- Driving: speed, gear, rpm
- Total: 55 fields available from shared memory @ 95 Hz

**Setup Data (once per session):**
- Complete car setup from REST API (172 parameters)
- Structure: `carSetup.garageValues` with parameter dicts
- Each parameter includes: key, value, stringValue, minValue, maxValue, available
- Categories: Suspension, aerodynamics, brakes, gearing, differential, tire pressures, etc.
- Examples: VM_BRAKE_BALANCE, VM_BRAKE_DUCTS, VM_FRONT_SPRING_RATE, VM_REAR_SPRING_RATE
- Only available when in garage with setup loaded

See `bugs/dashboard_data_requirements.md` for complete field mapping.
See `explore_rest_api.log` for real data structure from LMU.

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
- Windows: Ensure "Le Mans Ultimate.exe" is running
- Windows: Use `python tools/test_process_detection.py` to diagnose
- macOS: Change `target_process` to a running process (e.g., 'python', 'Chrome')
- Check config.json has correct process name: "Le Mans Ultimate" (not "LMU.exe")

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

### MVP Core Complete ✅ (2025-11-22)

**Implemented:**
- ✅ All core components implemented (DashboardPublisher, Monitor)
- ✅ Monitor connects to server (WebSocket client ready)
- ✅ Telemetry published at 2Hz (configurable)
- ✅ Setup data published once per session (REST API integration)
- ✅ All tests passing (51/51 unit tests)
- ✅ Works on macOS with mock data
- ✅ Works on Windows with real LMU (**Tested 2025-11-22**)
- ✅ Documentation updated (bug files + CLAUDE.md)
- ✅ Diagnostic tools created (4 testing utilities)

**Tested on Windows (2025-11-22):**
- ✅ Process detection working ("Le Mans Ultimate.exe")
- ✅ Telemetry reading at 95 Hz from shared memory
- ✅ Publishing at 2 Hz in logging mode
- ✅ 55 telemetry fields validated
- ✅ 172 setup parameters validated
- ✅ Field mappings verified and fixed
- ✅ All critical dashboard fields present

**Requires Server Integration:**
- ⏳ Manual testing checklist complete (server not available)
- ⏳ Integration tests with server (server not available)
- ⏳ End-to-end validation (requires full stack)
- ⏳ Extended performance testing (30+ min runs)

---

**Remember**: This is a **dashboard monitor**, not a CSV logger. We publish real-time data to a server, we don't save files locally.
