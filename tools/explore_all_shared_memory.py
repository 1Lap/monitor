#!/usr/bin/env python3
"""
Comprehensive Shared Memory Explorer

Explores ALL available data structures in rFactor 2 shared memory,
including extended info that might contain TC/ABS/brake bias values.

SimHub and Tiny Pedal get this data somehow - let's find it!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pyRfactor2SharedMemory.sharedMemoryAPI import SimInfoAPI, Cbytestring2Python
except ImportError:
    print("❌ pyRfactor2SharedMemory not available (Windows only)")
    print("This tool must be run on Windows with LMU running")
    sys.exit(1)


def explore_object(obj, name="", indent=0, max_depth=3):
    """
    Recursively explore an object's attributes

    Args:
        obj: Object to explore
        name: Name of the object
        indent: Current indentation level
        max_depth: Maximum recursion depth
    """
    if indent > max_depth:
        return

    prefix = "  " * indent

    # Get all attributes (excluding private/dunder)
    attrs = [attr for attr in dir(obj) if not attr.startswith('_')]

    for attr in attrs:
        try:
            value = getattr(obj, attr)
            value_type = type(value).__name__

            # Check for TC/ABS/brake keywords
            attr_lower = attr.lower()
            is_interesting = any(kw in attr_lower for kw in [
                'traction', 'tc', 'abs', 'brake', 'bias', 'setting',
                'control', 'assist', 'aid', 'setup'
            ])

            marker = "🔍" if is_interesting else "  "

            # Print attribute info
            if callable(value):
                print(f"{prefix}{marker} {attr}() -> {value_type}")
            elif value_type in ['int', 'float', 'bool', 'str']:
                print(f"{prefix}{marker} {attr}: {value_type} = {value}")
            elif value_type == 'bytes':
                try:
                    str_val = Cbytestring2Python(value)
                    print(f"{prefix}{marker} {attr}: bytes = '{str_val}'")
                except:
                    print(f"{prefix}{marker} {attr}: bytes")
            else:
                print(f"{prefix}{marker} {attr}: {value_type}")
                # Recursively explore complex objects
                if indent < max_depth and value_type not in ['type', 'module', 'function']:
                    explore_object(value, attr, indent + 1, max_depth)

        except Exception as e:
            print(f"{prefix}   {attr}: <error: {e}>")


def main():
    """Main exploration"""
    print("=" * 80)
    print("rFactor 2 / LMU Shared Memory - Comprehensive Explorer")
    print("=" * 80)
    print("Looking for TC/ABS/brake bias values...")
    print("=" * 80)
    print()

    info = SimInfoAPI()

    if not info.isSharedMemoryAvailable():
        print("❌ Shared memory not available")
        print("   - Is LMU running?")
        print("   - Is shared memory plugin enabled?")
        return

    print("✅ Shared memory available!")
    print()

    # Explore main structures
    structures = [
        ('SimInfoAPI', info, "Main API object"),
        ('Rf2Tele', info.Rf2Tele, "Telemetry structure"),
        ('Rf2Scor', info.Rf2Scor, "Scoring structure"),
    ]

    # Check for extended structures
    if hasattr(info, 'Rf2Ext'):
        structures.append(('Rf2Ext', info.Rf2Ext, "Extended structure"))
    if hasattr(info, 'Rf2Rules'):
        structures.append(('Rf2Rules', info.Rf2Rules, "Rules structure"))
    if hasattr(info, 'Rf2ForceFeedback'):
        structures.append(('Rf2ForceFeedback', info.Rf2ForceFeedback, "Force Feedback"))

    for name, obj, description in structures:
        print("\n" + "=" * 80)
        print(f"{name} - {description}")
        print("=" * 80)
        explore_object(obj, name, max_depth=2)

    # Special focus on player vehicle
    print("\n" + "=" * 80)
    print("Player Vehicle Telemetry (detailed)")
    print("=" * 80)
    try:
        tele = info.playersVehicleTelemetry()
        explore_object(tele, "PlayerTelemetry", max_depth=3)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 80)
    print("Player Vehicle Scoring (detailed)")
    print("=" * 80)
    try:
        scor = info.playersVehicleScoring()
        explore_object(scor, "PlayerScoring", max_depth=3)
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Look for attributes marked with 🔍 - these contain TC/ABS/brake keywords")
    print("If you find relevant fields, we can add them to telemetry_real.py")
    print("=" * 80)


if __name__ == '__main__':
    main()
