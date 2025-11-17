"""Telemetry reading module with cross-platform support"""

from .telemetry_interface import TelemetryReaderInterface, get_telemetry_reader

__all__ = ['TelemetryReaderInterface', 'get_telemetry_reader']
