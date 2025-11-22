#!/usr/bin/env python3
"""
Explore LMU Shared Memory API
Run with LMU active to see available telemetry fields

Usage:
    python tools/explore_shared_memory.py [--samples N] [--json] [--output FILE]

Requirements:
    - Windows OS
    - LMU.exe running
    - pyRfactor2SharedMemory installed

Example:
    # Basic exploration (100 samples ~1 second)
    python tools/explore_shared_memory.py

    # Extended capture with JSON output
    python tools/explore_shared_memory.py --samples 500 --json --output telemetry.json
"""
import sys
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.telemetry.telemetry_interface import get_telemetry_reader


def explore_telemetry(num_samples: int = 100, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Read telemetry samples from LMU

    Args:
        num_samples: Number of samples to collect
        verbose: Print progress updates

    Returns:
        List of telemetry data dictionaries
    """
    reader = get_telemetry_reader()

    if not reader.is_available():
        print("❌ ERROR: LMU not detected")
        print("\nTroubleshooting:")
        print("  1. Ensure LMU.exe is running")
        print("  2. Verify you're on Windows (shared memory not available on macOS)")
        print("  3. Check pyRfactor2SharedMemory is installed: pip install pyRfactor2SharedMemory")
        return []

    print(f"✅ LMU detected! Reading {num_samples} telemetry samples...")
    print("=" * 70)

    samples = []
    start_time = time.time()

    for i in range(num_samples):
        data = reader.read()
        if data:
            samples.append(data)
            if verbose and (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"  Progress: {i + 1}/{num_samples} samples ({rate:.1f} Hz)")

        time.sleep(0.01)  # 100Hz polling

    elapsed = time.time() - start_time
    actual_rate = len(samples) / elapsed if elapsed > 0 else 0

    print(f"\n✅ Captured {len(samples)} samples in {elapsed:.2f}s ({actual_rate:.1f} Hz)")

    return samples


def analyze_samples(samples: List[Dict[str, Any]]) -> None:
    """
    Analyze and display telemetry sample structure

    Args:
        samples: List of telemetry data dictionaries
    """
    if not samples:
        print("❌ No samples to analyze")
        return

    first = samples[0]

    print("\n" + "=" * 70)
    print("TELEMETRY STRUCTURE")
    print("=" * 70)

    # Show field summary
    print(f"\nTotal fields: {len(first)}")
    print("\nField listing (name: type):")
    print("-" * 70)

    for key in sorted(first.keys()):
        value = first[key]
        type_name = type(value).__name__

        # Show sample value for different types
        if isinstance(value, dict):
            subkeys = list(value.keys())[:3]
            sample = f"dict with {len(value)} keys: {subkeys}..."
        elif isinstance(value, list):
            sample = f"list with {len(value)} items"
        elif isinstance(value, (int, float)):
            sample = f"{value}"
        elif isinstance(value, str):
            sample = f"'{value}'"
        else:
            sample = str(value)

        print(f"  {key:30s} : {type_name:10s} = {sample}")

    # Critical dashboard fields check
    print("\n" + "=" * 70)
    print("DASHBOARD REQUIREMENTS CHECK")
    print("=" * 70)

    critical_fields = {
        'Fuel': ['fuel_remaining', 'fuel_capacity'],
        'Tires': ['tire_pressure', 'tire_temp', 'tire_wear'],
        'Brakes': ['brake_temp'],
        'Engine': ['engine_water_temp'],
        'Weather': ['track_temp', 'ambient_temp'],
        'Position': ['lap', 'race_position', 'lap_time'],
        'Speed/RPM': ['speed', 'rpm', 'gear'],
        'Session': ['player_name', 'car_name', 'track_name', 'session_type']
    }

    for category, fields in critical_fields.items():
        print(f"\n{category}:")
        for field in fields:
            status = "✅" if field in first else "❌"
            print(f"  {status} {field}")


def display_sample_data(samples: List[Dict[str, Any]]) -> None:
    """
    Display first sample in readable format

    Args:
        samples: List of telemetry data dictionaries
    """
    if not samples:
        return

    print("\n" + "=" * 70)
    print("SAMPLE TELEMETRY DATA (First Sample)")
    print("=" * 70)
    print(json.dumps(samples[0], indent=2, default=str))


def save_to_json(samples: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save samples to JSON file

    Args:
        samples: List of telemetry data dictionaries
        filepath: Output file path
    """
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(samples, f, indent=2, default=str)

    print(f"\n✅ Saved {len(samples)} samples to: {output_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Explore LMU shared memory telemetry API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic exploration
  python tools/explore_shared_memory.py

  # Extended capture (5 seconds at 100Hz)
  python tools/explore_shared_memory.py --samples 500

  # Save to JSON file
  python tools/explore_shared_memory.py --json --output telemetry.json

  # Verbose output
  python tools/explore_shared_memory.py --samples 1000 -v
        """
    )

    parser.add_argument(
        '--samples', '-n',
        type=int,
        default=100,
        help='Number of samples to collect (default: 100 = ~1 second)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Display first sample as JSON'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save samples to JSON file'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output (show progress)'
    )

    args = parser.parse_args()

    # Collect samples
    samples = explore_telemetry(args.samples, args.verbose)

    if not samples:
        sys.exit(1)

    # Analyze structure
    analyze_samples(samples)

    # Show sample data if requested
    if args.json:
        display_sample_data(samples)

    # Save to file if requested
    if args.output:
        save_to_json(samples, args.output)

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Review field names and types above")
    print("2. Compare with mock implementation (src/telemetry/telemetry_mock.py)")
    print("3. Update dashboard_data_requirements.md with actual field names")
    print("4. Verify all critical dashboard fields are available")

    if not args.output:
        print("\nTip: Use --output to save data for detailed analysis")

    sys.exit(0)


if __name__ == '__main__':
    main()
