#!/usr/bin/env python3
"""
Test TC/ABS/Brake Bias Reading from Shared Memory

Reads the specific fields we found and displays them live.
Run this while driving to see if values change when you adjust via HUD.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import shared memory library
try:
    from pyRfactor2SharedMemory.sharedMemoryAPI import SimInfoAPI, Cbytestring2Python
except ImportError:
    try:
        local_path = os.path.join(
            os.path.dirname(__file__), "..", "src", "pyRfactor2SharedMemory"
        )
        sys.path.insert(0, local_path)
        from sharedMemoryAPI import SimInfoAPI, Cbytestring2Python
    except ImportError as e:
        print("ERROR: pyRfactor2SharedMemory not available")
        print(f"   Error: {e}")
        sys.exit(1)


def main():
    """Main test loop"""
    print("=" * 80)
    print("TC/ABS/Brake Bias Live Test")
    print("=" * 80)
    print("Reading from:")
    print("  - Rf2Ext.mPhysics.mTractionControl")
    print("  - Rf2Ext.mPhysics.mAntiLockBrakes")
    print("  - Rf2Ext.mPhysics.mStabilityControl")
    print("  - PlayerTelemetry.mRearBrakeBias")
    print("=" * 80)
    print()

    info = SimInfoAPI()

    if not info.isSharedMemoryAvailable():
        print("ERROR: Shared memory not available")
        print("   - Is LMU running?")
        print("   - Are you in a session?")
        return

    print("SUCCESS: Shared memory available!")
    print("Press Ctrl+C to stop")
    print()

    poll_count = 0
    try:
        while True:
            poll_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')

            # Read from Rf2Ext (Extended structure)
            try:
                ext = info.Rf2Ext
                physics = ext.mPhysics

                tc = physics.mTractionControl
                abs_val = physics.mAntiLockBrakes
                stability = physics.mStabilityControl
            except AttributeError as e:
                print(f"ERROR: Cannot access Rf2Ext.mPhysics: {e}")
                print("This might mean Rf2Ext is not available in this version")
                return

            # Read from Player Telemetry
            try:
                tele = info.playersVehicleTelemetry()
                rear_brake_bias = tele.mRearBrakeBias
                # Convert to front brake bias percentage
                front_brake_bias = (1.0 - rear_brake_bias) * 100
            except AttributeError as e:
                print(f"ERROR: Cannot access telemetry: {e}")
                return

            # Display values
            print(f"\r[{timestamp}] Poll #{poll_count:3d} | ", end="")
            print(f"TC: {tc:2d} | ABS: {abs_val:2d} | Stability: {stability:2d} | ", end="")
            print(f"Brake Bias: {front_brake_bias:5.1f}% front ({rear_brake_bias*100:.1f}% rear)", end="")
            sys.stdout.flush()

            time.sleep(0.5)  # Update twice per second

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("Stopped")
        print("=" * 80)
        print(f"Total polls: {poll_count}")
        print()
        print("What did you see?")
        print("  - Did TC/ABS values match what you see on HUD?")
        print("  - Did values change when you adjusted via HUD?")
        print("  - Was brake bias correct?")


if __name__ == '__main__':
    main()
