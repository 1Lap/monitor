"""
Tests for DashboardPublisher

Tests the WebSocket client that publishes telemetry to the dashboard server.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.dashboard_publisher import DashboardPublisher


@pytest.fixture
def mock_socketio():
    """Mock socketio.Client"""
    with patch('src.dashboard_publisher.socketio.Client') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


def test_init_with_auto_session_id(mock_socketio):
    """Test initialization with auto session ID"""
    publisher = DashboardPublisher('http://localhost:5000')

    assert publisher.server_url == 'http://localhost:5000'
    assert publisher.session_id == 'auto'
    assert not publisher.connected
    assert publisher.sio is not None

    # Verify event handlers registered
    assert mock_socketio.on.called


def test_init_with_custom_session_id(mock_socketio):
    """Test initialization with custom session ID"""
    publisher = DashboardPublisher('http://localhost:5000', session_id='custom-123')

    assert publisher.session_id == 'custom-123'


def test_connect_success(mock_socketio):
    """Test successful connection to server"""
    publisher = DashboardPublisher('http://localhost:5000')

    result = publisher.connect()

    assert result is True
    mock_socketio.connect.assert_called_once_with('http://localhost:5000')


def test_connect_failure(mock_socketio):
    """Test connection failure handling"""
    mock_socketio.connect.side_effect = Exception("Connection refused")
    publisher = DashboardPublisher('http://localhost:5000')

    result = publisher.connect()

    assert result is False
    assert not publisher.connected


def test_on_connect_with_auto_session_id(mock_socketio):
    """Test _on_connect requests session ID when auto"""
    publisher = DashboardPublisher('http://localhost:5000', session_id='auto')

    publisher._on_connect()

    assert publisher.connected is True
    mock_socketio.emit.assert_called_once_with('request_session_id', {})


def test_on_connect_with_custom_session_id(mock_socketio):
    """Test _on_connect doesn't request session ID when custom"""
    publisher = DashboardPublisher('http://localhost:5000', session_id='custom-123')

    publisher._on_connect()

    assert publisher.connected is True
    # Should not request session ID
    mock_socketio.emit.assert_not_called()


def test_on_disconnect(mock_socketio):
    """Test _on_disconnect updates connected status"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True

    publisher._on_disconnect()

    assert publisher.connected is False


def test_on_session_id_assigned(mock_socketio):
    """Test _on_session_id_assigned updates session ID"""
    publisher = DashboardPublisher('http://localhost:5000')

    publisher._on_session_id_assigned({'session_id': 'server-assigned-123'})

    assert publisher.session_id == 'server-assigned-123'


def test_disconnect(mock_socketio):
    """Test disconnect from server"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True

    publisher.disconnect()

    mock_socketio.disconnect.assert_called_once()


def test_disconnect_when_not_connected(mock_socketio):
    """Test disconnect when not connected (no-op)"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = False

    publisher.disconnect()

    # Should not call disconnect
    mock_socketio.disconnect.assert_not_called()


def test_publish_setup_success(mock_socketio):
    """Test publishing setup data"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True
    publisher.session_id = 'test-123'

    setup_data = {
        'suspension': {'front_spring': 120.5},
        'aerodynamics': {'front_wing': 5}
    }

    publisher.publish_setup(setup_data)

    # Verify emit was called with correct event
    assert mock_socketio.emit.called
    call_args = mock_socketio.emit.call_args
    assert call_args[0][0] == 'setup_data'

    # Verify payload structure
    payload = call_args[0][1]
    assert payload['session_id'] == 'test-123'
    assert payload['setup'] == setup_data
    assert 'timestamp' in payload


def test_publish_setup_when_not_connected(mock_socketio):
    """Test publish_setup skips when not connected"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = False
    publisher.session_id = 'test-123'

    publisher.publish_setup({'suspension': {}})

    # Should not emit
    mock_socketio.emit.assert_not_called()


def test_publish_setup_when_no_session_id(mock_socketio):
    """Test publish_setup skips when session ID is auto"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True
    publisher.session_id = 'auto'

    publisher.publish_setup({'suspension': {}})

    # Should not emit (except the request_session_id from connect)
    # Reset the mock to ignore previous calls
    mock_socketio.emit.reset_mock()
    publisher.publish_setup({'suspension': {}})
    mock_socketio.emit.assert_not_called()


