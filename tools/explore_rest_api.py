#!/usr/bin/env python3
"""
Explore LMU REST API
Run with LMU active to see available setup/garage data

Usage:
    python tools/explore_rest_api.py [--output FILE]

Requirements:
    - LMU running (Windows or macOS)
    - LMU REST API enabled (default port 6397)
    - requests library installed

Example:
    # Basic exploration
    python tools/explore_rest_api.py

    # Save to file
    python tools/explore_rest_api.py --output rest_api_data.json
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.lmu_rest_api import LMURestAPI


def test_api_connection(api: LMURestAPI) -> bool:
    """
    Test basic API connectivity

    Args:
        api: LMURestAPI instance

    Returns:
        True if API is available, False otherwise
    """
    print("=" * 70)
    print("LMU REST API CONNECTION TEST")
    print("=" * 70)
    print(f"Testing connection to: {api.base_url}")
    print()

    if api.is_available():
        print("✅ LMU REST API is available")
        return True
    else:
        print("❌ LMU REST API is NOT available")
        print("\nTroubleshooting:")
        print("  1. Ensure LMU is running")
        print("  2. Verify REST API is enabled in LMU settings")
        print("  3. Check API port (default: 6397)")
        print("  4. Try accessing http://localhost:6397/rest/watch/version in browser")
        return False


def fetch_setup_data(api: LMURestAPI) -> Optional[Dict[str, Any]]:
    """
    Fetch car setup data from API

    Args:
        api: LMURestAPI instance

    Returns:
        Setup data dictionary or None if not available
    """
    print("\n" + "=" * 70)
    print("FETCHING SETUP DATA")
    print("=" * 70)
    print("Endpoint: GET /rest/garage/setup")
    print()

    setup = api.fetch_setup_data()

    if setup:
        print(f"✅ Setup data received ({len(setup)} top-level keys)")
        return setup
    else:
        print("❌ No setup data available")
        print("\nPossible reasons:")
        print("  - Not in garage/session")
        print("  - Setup not loaded")
        print("  - Endpoint may have different path")
        return None


def analyze_setup_structure(setup: Dict[str, Any]) -> None:
    """
    Analyze and display setup data structure

    Args:
        setup: Setup data dictionary
    """
    if not setup:
        return

    print("\n" + "=" * 70)
    print("SETUP DATA STRUCTURE")
    print("=" * 70)

    def print_structure(data: Any, indent: int = 0) -> None:
        """Recursively print data structure"""
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"{prefix}{key}: {{dict with {len(value)} keys}}")
                    print_structure(value, indent + 1)
                elif isinstance(value, list):
                    print(f"{prefix}{key}: [list with {len(value)} items]")
                    if value and isinstance(value[0], dict):
                        print(f"{prefix}  Example item:")
                        print_structure(value[0], indent + 2)
                else:
                    type_name = type(value).__name__
                    print(f"{prefix}{key}: {type_name} = {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data[:3]):  # Show first 3 items
                print(f"{prefix}[{i}]:")
                print_structure(item, indent + 1)
            if len(data) > 3:
                print(f"{prefix}... ({len(data) - 3} more items)")

    print_structure(setup)


def check_critical_fields(setup: Dict[str, Any]) -> None:
    """
    Check for critical dashboard setup fields

    Args:
        setup: Setup data dictionary
    """
    print("\n" + "=" * 70)
    print("CRITICAL SETUP FIELDS CHECK")
    print("=" * 70)

    # Expected setup categories based on RACE_DASHBOARD_PLAN.md
    critical_categories = {
        'Suspension': ['springs', 'dampers', 'antiroll', 'ride_height'],
        'Aerodynamics': ['front_wing', 'rear_wing', 'downforce'],
        'Gearing': ['gear_ratios', 'final_drive'],
        'Differential': ['diff_settings', 'differential'],
        'Brakes': ['brake_balance', 'brake_bias'],
        'Tires': ['tire_pressures', 'tire_pressure', 'pressures']
    }

    def search_dict(data: Any, search_terms: list) -> list:
        """Search for any of the terms in data structure"""
        found = []
        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                if any(term.lower() in key_lower for term in search_terms):
                    found.append(key)
                # Recursively search nested dicts
                found.extend(search_dict(value, search_terms))
        return found

    for category, search_terms in critical_categories.items():
        print(f"\n{category}:")
        found = search_dict(setup, search_terms)
        if found:
            for field in found:
                print(f"  ✅ {field}")
        else:
            print(f"  ❌ No matching fields found (searched: {', '.join(search_terms)})")


def display_json(setup: Dict[str, Any]) -> None:
    """
    Display setup data as formatted JSON

    Args:
        setup: Setup data dictionary
    """
    print("\n" + "=" * 70)
    print("SETUP DATA (JSON)")
    print("=" * 70)
    print(json.dumps(setup, indent=2, default=str))


def save_to_file(setup: Dict[str, Any], filepath: str) -> None:
    """
    Save setup data to JSON file

    Args:
        setup: Setup data dictionary
        filepath: Output file path
    """
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'endpoint': '/rest/garage/setup',
        'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
        'setup': setup
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"\n✅ Saved setup data to: {output_path}")


def explore_additional_endpoints(api: LMURestAPI) -> Dict[str, Any]:
    """
    Explore other potential REST API endpoints

    Args:
        api: LMURestAPI instance

    Returns:
        Dictionary of endpoint results
    """
    print("\n" + "=" * 70)
    print("EXPLORING ADDITIONAL ENDPOINTS")
    print("=" * 70)

    # Known rFactor 2 REST API endpoints to try
    endpoints = [
        '/rest/watch/version',
        '/rest/sessions/getAllVehicles',
        '/rest/race/car',
        '/rest/race/session',
        '/rest/garage/vehicle',
    ]

    results = {}

    for endpoint in endpoints:
        print(f"\nTrying: {endpoint}")
        try:
            import requests
            url = f"{api.base_url}{endpoint}"
            response = requests.get(url, timeout=2)

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  ✅ Success ({len(data)} keys)" if isinstance(data, dict) else f"  ✅ Success")
                    results[endpoint] = data
                except:
                    print(f"  ✅ Success (non-JSON response)")
                    results[endpoint] = response.text
            else:
                print(f"  ❌ Failed (HTTP {response.status_code})")

        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection error")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Explore LMU REST API endpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic exploration
  python tools/explore_rest_api.py

  # Save to file
  python tools/explore_rest_api.py --output rest_api_data.json

  # Explore all endpoints
  python tools/explore_rest_api.py --all

Notes:
  - LMU must be running with REST API enabled
  - Default API port is 6397
  - Some endpoints only work during active session
        """
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save data to JSON file'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Explore all known endpoints'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Display full JSON output'
    )

    args = parser.parse_args()

    # Create API client
    api = LMURestAPI()

    # Test connection
    if not test_api_connection(api):
        sys.exit(1)

    # Fetch setup data
    setup = fetch_setup_data(api)

    if setup:
        # Analyze structure
        analyze_setup_structure(setup)

        # Check critical fields
        check_critical_fields(setup)

        # Show full JSON if requested
        if args.json:
            display_json(setup)

        # Save to file if requested
        if args.output:
            save_to_file(setup, args.output)

    # Explore additional endpoints if requested
    if args.all:
        additional = explore_additional_endpoints(api)
        if additional and args.output:
            # Save all endpoint data
            output_path = Path(args.output)
            all_data_path = output_path.parent / f"{output_path.stem}_all{output_path.suffix}"
            with open(all_data_path, 'w') as f:
                json.dump(additional, f, indent=2, default=str)
            print(f"\n✅ Saved all endpoint data to: {all_data_path}")

    # Print next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Review setup data structure above")
    print("2. Identify fields needed for dashboard display")
    print("3. Update dashboard_data_requirements.md with actual field names")
    print("4. Compare with shared memory telemetry fields")

    if not args.output:
        print("\nTip: Use --output to save data for detailed analysis")

    if not args.all:
        print("Tip: Use --all to explore additional REST API endpoints")

    sys.exit(0)


if __name__ == '__main__':
    main()
