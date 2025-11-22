#!/usr/bin/env python3
"""
Setup Polling Diagnostic Tool

Tests REST API availability and change detection for car setup.

Usage:
    python tools/test_setup_polling.py [--interval SECONDS]

This tool:
- Polls REST API continuously at specified interval
- Shows current values of adjustable setup parameters
- Highlights when values change (useful for testing HUD changes)
- Works in garage or on-track

Test scenarios:
1. Run in GARAGE with setup loaded - should show all setup values
2. Run ON-TRACK - check if API still available
3. Change TC/brake bias via HUD while on-track - see if values update
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lmu_rest_api import LMURestAPI


class SetupMonitor:
    """Monitor setup changes via REST API"""

    def __init__(self, poll_interval: float = 2.0, debug: bool = False):
        """
        Initialize setup monitor

        Args:
            poll_interval: Seconds between polls (default: 2.0)
            debug: Enable debug output (default: False)
        """
        self.api = LMURestAPI()
        self.poll_interval = poll_interval
        self.previous_setup = None
        self.poll_count = 0
        self.debug = debug

    def extract_key_values(self, setup_data: dict) -> dict:
        """
        Extract commonly-adjusted values from setup

        These are values that can typically be changed on-track via HUD:
        - Traction control
        - ABS
        - Brake bias
        - Engine map
        - Fuel mixture

        Args:
            setup_data: Full setup data from REST API

        Returns:
            Dictionary of key setup parameters
        """
        # Navigate to garage values
        car_setup = setup_data.get('carSetup', {})
        garage_values = car_setup.get('garageValues', [])

        # Check if garage_values is valid
        if not isinstance(garage_values, list):
            print(f"⚠️  garageValues is not a list: {type(garage_values)}")
            return {}

        # Extract key parameters
        key_params = {}

        for i, param in enumerate(garage_values):
            # Handle unexpected data types
            if not isinstance(param, dict):
                # Skip non-dict entries (sometimes API returns strings)
                continue

            key = param.get('key', '')

            # Focus on commonly-adjusted parameters
            if any(keyword in key for keyword in [
                'TRACTION', 'TC', 'ABS', 'BRAKE_BALANCE', 'BRAKE_BIAS',
                'ENGINE', 'FUEL', 'MIXTURE', 'MAP'
            ]):
                key_params[key] = {
                    'value': param.get('value', 0.0),
                    'stringValue': param.get('stringValue', ''),
                    'minValue': param.get('minValue', 0.0),
                    'maxValue': param.get('maxValue', 0.0),
                }

        return key_params

    def format_value(self, param: dict) -> str:
        """
        Format parameter value for display

        Args:
            param: Parameter dictionary with value/stringValue

        Returns:
            Formatted string
        """
        string_val = param.get('stringValue', '')
        numeric_val = param.get('value', 0.0)

        if string_val:
            return f"{string_val} ({numeric_val:.2f})"
        return f"{numeric_val:.2f}"

    def detect_changes(self, current: dict, previous: dict) -> dict:
        """
        Detect changes between current and previous setup

        Args:
            current: Current setup values
            previous: Previous setup values

        Returns:
            Dictionary of changed parameters
        """
        if not previous:
            return {}

        changes = {}

        for key, current_param in current.items():
            if key not in previous:
                changes[key] = {
                    'old': None,
                    'new': current_param
                }
            elif current_param != previous[key]:
                changes[key] = {
                    'old': previous[key],
                    'new': current_param
                }

        return changes

    def print_header(self):
        """Print header"""
        print("\n" + "=" * 80)
        print("LMU Setup Polling Diagnostic Tool")
        print("=" * 80)
        print(f"Poll interval: {self.poll_interval}s")
        print(f"REST API: {self.api.base_url}")
        if self.debug:
            print("Debug mode: ENABLED (raw API responses will be saved)")
        print("=" * 80)
        print("\nTest scenarios:")
        print("  1. GARAGE: Load a setup, verify values are shown")
        print("  2. ON-TRACK: Start session, check if API still works")
        print("  3. CHANGE HUD: Adjust TC/brake bias via HUD, watch for changes")
        print("\nPress Ctrl+C to stop\n")

    def poll_once(self) -> bool:
        """
        Poll setup once and display results

        Returns:
            True if API available, False otherwise
        """
        self.poll_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S')

        print(f"\n[{timestamp}] Poll #{self.poll_count}")
        print("-" * 80)

        # Check API availability
        if not self.api.is_available():
            print("❌ REST API not available")
            print("   - Is LMU running?")
            print("   - Is REST API enabled? (Check LMU settings)")
            return False

        print("✅ REST API available")

        # Fetch setup data
        setup_data = self.api.fetch_setup_data()

        # Debug: Save raw API response
        if self.debug and setup_data:
            debug_file = f"debug_setup_{timestamp.replace(':', '')}.json"
            with open(debug_file, 'w') as f:
                json.dump(setup_data, f, indent=2)
            print(f"🔍 Debug: Saved raw API response to {debug_file}")

        if not setup_data:
            print("⚠️  No setup data returned")
            print("   - In garage? Try loading a setup")
            print("   - On-track? API may not be available during session")
            return True

        # Extract key values
        key_values = self.extract_key_values(setup_data)

        if not key_values:
            print("⚠️  Setup data available, but no adjustable parameters found")
            print(f"   - Total parameters: {len(setup_data.get('carSetup', {}).get('garageValues', []))}")
            return True

        # Detect changes
        changes = self.detect_changes(key_values, self.previous_setup)

        # Display key parameters
        print(f"\n📊 Adjustable Parameters ({len(key_values)} found):")
        print()

        for key, param in sorted(key_values.items()):
            value_str = self.format_value(param)

            # Highlight if changed
            if key in changes:
                old_val = self.format_value(changes[key]['old']) if changes[key]['old'] else 'N/A'
                print(f"  🔄 {key}")
                print(f"      OLD: {old_val}")
                print(f"      NEW: {value_str} ⬅️ CHANGED!")
            else:
                print(f"  • {key}: {value_str}")

        # Summary
        if changes:
            print(f"\n🔔 {len(changes)} parameter(s) changed!")
        else:
            print("\n✓ No changes detected")

        # Store for next comparison
        self.previous_setup = key_values

        return True

    def run(self):
        """Run continuous polling"""
        self.print_header()

        try:
            while True:
                self.poll_once()
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n\n" + "=" * 80)
            print("Stopped")
            print("=" * 80)
            print(f"Total polls: {self.poll_count}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Monitor LMU setup changes via REST API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Poll every 2 seconds (default)
  python tools/test_setup_polling.py

  # Poll every 1 second (faster change detection)
  python tools/test_setup_polling.py --interval 1

  # Poll every 5 seconds (less aggressive)
  python tools/test_setup_polling.py --interval 5

Test procedure:
  1. Start LMU and load a car/track
  2. IN GARAGE: Run this script, verify setup values shown
  3. Start a session and go ON-TRACK
  4. Check if script still shows values (tests on-track availability)
  5. Change TC or brake bias via in-game HUD
  6. Watch script output for changes (tests if HUD changes are detected)
        """
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=2.0,
        help='Polling interval in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (saves raw API responses to files)'
    )

    args = parser.parse_args()

    monitor = SetupMonitor(poll_interval=args.interval, debug=args.debug)
    monitor.run()


if __name__ == '__main__':
    main()
