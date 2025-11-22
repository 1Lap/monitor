# Manual Testing Guide - 1Lap Monitor

**Project:** 1Lap Race Dashboard - Monitor Component
**Version:** 1.0
**Date:** 2025-11-22
**Status:** Ready for Testing

---

## Overview

This guide provides step-by-step instructions for manual testing of the monitor component. Testing is divided into three categories:

1. **API Exploration** (Windows + LMU required)
2. **Local Development Testing** (macOS/Linux - no LMU needed)
3. **Integration Testing** (Windows + LMU + Server required)

---

## Prerequisites

### For All Tests
- Python 3.8+ installed
- Virtual environment activated
- All dependencies installed:
  ```bash
  pip install -r requirements.txt -r requirements-dev.txt
  ```

### For Windows/LMU Tests
- Windows OS
- Le Mans Ultimate (LMU) installed and running
- LMU REST API enabled (Settings → Developer → Enable REST API)
- Windows-specific dependencies:
  ```bash
  pip install -r requirements-windows.txt
  ```

### For Server Integration Tests
- Dashboard server running (localhost:5000 or cloud URL)
- Network connectivity
- `config.json` configured with server URL

---

## Testing Categories

## Category 1: API Exploration (Windows + LMU Required)

These tests explore what data is available from LMU and validate the API interfaces work correctly.

### Test 1.1: Shared Memory API Exploration

**Purpose:** Validate telemetry data is readable from LMU shared memory
**Platform:** Windows only
**Requirements:** LMU running
**Time:** 5-10 minutes

#### Steps:

1. **Start LMU**
   - Launch Le Mans Ultimate
   - Load into any session (practice, race, etc.)
   - Wait for session to be active

2. **Run exploration script**
   ```bash
   python tools/explore_shared_memory.py
   ```

3. **Expected output:**
   ```
   ✅ LMU detected! Reading 100 telemetry samples...
   ======================================================================

   ✅ Captured 100 samples in 1.02s (98.0 Hz)

   ======================================================================
   TELEMETRY STRUCTURE
   ======================================================================

   Total fields: XX

   Field listing (name: type):
   ----------------------------------------------------------------------
     ambient_temp                   : float      = 24.0
     brake_temp                     : dict       = dict with 4 keys: ['fl', 'fr', 'rl']...
     car_name                       : str        = 'Porsche 963 GTP'
     ...

   ======================================================================
   DASHBOARD REQUIREMENTS CHECK
   ======================================================================

   Fuel:
     ✅ fuel_remaining
     ✅ fuel_capacity

   Tires:
     ✅ tire_pressure
     ✅ tire_temp
     ✅ tire_wear
   ...
   ```

4. **Verify:**
   - [ ] LMU detected successfully
   - [ ] Samples captured at ~100 Hz
   - [ ] All critical dashboard fields are ✅ (green checkmarks)
   - [ ] Field names match or are similar to mock implementation

5. **Save output (optional):**
   ```bash
   python tools/explore_shared_memory.py --json --output telemetry_data.json
   ```

6. **Troubleshooting:**
   - **"LMU not detected"** → Ensure LMU.exe is running
   - **Low sample rate** → Close other applications consuming CPU
   - **Missing fields** → Try different session types (practice vs race)

---

### Test 1.2: REST API Exploration

**Purpose:** Validate car setup data is readable from LMU REST API
**Platform:** Windows or macOS (LMU required)
**Requirements:** LMU running with REST API enabled
**Time:** 5-10 minutes

#### Steps:

1. **Enable LMU REST API**
   - Open LMU Settings
   - Navigate to Developer settings
   - Enable "REST API" (default port: 6397)
   - Restart LMU if needed

2. **Verify API is accessible**
   - Open browser
   - Navigate to: `http://localhost:6397/rest/watch/version`
   - Should see version JSON response

3. **Load car setup in LMU**
   - Go to garage/setup screen
   - Load any car setup
   - Keep garage screen open

4. **Run exploration script**
   ```bash
   python tools/explore_rest_api.py
   ```

