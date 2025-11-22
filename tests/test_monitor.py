"""
Tests for Monitor

Tests the main monitor application entry point that orchestrates all components.
"""
import pytest
import json
import tempfile
import os
import time
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path


@pytest.fixture
def temp_config():
    """Create a temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "server_url": "http://localhost:5000",
            "session_id": "auto",
            "update_rate_hz": 2,
            "poll_interval": 0.01,
            "target_process": "LMU.exe"
        }
        json.dump(config, f)
        f.flush()
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.remove(f.name)


@pytest.fixture
def mock_components():
    """Mock all monitor components"""
    with patch('monitor.get_telemetry_reader') as mock_telemetry, \
         patch('monitor.LMURestAPI') as mock_rest_api, \
         patch('monitor.ProcessMonitor') as mock_process_monitor, \
         patch('monitor.DashboardPublisher') as mock_publisher:

        # Configure mocks
        mock_telemetry_instance = MagicMock()
        mock_telemetry_instance.is_available.return_value = True
        mock_telemetry_instance.read.return_value = {
            'lap': 5,
            'race_position': 3,
            'fuel_remaining': 42.5,
            'speed': 256.0
        }
        mock_telemetry.return_value = mock_telemetry_instance

        mock_api_instance = MagicMock()
        mock_api_instance.is_available.return_value = True
        mock_api_instance.fetch_setup_data.return_value = {'suspension': 'data'}
        mock_rest_api.return_value = mock_api_instance

        mock_pm_instance = MagicMock()
        mock_pm_instance.is_running.return_value = True
        mock_process_monitor.return_value = mock_pm_instance

        mock_pub_instance = MagicMock()
        mock_pub_instance.connect.return_value = True
        mock_pub_instance.is_ready.return_value = True
        mock_pub_instance.is_connected.return_value = True
        mock_publisher.return_value = mock_pub_instance

        yield {
            'telemetry': mock_telemetry_instance,
            'rest_api': mock_api_instance,
            'process_monitor': mock_pm_instance,
            'publisher': mock_pub_instance
        }


@pytest.fixture
def monitor_class():
    """Import Monitor class with mocked dependencies"""
    import sys
    # Ensure monitor.py is in the path
    sys.path.insert(0, '/home/user/monitor')

    with patch('monitor.get_telemetry_reader'), \
         patch('monitor.LMURestAPI'), \
         patch('monitor.ProcessMonitor'), \
         patch('monitor.DashboardPublisher'), \
         patch('monitor.signal.signal'):

        from monitor import Monitor
        yield Monitor


def test_monitor_init_loads_config(temp_config, monitor_class):
    """Test Monitor initializes and loads configuration"""
    monitor = monitor_class(temp_config)

    assert monitor.config['server_url'] == 'http://localhost:5000'
    assert monitor.config['update_rate_hz'] == 2
    assert monitor.config['target_process'] == 'LMU.exe'
    assert not monitor.running
    assert not monitor.setup_sent


def test_monitor_init_creates_components(temp_config, monitor_class, mock_components):
    """Test Monitor initializes all components"""
    with patch('monitor.get_telemetry_reader') as mock_telemetry, \
         patch('monitor.LMURestAPI') as mock_rest_api, \
         patch('monitor.ProcessMonitor') as mock_process_monitor, \
         patch('monitor.DashboardPublisher') as mock_publisher, \
         patch('monitor.signal.signal'):

        monitor = monitor_class(temp_config)

        # Verify components were created
        mock_telemetry.assert_called_once()
        mock_rest_api.assert_called_once()
        mock_process_monitor.assert_called_once()
        mock_publisher.assert_called_once()


def test_monitor_init_registers_signal_handlers(temp_config, monitor_class):
    """Test Monitor registers signal handlers for graceful shutdown"""
    import signal as signal_module

    with patch('monitor.signal.signal') as mock_signal, \
         patch('monitor.get_telemetry_reader'), \
         patch('monitor.LMURestAPI'), \
         patch('monitor.ProcessMonitor'), \
         patch('monitor.DashboardPublisher'):

        monitor = monitor_class(temp_config)

        # Verify signal handlers registered
        assert mock_signal.call_count >= 2
        # Check for SIGINT and SIGTERM
        calls = [call_args[0] for call_args in mock_signal.call_args_list]
        signals = [c[0] for c in calls]
        assert signal_module.SIGINT in signals
        assert signal_module.SIGTERM in signals


def test_monitor_load_config_missing_file(monitor_class):
    """Test Monitor handles missing config file gracefully"""
    # Use a unique filename to avoid conflicts
    test_config = 'test_nonexistent_config_12345.json'

    # Clean up if it exists from previous run
    if os.path.exists(test_config):
        os.remove(test_config)

    try:
        with patch('monitor.get_telemetry_reader'), \
             patch('monitor.LMURestAPI'), \
             patch('monitor.ProcessMonitor'), \
             patch('monitor.DashboardPublisher'), \
             patch('monitor.signal.signal'), \
             patch('builtins.print'), \
             pytest.raises(SystemExit):

            monitor = monitor_class(test_config)
    finally:
        # Clean up created file
        if os.path.exists(test_config):
            os.remove(test_config)


def test_monitor_load_config_invalid_json(monitor_class):
    """Test Monitor handles invalid JSON in config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        f.flush()

        try:
            with patch('monitor.get_telemetry_reader'), \
                 patch('monitor.LMURestAPI'), \
                 patch('monitor.ProcessMonitor'), \
                 patch('monitor.DashboardPublisher'), \
                 patch('monitor.signal.signal'), \
                 patch('builtins.print'), \
                 pytest.raises(SystemExit):

                monitor = monitor_class(f.name)
        finally:
            os.remove(f.name)


