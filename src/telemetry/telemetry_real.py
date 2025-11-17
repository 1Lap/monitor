"""Real telemetry reader from pyRfactor2SharedMemory (Windows only)"""

from typing import Dict, Any
from .telemetry_interface import TelemetryReaderInterface


class RealTelemetryReader(TelemetryReaderInterface):
    """
    Real telemetry from pyRfactor2SharedMemory

    This module only works on Windows with LMU and the
    rF2SharedMemoryMapPlugin enabled.
    """

    def __init__(self):
        try:
            import pyRfactor2SharedMemory as sm
            self.sm = sm
            self.shared_memory = None
        except ImportError:
            raise ImportError(
                "pyRfactor2SharedMemory not found. "
                "This module only works on Windows with the package installed."
            )

    def is_available(self) -> bool:
        """Check if shared memory is accessible"""
        try:
            # TODO: Implement actual check when on Windows
            # data = self.sm.read_telemetry()
            # return data is not None
            return True
        except Exception:
            return False

    def read(self) -> Dict[str, Any]:
        """
        Read from rF2 shared memory

        TODO: Implement actual mapping from rF2 shared memory to our telemetry dict
        This will be completed during Phase 6 (Windows testing)
        """
        # Placeholder - will be implemented on Windows
        raise NotImplementedError(
            "RealTelemetryReader.read() will be implemented during Windows testing phase"
        )

    def get_session_info(self) -> Dict[str, Any]:
        """
        Get session metadata from shared memory

        TODO: Implement during Phase 6 (Windows testing)
        """
        raise NotImplementedError(
            "RealTelemetryReader.get_session_info() will be implemented during Windows testing phase"
        )
