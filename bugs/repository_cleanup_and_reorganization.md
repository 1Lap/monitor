# Task: Comprehensive Repository Cleanup for Monitor

**Type:** Refactoring / Cleanup
**Priority:** High
**Phase:** MVP - Phase 0 (Before Implementation)
**Estimated Time:** 2-3 hours

---

## Overview

Clean up the forked writer repository to create a lean monitor repository by:
1. Archiving unneeded writer code (keep as reference)
2. Updating CLAUDE.md for monitor context
3. Creating monitor-specific project plan
4. Organizing documentation

## Objective

Transform the writer repository into a clean monitor repository while preserving the old code for reference.

---

## Part 1: Create Archive Structure

### Archive Folders to Create

```
_archive/
├── src/                    # Archived Python modules
├── tests/                  # Archived test files
├── docs/                   # Archived documentation
├── apps/                   # Archived application files
└── README.md               # Archive index
```

### Files to Archive

#### Python Modules (src/ → _archive/src/)
```bash
_archive/src/
├── csv_formatter.py        # CSV formatting - not needed
├── file_manager.py         # File management - not needed
├── session_manager.py      # Complex session tracking - too much
├── mvp_format.py           # Sample normalization for CSV - not needed
├── telemetry_loop.py       # Polling loop - monitor has simpler needs
├── tray_ui.py              # Tray UI - no UI in monitor
├── settings_ui.py          # Settings GUI - using config.json
├── update_checker.py       # Auto-update - not needed
├── update_manager.py       # Auto-update - not needed
├── update_ui.py            # Auto-update - not needed
├── version.py              # Version management - not needed
├── opponent_tracker.py     # Opponent tracking - not needed
└── app_paths.py            # App paths - not needed
```

#### Test Files (tests/ → _archive/tests/)
```bash
_archive/tests/
├── test_csv_formatter.py
├── test_file_manager.py
├── test_session_manager.py
├── test_sample_normalizer.py
├── test_telemetry_loop.py
├── test_tray_ui.py
├── test_settings_ui.py
├── test_update_checker.py
├── test_update_manager.py
├── test_update_ui.py
├── test_version.py
├── test_opponent_tracker.py
└── test_example_app_integration.py
```

#### Applications (→ _archive/apps/)
```bash
_archive/apps/
├── tray_app.py             # Tray application
├── example_app.py          # Example CSV logger
├── updater.py              # Auto-updater
├── build.bat               # Build script
└── build_installer.bat     # Installer build script
```

#### Documentation (→ _archive/docs/)
```bash
_archive/docs/
├── TELEMETRY_LOGGER_PLAN.md           # Old writer plan
├── MVP_LOGGING_PLAN.md                # Old CSV logging plan
├── AUTO_UPDATE_IMPLEMENTATION_PLAN.md # Auto-update plan
├── TECHNICAL_SPEC.md                  # Writer technical spec
├── telemetry_format_analysis.md       # CSV format spec
├── example.csv                        # CSV example
├── WINDOWS_BUILD_INSTRUCTIONS.md      # Build instructions
├── IMPLEMENTATION_GUIDE.md            # Writer implementation guide
├── RELEASE_NOTES_v0.2.0.md           # Old releases
├── RELEASE_NOTES_v0.3.0.md           # Old releases
├── PR_SUMMARY.md                      # Old PR
├── PR_DESCRIPTION.md                  # Old PR
└── installer/                         # Installer files
```

#### Old Bug Files (bugs/ → _archive/bugs/)
```bash
_archive/bugs/
├── filemanager_startup_directory_creation.md
├── readonly_program_files_permissions.md
├── capture_car_setups.md
├── terminal_window_on_startup.md
├── updater_arguments_error.md
├── update_ui_button_height.md
└── update_check_failure.md
```

### Files to Keep

#### Core Source Files
```bash
src/
├── telemetry/
│   ├── __init__.py
│   ├── telemetry_interface.py  ✅ Keep
│   ├── telemetry_real.py       ✅ Keep
│   └── telemetry_mock.py       ✅ Keep
├── process_monitor.py          ✅ Keep
├── lmu_rest_api.py             ✅ Keep
└── __init__.py                 ✅ Keep
```

#### Core Test Files
```bash
tests/
├── test_telemetry_mock.py      ✅ Keep
├── test_telemetry_real.py      ✅ Keep
├── test_process_monitor.py     ✅ Keep
└── test_lmu_rest_api.py        ✅ Keep
```

