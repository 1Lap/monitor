"""Main telemetry polling loop"""

import time
from typing import Dict, Any, Optional, Callable
from src.process_monitor import ProcessMonitor
from src.session_manager import SessionManager, SessionState
from src.telemetry.telemetry_interface import get_telemetry_reader


class TelemetryLoop:
    """
    Main telemetry polling loop that integrates all components

    Responsibilities:
    - Poll telemetry at ~100Hz
    - Monitor for target process (LMU)
    - Manage session state transitions
    - Buffer lap data
    - Trigger callbacks on lap completion
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize telemetry loop

        Args:
            config: Configuration dictionary with optional keys:
                - target_process: Process name to monitor (default: "LMU.exe")
                - poll_interval: Seconds between polls (default: 0.01 for ~100Hz)
                - on_lap_complete: Callback function(lap_data, lap_summary)
        """
        self.config = config or {}
        self.poll_interval = self.config.get('poll_interval', 0.01)

        # Initialize components
        self.process_monitor = ProcessMonitor(self.config)
        self.session_manager = SessionManager()
        self.telemetry_reader = get_telemetry_reader()

        # Callbacks
        self.on_lap_complete = self.config.get('on_lap_complete', None)

        # Control flags
        self._running = False
        self._paused = False

    def start(self):
        """Start the telemetry loop (non-blocking)"""
        self._running = True
        self._paused = False

    def stop(self):
        """Stop the telemetry loop"""
        self._running = False

    def pause(self):
        """Pause data collection (but keep running)"""
        self._paused = True
        self.session_manager.state = SessionState.PAUSED

    def resume(self):
        """Resume data collection"""
        self._paused = False
        if self.session_manager.state == SessionState.PAUSED:
            self.session_manager.state = SessionState.LOGGING

    def is_running(self) -> bool:
        """Check if loop is running"""
        return self._running

    def is_paused(self) -> bool:
        """Check if loop is paused"""
        return self._paused

    def run_once(self) -> Optional[Dict[str, Any]]:
        """
        Run one iteration of the loop

        Returns:
            Status dictionary with keys:
                - state: Current SessionState
                - process_detected: bool
                - telemetry_available: bool
                - lap: Current lap number
                - samples_buffered: Number of samples in buffer
                - lap_completed: bool (if lap just completed)
        """
        if not self._running:
            return None

        status = {
            'state': self.session_manager.state,
            'process_detected': False,
            'telemetry_available': False,
            'lap': self.session_manager.current_lap,
            'samples_buffered': len(self.session_manager.lap_samples),
            'lap_completed': False,
        }

        # Check if target process is running
        process_running = self.process_monitor.is_running()
        status['process_detected'] = process_running

        if not process_running:
            # No process -> go to IDLE
            if self.session_manager.state != SessionState.IDLE:
                self.session_manager.state = SessionState.IDLE
                self.session_manager.clear_lap_buffer()
            return status

        # Process detected
        if self.session_manager.state == SessionState.IDLE:
            self.session_manager.state = SessionState.DETECTED

        # If paused, don't collect data
        if self._paused:
            return status

        # Check if telemetry is available
        if not self.telemetry_reader.is_available():
            status['telemetry_available'] = False
            return status

        status['telemetry_available'] = True

        # Start logging if we haven't already
        if self.session_manager.state == SessionState.DETECTED:
            self.session_manager.state = SessionState.LOGGING
            self.session_manager.current_session_id = self.session_manager.generate_session_id()

        # Read telemetry
        try:
            telemetry = self.telemetry_reader.read()

            # Update session and check for events
            events = self.session_manager.update(telemetry)

            # Handle lap completion
            if events.get('lap_completed'):
                status['lap_completed'] = True

                # Get completed lap data
                lap_data = self.session_manager.get_lap_data()
                lap_summary = self.session_manager.get_lap_summary()

                # Trigger callback
                if self.on_lap_complete and len(lap_data) > 0:
                    self.on_lap_complete(lap_data, lap_summary)

                # Clear buffer for next lap
                self.session_manager.clear_lap_buffer()

            # Add sample to buffer
            self.session_manager.add_sample(telemetry)

            # Update status
            status['state'] = self.session_manager.state
            status['lap'] = self.session_manager.current_lap
            status['samples_buffered'] = len(self.session_manager.lap_samples)

        except Exception as e:
            self.session_manager.state = SessionState.ERROR
            status['state'] = SessionState.ERROR
            status['error'] = str(e)

        return status

    def run(self):
        """
        Run the telemetry loop continuously (blocking)

        This is the main loop that runs until stop() is called.
        Polls telemetry at the configured interval.
        """
        self.start()

        try:
            while self._running:
                self.run_once()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            # Graceful shutdown on Ctrl+C
            self.stop()