5. **Expected output:**
   ```
   ======================================================================
   LMU REST API CONNECTION TEST
   ======================================================================
   Testing connection to: http://localhost:6397

   ✅ LMU REST API is available

   ======================================================================
   FETCHING SETUP DATA
   ======================================================================
   Endpoint: GET /rest/garage/setup

   ✅ Setup data received (15 top-level keys)

   ======================================================================
   SETUP DATA STRUCTURE
   ======================================================================
     suspension: {dict with 8 keys}
       front_spring_rate: float = 120.5
       rear_spring_rate: float = 115.0
       ...
     aerodynamics: {dict with 4 keys}
       front_wing: int = 5
       rear_wing: int = 8
       ...

   ======================================================================
   CRITICAL SETUP FIELDS CHECK
   ======================================================================

   Suspension:
     ✅ front_spring_rate
     ✅ rear_spring_rate

   Aerodynamics:
     ✅ front_wing
     ✅ rear_wing
   ...
   ```

6. **Verify:**
   - [ ] REST API connection successful
   - [ ] Setup data received
   - [ ] Contains suspension, aerodynamics, brakes, gearing sections
   - [ ] Data values look reasonable

7. **Explore additional endpoints (optional):**
   ```bash
   python tools/explore_rest_api.py --all --output rest_api_full.json
   ```

8. **Troubleshooting:**
   - **"API not available"** → Check REST API is enabled in LMU settings
   - **"No setup data"** → Ensure you're in garage with setup loaded
   - **Connection refused** → Verify port 6397 is not blocked by firewall

---

## Category 2: Local Development Testing (No LMU Required)

These tests validate the monitor works on macOS/Linux using mock data.

### Test 2.1: Basic Startup

**Purpose:** Verify monitor starts and waits for process
**Platform:** Any
**Requirements:** None
**Time:** 2 minutes

#### Steps:

1. **Set invalid process name**
   - Edit `config.json`:
     ```json
     {
       "target_process": "NotARealProcess.exe",
       ...
     }
     ```

2. **Run monitor in log-only mode**
   ```bash
   python monitor.py --log-only
   ```

3. **Expected output:**
   ```
   [Monitor] Starting monitor (v1.0)
   [Monitor] Log-only mode (no server connection)
   [Monitor] Configuration loaded from config.json
   [Monitor] Waiting for process: NotARealProcess.exe
   [Monitor] Process not found, waiting...
   ```

4. **Verify:**
   - [ ] Monitor starts without errors
   - [ ] Shows waiting for process message
   - [ ] Can stop with Ctrl+C

5. **Stop monitor:** Press `Ctrl+C`

---

### Test 2.2: Mock Telemetry (macOS/Linux)

**Purpose:** Verify mock telemetry reader works
**Platform:** macOS/Linux (non-Windows)
**Requirements:** None
**Time:** 3 minutes

#### Steps:

1. **Set valid process name**
   - Edit `config.json`:
     ```json
     {
       "target_process": "python",
       ...
     }
     ```
   - Or use any running process (check with `ps aux | grep python`)

2. **Run monitor in log-only mode**
   ```bash
   python monitor.py --log-only
   ```

