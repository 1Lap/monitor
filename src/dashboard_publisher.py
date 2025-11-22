"""
Dashboard Publisher

Publishes telemetry and setup data to dashboard server via WebSocket.
"""
import socketio
from typing import Dict, Any, Optional
from datetime import datetime


class DashboardPublisher:
    """
    Publishes telemetry and setup data to dashboard server via WebSocket.

    This class manages WebSocket connection to the dashboard server and
    publishes real-time telemetry updates and car setup data.

    Attributes:
        server_url: Dashboard server URL (e.g., 'http://localhost:5000')
        session_id: Session ID or 'auto' to request from server
        connected: Connection status
        sio: SocketIO client instance
    """

    def __init__(self, server_url: str, session_id: str = 'auto'):
        """
        Initialize publisher.

        Args:
            server_url: Dashboard server URL (e.g., 'http://localhost:5000')
            session_id: Session ID or 'auto' to request from server
        """
        self.sio = socketio.Client()
        self.server_url = server_url
        self.session_id = session_id
        self.connected = False

        # Register event handlers
        self.sio.on('connect', self._on_connect)
        self.sio.on('disconnect', self._on_disconnect)
        self.sio.on('session_id_assigned', self._on_session_id_assigned)

    def _on_connect(self):
        """Handle connection to server."""
        print(f"[Publisher] Connected to {self.server_url}")
        self.connected = True

        # Request session ID if auto
        if self.session_id == 'auto':
            self.sio.emit('request_session_id', {})

    def _on_disconnect(self):
        """Handle disconnection from server."""
        print("[Publisher] Disconnected from server")
        self.connected = False

    def _on_session_id_assigned(self, data: Dict[str, str]):
        """
        Handle session ID assignment.

        Args:
            data: Dictionary containing 'session_id' key
        """
        self.session_id = data['session_id']
        print(f"[Publisher] Session ID: {self.session_id}")
        print(f"[Publisher] Dashboard URL: {self.server_url}/dashboard/{self.session_id}")

    def connect(self) -> bool:
        """
        Connect to server.

        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"[Publisher] Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from server."""
        if self.connected:
            self.sio.disconnect()

    def publish_setup(self, setup_data: Dict[str, Any]):
        """
        Publish car setup (once per session).

        Args:
            setup_data: Setup dictionary from REST API
        """
        if not self.connected:
            print("[Publisher] Not connected, skipping setup publish")
            return

        if self.session_id == 'auto':
            print("[Publisher] No session ID yet, skipping setup publish")
            return

        self.sio.emit('setup_data', {
            'session_id': self.session_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'setup': setup_data
        })
        print("[Publisher] Setup data published")

    def publish_telemetry(self, telemetry_data: Dict[str, Any]):
        """
        Publish live telemetry.

        Args:
            telemetry_data: Telemetry dictionary from TelemetryReader
        """
        if not self.connected:
            # Silently skip (telemetry is frequent, don't spam logs)
            return

        if self.session_id == 'auto':
            # Still waiting for session ID
            return

        # Extract dashboard fields
        dashboard_data = self._extract_dashboard_fields(telemetry_data)

        self.sio.emit('telemetry_update', {
            'session_id': self.session_id,
            'telemetry': dashboard_data
        })

    def _extract_dashboard_fields(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract only the fields needed by dashboard.

        This method filters the full telemetry data to include only
        fields required by the dashboard interface, reducing bandwidth
        and simplifying the dashboard implementation.

        Args:
            telemetry: Full telemetry dictionary from TelemetryReader

        Returns:
            Dashboard-compatible telemetry dictionary
        """
        # Handle field name variations between real and mock telemetry
        # Real LMU uses: fuel, fuel_capacity, race_position
        # Mock may use: fuel_remaining, fuel_at_start, race_position
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'lap': telemetry.get('lap', 0),
            'position': telemetry.get('race_position', 0),
            'lap_time': telemetry.get('lap_time', 0.0),
            'fuel': telemetry.get('fuel', telemetry.get('fuel_remaining', 0.0)),
            'fuel_capacity': telemetry.get('fuel_capacity', telemetry.get('fuel_at_start', 90.0)),
            'tire_pressures': telemetry.get('tyre_pressure', {}),
            'tire_temps': telemetry.get('tyre_temp', {}),
            'tire_wear': telemetry.get('tyre_wear', {}),
            'brake_temps': telemetry.get('brake_temp', {}),
            'engine_water_temp': telemetry.get('engine_temp', telemetry.get('engine_water_temp', 0.0)),
            'track_temp': telemetry.get('track_temp', 0.0),
            'ambient_temp': telemetry.get('ambient_temp', 0.0),
            'speed': telemetry.get('speed', 0.0),
            'gear': telemetry.get('gear', 0),
            'rpm': telemetry.get('rpm', 0.0),
            'player_name': telemetry.get('player_name', ''),
            'car_name': telemetry.get('car_name', ''),
            'track_name': telemetry.get('track_name', ''),
            'session_type': telemetry.get('session_type', ''),
        }

    def is_connected(self) -> bool:
        """
        Check if connected to server.

        Returns:
            True if connected, False otherwise
        """
        return self.connected

    def is_ready(self) -> bool:
        """
        Check if ready to publish (connected + has session ID).

        Returns:
            True if ready to publish, False otherwise
        """
        return self.connected and self.session_id != 'auto'
