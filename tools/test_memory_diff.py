#!/usr/bin/env python3
"""
Shared Memory Before/After Comparison Tool

Dumps ALL shared memory data, waits for you to change a setting,
then dumps again. Compare the two files to see what changed!
"""

import sys
import os
import json
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


def serialize_value(value):
    """
    Convert a value to JSON-serializable format

    Args:
        value: Any value from shared memory

    Returns:
        JSON-serializable representation
    """
    value_type = type(value).__name__

    if value_type in ['int', 'float', 'bool', 'str']:
        return value
    elif value_type == 'bytes':
        try:
            return Cbytestring2Python(value)
        except:
            return '<bytes>'
    elif value_type == 'NoneType':
        return None
    elif hasattr(value, '__dict__'):
        # Complex object - recursively serialize
        result = {}
        for attr in dir(value):
            if not attr.startswith('_'):
                try:
                    attr_value = getattr(value, attr)
                    if not callable(attr_value):
                        result[attr] = serialize_value(attr_value)
                except:
                    result[attr] = '<error>'
        return result
    else:
        return str(value)


def dump_all_data(info, label):
    """
    Dump all shared memory data to JSON

    Args:
        info: SimInfoAPI instance
        label: Label for this dump (e.g., "before", "after")

    Returns:
        Filename of dump
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"memory_dump_{label}_{timestamp}.json"

    print(f"\nDumping all shared memory data to: {filename}")

    data = {}

    # Dump Rf2Ext (Extended - has TC/ABS!)
    print("  - Reading Rf2Ext (Extended structure)...")
    try:
        data['Rf2Ext'] = serialize_value(info.Rf2Ext)
    except Exception as e:
        data['Rf2Ext'] = f"<error: {e}>"

    # Dump Rf2Tele (Telemetry)
    print("  - Reading Rf2Tele (Telemetry structure)...")
    try:
        data['Rf2Tele'] = serialize_value(info.Rf2Tele)
    except Exception as e:
        data['Rf2Tele'] = f"<error: {e}>"

    # Dump Rf2Scor (Scoring)
    print("  - Reading Rf2Scor (Scoring structure)...")
    try:
        data['Rf2Scor'] = serialize_value(info.Rf2Scor)
    except Exception as e:
        data['Rf2Scor'] = f"<error: {e}>"

    # Dump Player Telemetry
    print("  - Reading Player Vehicle Telemetry...")
    try:
        tele = info.playersVehicleTelemetry()
        data['PlayerTelemetry'] = serialize_value(tele)
    except Exception as e:
        data['PlayerTelemetry'] = f"<error: {e}>"

    # Dump Player Scoring
    print("  - Reading Player Vehicle Scoring...")
    try:
        scor = info.playersVehicleScoring()
        data['PlayerScoring'] = serialize_value(scor)
    except Exception as e:
        data['PlayerScoring'] = f"<error: {e}>"

    # Save to JSON
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"  - Dump complete: {filename}")

    return filename


def main():
    """Main comparison flow"""
    print("=" * 80)
    print("Shared Memory Before/After Comparison Tool")
    print("=" * 80)
    print()
    print("This tool will:")
    print("  1. Dump ALL shared memory data to 'before' file")
    print("  2. Wait for you to change a HUD setting (TC, brake bias, etc.)")
    print("  3. Dump ALL shared memory data to 'after' file")
    print("  4. You can then compare the files to see what changed!")
    print()
    print("=" * 80)

    info = SimInfoAPI()

    if not info.isSharedMemoryAvailable():
        print("ERROR: Shared memory not available")
        print("   - Is LMU running?")
        print("   - Are you in a session?")
        return

    print("SUCCESS: Shared memory available!")
    print()

    # BEFORE dump
    print("=" * 80)
    print("STEP 1: Taking 'BEFORE' snapshot")
    print("=" * 80)
    before_file = dump_all_data(info, "before")

    # Wait for user
    print()
    print("=" * 80)
    print("STEP 2: Make your change")
    print("=" * 80)
    print()
    print("Now:")
    print("  1. Go to your LMU session (ALT+TAB)")
    print("  2. Change a HUD setting (e.g., TC from 7 to 4)")
    print("  3. Come back here and press ENTER")
    print()
    input("Press ENTER after you've made the change... ")

    # AFTER dump
    print()
    print("=" * 80)
    print("STEP 3: Taking 'AFTER' snapshot")
    print("=" * 80)
    after_file = dump_all_data(info, "after")

    # Instructions
    print()
    print("=" * 80)
    print("DONE!")
    print("=" * 80)
    print()
    print(f"Before: {before_file}")
    print(f"After:  {after_file}")
    print()
    print("To compare and find what changed:")
    print()
    print("  Option 1 - Use diff tool (shows differences):")
    print(f"    diff {before_file} {after_file}")
    print()
    print("  Option 2 - Use Python to find differences:")
    print(f"    python -c \"import json; b=json.load(open('{before_file}')); a=json.load(open('{after_file}')); print('TC before:', b['Rf2Ext']['mPhysics']['mTractionControl']); print('TC after:', a['Rf2Ext']['mPhysics']['mTractionControl'])\"")
    print()
    print("  Option 3 - Push both files to repo and I'll analyze:")
    print(f"    git add {before_file} {after_file}")
    print("    git commit -m 'Memory dumps before/after TC change'")
    print("    git push")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
