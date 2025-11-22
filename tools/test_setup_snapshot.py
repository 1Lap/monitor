#!/usr/bin/env python3
"""
Setup Snapshot Tool

Takes a single snapshot of current setup and saves to file.
Useful for comparing garage vs. on-track setup data.

Usage:
    python tools/test_setup_snapshot.py [--output FILENAME]

Examples:
    # In garage
    python tools/test_setup_snapshot.py --output garage_setup.json

    # On-track
    python tools/test_setup_snapshot.py --output ontrack_setup.json

    # Compare
    diff garage_setup.json ontrack_setup.json
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lmu_rest_api import LMURestAPI


def take_snapshot(output_file: str = None):
    """
    Take a snapshot of current setup

    Args:
        output_file: Optional filename to save to (default: auto-generated)
    """
    api = LMURestAPI()

    print("=" * 80)
    print("LMU Setup Snapshot Tool")
    print("=" * 80)
    print(f"REST API: {api.base_url}")
    print()

    # Check API availability
    if not api.is_available():
        print("❌ REST API not available")
        print("   - Is LMU running?")
        print("   - Is REST API enabled in LMU settings?")
        return False

    print("✅ REST API available")

    # Fetch setup
    setup_data = api.fetch_setup_data()

    if not setup_data:
        print("⚠️  No setup data returned")
        print("   - In garage? Try loading a setup")
        print("   - On-track? API may not be available")
        return False

    # Count parameters
    garage_values = setup_data.get('carSetup', {}).get('garageValues', [])
    param_count = len(garage_values)

    print(f"✅ Setup data received ({param_count} parameters)")

    # Generate filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"setup_snapshot_{timestamp}.json"

    # Save to file
    with open(output_file, 'w') as f:
        json.dump(setup_data, f, indent=2)

    print(f"\n📝 Snapshot saved to: {output_file}")

    # Show sample of adjustable parameters
    print("\n📊 Sample adjustable parameters:")
    adjustable_keywords = ['TRACTION', 'TC', 'ABS', 'BRAKE', 'ENGINE', 'FUEL']

    shown = 0
    for param in garage_values:
        key = param.get('key', '')
        if any(kw in key for kw in adjustable_keywords):
            value = param.get('stringValue') or param.get('value', 0.0)
            print(f"  • {key}: {value}")
            shown += 1
            if shown >= 10:  # Limit output
                break

    if shown == 0:
        print("  (No commonly-adjustable parameters found)")

    print("\n" + "=" * 80)
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Take snapshot of current LMU setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test procedure to compare garage vs. on-track:

  1. Start LMU, load car/track
  2. IN GARAGE: Load a setup
  3. Run: python tools/test_setup_snapshot.py --output garage.json
  4. Start a session, go ON-TRACK
  5. Run: python tools/test_setup_snapshot.py --output ontrack.json
  6. Compare: diff garage.json ontrack.json

This will show if:
  - REST API works on-track (ontrack.json should exist)
  - Same data is available (should be identical if no changes)

Then test HUD changes:
  7. While on-track, change TC via HUD (e.g., 7 → 4)
  8. Run: python tools/test_setup_snapshot.py --output ontrack_after_hud.json
  9. Compare: diff ontrack.json ontrack_after_hud.json

This will show if REST API reflects HUD changes.
        """
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output filename (default: auto-generated with timestamp)'
    )

    args = parser.parse_args()

    success = take_snapshot(args.output)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