3. **Expected output:**
   ```
   [Monitor] Starting monitor (v1.0)
   [Monitor] Log-only mode (no server connection)
   [Monitor] Configuration loaded from config.json
   [Monitor] Waiting for process: python
   [Monitor] ✅ Process detected
   [Monitor] Using mock telemetry reader (non-Windows platform)

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📊 TELEMETRY
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Session: Practice @ Le Mans (Porsche 963 GTP)
   Driver: Test Driver

   Position: 3/20 | Lap 5 | Time: 3:42.123
   Speed: 256.3 km/h | Gear: 6 | RPM: 7267

   Fuel: 42.3 / 90.0 L (47%)

   Tire Pressure (PSI):        Tire Temp (°C):
     FL: 25.1  FR: 24.9          FL: 75.2  FR: 73.8
     RL: 25.3  RR: 25.0          RL: 78.1  RR: 76.5

   Brake Temp (°C):
     FL: 480   FR: 485
     RL: 612   RR: 615

   Engine: 109.5°C | Track: 41.8°C | Ambient: 24.0°C
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

4. **Verify:**
   - [ ] Process detected
   - [ ] Mock telemetry reader activated
   - [ ] Telemetry data updates every ~0.5 seconds
   - [ ] Data changes over time (lap counter increments, fuel decreases)
   - [ ] No errors or crashes

5. **Let run for 30 seconds** to observe lap progression

6. **Stop monitor:** Press `Ctrl+C`

---

### Test 2.3: Invalid Configuration

**Purpose:** Verify monitor handles missing/invalid config
**Platform:** Any
**Requirements:** None
**Time:** 2 minutes

#### Steps:

1. **Backup existing config**
   ```bash
   mv config.json config.json.bak
   ```

2. **Run monitor**
   ```bash
   python monitor.py
   ```

3. **Expected output:**
   ```
   [Monitor] Configuration file not found: config.json
   [Monitor] Creating default configuration...
   [Monitor] ✅ Default config created: config.json
   [Monitor] Please review config.json and restart
   ```

4. **Verify:**
   - [ ] Monitor detects missing config
   - [ ] Creates default config.json
   - [ ] Exits gracefully (no crash)
   - [ ] config.json file exists

5. **Check created config:**
   ```bash
   cat config.json
   ```
   - Should match config.json.example

6. **Restore original config**
   ```bash
   mv config.json.bak config.json
   ```

---

### Test 2.4: Server Connection Test

**Purpose:** Verify server connection test utility works
**Platform:** Any
**Requirements:** Dashboard server running (or test failure case)
**Time:** 3 minutes

#### Steps (Server Running):

1. **Start dashboard server**
   - Ensure server is running at `http://localhost:5000`

2. **Run connection test**
   ```bash
   python tools/test_server_connection.py
   ```

3. **Expected output:**
   ```
   ============================================================
   Dashboard Server Connection Test
   ============================================================
   Server URL: http://localhost:5000

   [1/4] Testing connection...
   ✅ Connected to server
   ✅ Session ID received: abc-123-def
      Dashboard URL: http://localhost:5000/dashboard/abc-123-def

   [2/4] Testing setup data publish...
   ✅ Setup data sent

   [3/4] Testing telemetry publish...
   ✅ Telemetry data sent (3 updates)

   [4/4] Testing disconnect...
   ✅ Disconnected cleanly

   ============================================================
   Test Summary
   ============================================================
   Connection:     ✅ PASS
   Session ID:     ✅ PASS
   Setup publish:  ✅ PASS
   Telemetry pub:  ✅ PASS
   ============================================================
   🎉 All tests passed!
   ```

4. **Verify:**
   - [ ] All 4 tests pass
   - [ ] Session ID received
   - [ ] Dashboard URL displayed

#### Steps (Server Not Running):

1. **Stop dashboard server** (if running)

2. **Run connection test**
   ```bash
   python tools/test_server_connection.py
   ```

3. **Expected output:**
   ```
   ============================================================
   Dashboard Server Connection Test
   ============================================================
   Server URL: http://localhost:5000

   [1/4] Testing connection...
   ❌ Error: Connection refused
   ```

4. **Verify:**
   - [ ] Error message displayed
   - [ ] No crash or hang
   - [ ] Exits gracefully

---

## Category 3: Integration Testing (Windows + LMU + Server)

These tests require the complete stack: Windows, LMU running, and dashboard server active.

### Test 3.1: End-to-End Flow

**Purpose:** Validate complete monitor → server → dashboard flow
**Platform:** Windows
**Requirements:** LMU running, server running
**Time:** 10-15 minutes

#### Setup:

1. **Start dashboard server**
   ```bash
   # In server repository
   python server.py
   ```
   - Note the server URL (e.g., `http://localhost:5000`)

2. **Configure monitor**
   - Edit `config.json`:
     ```json
     {
       "server_url": "http://localhost:5000",
       "session_id": "auto",
       "update_rate_hz": 2,
       "poll_interval": 0.01,
       "target_process": "LMU.exe"
     }
     ```

3. **Start LMU**
   - Launch Le Mans Ultimate
   - Load into practice/race session
   - Go to garage and load car setup

