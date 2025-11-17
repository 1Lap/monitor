# GitHub Issues for LMU Telemetry Logger

This file contains GitHub issues that can be created for task tracking. Each section represents one issue.

---

## Issue #1: Phase 1 - Project Setup and Mock Telemetry System

**Labels**: `phase-1`, `setup`, `cross-platform`

**Description**

Set up the development environment and create a mock telemetry system for macOS development.

**Tasks**

- [ ] Create git repository and initialize
- [ ] Setup Python virtual environment
- [ ] Create project structure matching TECHNICAL_SPEC.md
- [ ] Create `requirements.txt`, `requirements-windows.txt`, `requirements-dev.txt`
- [ ] Install dependencies on macOS
- [ ] Implement `TelemetryReaderInterface` abstract class
- [ ] Implement `MockTelemetryReader` with realistic data
- [ ] Add platform detection in telemetry module
- [ ] Study `example.csv` and map all required fields
- [ ] Review TinyPedal code for session detection patterns

**Acceptance Criteria**

- ✅ Git repository initialized with proper .gitignore
- ✅ Virtual environment created and documented in README
- ✅ All dependencies install without errors
- ✅ Project structure matches spec
- ✅ `MockTelemetryReader` returns valid telemetry dictionary
- ✅ Platform detection correctly identifies macOS vs Windows
- ✅ At least 1 unit test for mock telemetry passes
- ✅ Mock data includes all fields from example.csv

**Definition of Done**

Code merged to main branch, all tests passing, documented in README.

**Estimated Time**: 6-7 hours

---

## Issue #2: Phase 2.1 - Process Monitor and Auto-Detection

**Labels**: `phase-2`, `core`, `cross-platform`

**Description**

Implement process monitoring to detect when LMU (or test process on macOS) is running.

**Tasks**

- [ ] Implement `ProcessMonitor` class using psutil
- [ ] Add configurable target process name
- [ ] Implement `is_running()` method
- [ ] Implement `wait_for_process()` method
- [ ] Test with Chrome/VS Code on macOS
- [ ] Add state transitions (idle → detected)
- [ ] Write unit tests for process detection
- [ ] Handle edge cases (process crashes, multiple instances)

**Acceptance Criteria**

- ✅ `ProcessMonitor` detects Chrome on macOS
- ✅ State transitions work correctly
- ✅ Poll interval is configurable
- ✅ Handles process crash gracefully
- ✅ Unit tests cover all state transitions
- ✅ CPU usage < 1% when idle (measured)

**Definition of Done**

Code merged, tests passing, performance validated.

**Estimated Time**: 2-3 hours

---

## Issue #3: Phase 2.2 - Main Telemetry Loop and Session Manager

**Labels**: `phase-2`, `core`, `cross-platform`

**Description**

Implement the main telemetry reading loop and session state management.

**Tasks**

- [ ] Implement `SessionManager` class
- [ ] Add session state machine (idle/detected/logging/paused/error)
- [ ] Implement lap tracking and detection
- [ ] Create main telemetry loop running at ~100Hz
- [ ] Integrate `ProcessMonitor` and `TelemetryReader`
- [ ] Implement sample buffering (deque)
- [ ] Add lap completion event detection
- [ ] Write unit tests for session manager
- [ ] Write integration test for full pipeline (mock)

**Acceptance Criteria**

- ✅ Main loop polls at 100Hz ±5% (measured with timing)
- ✅ Lap completion detected correctly (test with mock data)
- ✅ Sample buffer stores data efficiently
- ✅ State machine handles all transitions
- ✅ Unit tests pass for session management
- ✅ Integration test: mock telemetry → buffered samples
- ✅ Memory usage < 50MB with full buffer

**Definition of Done**

Code merged, all tests passing, performance targets met.

**Estimated Time**: 5-6 hours

---

## Issue #4: Phase 3 - CSV Formatter Implementation

**Labels**: `phase-3`, `formatter`, `cross-platform`

**Description**

Implement CSV formatting that exactly matches example.csv structure.

**Tasks**