def test_monitor_start_connects_to_server(temp_config, monitor_class, mock_components):
    """Test Monitor start() connects to dashboard server"""
    with patch('monitor.get_telemetry_reader') as mock_telem, \
         patch('monitor.LMURestAPI') as mock_api, \
         patch('monitor.ProcessMonitor') as mock_pm, \
         patch('monitor.DashboardPublisher') as mock_pub, \
         patch('monitor.signal.signal'), \
         patch('builtins.print'):

        # Setup mocks
        mock_pub_instance = MagicMock()
        mock_pub_instance.connect.return_value = True
        mock_pub_instance.is_ready.return_value = True
        mock_pub.return_value = mock_pub_instance

        mock_pm_instance = MagicMock()
        mock_pm_instance.is_running.return_value = False  # No LMU running
        mock_pm.return_value = mock_pm_instance

        mock_telem.return_value = MagicMock()
        mock_api.return_value = MagicMock()

        monitor = monitor_class(temp_config)

        # Start in a thread that we can stop quickly
        import threading
        def run_monitor():
            monitor.start()

        thread = threading.Thread(target=run_monitor)
        thread.start()

        # Give it a moment to connect
        time.sleep(0.1)

        # Stop monitor
        monitor.stop()
        thread.join(timeout=1)

        # Verify connection was attempted
        mock_pub_instance.connect.assert_called_once()


def test_monitor_start_fails_if_server_offline(temp_config, monitor_class):
    """Test Monitor start() handles server connection failure"""
    with patch('monitor.get_telemetry_reader') as mock_telem, \
         patch('monitor.LMURestAPI') as mock_api, \
         patch('monitor.ProcessMonitor') as mock_pm, \
         patch('monitor.DashboardPublisher') as mock_pub, \
         patch('monitor.signal.signal'), \
         patch('builtins.print'):

        # Setup mocks - connection fails
        mock_pub_instance = MagicMock()
        mock_pub_instance.connect.return_value = False
        mock_pub.return_value = mock_pub_instance

        mock_telem.return_value = MagicMock()
        mock_api.return_value = MagicMock()
        mock_pm.return_value = MagicMock()

        monitor = monitor_class(temp_config)
        monitor.start()

        # Verify connection was attempted
        mock_pub_instance.connect.assert_called_once()
        # Monitor should return early without entering main loop
        assert not monitor.running


def test_monitor_sends_setup_once_when_lmu_detected(temp_config, monitor_class):
    """Test Monitor sends setup data once when LMU is detected"""
    with patch('monitor.get_telemetry_reader') as mock_telem, \
         patch('monitor.LMURestAPI') as mock_api, \
         patch('monitor.ProcessMonitor') as mock_pm, \
         patch('monitor.DashboardPublisher') as mock_pub, \
         patch('monitor.signal.signal'), \
         patch('builtins.print'):

        # Setup mocks
        mock_pub_instance = MagicMock()
        mock_pub_instance.connect.return_value = True
        mock_pub_instance.is_ready.return_value = True
        mock_pub.return_value = mock_pub_instance

        mock_api_instance = MagicMock()
        mock_api_instance.is_available.return_value = True
        mock_api_instance.fetch_setup_data.return_value = {'suspension': 'test_data'}
        mock_api.return_value = mock_api_instance

        mock_pm_instance = MagicMock()
        # Start not running, then running
        mock_pm_instance.is_running.side_effect = [False, True, True, True]
        mock_pm.return_value = mock_pm_instance

        mock_telem_instance = MagicMock()
        mock_telem_instance.is_available.return_value = True
        mock_telem_instance.read.return_value = {'lap': 1}
        mock_telem.return_value = mock_telem_instance

        monitor = monitor_class(temp_config)

        # Start and stop quickly
        import threading
        def run_monitor():
            monitor.start()

        thread = threading.Thread(target=run_monitor)
        thread.start()

        time.sleep(1.5)  # Let it run a bit (needs to wait past the 1s sleep when process not found)
        monitor.stop()
        thread.join(timeout=1)

        # Verify setup was sent exactly once
        mock_api_instance.fetch_setup_data.assert_called_once()
        mock_pub_instance.publish_setup.assert_called_once_with({'suspension': 'test_data'})


