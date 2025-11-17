# LMU Telemetry Logger - Claude Instructions

## Project Overview

This is a background telemetry logger for Le Mans Ultimate (LMU) that automatically captures and exports telemetry data to CSV files. The project uses a **cross-platform development strategy**: develop on macOS with mocks, then test/deploy on Windows with real LMU data.

**Current Status**: Phases 1-5 complete (core system functional), ready for Phase 6 (Windows testing)

## Development Philosophy

### Test-Driven Development (TDD)
- **ALWAYS write tests before code** when implementing new features
- Tests should fail first, then write code to make them pass
- Current coverage: **61/61 tests passing, 100% coverage of implemented modules**
- If tests can't pass after trying, ask user before modifying tests

### Cross-Platform Architecture
- Abstract platform-specific code behind interfaces
- `src/telemetry/telemetry_interface.py` - defines `TelemetryReaderInterface`
- `src/telemetry/telemetry_mock.py` - macOS implementation (simulates telemetry)
- `src/telemetry/telemetry_real.py` - Windows implementation (TODO: Phase 6)
- Platform detection: `sys.platform == 'win32'` → real, else → mock

## Project Architecture

### Core Components (All Complete ✅)

1. **TelemetryReader** (`src/telemetry/`)
   - Interface-based design for cross-platform support
   - Mock reader simulates realistic racing data with lap progression
   - Real reader uses `pyRfactor2SharedMemory` (Windows only)

2. **ProcessMonitor** (`src/process_monitor.py`)
   - Auto-detects target process (LMU.exe on Windows, configurable on macOS)
   - Uses `psutil` for cross-platform process detection
   - Case-insensitive, partial name matching

3. **SessionManager** (`src/session_manager.py`)
   - Tracks session state: IDLE → DETECTED → LOGGING → (lap complete)
   - Detects lap changes by monitoring lap number
   - Buffers telemetry samples for current lap
   - Generates unique session IDs (timestamp-based)

4. **TelemetryLoop** (`src/telemetry_loop.py`)
   - Main polling loop (~100Hz by default)
   - Integrates ProcessMonitor, SessionManager, TelemetryReader
   - Triggers callbacks on lap completion
   - Supports pause/resume, start/stop

5. **CSVFormatter** (`src/csv_formatter.py`)
   - Formats telemetry data matching `example.csv` structure
   - 6 sections: player metadata, lap summary, session metadata, car setup, header, samples
   - Handles 100+ fields per sample
   - See `example.csv` for exact format reference

6. **FileManager** (`src/file_manager.py`)
   - Saves CSV files to disk with configurable naming
   - Default: `{session_id}_lap{lap}.csv`
   - Sanitizes filenames, manages output directory
   - Utilities: list, delete, filter by session

### Integration Example
- `example_app.py` - Complete working application
- Demonstrates all components working together
- Run with: `python example_app.py`

## Testing Requirements

### Running Tests
```bash
# All tests
pytest -v

# Specific module
pytest tests/test_telemetry_loop.py -v

# With coverage
pytest --cov=src --cov-report=html
```

### Test Organization
- Each module has corresponding test file: `test_<module>.py`
- Use pytest fixtures for setup/teardown (see `test_file_manager.py`)
- Mock time-dependent behavior when needed
- Test edge cases and error conditions

### Test Coverage by Module
- `test_telemetry_mock.py` - 7 tests
- `test_process_monitor.py` - 5 tests
- `test_session_manager.py` - 7 tests
- `test_telemetry_loop.py` - 13 tests
- `test_csv_formatter.py` - 13 tests
- `test_file_manager.py` - 16 tests

## Phase Status

### ✅ Completed (Phases 1-5)
- [x] Mock telemetry system
- [x] Process monitoring & auto-detection
- [x] Session management & lap tracking
- [x] Main telemetry loop (~100Hz)
- [x] CSV formatter (matches example.csv)
- [x] File management system
- [x] Integration example app

### 🔄 Current Phase: Phase 6 - Windows Testing
**You are here** - Ready to test on Windows with real LMU

Tasks:
1. Implement `RealTelemetryReader` in `src/telemetry/telemetry_real.py`
   - Use `pyRfactor2SharedMemory` library
   - Map shared memory fields to our telemetry dict format
   - Reference: `telemetry_mock.py` for field structure
2. Test with live LMU on Windows
3. Verify CSV output matches expected format
4. Fix any platform-specific issues

### ⏳ Pending: Phase 7 - Distribution
- Build standalone .exe with PyInstaller
- Optional: System tray UI (pystray)
- Final documentation

## Important Code Patterns

### 1. Platform Detection
```python
from src.telemetry.telemetry_interface import get_telemetry_reader

# Automatically returns correct implementation
reader = get_telemetry_reader()  # Mock on macOS, Real on Windows
```