#### Test Steps:

1. **Start monitor**
   ```bash
   python monitor.py
   ```

2. **Expected output:**
   ```
   [Monitor] Starting monitor (v1.0)
   [Monitor] Configuration loaded from config.json
   [Monitor] Connecting to server: http://localhost:5000
   [Monitor] ✅ Connected to server
   [Monitor] ✅ Session ID assigned: abc-123-def
   [Monitor] Dashboard URL: http://localhost:5000/dashboard/abc-123-def
   [Monitor] Waiting for process: LMU.exe
   [Monitor] ✅ Process detected
   [Monitor] ✅ Setup data sent
   [Monitor] Publishing telemetry at 2 Hz...
   ```

3. **Verify monitor output:**
   - [ ] Connects to server successfully
   - [ ] Receives session ID
   - [ ] Displays dashboard URL
   - [ ] Detects LMU process
   - [ ] Sends setup data (once)
   - [ ] Publishing telemetry (continuous)
   - [ ] No errors or warnings

4. **Open dashboard in browser**
   - Navigate to dashboard URL shown in monitor output
   - Example: `http://localhost:5000/dashboard/abc-123-def`

5. **Verify dashboard display:**
   - [ ] Dashboard loads successfully
   - [ ] Session info displayed (track, car, driver)
   - [ ] Lap counter updates
   - [ ] Fuel gauge shows correct level
   - [ ] Tire data updates (pressures, temps)
   - [ ] Brake temps update
   - [ ] Speed/RPM/gear update in real-time
   - [ ] Setup tab shows car setup data

6. **Test live updates:**
   - [ ] Drive in LMU and watch dashboard update
   - [ ] Fuel decreases over time
   - [ ] Lap counter increments
   - [ ] Tire temps change
   - [ ] All updates happen at ~2 Hz (smooth but not jittery)

7. **Test LMU restart:**
   - Close LMU
   - Monitor should show: `[Monitor] Process lost, waiting...`
   - Restart LMU
   - Monitor should re-detect and re-send setup

8. **Verify:**
   - [ ] Monitor detects LMU shutdown
   - [ ] Monitor re-detects LMU on restart
   - [ ] Setup data re-sent after restart
   - [ ] Dashboard reconnects and resumes

9. **Stop monitor:** Press `Ctrl+C`
   - [ ] Monitor exits cleanly
   - [ ] No errors on shutdown

---

### Test 3.2: Server Reconnection

**Purpose:** Verify monitor handles server disconnection gracefully
**Platform:** Windows
**Requirements:** LMU running, server running
**Time:** 5 minutes

#### Steps:

1. **Start monitor with LMU and server running**
   ```bash
   python monitor.py
   ```

2. **Verify normal operation:**
   - Monitor connected
   - Telemetry publishing

3. **Kill server process**
   - Stop the dashboard server

4. **Observe monitor behavior:**
   - Monitor should detect disconnection
   - Should attempt reconnection (depends on implementation)

5. **Restart server**

6. **Verify:**
   - [ ] Monitor detects server loss
   - [ ] Monitor handles disconnection gracefully (no crash)
   - [ ] Monitor reconnects when server returns (or requires restart)

**Note:** Current MVP may require manual restart. Future versions will have auto-reconnect.

---

### Test 3.3: Performance Validation

**Purpose:** Verify monitor performance meets requirements
**Platform:** Windows
**Requirements:** LMU running, server running
**Time:** 30 minutes

#### Test 3.3.1: Update Rate

1. **Start monitor with verbose logging**
   ```bash
   python monitor.py --log-only
   ```

2. **Observe telemetry update frequency**
   - Should be ~2 updates per second
   - ±10% variance is acceptable (1.8 - 2.2 Hz)

3. **Verify:**
   - [ ] Update rate is ~2 Hz
   - [ ] Updates are consistent (no big gaps)
   - [ ] No warnings about slow updates

#### Test 3.3.2: Memory Usage

1. **Start monitor**
   ```bash
   python monitor.py
   ```

2. **Monitor memory usage** (Windows Task Manager or `psutil`)
   - Check initial memory: ~XX MB
   - Run for 30 minutes
   - Check final memory: Should be stable

