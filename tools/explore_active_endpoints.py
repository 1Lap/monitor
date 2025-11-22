#!/usr/bin/env python3
"""
Explore REST API endpoints for ACTIVE (not setup) values

Tests various endpoints to find where active TC/ABS/brake bias values are exposed.
"""

import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def test_endpoint(base_url: str, path: str) -> dict:
    """
    Test a single endpoint

    Args:
        base_url: Base URL (e.g., http://localhost:6397)
        path: Endpoint path (e.g., /rest/hud)

    Returns:
        Response data or error dict
    """
    try:
        url = f"{base_url}{path}"
        req = Request(url)
        with urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            return {'success': True, 'data': data}
    except (URLError, HTTPError) as e:
        return {'success': False, 'error': str(e)}
    except json.JSONDecodeError:
        return {'success': False, 'error': 'Invalid JSON'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    """Test various endpoints for active setup values"""
    base_url = "http://localhost:6397"

    print("=" * 80)
    print("LMU REST API - Active Values Explorer")
    print("=" * 80)
    print(f"Base URL: {base_url}")
    print()
    print("Goal: Find where ACTIVE TC/ABS/brake bias values are exposed")
    print("      (not garage setup, but what's currently in use)")
    print("=" * 80)
    print()

    # Endpoints to test
    endpoints = [
        ("/rest/hud", "HUD data (might show active TC/ABS)"),
        ("/rest/garage/PitMenu/receivePitMenu", "Pit menu (current adjustable settings)"),
        ("/rest/strategy/overall", "Strategy info"),
        ("/rest/watch/sessionInfo", "Session info"),
        ("/rest/garage/UIScreen/CarSetupOverview", "Garage setup (current endpoint)"),
        ("/rest/garage/getPlayerGarageData", "Player garage data"),
        ("/rest/sessions", "Sessions info"),
        ("/rest/sessions/GetGameState", "Game state"),
    ]

    results = {}

    for path, description in endpoints:
        print(f"\n{'='*80}")
        print(f"Testing: {path}")
        print(f"Purpose: {description}")
        print("-" * 80)

        result = test_endpoint(base_url, path)

        if result['success']:
            print("✅ SUCCESS - Data retrieved")

            # Check for TC/ABS/brake keywords
            data_str = json.dumps(result['data'], indent=2)
            keywords = ['traction', 'TC', 'ABS', 'brake', 'bias']
            found_keywords = []

            for keyword in keywords:
                if keyword.lower() in data_str.lower():
                    found_keywords.append(keyword)

            if found_keywords:
                print(f"🔍 Keywords found: {', '.join(found_keywords)}")
            else:
                print("⚠️  No TC/ABS/brake keywords found")

            # Save full response
            filename = f"endpoint_{path.replace('/', '_')}.json"
            with open(filename, 'w') as f:
                json.dump(result['data'], f, indent=2)
            print(f"📝 Saved to: {filename}")

            results[path] = {
                'success': True,
                'keywords': found_keywords,
                'filename': filename
            }

        else:
            print(f"❌ FAILED - {result['error']}")
            results[path] = {'success': False, 'error': result['error']}

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = [p for p, r in results.items() if r['success']]
    with_keywords = [p for p, r in results.items() if r.get('success') and r.get('keywords')]

    print(f"\nEndpoints tested: {len(endpoints)}")
    print(f"Successful: {len(successful)}")
    print(f"With TC/ABS/brake keywords: {len(with_keywords)}")

    if with_keywords:
        print("\n🎯 Promising endpoints (contain TC/ABS/brake keywords):")
        for path in with_keywords:
            keywords = results[path]['keywords']
            filename = results[path]['filename']
            print(f"\n  {path}")
            print(f"    Keywords: {', '.join(keywords)}")
            print(f"    File: {filename}")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review the saved JSON files for endpoints with keywords")
    print("2. Look for fields that might contain ACTIVE values (not garage setup)")
    print("3. Test changing TC via HUD and re-run this script to see which values change")
    print()
    print("Key question: Which endpoint shows the TC value that changes when you")
    print("              adjust it via HUD while on-track?")
    print("=" * 80)


if __name__ == '__main__':
    main()
