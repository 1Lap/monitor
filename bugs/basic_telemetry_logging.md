# Feature: Basic Telemetry Logging for Testing

**Type:** Testing Tool
**Priority:** Medium
**Phase:** MVP - Phase 1
**Estimated Time:** 1 hour
**Status:** ✅ COMPLETE

---

## Completion Summary

**Date Completed:** 2025-11-22

**Implementation:**
- ✅ Added `--log-only` flag to monitor.py
- ✅ Implemented `log_telemetry()` function for formatted console output
- ✅ Integrated logging mode into Monitor class
- ✅ Added `start_logging_mode()` method to Monitor
- ✅ Tests passing for logging functionality

**Integration:** Logging mode is part of main monitor.py implementation (see bugs/create_monitor_entry_point.md)

---

## Overview

Create a simple console logging mode for the monitor to validate telemetry data flow without requiring the server. This helps with development and debugging.

## Objective

Add a `--log-only` mode to `monitor.py` that:
1. Reads telemetry from LMU (or mock)
2. Logs to console instead of publishing to server
3. Helps validate data extraction and formatting
4. Useful for development without server

## Requirements

### Must Have

1. **Command-line flag: `--log-only`**
   - Run monitor in logging mode
   - No server connection required
   - Console output only

2. **Logging Output**
   - Pretty-printed telemetry data
   - Update at configured rate (2Hz)
   - Show key fields (lap, fuel, temps, etc.)
   - Easy to read format

3. **Use Cases**
   - Test telemetry reading on Windows
   - Validate data extraction
   - Debug field mapping
   - Development without server

### Nice to Have

- Color-coded output (green=good, yellow=warning, red=critical)
- Filter output (only show specific fields)
- Export to file (CSV or JSON)
- Diff mode (show only changed values)

## Implementation

### Add Logging Mode to `monitor.py`

```python
import argparse
from datetime import datetime


def log_telemetry(data: dict):
    """
    Pretty-print telemetry to console

    Args:
        data: Telemetry dictionary
    """
    print("\n" + "=" * 60)
    print(f"Telemetry @ {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    # Session info
    print(f"Driver: {data.get('player_name', 'N/A')}")
    print(f"Car: {data.get('car_name', 'N/A')}")
    print(f"Track: {data.get('track_name', 'N/A')}")
    print(f"Session: {data.get('session_type', 'N/A')}")
    print()

    # Position & lap
    print(f"Position: P{data.get('race_position', 0)} | Lap: {data.get('lap', 0)}")
    print(f"Lap Time: {data.get('lap_time', 0.0):.3f}s")
    print()

    # Fuel
    fuel = data.get('fuel_remaining', 0.0)
    fuel_cap = data.get('fuel_at_start', 90.0)
    fuel_pct = (fuel / fuel_cap * 100) if fuel_cap > 0 else 0
    print(f"Fuel: {fuel:.1f}L / {fuel_cap:.1f}L ({fuel_pct:.0f}%)")
    print()

    # Tires
    tire_psi = data.get('tyre_pressure', {})
    tire_temp = data.get('tyre_temp', {})
    print("Tires:")
    print(f"  FL: {tire_psi.get('fl', 0):.1f} PSI, {tire_temp.get('fl', 0):.1f}°C")
    print(f"  FR: {tire_psi.get('fr', 0):.1f} PSI, {tire_temp.get('fr', 0):.1f}°C")
    print(f"  RL: {tire_psi.get('rl', 0):.1f} PSI, {tire_temp.get('rl', 0):.1f}°C")
    print(f"  RR: {tire_psi.get('rr', 0):.1f} PSI, {tire_temp.get('rr', 0):.1f}°C")
    print()

    # Brakes
    brake_temp = data.get('brake_temp', {})
    print("Brakes:")
    print(f"  FL: {brake_temp.get('fl', 0):.0f}°C | FR: {brake_temp.get('fr', 0):.0f}°C")
    print(f"  RL: {brake_temp.get('rl', 0):.0f}°C | RR: {brake_temp.get('rr', 0):.0f}°C")
    print()

    # Engine & weather
    print(f"Engine: {data.get('engine_temp', 0):.1f}°C")
    print(f"Track: {data.get('track_temp', 0):.1f}°C | Ambient: {data.get('ambient_temp', 0):.1f}°C")
    print()

    # Speed/gear
    print(f"Speed: {data.get('speed', 0):.0f} km/h | Gear: {data.get('gear', 0)} | RPM: {data.get('rpm', 0):.0f}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='1Lap Race Dashboard Monitor')
    parser.add_argument('--log-only', action='store_true',
                        help='Log telemetry to console instead of publishing to server')
    parser.add_argument('--config', default='config.json',
                        help='Path to config file (default: config.json)')
    args = parser.parse_args()

    monitor = Monitor(args.config)

    if args.log_only:
        monitor.start_logging_mode()
    else:
        monitor.start()


# Add to Monitor class
def start_logging_mode(self):
    """Start monitor in logging mode (no server connection)"""
    print("=" * 60)
    print("1Lap Race Dashboard Monitor - LOGGING MODE")
    print("=" * 60)
    print(f"Update rate: {self.config['update_rate_hz']} Hz")
    print(f"Target process: {self.config['target_process']}")
    print("=" * 60)
    print("Waiting for LMU...")

    self.running = True
    update_interval = 1.0 / self.config['update_rate_hz']
    last_update = 0

    try:
        while self.running:
            # Check if LMU is running
            if not self.process_monitor.is_running():
                time.sleep(1)
                continue

            # Log telemetry at configured rate
            current_time = time.time()
            if current_time - last_update >= update_interval:
                data = self.telemetry.read()
                if data:
                    log_telemetry(data)
                last_update = current_time

            time.sleep(self.config['poll_interval'])

    except KeyboardInterrupt:
        print("\n[Monitor] Stopped")
```