def test_monitor_publishes_telemetry_at_configured_rate(temp_config, monitor_class):
    """Test Monitor publishes telemetry at configured rate (2Hz)"""
    with patch('monitor.get_telemetry_reader') as mock_telem, \
         patch('monitor.LMURestAPI') as mock_api, \
         patch('monitor.ProcessMonitor') as mock_pm, \
         patch('monitor.DashboardPublisher') as mock_pub, \
         patch('monitor.signal.signal'), \
         patch('builtins.print'):

        # Setup mocks
        mock_pub_instance = MagicMock()
        mock_pub_instance.connect.return_value = True
        mock_pub_instance.is_ready.return_value = True
        mock_pub.return_value = mock_pub_instance

        mock_api_instance = MagicMock()
        mock_api_instance.is_available.return_value = True
        mock_api_instance.fetch_setup_data.return_value = {}
        mock_api.return_value = mock_api_instance

        mock_pm_instance = MagicMock()
        mock_pm_instance.is_running.return_value = True
        mock_pm.return_value = mock_pm_instance

        mock_telem_instance = MagicMock()
        mock_telem_instance.is_available.return_value = True
        mock_telem_instance.read.return_value = {'lap': 1}
        mock_telem.return_value = mock_telem_instance

        monitor = monitor_class(temp_config)

        # Start and run for ~1 second (should get ~2 telemetry publishes at 2Hz)
        import threading
        def run_monitor():
            monitor.start()

        thread = threading.Thread(target=run_monitor)
        thread.start()

        time.sleep(1.0)
        monitor.stop()
        thread.join(timeout=1)

        # Verify telemetry was published (should be around 2 times for 1 second at 2Hz)
        # Allow some variance due to timing
        assert mock_pub_instance.publish_telemetry.call_count >= 1
        assert mock_pub_instance.publish_telemetry.call_count <= 4


def test_monitor_stop_disconnects_publisher(temp_config, monitor_class):
    """Test Monitor stop() disconnects from server"""
    with patch('monitor.get_telemetry_reader'), \
         patch('monitor.LMURestAPI'), \
         patch('monitor.ProcessMonitor'), \
         patch('monitor.DashboardPublisher') as mock_pub, \
         patch('monitor.signal.signal'), \
         patch('builtins.print'):

        mock_pub_instance = MagicMock()
        mock_pub.return_value = mock_pub_instance

        monitor = monitor_class(temp_config)
        monitor.stop()

        # Verify disconnect was called
        mock_pub_instance.disconnect.assert_called_once()


def test_monitor_logging_mode_no_server_connection(temp_config, monitor_class):
    """Test Monitor logging mode doesn't connect to server"""
    with patch('monitor.get_telemetry_reader') as mock_telem, \
         patch('monitor.LMURestAPI'), \
         patch('monitor.ProcessMonitor') as mock_pm, \
         patch('monitor.DashboardPublisher') as mock_pub, \
         patch('monitor.signal.signal'), \
         patch('builtins.print'):

        mock_pm_instance = MagicMock()
        mock_pm_instance.is_running.return_value = False  # No process running
        mock_pm.return_value = mock_pm_instance

        mock_telem_instance = MagicMock()
        mock_telem_instance.is_available.return_value = True
        mock_telem_instance.read.return_value = {'lap': 1}
        mock_telem.return_value = mock_telem_instance

        mock_pub_instance = MagicMock()
        mock_pub.return_value = mock_pub_instance

        monitor = monitor_class(temp_config)

        # Start logging mode and stop quickly
        import threading
        def run_logging():
            monitor.start_logging_mode()

        thread = threading.Thread(target=run_logging)
        thread.start()

        time.sleep(0.1)
        monitor.stop()
        thread.join(timeout=1)

        # Verify server connection was NOT attempted
        mock_pub_instance.connect.assert_not_called()


