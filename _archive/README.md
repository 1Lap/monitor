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
- Historical context

## Archive Structure

```
_archive/
├── src/           # Python modules
│   ├── csv_formatter.py
│   ├── file_manager.py
│   ├── session_manager.py
│   ├── mvp_format.py
│   ├── telemetry_loop.py
│   ├── tray_ui.py
│   ├── settings_ui.py
│   ├── update_*.py (checker, manager, ui)
│   ├── version.py
│   ├── opponent_tracker.py
│   └── app_paths.py
├── tests/         # Test files for archived modules
├── apps/          # Applications (tray_app, example_app, updater, build scripts)
├── docs/          # Documentation, plans, and installer files
└── bugs/          # Old bug reports from writer project
```

## Key Archived Components

### CSV Logging System
- **CSVFormatter** - CSV file formatting (12-column MVP format)
- **FileManager** - File saving and management
- **SampleNormalizer** (mvp_format.py) - Data normalization for CSV output

### Session Management
- **SessionManager** - Complex session/lap tracking with buffering
- **TelemetryLoop** - Polling loop with lap completion callbacks

### User Interface
- **TrayUI** - System tray interface (pystray)
- **SettingsUI** - tkinter settings dialog
- **Config management** - GUI-based configuration

### Auto-Update System
- **UpdateChecker** - GitHub release checking
- **UpdateManager** - Update orchestration
- **UpdateUI** - Update notifications and dialogs
- **Updater script** - External .exe replacement

### Other Components
- **OpponentTracker** - Track opponent vehicles
- **AppPaths** - Application path management

## Original Project Status

Writer project status at time of fork:
- **Phases 1-6:** Complete ✅
- **Phase 7:** Distribution (in progress)
- **Tests:** 175 tests passing
- **Windows .exe:** Built and tested
- **Installer:** Inno Setup installer implemented
- **Auto-update:** Complete with GitHub integration

## Using Archived Code

### As Reference
Browse the archive to understand:
- Telemetry data structure patterns
- Session state management approaches
- Testing strategies
- Cross-platform design patterns

### Do NOT:
- Move archived code back to `src/` directly
- Copy large chunks without adapting to monitor needs
- Reintroduce complexity that monitor doesn't need

### Instead:
- Adapt patterns for monitor requirements
- Simplify where possible
- Keep monitor focused on publishing, not file management

## Documentation

Archived documentation includes:
- **TELEMETRY_LOGGER_PLAN.md** - Original writer implementation plan
- **MVP_LOGGING_PLAN.md** - CSV logging strategy
- **AUTO_UPDATE_IMPLEMENTATION_PLAN.md** - Auto-update architecture
- **TECHNICAL_SPEC.md** - Detailed component specifications
- **telemetry_format_analysis.md** - CSV format specification
- **example.csv** - Reference CSV output

See `docs/` directory for complete archived documentation.

## Migration Notes

### What Changed for Monitor

| Writer Component | Monitor Equivalent | Notes |
|------------------|-------------------|-------|
| CSVFormatter | DashboardPublisher | Publishes JSON via WebSocket instead of CSV files |
| FileManager | (removed) | No file management needed |
| SessionManager | Simple state flag | No lap tracking, just "setup sent" boolean |
| TelemetryLoop | Direct polling in monitor.py | Simpler loop without callbacks |
| TrayUI | (removed) | No UI, runs as background service |
| SettingsUI | config.json | Simple JSON configuration |
| Auto-update | (removed) | Manual updates for monitor |

### Data Flow Comparison

**Writer (CSV Logger):**
```
LMU → Shared Memory → TelemetryLoop → SessionManager → CSVFormatter → FileManager → CSV Files
```

**Monitor (Dashboard Publisher):**
```
LMU → Shared Memory → Monitor → DashboardPublisher → WebSocket → Server
```

## Questions?

If you need to reference archived code:
1. Check this README for component overview
2. Browse `src/` for implementation details
3. Check `docs/` for architecture documentation
4. Review `tests/` for usage examples

Remember: The monitor is simpler by design. Don't reintroduce complexity unless there's a clear need!

---

**Archive Date:** 2025-11-22
**Writer Project:** Phases 1-6 complete, Phase 7 in progress
**Monitor Project:** MVP implementation phase
