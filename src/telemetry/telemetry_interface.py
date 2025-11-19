"""Abstract interface for telemetry reading with platform detection"""

import sys
from abc import ABC, abstractmethod
from typing import Dict, Any


class TelemetryReaderInterface(ABC):
    """Abstract interface for telemetry reading"""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if telemetry data is available"""
        pass

    @abstractmethod
    def read(self) -> Dict[str, Any]:
        """
        Read current telemetry data

        Returns:
            Dictionary with telemetry fields as defined in TECHNICAL_SPEC.md
        """
        pass

    @abstractmethod
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get session metadata (track, car, event type)

        Returns:
            Dictionary with session information
        """
        pass

    @abstractmethod
    def get_all_vehicles(self) -> list[Dict[str, Any]]:
        """
        Get telemetry for all vehicles in the session (for opponent tracking)

        Returns:
            List of telemetry dictionaries, one per vehicle.
            Each dict includes 'driver_name', 'control' (control type), and telemetry fields.
            Returns empty list if not in multiplayer or no opponents available.
        """
        pass


def get_telemetry_reader() -> TelemetryReaderInterface:
    """
    Factory function to get appropriate telemetry reader based on platform

    Returns:
        MockTelemetryReader on macOS/Linux (development)
        RealTelemetryReader on Windows (production)
    """
    if sys.platform == 'win32':
        try:
            from .telemetry_real import RealTelemetryReader
            return RealTelemetryReader()
        except ImportError:
            # Fallback to mock if Windows but pyRfactor2SharedMemory not installed
            from .telemetry_mock import MockTelemetryReader
            return MockTelemetryReader()
    else:
        # macOS/Linux - use mock for development
        from .telemetry_mock import MockTelemetryReader
        return MockTelemetryReader()
