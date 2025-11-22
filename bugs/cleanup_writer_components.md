# Task: Clean Up Writer Components

**Type:** Refactoring
**Priority:** Medium
**Phase:** MVP - Phase 1
**Estimated Time:** 1-2 hours

---

## Overview

Remove unnecessary components from the forked `writer` repository to create a clean `monitor` repository. This cleanup will remove UI, file management, and auto-update components that are not needed for dashboard monitoring.

## Objective

Transform the `writer` repository into a lean `monitor` repository by:
1. Removing unneeded files and directories
2. Updating documentation
3. Simplifying dependencies
4. Maintaining only dashboard-relevant components

## Files to Remove

Based on `RACE_DASHBOARD_PLAN.md`:

### Python Modules
```bash
src/csv_formatter.py          # Not writing CSV files
src/file_manager.py            # Not managing files
src/session_manager.py         # Simplify or remove (no lap tracking)
src/tray_ui.py                 # No UI needed
src/settings_ui.py             # Using simple config.json instead
src/update_checker.py          # No auto-update
src/update_manager.py          # No auto-update
src/update_ui.py               # No auto-update
src/version.py                 # Not needed
src/mvp_format.py              # Not formatting to CSV
```

### Test Files
```bash
tests/test_csv_formatter.py
tests/test_file_manager.py
tests/test_sample_normalizer.py  # If not needed
tests/test_settings_ui.py
tests/test_update_checker.py
tests/test_update_manager.py
tests/test_update_ui.py
tests/test_version.py
tests/test_tray_ui.py
```

### Application Files
```bash
tray_app.py                    # No tray UI
example_app.py                 # Replace with monitor.py
updater.py                     # No auto-update
build.bat                      # Not building .exe (maybe later)
build_installer.bat            # Not building installer
```

### Directories
```bash
installer/                     # Not distributing as installer
```

### Documentation (Update or Remove)
```bash
AUTO_UPDATE_IMPLEMENTATION_PLAN.md  # Remove
MVP_LOGGING_PLAN.md                 # Remove (was for CSV)
TECHNICAL_SPEC.md                   # Update for monitor
TELEMETRY_LOGGER_PLAN.md            # Update for monitor
USER_GUIDE.md                       # Update for monitor
example.csv                         # Remove
telemetry_format_analysis.md        # Remove
```

## Files to Keep

### Core Components
```bash
src/telemetry/
  telemetry_interface.py       ✅ Keep
  telemetry_real.py            ✅ Keep
  telemetry_mock.py            ✅ Keep
  __init__.py                  ✅ Keep

src/lmu_rest_api.py            ✅ Keep
src/process_monitor.py         ✅ Keep

tests/test_telemetry_real.py   ✅ Keep
tests/test_telemetry_mock.py   ✅ Keep
tests/test_lmu_rest_api.py     ✅ Keep
tests/test_process_monitor.py  ✅ Keep
```

### New Files (to be created)
```bash
src/dashboard_publisher.py     ✅ NEW
monitor.py                     ✅ NEW
config.json                    ✅ NEW

tests/test_dashboard_publisher.py  ✅ NEW
tests/test_monitor_integration.py  ✅ NEW
```

### Documentation
```bash
README.md                      ✅ UPDATE (monitor-specific)
CLAUDE.md                      ✅ UPDATE (monitor context)
RACE_DASHBOARD_PLAN.md         ✅ KEEP (master plan)
.claude/                       ✅ KEEP
bugs/                          ✅ KEEP
```

### Configuration
```bash
requirements.txt               ✅ UPDATE (minimal deps)
requirements-dev.txt           ✅ KEEP
requirements-windows.txt       ✅ KEEP (for LMU)
pytest.ini                     ✅ KEEP
.gitignore                     ✅ KEEP
```

## Updated Dependencies

**`requirements.txt`** (minimal)
```txt
pyRfactor2SharedMemory>=0.1.0  # Windows only
psutil>=5.9.0                   # Process monitoring
python-socketio[client]>=5.9.0  # WebSocket client
requests>=2.28.0                # REST API client
```

**Remove from requirements:**
```txt
pystray                         # Tray UI - not needed
tkinter                         # Settings UI - not needed
innosetup                       # Installer - not needed
```

## Git Operations

### Option 1: Clean History (Recommended)

Create a fresh monitor repo without writer history:

