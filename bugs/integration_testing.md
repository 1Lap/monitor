# Task: Integration Testing Checklist

**Type:** Testing
**Priority:** High
**Phase:** MVP - Phase 1
**Estimated Time:** 2-3 hours

---

## Overview

Create comprehensive integration tests to validate the complete monitor system works end-to-end, from LMU detection to dashboard publishing.

## Objective

Ensure all monitor components work together correctly:
1. Configuration loading
2. Component initialization
3. Process detection
4. Telemetry reading
5. Setup fetching
6. Dashboard publishing
7. Error handling

## Test Categories

### 1. Unit Tests (Existing)

Already implemented for core components:
- ✅ `test_telemetry_mock.py` (7 tests)
- ✅ `test_telemetry_real.py` (2 tests)
- ✅ `test_lmu_rest_api.py` (existing)
- ✅ `test_process_monitor.py` (5 tests)

Need to add:
- ⬜ `test_dashboard_publisher.py` (NEW)
- ⬜ `test_monitor_integration.py` (NEW)

### 2. Integration Tests (New)

**`tests/test_monitor_integration.py`**

```python
"""
Integration tests for monitor system
Tests end-to-end flow without requiring real LMU or server
"""
import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from monitor import Monitor


@pytest.fixture
def test_config(tmp_path):
    """Create test config file"""
    config = {
        'server_url': 'http://localhost:5000',
        'session_id': 'auto',
        'update_rate_hz': 2,
        'poll_interval': 0.01,
        'target_process': 'test.exe'
    }
    config_path = tmp_path / 'test_config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f)
    return str(config_path)


class TestMonitorIntegration:
    """Integration tests for Monitor class"""

    def test_monitor_initialization(self, test_config):
        """Test monitor initializes all components"""
        monitor = Monitor(test_config)

        assert monitor.config is not None
        assert monitor.telemetry is not None
        assert monitor.rest_api is not None
        assert monitor.process_monitor is not None
        assert monitor.publisher is not None
        assert not monitor.running
        assert not monitor.setup_sent

    def test_config_loading(self, test_config):
        """Test configuration loading"""
        monitor = Monitor(test_config)

        assert monitor.config['server_url'] == 'http://localhost:5000'
        assert monitor.config['update_rate_hz'] == 2
        assert monitor.config['target_process'] == 'test.exe'

    def test_default_config_creation(self, tmp_path):
        """Test default config creation when missing"""
        missing_config = tmp_path / 'missing.json'

        with pytest.raises(SystemExit):
            Monitor(str(missing_config))

        # Check default config was created
        assert missing_config.exists()
        with open(missing_config) as f:
            config = json.load(f)
        assert 'server_url' in config
        assert 'update_rate_hz' in config

    @patch('monitor.DashboardPublisher')
    @patch('monitor.ProcessMonitor')
    @patch('monitor.get_telemetry_reader')
    def test_start_without_lmu(self, mock_telem, mock_process, mock_publisher, test_config):
        """Test monitor behavior when LMU not running"""
        # Setup mocks
        mock_process.return_value.is_running.return_value = False
        mock_publisher.return_value.connect.return_value = True
        mock_publisher.return_value.is_ready.return_value = True

        monitor = Monitor(test_config)

        # Start in background thread
        import threading
        thread = threading.Thread(target=monitor.start)
        thread.daemon = True
        thread.start()

        time.sleep(0.5)
        monitor.stop()

        # Should not send setup (LMU not running)
        assert not monitor.setup_sent

    @patch('monitor.DashboardPublisher')
    @patch('monitor.ProcessMonitor')
    @patch('monitor.LMURestAPI')
    @patch('monitor.get_telemetry_reader')
    def test_start_with_lmu(self, mock_telem, mock_api, mock_process, mock_publisher, test_config):
        """Test monitor behavior when LMU is running"""
        # Setup mocks
        mock_process.return_value.is_running.return_value = True
        mock_api.return_value.is_available.return_value = True
        mock_api.return_value.fetch_setup_data.return_value = {'test': 'setup'}
        mock_telem.return_value.is_available.return_value = True
        mock_telem.return_value.read.return_value = {'lap': 1, 'fuel': 50.0}
        mock_publisher.return_value.connect.return_value = True
        mock_publisher.return_value.is_ready.return_value = True

        monitor = Monitor(test_config)

        # Start in background thread
        import threading
        thread = threading.Thread(target=monitor.start)
        thread.daemon = True
        thread.start()

        time.sleep(1.0)  # Let it run for 1 second
        monitor.stop()

        # Should have sent setup
        assert monitor.setup_sent

        # Verify publisher methods called
        mock_publisher.return_value.publish_setup.assert_called_once()
        assert mock_publisher.return_value.publish_telemetry.call_count > 0

    @patch('monitor.DashboardPublisher')
    def test_server_connection_failure(self, mock_publisher, test_config):
        """Test behavior when server connection fails"""
        mock_publisher.return_value.connect.return_value = False

        monitor = Monitor(test_config)
        monitor.start()  # Should exit gracefully

        # No crash, just exit
        assert not monitor.running

    def test_logging_mode(self, test_config):
        """Test --log-only mode"""
        # TODO: Implement when logging mode is added
        pass


class TestDashboardPublisherIntegration:
    """Integration tests for DashboardPublisher"""

    @patch('src.dashboard_publisher.socketio.Client')
    def test_publisher_workflow(self, mock_sio):
        """Test complete publisher workflow"""
        from src.dashboard_publisher import DashboardPublisher

        # Setup mock
        mock_client = MagicMock()
        mock_sio.return_value = mock_client

        publisher = DashboardPublisher('http://localhost:5000')

        # Connect
        assert publisher.connect()

        # Simulate session ID assignment
        publisher._on_session_id_assigned({'session_id': 'test-123'})
        assert publisher.session_id == 'test-123'
        assert publisher.is_ready()

        # Publish setup
        setup = {'suspension': {'front_spring': 120.5}}
        publisher.publish_setup(setup)

        # Publish telemetry
        telemetry = {
            'lap': 5,
            'fuel_remaining': 42.3,
            'speed': 256.3,
            'tyre_pressure': {'fl': 25.1, 'fr': 24.9, 'rl': 25.3, 'rr': 25.0}
        }
        publisher.publish_telemetry(telemetry)

        # Verify emits
        assert mock_client.emit.call_count >= 2  # setup + telemetry

        # Disconnect
        publisher.disconnect()


class TestEndToEndFlow:
    """End-to-end integration tests"""

    @patch('monitor.socketio.Client')
    @patch('monitor.ProcessMonitor')
    @patch('monitor.LMURestAPI')
    @patch('monitor.get_telemetry_reader')
    def test_complete_workflow(self, mock_telem, mock_api, mock_process, mock_sio, test_config):
        """Test complete monitor workflow end-to-end"""
        # Setup mocks for complete flow
        mock_process.return_value.is_running.return_value = True

        mock_api.return_value.is_available.return_value = True
        mock_api.return_value.fetch_setup_data.return_value = {
            'suspension': {'front_spring': 120.5},
            'aerodynamics': {'front_wing': 5}
        }

        mock_telem.return_value.is_available.return_value = True
        mock_telem.return_value.read.return_value = {
            'lap': 5,
            'race_position': 3,
            'lap_time': 123.456,
            'fuel_remaining': 42.3,
            'fuel_at_start': 90.0,
            'tyre_pressure': {'fl': 25.1, 'fr': 24.9, 'rl': 25.3, 'rr': 25.0},
            'tyre_temp': {'fl': 75.2, 'fr': 73.8, 'rl': 78.1, 'rr': 76.5},
            'brake_temp': {'fl': 480, 'fr': 485, 'rl': 612, 'rr': 615},
            'engine_temp': 109.5,
            'track_temp': 41.8,
            'ambient_temp': 24.0,
            'speed': 256.3,
            'gear': 6,
            'rpm': 7267.0,
            'player_name': 'Test Driver',
            'car_name': 'Test Car',
            'track_name': 'Test Track',
            'session_type': 'Race'
        }

        # Mock WebSocket client
        mock_client = MagicMock()
        mock_sio.return_value = mock_client

        # Create and start monitor
        monitor = Monitor(test_config)

        # Simulate connection and session ID
        monitor.publisher._on_connect()
        monitor.publisher._on_session_id_assigned({'session_id': 'test-123'})

        # Run for a short time
        import threading
        thread = threading.Thread(target=monitor.start)
        thread.daemon = True
        thread.start()

        time.sleep(2.0)  # Run for 2 seconds
        monitor.stop()

        # Verify flow
        assert monitor.setup_sent
        assert mock_client.emit.call_count > 2  # At least setup + some telemetry

        # Verify setup was published
        setup_calls = [call for call in mock_client.emit.call_args_list
                       if call[0][0] == 'setup_data']
        assert len(setup_calls) >= 1

        # Verify telemetry was published
        telem_calls = [call for call in mock_client.emit.call_args_list
                       if call[0][0] == 'telemetry_update']
        assert len(telem_calls) >= 2  # At 2Hz for 2 seconds = ~4 updates
```

