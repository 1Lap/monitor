# Feature: Test Server Connection Script

**Type:** Testing Tool
**Priority:** Low
**Phase:** MVP - Phase 1
**Estimated Time:** 30 minutes

---

## Overview

Create a simple test script to validate connection to the dashboard server before running the full monitor. This helps debug server connectivity issues independently.

## Objective

Build a minimal test script that:
1. Attempts to connect to server
2. Requests session ID
3. Sends test data
4. Validates WebSocket communication
5. Reports success/failure

## Requirements

### Must Have

1. **Script: `tools/test_server_connection.py`**
   - Command-line tool
   - Takes server URL as argument
   - Tests WebSocket connection
   - Displays results

2. **Connection Tests**
   - Connect to server
   - Request session ID
   - Send test setup data
   - Send test telemetry data
   - Disconnect cleanly

3. **Output**
   - Clear success/failure messages
   - Connection status
   - Session ID received
   - Any errors encountered

### Nice to Have

- Timeout handling
- Retry logic
- Performance metrics (latency)
- Verbose mode for debugging

## Implementation

```python
#!/usr/bin/env python3
"""
Test Dashboard Server Connection
Simple script to validate WebSocket connection to dashboard server
"""
import sys
import time
import argparse
import socketio
from datetime import datetime


def test_server_connection(server_url: str, verbose: bool = False):
    """
    Test connection to dashboard server

    Args:
        server_url: Server URL (e.g., 'http://localhost:5000')
        verbose: Print verbose output

    Returns:
        True if all tests pass, False otherwise
    """
    print("=" * 60)
    print("Dashboard Server Connection Test")
    print("=" * 60)
    print(f"Server URL: {server_url}")
    print()

    # State tracking
    connected = False
    session_id = None
    setup_sent = False
    telemetry_sent = False

    # Create WebSocket client
    sio = socketio.Client()

    # Event handlers
    @sio.event
    def connect():
        nonlocal connected
        print("✅ Connected to server")
        connected = True

        # Request session ID
        if verbose:
            print("  → Requesting session ID...")
        sio.emit('request_session_id', {})

    @sio.event
    def disconnect():
        print("❌ Disconnected from server")

    @sio.event
    def session_id_assigned(data):
        nonlocal session_id
        session_id = data['session_id']
        print(f"✅ Session ID received: {session_id}")
        print(f"   Dashboard URL: {server_url}/dashboard/{session_id}")

    @sio.on('*')
    def catch_all(event, data):
        if verbose:
            print(f"  ← Event: {event}")
            print(f"     Data: {data}")

    # Test sequence
    try:
        # Test 1: Connect
        print("[1/4] Testing connection...")
        sio.connect(server_url, wait_timeout=5)

        if not connected:
            print("❌ Failed to connect")
            return False

        # Wait for session ID
        timeout = 5
        start = time.time()
        while not session_id and (time.time() - start) < timeout:
            time.sleep(0.1)

        if not session_id:
            print("❌ Failed to receive session ID")
            return False

        # Test 2: Send setup data
        print("\n[2/4] Testing setup data publish...")
        test_setup = {
            'suspension': {
                'front_spring_rate': 120.5,
                'rear_spring_rate': 115.0
            },
            'aerodynamics': {
                'front_wing': 5,
                'rear_wing': 8
            }
        }

        sio.emit('setup_data', {
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'setup': test_setup
        })

        time.sleep(0.2)
        print("✅ Setup data sent")
        setup_sent = True

        # Test 3: Send telemetry data
        print("\n[3/4] Testing telemetry publish...")
        test_telemetry = {
            'timestamp': datetime.utcnow().isoformat(),
            'lap': 5,
            'position': 3,
            'lap_time': 123.456,
            'fuel': 42.3,
            'fuel_capacity': 90.0,
            'tire_pressures': {'fl': 25.1, 'fr': 24.9, 'rl': 25.3, 'rr': 25.0},
            'tire_temps': {'fl': 75.2, 'fr': 73.8, 'rl': 78.1, 'rr': 76.5},
            'brake_temps': {'fl': 480.0, 'fr': 485.0, 'rl': 612.0, 'rr': 615.0},
            'engine_water_temp': 109.5,
            'track_temp': 41.8,
            'ambient_temp': 24.0,
            'speed': 256.3,
            'gear': 6,
            'rpm': 7267.0,
            'player_name': 'Test Driver',
            'car_name': 'Test Car',
            'track_name': 'Test Track',
            'session_type': 'Test'
        }

        # Send a few telemetry updates
        for i in range(3):
            sio.emit('telemetry_update', {
                'session_id': session_id,
                'telemetry': test_telemetry
            })
            time.sleep(0.5)

        print("✅ Telemetry data sent (3 updates)")
        telemetry_sent = True

        # Test 4: Disconnect
        print("\n[4/4] Testing disconnect...")
        sio.disconnect()
        time.sleep(0.2)
        print("✅ Disconnected cleanly")

        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Connection:     {'✅ PASS' if connected else '❌ FAIL'}")
        print(f"Session ID:     {'✅ PASS' if session_id else '❌ FAIL'}")
        print(f"Setup publish:  {'✅ PASS' if setup_sent else '❌ FAIL'}")
        print(f"Telemetry pub:  {'✅ PASS' if telemetry_sent else '❌ FAIL'}")
        print("=" * 60)

        all_passed = connected and session_id and setup_sent and telemetry_sent
        if all_passed:
            print("🎉 All tests passed!")
        else:
            print("❌ Some tests failed")

        return all_passed

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        if verbose:
            traceback.print_exc()
        return False
    finally:
        if sio.connected:
            sio.disconnect()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Test connection to dashboard server'
    )
    parser.add_argument(
        '--server',
        default='http://localhost:5000',
        help='Server URL (default: http://localhost:5000)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    success = test_server_connection(args.server, args.verbose)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

## Usage

### Basic Test
```bash
# Test localhost server
python tools/test_server_connection.py