```bash
# 1. Create new repo
mkdir monitor
cd monitor
git init

# 2. Copy needed files from writer
cp -r ../writer/src/telemetry ./src/
cp -r ../writer/src/lmu_rest_api.py ./src/
cp -r ../writer/src/process_monitor.py ./src/
cp -r ../writer/tests/test_telemetry_*.py ./tests/
cp -r ../writer/tests/test_lmu_rest_api.py ./tests/
cp -r ../writer/tests/test_process_monitor.py ./tests/

# 3. Copy config files
cp ../writer/requirements*.txt .
cp ../writer/pytest.ini .
cp ../writer/.gitignore .

# 4. Initialize
git add .
git commit -m "Initial monitor repository (from writer)"
git remote add origin git@github.com:1Lap/monitor.git
git push -u origin main
```

### Option 2: Fork and Clean (Keep History)

Fork writer and remove unneeded components:

```bash
# 1. Clone writer
git clone git@github.com:1Lap/writer.git monitor
cd monitor

# 2. Remove unneeded files
git rm src/csv_formatter.py
git rm src/file_manager.py
git rm src/session_manager.py  # Or simplify
git rm src/tray_ui.py
git rm src/settings_ui.py
git rm src/update_*.py
git rm src/version.py
git rm src/mvp_format.py

git rm tests/test_csv_formatter.py
git rm tests/test_file_manager.py
git rm tests/test_settings_ui.py
git rm tests/test_update_*.py
git rm tests/test_tray_ui.py

git rm tray_app.py
git rm example_app.py
git rm updater.py
git rm build.bat
git rm build_installer.bat
git rm -r installer/

git rm AUTO_UPDATE_IMPLEMENTATION_PLAN.md
git rm MVP_LOGGING_PLAN.md
git rm example.csv
git rm telemetry_format_analysis.md

# 3. Commit cleanup
git commit -m "Remove writer-specific components for monitor"

# 4. Update remote
git remote set-url origin git@github.com:1Lap/monitor.git
git push -u origin main
```

## Implementation Steps

1. **Decide on approach** (fresh repo vs. fork)
2. **Remove unneeded files**
3. **Update README.md** with monitor-specific docs
4. **Update CLAUDE.md** with monitor context
5. **Simplify requirements.txt**
6. **Update .gitignore** if needed
7. **Test remaining components** (run existing tests)
8. **Commit and push**

## Validation Checklist

- [ ] All unneeded files removed
- [ ] Core components remain intact
- [ ] Tests still pass for kept components
- [ ] Dependencies updated (minimal)
- [ ] Documentation updated
- [ ] README reflects monitor purpose
- [ ] Git history clean (if fresh repo)
- [ ] Pushed to new `monitor` repository

## Testing After Cleanup

```bash
# Run remaining tests
pytest -v

# Expected passing tests:
# - test_telemetry_mock.py (7 tests)
# - test_telemetry_real.py (2 tests)
# - test_lmu_rest_api.py (existing tests)
# - test_process_monitor.py (5 tests)
# Total: ~14 tests
```

## Documentation Updates

### Update `README.md`

```markdown
# 1Lap Race Dashboard Monitor

Background service that reads LMU telemetry and publishes to dashboard server.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure server URL in `config.json`

3. Run monitor:
   ```bash
   python monitor.py
   ```

## Configuration

Edit `config.json`:
- `server_url`: Dashboard server URL
- `update_rate_hz`: Telemetry publish rate (default: 2Hz)
- `target_process`: Process to monitor (default: `LMU.exe`)

## How It Works

1. Monitors for LMU.exe process
2. Reads telemetry from shared memory (50-100Hz)
3. Fetches car setup from REST API (once per session)
4. Publishes to dashboard server (2Hz)
5. Server broadcasts to web dashboards

## See Also

- [server](https://github.com/1Lap/server) - Dashboard web service
- [RACE_DASHBOARD_PLAN.md](RACE_DASHBOARD_PLAN.md) - Complete implementation plan
```

### Update `CLAUDE.md`

- Remove Phase 1-6 details (from writer)
- Add monitor-specific context
- Update project overview
- Keep TDD philosophy
- Update file references

## Related Files

- `RACE_DASHBOARD_PLAN.md` - Monitor repository structure
- `bugs/create_monitor_entry_point.md` - New monitor.py
- `bugs/implement_dashboard_publisher.md` - New component

---

**Next Steps:** After cleanup, implement new monitor components (DashboardPublisher, monitor.py).