#### Documentation
```bash
# Root
├── README.md                   ✅ Keep (update for monitor)
├── RACE_DASHBOARD_PLAN.md      ✅ Keep (master plan)
├── MONITOR_PLAN.md             ✅ CREATE NEW
├── CHANGELOG.md                ✅ Keep (start fresh for monitor)
├── USER_GUIDE.md               ✅ Keep (update for monitor)
├── .claude/CLAUDE.md           ✅ Keep (UPDATE)

# Bugs
bugs/
├── MVP_MONITOR_TASKS.md        ✅ Keep (new)
├── api_exploration_*.md        ✅ Keep (new)
├── implement_*.md              ✅ Keep (new)
├── create_*.md                 ✅ Keep (new)
└── ... (all new monitor tasks) ✅ Keep
```

---

## Part 2: Update CLAUDE.md

### New CLAUDE.md Structure

```markdown
# 1Lap Monitor - Claude Instructions

## Project Overview

This is the **monitor** component of the 1Lap Race Dashboard system. It reads telemetry from Le Mans Ultimate (LMU) and publishes real-time data to the dashboard server via WebSocket.

**Architecture:** Part of 3-repository system (monitor → server → dashboard)
**Current Status:** MVP Implementation Phase

## Development Philosophy

### Test-Driven Development (TDD)
- Write tests before code
- Tests should fail first, then implement
- Current coverage: [X] tests passing
- Maintain high test coverage

### Cross-Platform Architecture
- Develop on macOS with mocks
- Test/deploy on Windows with real LMU
- Abstract platform-specific code behind interfaces

## Project Architecture

### Core Components

1. **TelemetryReader** (src/telemetry/)
   - Interface-based design
   - Mock reader for development (macOS)
   - Real reader for production (Windows + LMU)

2. **ProcessMonitor** (src/process_monitor.py)
   - Detects LMU.exe process
   - Cross-platform using psutil

3. **LMURestAPI** (src/lmu_rest_api.py)
   - Fetches car setup from REST API
   - localhost:6397 endpoint

4. **DashboardPublisher** (src/dashboard_publisher.py) - TO IMPLEMENT
   - WebSocket client
   - Publishes telemetry (2Hz)
   - Publishes setup (once per session)

5. **Monitor** (monitor.py) - TO IMPLEMENT
   - Main entry point
   - Orchestrates all components
   - Configuration management

### Data Flow

```
LMU.exe (Windows)
    ↓
Shared Memory (100Hz) + REST API (setup)
    ↓
Monitor (Python)
    ↓
WebSocket (2Hz)
    ↓
Dashboard Server
    ↓
Web Dashboard (Browser)
```

## Implementation Phases

### Phase 1: MVP (Current)
- [ ] API exploration and validation
- [ ] DashboardPublisher implementation
- [ ] Monitor.py entry point
- [ ] Basic testing
- [ ] Integration with server

See `bugs/MVP_MONITOR_TASKS.md` for detailed task breakdown.

## Testing Requirements

### Running Tests
```bash
pytest -v
pytest --cov=src --cov-report=html
```

### Test Organization
- Unit tests for each module
- Integration tests for end-to-end flow
- Mock-based testing for cross-platform

### Current Test Coverage
- test_telemetry_mock.py (7 tests) ✅
- test_telemetry_real.py (2 tests) ✅
- test_process_monitor.py (5 tests) ✅
- test_lmu_rest_api.py (existing) ✅
- test_dashboard_publisher.py (TO ADD)
- test_monitor_integration.py (TO ADD)

## Common Commands

### Development
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run tests
pytest -v

# Run monitor
python monitor.py

# Run monitor in logging mode (no server)
python monitor.py --log-only
```

## Important Files & References

### Key Files
- `RACE_DASHBOARD_PLAN.md` - Master plan for 3-repo system
- `MONITOR_PLAN.md` - Monitor-specific implementation plan
- `bugs/MVP_MONITOR_TASKS.md` - MVP task breakdown
- `monitor.py` - Main entry point (TO CREATE)
- `config.json` - Configuration (TO CREATE)

### Configuration
```json
{
  "server_url": "http://localhost:5000",
  "session_id": "auto",
  "update_rate_hz": 2,
  "poll_interval": 0.01,
  "target_process": "LMU.exe"
}
```

## Code Style & Conventions