# Expected output:
# ============================================================
# Dashboard Server Connection Test
# ============================================================
# Server URL: http://localhost:5000
#
# [1/4] Testing connection...
# ✅ Connected to server
# ✅ Session ID received: abc-def-ghi
#    Dashboard URL: http://localhost:5000/dashboard/abc-def-ghi
#
# [2/4] Testing setup data publish...
# ✅ Setup data sent
#
# [3/4] Testing telemetry publish...
# ✅ Telemetry data sent (3 updates)
#
# [4/4] Testing disconnect...
# ✅ Disconnected cleanly
#
# ============================================================
# Test Summary
# ============================================================
# Connection:     ✅ PASS
# Session ID:     ✅ PASS
# Setup publish:  ✅ PASS
# Telemetry pub:  ✅ PASS
# ============================================================
# 🎉 All tests passed!
```

### Test Custom Server
```bash
# Test cloud server
python tools/test_server_connection.py --server http://dashboard.1lap.io

# Test with verbose output
python tools/test_server_connection.py -v
```

### Test Failure Scenarios

```bash
# Server offline (should fail gracefully)
python tools/test_server_connection.py --server http://localhost:9999

# Expected output:
# ============================================================
# Dashboard Server Connection Test
# ============================================================
# Server URL: http://localhost:9999
#
# [1/4] Testing connection...
# ❌ Error: Connection error
```

## Use Cases

1. **Pre-flight Check:** Verify server is running before starting monitor
2. **Network Debugging:** Test connectivity to cloud server
3. **Server Validation:** Verify server implements correct API
4. **CI/CD Testing:** Automated server testing

## Validation Checklist

- [ ] Script connects to server
- [ ] Receives session ID
- [ ] Sends setup data
- [ ] Sends telemetry data
- [ ] Disconnects cleanly
- [ ] Handles errors gracefully
- [ ] Clear pass/fail output
- [ ] Works with local server
- [ ] Works with cloud server

## Dependencies

- `python-socketio[client]` (already in requirements.txt)

## Integration with Monitor

Can be used as pre-flight check in monitor:

```python
# In monitor.py (optional)
def check_server(self):
    """Pre-flight server check"""
    print("[Monitor] Testing server connection...")

    # Quick connection test
    try:
        test_sio = socketio.Client()
        test_sio.connect(self.config['server_url'], wait_timeout=5)
        test_sio.disconnect()
        print("[Monitor] ✅ Server is reachable")
        return True
    except Exception as e:
        print(f"[Monitor] ❌ Server not reachable: {e}")
        print("[Monitor] Use tools/test_server_connection.py to debug")
        return False
```

## Related Files

- `src/dashboard_publisher.py` - Publisher implementation
- `monitor.py` - Main application
- `RACE_DASHBOARD_PLAN.md` - API contract

---

**Next Steps:** Use this tool to validate server implementation when server repo is ready.