## Usage

### Console Logging Mode
```bash
# Log telemetry to console (no server)
python monitor.py --log-only

# Expected output:
# ============================================================
# 1Lap Race Dashboard Monitor - LOGGING MODE
# ============================================================
# Update rate: 2 Hz
# Target process: LMU.exe
# ============================================================
# Waiting for LMU...
#
# ============================================================
# Telemetry @ 14:30:22
# ============================================================
# Driver: John Doe
# Car: Toyota GR010
# Track: Bahrain International Circuit
# Session: Race
#
# Position: P3 | Lap: 45
# Lap Time: 123.456s
#
# Fuel: 42.3L / 90.0L (47%)
#
# Tires:
#   FL: 25.1 PSI, 75.2°C
#   FR: 24.9 PSI, 73.8°C
#   RL: 25.3 PSI, 78.1°C
#   RR: 25.0 PSI, 76.5°C
#
# Brakes:
#   FL: 480°C | FR: 485°C
#   RL: 612°C | RR: 615°C
#
# Engine: 109.5°C
# Track: 41.8°C | Ambient: 24.0°C
#
# Speed: 256 km/h | Gear: 6 | RPM: 7267
```

### Normal Mode (with server)
```bash
# Normal mode (publish to server)
python monitor.py
```

## Benefits

1. **Development:** Test without server running
2. **Debugging:** Validate data extraction
3. **Windows Testing:** See actual LMU data
4. **Field Validation:** Confirm all fields are available
5. **Quick Check:** Verify monitor is working

## Testing

### Test Cases

1. **Log mode without LMU:**
   ```bash
   python monitor.py --log-only
   # Should wait for LMU
   ```

2. **Log mode with LMU:**
   ```bash
   # Start LMU
   python monitor.py --log-only
   # Should display telemetry every 0.5s (2Hz)
   ```

3. **Log mode with mock data:**
   ```bash
   # On macOS (uses mock)
   python monitor.py --log-only
   # Set target_process to "python" in config
   ```

4. **Ctrl+C shutdown:**
   ```bash
   python monitor.py --log-only
   # Press Ctrl+C
   # Should exit gracefully
   ```

## Validation Checklist

- [x] `--log-only` flag works
- [x] Logs telemetry to console
- [x] Updates at configured rate (2Hz)
- [x] Shows all key fields
- [x] Readable format
- [x] Works with mock data
- [ ] Works with real LMU data (requires manual testing on Windows)
- [x] Graceful shutdown

## Dependencies

- Existing monitor components
- `argparse` (stdlib)

## Related Files

- `monitor.py` - Main entry point
- `src/telemetry/telemetry_interface.py` - Telemetry source
- `bugs/create_monitor_entry_point.md` - Monitor implementation

---

**Next Steps:** Use this mode to validate telemetry data on Windows before implementing full dashboard integration.