- Google-style docstrings
- Type hints for function signatures
- snake_case for functions/variables
- PascalCase for classes
- ~100 char line length

## Troubleshooting

### Tests failing?
- Check virtual environment
- Ensure dependencies installed
- Run single test to isolate issue

### Monitor not detecting process?
- macOS: Change target_process to running process
- Windows: Ensure LMU.exe is running

### Can't connect to server?
- Check server is running
- Verify server_url in config.json
- Use `python tools/test_server_connection.py`

## Archive

Old writer project code has been archived to `_archive/` for reference.
See `_archive/README.md` for details on archived components.

---

**Remember**: This is a dashboard monitor, not a CSV logger. We publish data to a server, we don't save files.
```

---

## Part 3: Create MONITOR_PLAN.md

Create a monitor-specific plan document:

```markdown
# 1Lap Monitor - Implementation Plan

## Overview

The monitor component reads LMU telemetry and publishes to the dashboard server.

## Architecture

[Insert monitor-specific architecture details]

## Implementation Phases

### Phase 1: MVP
[Details from MVP_MONITOR_TASKS.md]

### Phase 2: Polish
[Future enhancements]

## API Integration

### Shared Memory API
[Details on telemetry reading]

### REST API
[Details on setup fetching]

### WebSocket API
[Details on server communication]

## Testing Strategy

[Testing approach]

## Deployment

[How to deploy monitor]
```

---

## Part 4: Create Archive Index

**`_archive/README.md`**

```markdown
# Archived Writer Project Code

This directory contains code from the original **writer** project (CSV telemetry logger).

The writer project has been forked to create the **monitor** project (dashboard publisher).

## Why Archived?

The monitor component has different requirements than the writer:
- Monitor publishes to server (no CSV files)
- Monitor has simpler session tracking (no lap detection)
- Monitor has no UI (no tray icon, settings dialog)
- Monitor has no auto-update (simpler deployment)

However, we keep the writer code as reference for:
- Understanding telemetry data structures
- Reusing session management patterns
- Reference for future features

## Archive Structure

```
_archive/
├── src/           # Python modules
├── tests/         # Test files
├── apps/          # Applications (tray_app, example_app, etc.)
├── docs/          # Documentation and plans
└── bugs/          # Old bug reports
```

## Key Archived Components

- **CSVFormatter** - CSV file formatting (12-column MVP format)
- **FileManager** - File saving and management
- **SessionManager** - Complex session/lap tracking
- **TelemetryLoop** - Polling loop with callbacks
- **TrayUI** - System tray interface
- **SettingsUI** - tkinter settings dialog
- **Auto-Update System** - GitHub release checking and installation

## Using Archived Code

Browse the archive to understand patterns and data structures.
Do not move archived code back to `src/` - instead, adapt patterns for monitor needs.

## Original Project Status

Writer project status at time of fork:
- Phases 1-6 complete
- Phase 7 (distribution) in progress
- 175 tests passing
- Windows .exe built and tested
- Installer implemented

See archived documentation for complete details.
```

---

## Implementation Steps

### Step 1: Create Archive Structure

```bash
# Create archive directories
mkdir -p _archive/{src,tests,apps,docs,bugs}

# Move Python modules
git mv src/csv_formatter.py _archive/src/
git mv src/file_manager.py _archive/src/
git mv src/session_manager.py _archive/src/
git mv src/mvp_format.py _archive/src/
git mv src/telemetry_loop.py _archive/src/
git mv src/tray_ui.py _archive/src/
git mv src/settings_ui.py _archive/src/
git mv src/update_checker.py _archive/src/
git mv src/update_manager.py _archive/src/
git mv src/update_ui.py _archive/src/
git mv src/version.py _archive/src/
git mv src/opponent_tracker.py _archive/src/
git mv src/app_paths.py _archive/src/

# Move test files
git mv tests/test_csv_formatter.py _archive/tests/
git mv tests/test_file_manager.py _archive/tests/
git mv tests/test_session_manager.py _archive/tests/
git mv tests/test_sample_normalizer.py _archive/tests/
git mv tests/test_telemetry_loop.py _archive/tests/
git mv tests/test_tray_ui.py _archive/tests/
git mv tests/test_settings_ui.py _archive/tests/
git mv tests/test_update_checker.py _archive/tests/
git mv tests/test_update_manager.py _archive/tests/
git mv tests/test_update_ui.py _archive/tests/
git mv tests/test_version.py _archive/tests/
git mv tests/test_opponent_tracker.py _archive/tests/
git mv tests/test_example_app_integration.py _archive/tests/