### 2. Lap Completion Callback
```python
def on_lap_complete(lap_data, lap_summary):
    # lap_data: List[Dict] - all samples
    # lap_summary: Dict - lap time, sectors, etc.
    csv = formatter.format_lap(lap_data, lap_summary, session_info)
    file_manager.save_lap(csv, lap_summary, session_info)

loop = TelemetryLoop({'on_lap_complete': on_lap_complete})
```

### 3. Telemetry Data Structure
All telemetry dictionaries should include these key fields:
```python
{
    'lap': int,
    'speed': float,  # km/h
    'engine_rpm': float,
    'lap_distance': float,  # meters
    'total_distance': float,
    'brake_temp': {'fl': float, 'fr': float, 'rl': float, 'rr': float},
    'tyre_temp': {'fl': float, 'fr': float, 'rl': float, 'rr': float},
    # ... 100+ more fields
}
```
See `telemetry_mock.py` for complete field list.

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

# Run example app
python example_app.py
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

# Create PR (when ready)
gh pr create --draft
```

## Important Files & References

### Key Files
- `example.csv` - **Reference CSV format** (ground truth for CSV structure)
- `TECHNICAL_SPEC.md` - Detailed component specifications
- `TELEMETRY_LOGGER_PLAN.md` - High-level architecture and plan
- `example_app.py` - Working integration example

### Configuration Patterns
```python
# ProcessMonitor
config = {'target_process': 'LMU.exe'}  # or 'python' for testing

# TelemetryLoop
config = {
    'target_process': 'LMU.exe',
    'poll_interval': 0.01,  # 100Hz
    'on_lap_complete': callback_function
}

# FileManager
config = {
    'output_dir': './telemetry_output',
    'filename_format': '{session_id}_lap{lap}.csv'
}
```

## Windows-Specific Notes (Phase 6)

### When implementing RealTelemetryReader:

1. **Install Windows dependencies first:**
   ```bash
   pip install -r requirements-windows.txt
   ```

2. **Import pyRfactor2SharedMemory:**
   ```python
   import pyRfactor2SharedMemory as sm
   ```

3. **Map shared memory to our format:**
   - Study the library's data structure
   - Match field names to our telemetry dict
   - Handle conversion (units, data types)
   - Reference `telemetry_mock.py` for target structure

4. **Test with LMU running:**
   - Start LMU
   - Run example_app.py
   - Drive a lap
   - Check output CSV matches example.csv format

5. **Common issues to watch for:**
   - Shared memory not available (LMU not running)
   - Field name mismatches
   - Unit conversions (e.g., m/s vs km/h)
   - Missing fields (use defaults like mock does)

## Code Style & Conventions

- **Docstrings**: All functions/classes have Google-style docstrings
- **Type hints**: Use when helpful, especially for function signatures
- **Imports**: Group by stdlib, third-party, local
- **Naming**:
  - snake_case for functions/variables
  - PascalCase for classes
  - UPPER_CASE for constants
- **Line length**: Keep reasonable (~100 chars when possible)

## Troubleshooting

### Tests failing?
1. Check virtual environment is activated
2. Ensure all dependencies installed
3. Read test output carefully - tests are descriptive
4. Run single test file to isolate issue

### Example app not detecting process?
- macOS: Change `target_process` to a running process (e.g., 'python', 'Chrome')
- Windows: Ensure LMU.exe is running

### CSV format doesn't match?
- Compare with `example.csv` line by line
- Check CSVFormatter field order
- Verify all 6 sections present

## Next Session Checklist

When continuing work on Windows:

1. ✅ Pull latest code from git
2. ✅ Create Windows virtual environment
3. ✅ Install dependencies (including requirements-windows.txt)
4. ✅ Run tests to verify everything works
5. ✅ Read this file for context
6. ✅ Start Phase 6: Implement RealTelemetryReader
7. ✅ Test with live LMU

## Questions to Ask User

Before making significant changes:
- **Adding new dependencies?** → Ask first
- **Changing test behavior?** → Only if tests can't pass after thorough attempts
- **Modifying core architecture?** → Discuss rationale
- **Platform-specific code?** → Ensure cross-platform compatibility maintained

## Success Criteria

### For Phase 6 (Windows Testing):
- [ ] RealTelemetryReader implemented
- [ ] Reads data from LMU shared memory
- [ ] Example app works on Windows with live LMU
- [ ] CSV files generated match example.csv format
- [ ] All existing tests still pass
- [ ] New tests for RealTelemetryReader (if needed)

### For Phase 7 (Distribution):
- [ ] PyInstaller builds working .exe
- [ ] .exe runs standalone (no Python required)
- [ ] Documentation complete
- [ ] Ready for release

---

**Remember**: This project follows TDD - write tests first, make them fail, then implement to make them pass. The user values this approach, so maintain it throughout.
