# Feature: Create Monitor Entry Point

**Type:** Implementation
**Priority:** High
**Phase:** MVP - Phase 1
**Estimated Time:** 2-3 hours
**Status:** ✅ COMPLETE

---

## Completion Summary

**Date Completed:** 2025-11-22

**Implementation:**
- ✅ Created `monitor.py` with Monitor class
- ✅ Implemented main entry point with argparse
- ✅ Added --log-only mode for console logging
- ✅ Created `config.json` with default configuration
- ✅ Added `fetch_setup_data()` method to LMURestAPI
- ✅ Written 15 comprehensive tests (all passing)
- ✅ All 51 project tests passing

**Files Created:**
- `/home/user/monitor/monitor.py` - Main entry point
- `/home/user/monitor/config.json` - Default configuration
- `/home/user/monitor/tests/test_monitor.py` - Comprehensive test suite (15 tests)

**Files Modified:**
- `/home/user/monitor/src/lmu_rest_api.py` - Added `fetch_setup_data()` method

---

## Overview

Create the main entry point (`monitor.py`) that orchestrates all monitor components: process detection, telemetry reading, REST API fetching, and dashboard publishing.

## Objective

Build a production-ready monitor application that:
1. Loads configuration from `config.json`
2. Waits for LMU process
3. Connects to dashboard server
4. Fetches setup data once
5. Continuously publishes telemetry (2Hz)
6. Handles errors gracefully

## Requirements

### Must Have

1. **File: `monitor.py`**
   - Main entry point for monitor
   - Configuration loading
   - Component initialization
   - Main loop with error handling
   - Graceful shutdown

2. **Configuration: `config.json`**
   - Server URL
   - Update rate (Hz)
   - Process name (LMU.exe)
   - Session ID (auto or manual)

3. **Integration**
   - Use `ProcessMonitor` to detect LMU
   - Use `TelemetryReader` for telemetry
   - Use `LMURestAPI` for setup
   - Use `DashboardPublisher` for publishing

4. **Logging**
   - Console output for status
   - Connection status
   - Error messages
   - Dashboard URL display

### Nice to Have

- Signal handling (Ctrl+C graceful shutdown)
- Auto-reconnect to server on disconnect
- Retry logic for REST API
- Logging to file
- Status indicators (colors)

## Implementation

```python
"""
1Lap Race Dashboard Monitor
Reads LMU telemetry and publishes to dashboard server
"""
import json
import time
import signal
import sys
from pathlib import Path
from datetime import datetime

from src.telemetry.telemetry_interface import get_telemetry_reader
from src.lmu_rest_api import LMURestAPI
from src.process_monitor import ProcessMonitor
from src.dashboard_publisher import DashboardPublisher


class Monitor:
    """Main monitor application"""

    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize monitor

        Args:
            config_path: Path to config.json
        """
        self.config = self._load_config(config_path)
        self.running = False
        self.setup_sent = False

        # Initialize components
        self.telemetry = get_telemetry_reader()
        self.rest_api = LMURestAPI()
        self.process_monitor = ProcessMonitor({
            'target_process': self.config['target_process']
        })
        self.publisher = DashboardPublisher(
            server_url=self.config['server_url'],
            session_id=self.config.get('session_id', 'auto')
        )

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path) as f:
                config = json.load(f)
            print(f"[Monitor] Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            print(f"[Monitor] ERROR: Config file not found: {config_path}")
            print("[Monitor] Creating default config.json...")
            self._create_default_config(config_path)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[Monitor] ERROR: Invalid JSON in config: {e}")
            sys.exit(1)

    def _create_default_config(self, config_path: str):
        """Create default config.json"""
        default_config = {
            "server_url": "http://localhost:5000",
            "session_id": "auto",
            "update_rate_hz": 2,
            "poll_interval": 0.01,
            "target_process": "LMU.exe"
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"[Monitor] Default config created: {config_path}")
        print("[Monitor] Edit config.json and run again")

    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print("\n[Monitor] Shutdown signal received")
        self.stop()

    def start(self):
        """Start monitor"""
        print("=" * 60)
        print("1Lap Race Dashboard Monitor")
        print("=" * 60)
        print(f"Server: {self.config['server_url']}")
        print(f"Update rate: {self.config['update_rate_hz']} Hz")
        print(f"Target process: {self.config['target_process']}")
        print("=" * 60)

        # Connect to server
        print("[Monitor] Connecting to dashboard server...")
        if not self.publisher.connect():
            print("[Monitor] ERROR: Failed to connect to server")
            print("[Monitor] Make sure server is running")
            return

        # Wait for session ID
        print("[Monitor] Waiting for session ID...")
        timeout = 10
        start_time = time.time()
        while not self.publisher.is_ready():
            if time.time() - start_time > timeout:
                print("[Monitor] ERROR: Timeout waiting for session ID")
                return
            time.sleep(0.1)

        print("[Monitor] Ready!")
        print("=" * 60)

        # Main loop
        self.running = True
        update_interval = 1.0 / self.config['update_rate_hz']
        last_update = 0

        try:
            while self.running:
                # Check if LMU is running
                if not self.process_monitor.is_running():
                    if self.setup_sent:
                        print("[Monitor] LMU process stopped")
                        self.setup_sent = False
                    time.sleep(1)
                    continue

                # LMU detected - send setup once
                if not self.setup_sent:
                    print("[Monitor] LMU detected, fetching setup...")
                    self._send_setup()

                # Publish telemetry at configured rate
                current_time = time.time()
                if current_time - last_update >= update_interval:
                    self._send_telemetry()
                    last_update = current_time

                # Sleep briefly to avoid busy loop
                time.sleep(self.config['poll_interval'])

        except Exception as e:
            print(f"[Monitor] ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()

    def _send_setup(self):
        """Fetch and send setup data"""
        if not self.rest_api.is_available():
            print("[Monitor] REST API not available, skipping setup")
            self.setup_sent = True  # Don't keep trying
            return

        setup = self.rest_api.fetch_setup_data()
        if setup:
            self.publisher.publish_setup(setup)
            print("[Monitor] Setup data sent")
            self.setup_sent = True
        else:
            print("[Monitor] No setup data available")
            self.setup_sent = True  # Don't keep trying

    def _send_telemetry(self):
        """Read and send telemetry data"""
        if not self.telemetry.is_available():
            return

        data = self.telemetry.read()
        if data:
            self.publisher.publish_telemetry(data)

    def stop(self):
        """Stop monitor"""
        print("[Monitor] Stopping...")
        self.running = False
        self.publisher.disconnect()
        print("[Monitor] Stopped")


def main():
    """Main entry point"""
    monitor = Monitor()
    monitor.start()


if __name__ == '__main__':
    main()
```