# Move applications
git mv tray_app.py _archive/apps/
git mv example_app.py _archive/apps/
git mv updater.py _archive/apps/
git mv build.bat _archive/apps/
git mv build_installer.bat _archive/apps/

# Move documentation
git mv TELEMETRY_LOGGER_PLAN.md _archive/docs/
git mv MVP_LOGGING_PLAN.md _archive/docs/
git mv AUTO_UPDATE_IMPLEMENTATION_PLAN.md _archive/docs/
git mv TECHNICAL_SPEC.md _archive/docs/
git mv telemetry_format_analysis.md _archive/docs/
git mv example.csv _archive/docs/
git mv WINDOWS_BUILD_INSTRUCTIONS.md _archive/docs/
git mv IMPLEMENTATION_GUIDE.md _archive/docs/
git mv RELEASE_NOTES_v0.2.0.md _archive/docs/
git mv RELEASE_NOTES_v0.3.0.md _archive/docs/
git mv PR_SUMMARY.md _archive/docs/
git mv PR_DESCRIPTION.md _archive/docs/
git mv installer _archive/docs/

# Move old bug files
git mv bugs/filemanager_startup_directory_creation.md _archive/bugs/
git mv bugs/readonly_program_files_permissions.md _archive/bugs/
git mv bugs/capture_car_setups.md _archive/bugs/
git mv bugs/terminal_window_on_startup.md _archive/bugs/
git mv bugs/updater_arguments_error.md _archive/bugs/
git mv bugs/update_ui_button_height.md _archive/bugs/
git mv bugs/update_check_failure.md _archive/bugs/

# Create archive index
# (Create _archive/README.md with content above)
```

### Step 2: Update CLAUDE.md

```bash
# Update .claude/CLAUDE.md with new content
# (Use content above)
```

### Step 3: Create MONITOR_PLAN.md

```bash
# Create MONITOR_PLAN.md
# (Use content above, expand with details)
```

### Step 4: Update README.md

Update README.md to describe monitor instead of writer:

```markdown
# 1Lap Race Dashboard Monitor

Background service that reads LMU telemetry and publishes to dashboard server.

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Edit `config.json` with server URL
3. Run monitor: `python monitor.py`

## Features

- Reads telemetry from LMU (100Hz)
- Fetches car setup from REST API
- Publishes to dashboard server (2Hz)
- Cross-platform (Windows + macOS with mocks)

## See Also

- [server](https://github.com/1Lap/server) - Dashboard web service
- [RACE_DASHBOARD_PLAN.md](RACE_DASHBOARD_PLAN.md) - Complete system plan
- [MONITOR_PLAN.md](MONITOR_PLAN.md) - Monitor implementation plan
```

### Step 5: Commit

```bash
git add -A
git commit -m "Archive writer components and update for monitor

- Move writer code to _archive/ for reference
- Update CLAUDE.md for monitor context
- Create MONITOR_PLAN.md
- Update README.md
- Preserve old code as reference without cluttering repo"
```

---

## Validation Checklist

- [ ] Archive structure created
- [ ] All writer code moved to _archive/
- [ ] Core monitor code remains in src/
- [ ] Tests still pass for remaining code
- [ ] CLAUDE.md updated for monitor
- [ ] MONITOR_PLAN.md created
- [ ] README.md updated
- [ ] _archive/README.md created
- [ ] All changes committed
- [ ] Repository clean and focused

---

## After Cleanup

Repository structure should be:

```
monitor/
├── src/
│   ├── telemetry/          ✅ Keep
│   ├── process_monitor.py  ✅ Keep
│   └── lmu_rest_api.py     ✅ Keep
├── tests/                  ✅ Minimal (4-5 test files)
├── bugs/                   ✅ Monitor tasks only
├── _archive/               ✅ Writer code reference
├── monitor.py              ✅ TO CREATE
├── config.json             ✅ TO CREATE
├── RACE_DASHBOARD_PLAN.md  ✅ Keep
├── MONITOR_PLAN.md         ✅ CREATE
├── README.md               ✅ UPDATE
└── .claude/CLAUDE.md       ✅ UPDATE
```

Clean, focused, ready for monitor development!

---

**Estimated Time:** 2-3 hours
**Priority:** High - Do before implementing new monitor components
**Dependencies:** None - can do immediately