def test_monitor_logging_mode_prints_telemetry(temp_config, monitor_class):
    """Test Monitor logging mode prints telemetry to console"""
    with patch('monitor.get_telemetry_reader') as mock_telem, \
         patch('monitor.LMURestAPI'), \
         patch('monitor.ProcessMonitor') as mock_pm, \
         patch('monitor.DashboardPublisher'), \
         patch('monitor.signal.signal'), \
         patch('monitor.log_telemetry') as mock_log, \
         patch('builtins.print'):

        mock_pm_instance = MagicMock()
        mock_pm_instance.is_running.return_value = True
        mock_pm.return_value = mock_pm_instance

        mock_telem_instance = MagicMock()
        mock_telem_instance.is_available.return_value = True
        test_data = {'lap': 5, 'speed': 250}
        mock_telem_instance.read.return_value = test_data
        mock_telem.return_value = mock_telem_instance

        monitor = monitor_class(temp_config)

        # Start logging mode and stop quickly
        import threading
        def run_logging():
            monitor.start_logging_mode()

        thread = threading.Thread(target=run_logging)
        thread.start()

        time.sleep(0.6)  # Let it log once or twice at 2Hz
        monitor.stop()
        thread.join(timeout=1)

        # Verify log_telemetry was called
        assert mock_log.called
        # Verify it was called with the test data
        mock_log.assert_called_with(test_data)


def test_monitor_handles_telemetry_errors_gracefully(temp_config, monitor_class):
    """Test Monitor handles telemetry read errors without crashing"""
    with patch('monitor.get_telemetry_reader') as mock_telem, \
         patch('monitor.LMURestAPI') as mock_api, \
         patch('monitor.ProcessMonitor') as mock_pm, \
         patch('monitor.DashboardPublisher') as mock_pub, \
         patch('monitor.signal.signal'), \
         patch('builtins.print'):

        mock_pub_instance = MagicMock()
        mock_pub_instance.connect.return_value = True
        mock_pub_instance.is_ready.return_value = True
        mock_pub.return_value = mock_pub_instance

        mock_api_instance = MagicMock()
        mock_api_instance.is_available.return_value = False
        mock_api.return_value = mock_api_instance

        mock_pm_instance = MagicMock()
        mock_pm_instance.is_running.return_value = True
        mock_pm.return_value = mock_pm_instance

        mock_telem_instance = MagicMock()
        mock_telem_instance.is_available.return_value = True
        # Telemetry read returns None (error case)
        mock_telem_instance.read.return_value = None
        mock_telem.return_value = mock_telem_instance

        monitor = monitor_class(temp_config)

        # Start and stop quickly
        import threading
        def run_monitor():
            monitor.start()

        thread = threading.Thread(target=run_monitor)
        thread.start()

        time.sleep(0.2)
        monitor.stop()
        thread.join(timeout=1)

        # Monitor should handle gracefully (no crash)
        # Telemetry should not be published when None
        # This tests that the monitor doesn't crash on None telemetry


def test_monitor_create_default_config(monitor_class):
    """Test Monitor creates default config when missing"""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, 'new_config.json')

    try:
        with patch('monitor.get_telemetry_reader'), \
             patch('monitor.LMURestAPI'), \
             patch('monitor.ProcessMonitor'), \
             patch('monitor.DashboardPublisher'), \
             patch('monitor.signal.signal'), \
             patch('builtins.print'), \
             pytest.raises(SystemExit):

            monitor = monitor_class(config_path)

        # Verify config was created
        assert os.path.exists(config_path)

        # Verify contents
        with open(config_path) as f:
            config = json.load(f)

        assert config['server_url'] == 'http://localhost:5000'
        assert config['session_id'] == 'auto'
        assert config['update_rate_hz'] == 2
        assert config['poll_interval'] == 0.01
        assert config['target_process'] == 'LMU.exe'

    finally:
        if os.path.exists(config_path):
            os.remove(config_path)
        os.rmdir(temp_dir)


def test_log_telemetry_function():
    """Test log_telemetry function prints formatted telemetry"""
    from monitor import log_telemetry

    test_data = {
        'player_name': 'Test Driver',
        'car_name': 'Test Car',
        'track_name': 'Test Track',
        'session_type': 'Race',
        'race_position': 3,
        'lap': 10,
        'lap_time': 95.342,
        'fuel_remaining': 42.5,
        'fuel_at_start': 90.0,
        'tyre_pressure': {'fl': 28.5, 'fr': 28.3, 'rl': 27.9, 'rr': 28.1},
        'tyre_temp': {'fl': 85.0, 'fr': 86.0, 'rl': 83.0, 'rr': 84.0},
        'brake_temp': {'fl': 450.0, 'fr': 455.0, 'rl': 420.0, 'rr': 425.0},
        'engine_temp': 92.5,
        'track_temp': 32.0,
        'ambient_temp': 22.0,
        'speed': 287.5,
        'gear': 7,
        'rpm': 9200.0
    }

    with patch('builtins.print') as mock_print:
        log_telemetry(test_data)

        # Verify print was called multiple times (formatted output)
        assert mock_print.call_count > 5

        # Check that key information was printed
        printed_output = ' '.join([str(call_args[0]) for call_args in mock_print.call_args_list])
        assert 'Test Driver' in printed_output or 'Test Car' in printed_output