### 3. Manual Testing Checklist

#### Local Development (macOS/Mock)

- [ ] **Test 1: Basic startup**
  ```bash
  python monitor.py --log-only
  # Should show waiting for process
  ```

- [ ] **Test 2: Mock telemetry**
  ```bash
  # Set target_process to "python" in config.json
  python monitor.py --log-only
  # Should show mock telemetry
  ```

- [ ] **Test 3: Invalid config**
  ```bash
  mv config.json config.json.bak
  python monitor.py
  # Should create default config and exit
  ```

#### Windows Testing (with LMU)

- [ ] **Test 4: LMU detection**
  ```bash
  # Start LMU first
  python monitor.py --log-only
  # Should detect LMU and show telemetry
  ```

- [ ] **Test 5: REST API fetching**
  ```bash
  # In garage with setup loaded
  python monitor.py --log-only
  # Should fetch and log setup data
  ```

- [ ] **Test 6: Server connection**
  ```bash
  # Start server first
  python monitor.py
  # Should connect, get session ID, publish data
  ```

- [ ] **Test 7: Reconnection**
  ```bash
  # Start monitor, then kill server, restart server
  # Monitor should reconnect
  ```

- [ ] **Test 8: LMU restart**
  ```bash
  # Start monitor, start LMU, stop LMU, start LMU
  # Monitor should re-send setup after restart
  ```