def test_publish_telemetry_success(mock_socketio):
    """Test publishing telemetry data"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True
    publisher.session_id = 'test-123'

    telemetry_data = {
        'lap': 5,
        'race_position': 3,
        'lap_time': 95.342,
        'fuel_remaining': 42.5,
        'fuel_at_start': 90.0,
        'speed': 256.3,
        'gear': 6,
        'rpm': 8500.0,
        'player_name': 'TestDriver',
        'car_name': 'LMP2',
        'track_name': 'Le Mans'
    }

    publisher.publish_telemetry(telemetry_data)

    # Verify emit was called
    assert mock_socketio.emit.called
    call_args = mock_socketio.emit.call_args
    assert call_args[0][0] == 'telemetry_update'

    # Verify payload structure
    payload = call_args[0][1]
    assert payload['session_id'] == 'test-123'
    assert 'telemetry' in payload

    # Verify extracted fields
    telemetry = payload['telemetry']
    assert telemetry['lap'] == 5
    assert telemetry['position'] == 3
    assert telemetry['fuel'] == 42.5
    assert telemetry['speed'] == 256.3
    assert 'timestamp' in telemetry


def test_publish_telemetry_when_not_connected(mock_socketio):
    """Test publish_telemetry skips silently when not connected"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = False
    publisher.session_id = 'test-123'

    publisher.publish_telemetry({'lap': 5})

    # Should not emit
    mock_socketio.emit.assert_not_called()


def test_publish_telemetry_when_no_session_id(mock_socketio):
    """Test publish_telemetry skips when session ID is auto"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True
    publisher.session_id = 'auto'

    # Reset mock to ignore previous calls
    mock_socketio.emit.reset_mock()

    publisher.publish_telemetry({'lap': 5})

    # Should not emit
    mock_socketio.emit.assert_not_called()


def test_extract_dashboard_fields(mock_socketio):
    """Test _extract_dashboard_fields extracts correct fields"""
    publisher = DashboardPublisher('http://localhost:5000')

    full_telemetry = {
        'lap': 10,
        'race_position': 1,
        'lap_time': 90.123,
        'fuel_remaining': 35.2,
        'fuel_at_start': 90.0,
        'tyre_pressure': {'FL': 28.5, 'FR': 28.3, 'RL': 27.9, 'RR': 28.1},
        'tyre_temp': {'FL': 85.0, 'FR': 86.0, 'RL': 83.0, 'RR': 84.0},
        'tyre_wear': {'FL': 0.95, 'FR': 0.94, 'RL': 0.96, 'RR': 0.95},
        'brake_temp': {'FL': 450.0, 'FR': 455.0, 'RL': 420.0, 'RR': 425.0},
        'engine_temp': 92.5,
        'track_temp': 32.0,
        'ambient_temp': 22.0,
        'speed': 287.5,
        'gear': 7,
        'rpm': 9200.0,
        'player_name': 'John Doe',
        'car_name': 'Hypercar',
        'track_name': 'Spa-Francorchamps',
        'session_type': 'Race',
        # Extra fields that should not be extracted
        'engine_vibration': 0.5,
        'suspension_travel': [10, 15, 12, 14]
    }

    dashboard_data = publisher._extract_dashboard_fields(full_telemetry)

    # Verify essential fields
    assert dashboard_data['lap'] == 10
    assert dashboard_data['position'] == 1
    assert dashboard_data['lap_time'] == 90.123
    assert dashboard_data['fuel'] == 35.2
    assert dashboard_data['fuel_capacity'] == 90.0
    assert dashboard_data['tire_pressures'] == {'FL': 28.5, 'FR': 28.3, 'RL': 27.9, 'RR': 28.1}
    assert dashboard_data['speed'] == 287.5
    assert dashboard_data['gear'] == 7
    assert dashboard_data['rpm'] == 9200.0
    assert dashboard_data['player_name'] == 'John Doe'
    assert 'timestamp' in dashboard_data

    # Verify extra fields are not included
    assert 'engine_vibration' not in dashboard_data
    assert 'suspension_travel' not in dashboard_data


def test_extract_dashboard_fields_with_missing_fields(mock_socketio):
    """Test _extract_dashboard_fields handles missing fields gracefully"""
    publisher = DashboardPublisher('http://localhost:5000')

    minimal_telemetry = {
        'lap': 1,
        'speed': 100.0
    }

    dashboard_data = publisher._extract_dashboard_fields(minimal_telemetry)

    # Verify defaults for missing fields
    assert dashboard_data['lap'] == 1
    assert dashboard_data['speed'] == 100.0
    assert dashboard_data['position'] == 0
    assert dashboard_data['fuel'] == 0.0
    assert dashboard_data['fuel_capacity'] == 90.0  # Default
    assert dashboard_data['gear'] == 0


def test_is_connected(mock_socketio):
    """Test is_connected returns connection status"""
    publisher = DashboardPublisher('http://localhost:5000')

    assert publisher.is_connected() is False

    publisher.connected = True
    assert publisher.is_connected() is True


def test_is_ready_when_connected_with_session_id(mock_socketio):
    """Test is_ready returns True when connected with session ID"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True
    publisher.session_id = 'test-123'

    assert publisher.is_ready() is True


def test_is_ready_when_not_connected(mock_socketio):
    """Test is_ready returns False when not connected"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = False
    publisher.session_id = 'test-123'

    assert publisher.is_ready() is False


def test_is_ready_when_no_session_id(mock_socketio):
    """Test is_ready returns False when session ID is auto"""
    publisher = DashboardPublisher('http://localhost:5000')
    publisher.connected = True
    publisher.session_id = 'auto'

    assert publisher.is_ready() is False