- [ ] Implement `CSVFormatter` class
- [ ] Implement player metadata formatting (line 1)
- [ ] Implement lap summary formatting (lines 2-3)
- [ ] Implement session metadata formatting (lines 4-5)
- [ ] Implement car setup formatting (lines 6-7)
- [ ] Implement telemetry header formatting (line 8)
- [ ] Implement telemetry samples formatting (lines 9+)
- [ ] Add field precision formatting (floats to 8 decimals)
- [ ] Add data mapping layer from telemetry dict to CSV
- [ ] Implement field calculations (sector times, distances)
- [ ] Write unit tests for each section
- [ ] Write integration test comparing output to example.csv

**Acceptance Criteria**

- ✅ All 6 CSV sections format correctly
- ✅ Output matches example.csv format exactly (automated comparison)
- ✅ Field precision matches specification
- ✅ Unit tests for each section pass
- ✅ Integration test validates complete lap CSV
- ✅ Edge cases handled (0 samples, 10,000 samples)
- ✅ Date formatting matches example

**Definition of Done**

Code merged, output validated against example.csv byte-for-byte (excluding dynamic values).

**Estimated Time**: 7-8 hours

---

## Issue #5: Phase 4.1 - File Manager

**Labels**: `phase-4`, `io`, `cross-platform`

**Description**

Implement file writing and management with error handling.

**Tasks**

- [ ] Implement `FileManager` class
- [ ] Implement filename generation from metadata
- [ ] Implement directory creation (with parents)
- [ ] Implement CSV file writing
- [ ] Add disk full error handling
- [ ] Add write retry logic (3 attempts)
- [ ] Add file write buffering for errors
- [ ] Write unit tests for file operations
- [ ] Write integration test for full pipeline (lap → file)

**Acceptance Criteria**

- ✅ Files written to correct directory
- ✅ Filename matches spec: `{player}_{track}_{date}_{session}.csv`
- ✅ Disk full handled gracefully (mock test)
- ✅ Write failures retry 3 times
- ✅ Integration test: lap completion → file exists on disk
- ✅ File write completes in < 500ms (measured)

**Definition of Done**

Code merged, error handling tested, performance validated.

**Estimated Time**: 2-3 hours

---

## Issue #6: Phase 4.2 - Configuration Management

**Labels**: `phase-4`, `config`, `cross-platform`

**Description**

Implement configuration file loading, validation, and default generation.

**Tasks**

- [ ] Create `config.py` module
- [ ] Implement config.json schema (from TECHNICAL_SPEC.md)
- [ ] Implement default config generation
- [ ] Implement config file loading
- [ ] Implement config validation
- [ ] Implement config merging (user + defaults)
- [ ] Handle corrupt/invalid config files
- [ ] Write unit tests for config loading

**Acceptance Criteria**

- ✅ Creates default config.json on first run
- ✅ Loads user config and merges with defaults
- ✅ Validates all config values
- ✅ Handles corrupt JSON gracefully (uses defaults)
- ✅ Logs warnings for invalid settings
- ✅ Unit tests cover all config scenarios

**Definition of Done**

Code merged, all config scenarios tested.

**Estimated Time**: 2 hours

---

## Issue #7: Phase 5 - System Tray UI

**Labels**: `phase-5`, `ui`, `cross-platform`

**Description**

Implement system tray icon and menu using pystray.

**Tasks**

- [ ] Implement `TrayUI` class
- [ ] Create icon images (gray, green, red, yellow)
- [ ] Implement context menu
- [ ] Add menu items: Status, Open Folder, Open Logs, Enable/Disable, Settings, Add to Startup, Exit
- [ ] Implement status icon updates
- [ ] Add click handlers for all menu items
- [ ] Implement "Open Output Folder" functionality
- [ ] Implement "Add to Startup" functionality (Windows startup folder)
- [ ] Test on macOS menu bar
- [ ] Write integration tests with mock callbacks

**Acceptance Criteria**

- ✅ Icon appears in macOS menu bar
- ✅ All menu items functional
- ✅ Icon color changes with status updates
- ✅ "Open Folder" opens correct directory
- ✅ "Add to Startup" creates shortcut (Windows) or shows instructions (macOS)
- ✅ Exit cleanly shuts down application
- ✅ Tooltips show correct status