## Configuration Format

**`config.json`**
```json
{
  "server_url": "http://localhost:5000",
  "session_id": "auto",
  "update_rate_hz": 2,
  "poll_interval": 0.01,
  "target_process": "LMU.exe"
}
```

### Configuration Fields

- `server_url` - Dashboard server URL (local or cloud)
- `session_id` - Session ID or "auto" to request from server
- `update_rate_hz` - Telemetry publish rate (default: 2Hz)
- `poll_interval` - Telemetry read interval (default: 0.01s = 100Hz)
- `target_process` - Process to monitor (default: "LMU.exe")

## Testing Strategy

### Manual Testing

1. **Test without server:**
   ```bash
   python monitor.py
   # Should show connection error
   ```

2. **Test without LMU:**
   ```bash
   # Start server first
   python monitor.py
   # Should connect, wait for LMU
   ```

3. **Test with LMU:**
   ```bash
   # Start server, start LMU, start monitor
   python monitor.py
   # Should connect, fetch setup, publish telemetry
   ```

4. **Test Ctrl+C shutdown:**
   ```bash
   python monitor.py
   # Press Ctrl+C
   # Should shutdown gracefully
   ```

### Integration Test

```python
# tests/test_monitor_integration.py

def test_monitor_initialization():
    """Test monitor initializes components"""
    monitor = Monitor()
    assert monitor.telemetry is not None
    assert monitor.rest_api is not None
    assert monitor.process_monitor is not None
    assert monitor.publisher is not None


def test_monitor_config_loading():
    """Test config loading"""
    # Create test config
    config = {
        'server_url': 'http://test:5000',
        'update_rate_hz': 5,
        'target_process': 'test.exe'
    }
    with open('test_config.json', 'w') as f:
        json.dump(config, f)

    monitor = Monitor('test_config.json')
    assert monitor.config['server_url'] == 'http://test:5000'
    assert monitor.config['update_rate_hz'] == 5

    # Cleanup
    os.remove('test_config.json')
```

## Usage

### Local Development
```bash
# 1. Edit config.json (set server URL)
# 2. Start monitor
python monitor.py

# Expected output:
# ============================================================
# 1Lap Race Dashboard Monitor
# ============================================================
# Server: http://localhost:5000
# Update rate: 2 Hz
# Target process: LMU.exe
# ============================================================
# [Monitor] Connecting to dashboard server...
# [Publisher] Connected to http://localhost:5000
# [Monitor] Waiting for session ID...
# [Publisher] Session ID: abc-def-ghi
# [Publisher] Dashboard URL: http://localhost:5000/dashboard/abc-def-ghi
# [Monitor] Ready!
# ============================================================
# [Monitor] LMU detected, fetching setup...
# [Publisher] Setup data sent
# [Monitor] Setup data sent
```

### Windows with LMU
```bash
# Set config to LMU.exe
python monitor.py
```

### macOS Development (Mock Mode)
```bash
# Set target_process to a running process (e.g., "python")
python monitor.py
```

## Error Handling

### Scenarios to Handle

1. **Server offline**
   - Show error message
   - Exit gracefully

2. **LMU not running**
   - Wait and retry
   - Don't spam logs

3. **REST API unavailable**
   - Skip setup (not critical)
   - Continue with telemetry

4. **Disconnection during session**
   - Attempt reconnection
   - Buffer telemetry (optional)

5. **Invalid config**
   - Show error
   - Create default config
   - Exit

## Validation Checklist

- [x] Loads config from config.json
- [x] Creates default config if missing
- [x] Connects to server
- [x] Receives session ID
- [x] Displays dashboard URL
- [x] Detects LMU process
- [x] Fetches setup data once
- [x] Publishes telemetry at 2Hz
- [x] Handles Ctrl+C gracefully
- [ ] Reconnects on disconnect (future enhancement)
- [ ] Works on Windows with LMU (requires manual testing)
- [x] Works on macOS with mock data

## Dependencies

All existing components:
- `src.telemetry.telemetry_interface`
- `src.lmu_rest_api`
- `src.process_monitor`
- `src.dashboard_publisher` (new)

## Related Files

- `RACE_DASHBOARD_PLAN.md` - Architecture
- `bugs/implement_dashboard_publisher.md` - Publisher component
- `config.json` - Configuration

---

**Next Steps:** After implementing, test end-to-end with server (when available) or mock server.