3. **Verify:**
   - [ ] Initial memory < 100 MB
   - [ ] Memory stable over time (no leaks)
   - [ ] No growth trend over 30 minutes

#### Test 3.3.3: CPU Usage

1. **Start monitor**

2. **Monitor CPU usage** (Windows Task Manager)
   - Should be < 5% on modern hardware
   - May spike briefly during startup

3. **Verify:**
   - [ ] CPU usage < 5% during normal operation
   - [ ] No sustained high CPU usage

---

## Test Results Checklist

Use this checklist to track your testing progress:

### API Exploration (Windows + LMU)
- [ ] Test 1.1: Shared Memory API Exploration
- [ ] Test 1.2: REST API Exploration

### Local Development (Any Platform)
- [ ] Test 2.1: Basic Startup
- [ ] Test 2.2: Mock Telemetry (macOS/Linux)
- [ ] Test 2.3: Invalid Configuration
- [ ] Test 2.4: Server Connection Test

### Integration (Windows + LMU + Server)
- [ ] Test 3.1: End-to-End Flow
- [ ] Test 3.2: Server Reconnection
- [ ] Test 3.3.1: Update Rate Performance
- [ ] Test 3.3.2: Memory Usage Performance
- [ ] Test 3.3.3: CPU Usage Performance

---

## Reporting Issues

If you encounter issues during testing:

1. **Document the problem:**
   - Test number and name
   - Expected behavior
   - Actual behavior
   - Error messages (full text)
   - Screenshots (if relevant)

2. **Include environment info:**
   - OS and version
   - Python version (`python --version`)
   - LMU version (if applicable)
   - Dependencies versions (`pip list`)

3. **Attach logs:**
   - Monitor output (copy from terminal)
   - Server logs (if applicable)
   - Any error stack traces

4. **Create GitHub issue:**
   - Use template: `Bug Report - [Test X.Y] Brief Description`
   - Include all info from steps 1-3

---

## Success Criteria

Testing is complete when:

- [ ] All API exploration tests pass (Windows)
- [ ] All local development tests pass (macOS/Linux)
- [ ] All integration tests pass (Windows + Server)
- [ ] Performance meets targets:
  - Update rate: 2 Hz ± 10%
  - Memory: < 100 MB, stable
  - CPU: < 5%
- [ ] No crashes or unhandled errors
- [ ] Dashboard displays all data correctly
- [ ] Documentation matches actual behavior

---

## Next Steps After Testing

1. **Document findings:**
   - Update `docs/shared_memory_fields.txt` (from Test 1.1)
   - Update `docs/rest_api_responses.txt` (from Test 1.2)
   - Note any field name differences from mock

2. **Update code if needed:**
   - Fix any bugs found
   - Adjust field mappings if API differs from mock
   - Update tests if behavior changed

3. **Update documentation:**
   - Mark tests as complete in bug files
   - Update CLAUDE.md with any changes
   - Update README with setup instructions

4. **Prepare for deployment:**
   - Package for Windows distribution
   - Create user guide
   - Set up CI/CD for automated testing

---

## Tools Reference

Quick reference for test tools:

```bash
# API Exploration
python tools/explore_shared_memory.py              # Test shared memory API
python tools/explore_shared_memory.py --json       # Show full JSON output
python tools/explore_shared_memory.py --output telemetry.json  # Save to file

python tools/explore_rest_api.py                   # Test REST API
python tools/explore_rest_api.py --all             # Test all endpoints
python tools/explore_rest_api.py --output setup.json  # Save to file

# Server Connection
python tools/test_server_connection.py             # Test localhost
python tools/test_server_connection.py --server http://example.com  # Test cloud
python tools/test_server_connection.py -v          # Verbose output

# Monitor
python monitor.py                                  # Normal mode (connects to server)
python monitor.py --log-only                       # Log mode (no server)

# Tests
pytest -v                                          # Run all unit tests
pytest tests/test_monitor.py -v                    # Run specific test file
pytest --cov=src --cov-report=html                 # Coverage report
```

---

**Good luck with testing! 🏁**