### 4. Performance Testing

- [ ] **Test 9: Update rate accuracy**
  ```bash
  # Monitor telemetry publish rate
  # Should be ~2Hz (±10%)
  ```

- [ ] **Test 10: Memory usage**
  ```bash
  # Run for extended period (30 min)
  # Monitor memory usage (should be stable)
  ```

- [ ] **Test 11: CPU usage**
  ```bash
  # Monitor CPU usage
  # Should be < 5% on modern hardware
  ```

### 5. Error Handling Tests

- [ ] **Test 12: Server offline**
  ```bash
  # Start monitor without server
  # Should show error and exit gracefully
  ```

- [ ] **Test 13: LMU crash**
  ```bash
  # Monitor running, kill LMU process
  # Should detect and wait for restart
  ```

- [ ] **Test 14: Network disconnect**
  ```bash
  # Disconnect network during session
  # Should handle gracefully
  ```

## Success Criteria

### All Tests Pass

- ✅ Unit tests pass (14+ tests)
- ✅ Integration tests pass (10+ tests)
- ✅ Manual testing checklist complete
- ✅ No memory leaks
- ✅ No crashes
- ✅ Graceful error handling

### Performance Targets

- Update rate: 2Hz ± 10%
- Memory: < 100MB
- CPU: < 5%
- Startup time: < 5 seconds

## Running Tests

```bash
# All tests
pytest -v

# Integration tests only
pytest tests/test_monitor_integration.py -v

# With coverage
pytest --cov=src --cov=monitor --cov-report=html

# Specific test
pytest tests/test_monitor_integration.py::TestMonitorIntegration::test_start_with_lmu -v
```

## Dependencies

- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `unittest.mock` - Mocking

## Related Files

- `monitor.py` - Main application
- `src/dashboard_publisher.py` - Publisher component
- `bugs/create_monitor_entry_point.md` - Monitor implementation
- `bugs/implement_dashboard_publisher.md` - Publisher implementation

---

**Next Steps:** Run all tests and validate end-to-end flow before considering MVP complete.
