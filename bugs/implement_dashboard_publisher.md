# Feature: Implement Dashboard Publisher

**Type:** Implementation
**Priority:** High
**Phase:** MVP - Phase 1
**Estimated Time:** 3-4 hours

---

## Overview

Implement the `DashboardPublisher` class that connects to the dashboard server via WebSocket and publishes telemetry and setup data. This is the core communication component for the monitor.

## Objective

Create a production-ready WebSocket client that:
1. Connects to dashboard server
2. Requests/receives session ID
3. Publishes setup data (once per session)
4. Publishes telemetry data (2Hz)
5. Handles reconnection gracefully

## Requirements

### Must Have

1. **File: `src/dashboard_publisher.py`**
   - `DashboardPublisher` class
   - WebSocket connection using `python-socketio[client]`
   - Session ID management
   - Setup and telemetry publishing methods
   - Connection status tracking

2. **WebSocket Events**
   - `connect` - Handle connection
   - `disconnect` - Handle disconnection
   - `session_id_assigned` - Receive session ID from server
   - Emit `request_session_id` - Request new session
   - Emit `setup_data` - Publish setup
   - Emit `telemetry_update` - Publish telemetry

3. **Error Handling**
   - Connection failures (server offline)
   - Disconnection/reconnection logic
   - Invalid session ID handling
   - Network timeouts

4. **Tests: `tests/test_dashboard_publisher.py`**
   - Test connection to server
   - Test session ID request/assignment
   - Test setup publishing
   - Test telemetry publishing
   - Test reconnection logic
   - Mock WebSocket for testing

### Nice to Have

- Connection retry with exponential backoff
- Buffering telemetry during disconnection
- Publish queue (if server is slow)
- Connection health monitoring
- Metrics (messages sent, errors, etc.)

## API Contract

Based on `RACE_DASHBOARD_PLAN.md`:

### Events: Monitor → Server

#### Request Session ID
```python
sio.emit('request_session_id', {})
```

#### Publish Setup
```python
sio.emit('setup_data', {
    'session_id': 'abc-def-ghi',
    'timestamp': '2025-11-22T14:30:22.123Z',
    'setup': { ... }  # From REST API
})
```

#### Publish Telemetry
```python
sio.emit('telemetry_update', {
    'session_id': 'abc-def-ghi',
    'telemetry': { ... }  # From shared memory
})
```

### Events: Server → Monitor

#### Session ID Assigned
```python
@sio.event
def session_id_assigned(data):
    # data = {'session_id': 'abc-def-ghi'}
    self.session_id = data['session_id']
```

## Implementation Outline

```python
"""
Dashboard Publisher
Publishes telemetry and setup to dashboard server via WebSocket
"""
import socketio
from typing import Dict, Any, Optional
from datetime import datetime


class DashboardPublisher:
    """
    Publishes telemetry and setup data to dashboard server via WebSocket
    """

    def __init__(self, server_url: str, session_id: str = 'auto'):
        """
        Initialize publisher

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
        """Handle connection to server"""
        print(f"[Publisher] Connected to {self.server_url}")
        self.connected = True

        # Request session ID if auto
        if self.session_id == 'auto':
            self.sio.emit('request_session_id', {})

    def _on_disconnect(self):
        """Handle disconnection from server"""
        print("[Publisher] Disconnected from server")
        self.connected = False

    def _on_session_id_assigned(self, data: Dict[str, str]):
        """Handle session ID assignment"""
        self.session_id = data['session_id']
        print(f"[Publisher] Session ID: {self.session_id}")
        print(f"[Publisher] Dashboard URL: {self.server_url}/dashboard/{self.session_id}")

    def connect(self) -> bool:
        """
        Connect to server

        Returns:
            True if connected, False otherwise
        """
        try:
            self.sio.connect(self.server_url)
            return True
        except Exception as e:
            print(f"[Publisher] Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from server"""
        if self.connected:
            self.sio.disconnect()

    def publish_setup(self, setup_data: Dict[str, Any]):
        """
        Publish car setup (once per session)

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
            'timestamp': datetime.utcnow().isoformat(),
            'setup': setup_data
        })
        print("[Publisher] Setup data published")

    def publish_telemetry(self, telemetry_data: Dict[str, Any]):
        """
        Publish live telemetry

        Args:
            telemetry_data: Telemetry dictionary from TelemetryReader
        """
        if not self.connected:
            # Silently skip (telemetry is frequent, don't spam logs)
            return

        if self.session_id == 'auto':
            # Still waiting for session ID
            return

        # Extract dashboard fields (see dashboard_data_requirements.md)
        dashboard_data = self._extract_dashboard_fields(telemetry_data)

        self.sio.emit('telemetry_update', {
            'session_id': self.session_id,
            'telemetry': dashboard_data
        })

    def _extract_dashboard_fields(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract only the fields needed by dashboard

        Args:
            telemetry: Full telemetry dictionary

        Returns:
            Dashboard-compatible telemetry dict
        """
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'lap': telemetry.get('lap', 0),
            'position': telemetry.get('race_position', 0),
            'lap_time': telemetry.get('lap_time', 0.0),
            'fuel': telemetry.get('fuel_remaining', 0.0),
            'fuel_capacity': telemetry.get('fuel_at_start', 90.0),
            'tire_pressures': telemetry.get('tyre_pressure', {}),
            'tire_temps': telemetry.get('tyre_temp', {}),
            'tire_wear': telemetry.get('tyre_wear', {}),
            'brake_temps': telemetry.get('brake_temp', {}),
            'engine_water_temp': telemetry.get('engine_temp', 0.0),
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
        """Check if connected to server"""
        return self.connected

    def is_ready(self) -> bool:
        """Check if ready to publish (connected + has session ID)"""
        return self.connected and self.session_id != 'auto'
```

