#!/usr/bin/env python3
"""
Test Process Detection
Quick utility to test if the monitor can detect LMU.exe
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.process_monitor import ProcessMonitor
import psutil


def main():
    print("=" * 70)
    print("PROCESS DETECTION TEST")
    print("=" * 70)

    # List all running processes
    print("\n[1] Listing all running processes containing 'lmu':")
    print("-" * 70)
    found_lmu = False
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            name = proc.info['name']
            if name and 'lmu' in name.lower():
                print(f"  ✅ Found: {name} (PID: {proc.info['pid']})")
                if proc.info['exe']:
                    print(f"     Path: {proc.info['exe']}")
                found_lmu = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not found_lmu:
        print("  ❌ No processes containing 'lmu' found")
        print("\nℹ️  Make sure LMU is running before testing")

    # Test the ProcessMonitor class
    print("\n" + "=" * 70)
    print("[2] Testing ProcessMonitor class:")
    print("-" * 70)

    config = {'target_process': 'Le Mans Ultimate'}
    monitor = ProcessMonitor(config)

    print(f"  Target process: {config['target_process']}")

    if monitor.is_running():
        print("  ✅ ProcessMonitor detected LMU!")
        info = monitor.get_process_info()
        if info:
            print(f"     PID: {info['pid']}")
            print(f"     Name: {info['name']}")
            print(f"     Status: {info['status']}")
    else:
        print("  ❌ ProcessMonitor did NOT detect LMU")
        print("\nTroubleshooting:")
        print("  1. Ensure 'Le Mans Ultimate.exe' is running")
        print("  2. Check Task Manager to verify process name")
        print("  3. Try running this script as Administrator")

    # Test alternative process names
    print("\n" + "=" * 70)
    print("[3] Testing alternative process names:")
    print("-" * 70)

    alternatives = ['Le Mans Ultimate', 'Le Mans Ultimate.exe', 'LMU', 'lmu.exe']
    for alt in alternatives:
        config_alt = {'target_process': alt}
        monitor_alt = ProcessMonitor(config_alt)
        status = "✅ FOUND" if monitor_alt.is_running() else "❌ Not found"
        print(f"  {status}: '{alt}'")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