**Definition of Done**

Code merged, UI tested on macOS, all menu items work.

**Estimated Time**: 4-5 hours

---

## Issue #8: Phase 6 - Integration Testing on macOS

**Labels**: `phase-6`, `testing`, `macOS`

**Description**

Complete integration testing of full pipeline with mock data on macOS.

**Tasks**

- [ ] Complete unit test suite (target: 80% coverage)
- [ ] Run pytest-cov to measure coverage
- [ ] Write integration test: process detection → telemetry → CSV → file
- [ ] Write integration test: multi-lap session (3 laps)
- [ ] Write integration test: error recovery (disk full mock)
- [ ] Test with Chrome as target process on macOS
- [ ] Verify all state transitions
- [ ] Performance testing (CPU/memory monitoring)
- [ ] Fix any bugs discovered during testing

**Acceptance Criteria**

- ✅ Unit test coverage ≥ 80%
- ✅ All integration tests pass
- ✅ Full pipeline test: mock data → 3 CSV files created
- ✅ Error recovery tests pass
- ✅ CPU usage < 1% idle, < 5% logging (macOS)
- ✅ Memory usage < 100MB
- ✅ No memory leaks after 10 minute run

**Definition of Done**

All tests passing, coverage report generated, performance validated.

**Estimated Time**: 7-8 hours

---

## Issue #9: Phase 7.1 - Windows Setup and Real Telemetry

**Labels**: `phase-7`, `windows`, `integration`

**Description**

Setup Windows environment and integrate real telemetry from pyRfactor2SharedMemory.

**Tasks**

- [ ] Clone repository on Windows machine
- [ ] Setup Python environment on Windows
- [ ] Install Windows-specific dependencies
- [ ] Verify rF2SharedMemoryMapPlugin exists in LMU
- [ ] Edit CustomPluginVariables.JSON to enable plugin
- [ ] Implement `RealTelemetryReader` class
- [ ] Map rF2 shared memory fields to our telemetry dict
- [ ] Test telemetry reading with LMU running
- [ ] Verify platform detection switches to real telemetry on Windows

**Acceptance Criteria**

- ✅ Application runs on Windows
- ✅ Plugin enabled in LMU
- ✅ `RealTelemetryReader` reads shared memory successfully
- ✅ Telemetry dict fields populated correctly
- ✅ Platform detection uses real telemetry on Windows
- ✅ Unit tests still pass on Windows

**Definition of Done**

Real telemetry integration complete, basic functionality verified.

**Estimated Time**: 2-3 hours

---

## Issue #10: Phase 7.2 - Live Testing with LMU

**Labels**: `phase-7`, `windows`, `testing`

**Description**

Perform comprehensive live testing with Le Mans Ultimate.

**Tasks**

- [ ] Test: Single practice lap → verify CSV created
- [ ] Test: 3 practice laps → verify 3 files created
- [ ] Test: 5 lap race → verify all laps recorded
- [ ] Test: Interrupted lap → verify handling
- [ ] Test: Auto-detection (start logger before LMU)
- [ ] Test: Process crash recovery
- [ ] Validate CSV output against example.csv
- [ ] Compare CSV with other telemetry tools (if available)
- [ ] Performance testing (30 minute session)
- [ ] Monitor CPU/RAM during gameplay
- [ ] Test all tray menu functions on Windows
- [ ] Document any issues or bugs

**Acceptance Criteria**

- ✅ CSV files match example.csv structure exactly
- ✅ All laps recorded without gaps
- ✅ Auto-detection works reliably
- ✅ Performance: < 5% CPU, < 100MB RAM during gameplay
- ✅ No game lag or stuttering
- ✅ System tray functions correctly on Windows
- ✅ Error handling tested (crash scenarios)
- ✅ At least 3 different session types tested

**Definition of Done**

Live testing complete, all scenarios pass, performance validated.

**Estimated Time**: 5-6 hours

---

## Issue #11: Phase 7.3 - PyInstaller Build and Packaging

**Labels**: `phase-7`, `windows`, `packaging`

**Description**

Build standalone .exe and create release package.