## Testing Strategy

```python
# tests/test_dashboard_publisher.py

import pytest
from unittest.mock import Mock, patch
from src.dashboard_publisher import DashboardPublisher


@pytest.fixture
def mock_socketio():
    with patch('src.dashboard_publisher.socketio.Client') as mock:
        yield mock


def test_init(mock_socketio):
    """Test initialization"""
    publisher = DashboardPublisher('http://localhost:5000')
    assert publisher.server_url == 'http://localhost:5000'
    assert publisher.session_id == 'auto'
    assert not publisher.connected


def test_connect_success(mock_socketio):
    """Test successful connection"""
    publisher = DashboardPublisher('http://localhost:5000')
    assert publisher.connect()


def test_connect_failure(mock_socketio):
    """Test connection failure"""
    mock_socketio.return_value.connect.side_effect = Exception("Connection error")
    publisher = DashboardPublisher('http://localhost:5000')
    assert not publisher.connect()


def test_session_id_assignment(mock_socketio):
    """Test session ID assignment"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher._on_session_id_assigned({'session_id': 'test-123'})
    assert publisher.session_id == 'test-123'


def test_publish_setup():
    """Test setup publishing"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True
    publisher.session_id = 'test-123'

    setup = {'suspension': {'front_spring': 120.5}}
    publisher.publish_setup(setup)

    # Verify emit was called
    publisher.sio.emit.assert_called_once()


def test_publish_telemetry():
    """Test telemetry publishing"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True
    publisher.session_id = 'test-123'

    telemetry = {
        'lap': 5,
        'fuel_remaining': 42.3,
        'speed': 256.3,
        # ... more fields
    }
    publisher.publish_telemetry(telemetry)

    # Verify emit was called
    publisher.sio.emit.assert_called_once()


def test_skip_publish_when_disconnected():
    """Test that publish is skipped when disconnected"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = False

    publisher.publish_telemetry({'lap': 5})

    # Should not emit
    publisher.sio.emit.assert_not_called()
```

## Dependencies

Add to `requirements.txt`:
```
python-socketio[client]>=5.9.0
```

## Implementation Steps

1. Create `src/dashboard_publisher.py`
2. Implement `DashboardPublisher` class
3. Add WebSocket event handlers
4. Implement field extraction logic
5. Create comprehensive tests
6. Test with mock server (or wait for server implementation)

## Validation Checklist

- [ ] Class initialization works
- [ ] Connection to server succeeds
- [ ] Session ID request/assignment works
- [ ] Setup publishing works
- [ ] Telemetry publishing works (2Hz)
- [ ] Disconnection handled gracefully
- [ ] Tests pass
- [ ] No memory leaks (disconnect cleanup)

## Related Files

- `RACE_DASHBOARD_PLAN.md` - API contract
- `bugs/dashboard_data_requirements.md` - Field mapping
- `src/telemetry/telemetry_interface.py` - Telemetry source
- `src/lmu_rest_api.py` - Setup source

---

**Next Steps:** After implementing, integrate into `monitor.py` entry point.
