# Future Enhancements

This file tracks potential enhancements and feature ideas that are not currently prioritized.

---

## Car Setup Data Not Captured

**Status**: Enhancement
**Priority**: Low

Currently the car setup section shows all zeros. Need to map setup data from shared memory if available.

---

## Some Telemetry Fields Default to Zero

**Status**: Enhancement
**Priority**: Low

Fields not available in shared memory:
- Oil pressure
- Wind speed/direction
- DRS availability
- Suspension acceleration
- Some wheel/tire metrics

These are set to default values (0.0) in the output.