**Tasks**

- [ ] Create PyInstaller build script (`build.py`)
- [ ] Configure PyInstaller options (onefile, windowed, icon)
- [ ] Build .exe on Windows
- [ ] Test .exe on clean Windows machine (no Python)
- [ ] Verify all dependencies bundled
- [ ] Test system tray icon in .exe
- [ ] Test all functionality in .exe
- [ ] Optimize .exe size (UPX compression)
- [ ] Create release package (exe + README + config example)
- [ ] Test auto-start functionality

**Acceptance Criteria**

- ✅ .exe builds without errors
- ✅ .exe runs on clean Windows 10/11 (no Python installed)
- ✅ All functionality works in .exe
- ✅ System tray icon displays correctly
- ✅ File size < 50MB
- ✅ No console window appears
- ✅ Startup time < 2 seconds
- ✅ Add to Startup creates correct shortcut

**Definition of Done**

.exe tested and validated, ready for distribution.

**Estimated Time**: 2-3 hours

---

## Issue #12: Phase 7.4 - Documentation

**Labels**: `phase-7`, `documentation`

**Description**

Create comprehensive user and developer documentation.

**Tasks**

- [ ] Write README.md with Quick Start section
- [ ] Document installation (download .exe)
- [ ] Document first-time setup
- [ ] Document configuration options
- [ ] Create troubleshooting guide
  - Plugin not enabled
  - No telemetry detected
  - Output directory issues
  - Performance problems
- [ ] Write CONTRIBUTING.md for developers
- [ ] Document macOS development setup
- [ ] Document Windows build process
- [ ] Add example CSV to repository
- [ ] Add screenshots of system tray
- [ ] Create LICENSE file

**Acceptance Criteria**

- ✅ README.md complete with Quick Start (< 5 steps to get started)
- ✅ Troubleshooting guide covers top 5 issues
- ✅ Developer guide explains macOS + Windows workflow
- ✅ Screenshots included
- ✅ Example CSV included
- ✅ LICENSE chosen and added
- ✅ Documentation reviewed and clear

**Definition of Done**

Documentation complete, reviewed, and included in release.

**Estimated Time**: 3-4 hours

---

## Issue #13: Phase 7.5 - Release Preparation

**Labels**: `phase-7`, `release`

**Description**

Final validation and GitHub release creation.

**Tasks**

- [ ] Final end-to-end test on Windows
- [ ] Verify all acceptance criteria met
- [ ] Create GitHub release tag (v1.0.0)
- [ ] Upload .exe to GitHub releases
- [ ] Upload example CSV
- [ ] Write release notes
- [ ] Post to OverTake.gg forum (optional)
- [ ] Create video demo (optional)

**Acceptance Criteria**

- ✅ All phase acceptance criteria met
- ✅ GitHub release created
- ✅ Release package includes: .exe, README, config example, LICENSE
- ✅ Release notes describe features and installation
- ✅ Download link tested
- ✅ Zero critical bugs outstanding

**Definition of Done**

v1.0.0 released on GitHub, ready for users.

**Estimated Time**: 1-2 hours

---

## Bonus Issue: Optional Enhancements

**Labels**: `enhancement`, `future`

**Description**

Optional features for future versions.

**Ideas**

- [ ] Windows toast notifications
- [ ] Real-time telemetry viewer
- [ ] Session comparison tool
- [ ] Cloud backup of telemetry
- [ ] Multiple output formats (JSON, binary)
- [ ] Live streaming integration
- [ ] Automatic telemetry analysis
- [ ] macOS native app (not just CLI)

**Priority**: Low (post-v1.0)

---

## How to Use These Issues

1. Create GitHub repository
2. Go to Issues tab
3. Copy each section above into a new issue
4. Use labels to organize
5. Assign to developers
6. Track progress with GitHub Projects (optional)

**Recommended Workflow:**
- Create all issues
- Add to GitHub Project board
- Use columns: Backlog → In Progress → Review → Done
- Move issues as work progresses
- Close issues when acceptance criteria met

---

**Total Issues**: 13 main issues + 1 bonus
**Total Estimated Time**: 48-57 hours (4-6 working days)
