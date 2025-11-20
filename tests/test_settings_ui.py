"""Tests for settings UI and configuration management"""

import pytest
import tempfile
import json
import shutil
from pathlib import Path
from src.settings_ui import SettingsConfig


class TestSettingsConfig:
    """Test suite for SettingsConfig (backend logic, no GUI)"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test config files"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup after test
        if temp_path.exists():
            shutil.rmtree(temp_path)

    @pytest.fixture
    def config_file(self, temp_dir):
        """Create a temporary config file path"""
        return temp_dir / "config.json"

    def test_load_config_creates_defaults_if_missing(self, config_file):
        """Should return default config when file doesn't exist"""
        config = SettingsConfig(config_file)

        assert not config_file.exists()
        assert config.get('output_dir') == './telemetry_output'
        assert config.get('target_process') == 'Le Mans Ultimate'
        assert config.get('poll_interval') == 0.01  # 100Hz
        assert config.get('track_opponents') is True
        assert config.get('track_opponent_ai') is False

    def test_load_config_from_existing_file(self, config_file):
        """Should load config from existing JSON file"""
        # Write test config
        test_config = {
            'output_dir': '/custom/path',
            'target_process': 'TestProcess',
            'poll_interval': 0.02,  # 50Hz
            'track_opponents': False,
        }
        with open(config_file, 'w') as f:
            json.dump(test_config, f)

        # Load config
        config = SettingsConfig(config_file)

        assert config.get('output_dir') == '/custom/path'
        assert config.get('target_process') == 'TestProcess'
        assert config.get('poll_interval') == 0.02
        assert config.get('track_opponents') is False
        # Should merge with defaults for missing keys
        assert config.get('track_opponent_ai') is False

    def test_save_config_writes_json_file(self, config_file):
        """Should write config to JSON file"""
        config = SettingsConfig(config_file)
        config.set('output_dir', '/new/path')
        config.set('poll_interval', 0.005)  # 200Hz
        config.save()

        # Verify file was created
        assert config_file.exists()

        # Verify contents
        with open(config_file, 'r') as f:
            saved_data = json.load(f)

        assert saved_data['output_dir'] == '/new/path'
        assert saved_data['poll_interval'] == 0.005

    def test_restore_defaults(self, config_file):
        """Should restore all values to defaults"""
        # Create config with custom values
        test_config = {
            'output_dir': '/custom/path',
            'target_process': 'CustomProcess',
            'poll_interval': 0.05,
        }
        with open(config_file, 'w') as f:
            json.dump(test_config, f)

        # Load and restore defaults
        config = SettingsConfig(config_file)
        config.restore_defaults()

        # Verify defaults restored
        assert config.get('output_dir') == './telemetry_output'
        assert config.get('target_process') == 'Le Mans Ultimate'
        assert config.get('poll_interval') == 0.01

    def test_validate_output_directory_valid(self, temp_dir, config_file):
        """Should validate that output directory is accessible"""
        config = SettingsConfig(config_file)
        config.set('output_dir', str(temp_dir))

        is_valid, error_msg = config.validate()
        assert is_valid is True
        assert error_msg is None

    def test_validate_output_directory_invalid(self, config_file):
        """Should detect invalid output directory"""
        config = SettingsConfig(config_file)
        # Set to a path that doesn't exist and can't be created (invalid chars)
        config.set('output_dir', '/\x00/invalid/path')

        is_valid, error_msg = config.validate()
        assert is_valid is False
        assert error_msg is not None
        assert 'output_dir' in error_msg.lower()

    def test_validate_poll_interval_valid(self, config_file):
        """Should validate poll interval is positive"""
        config = SettingsConfig(config_file)
        config.set('poll_interval', 0.01)

        is_valid, error_msg = config.validate()
        assert is_valid is True

    def test_validate_poll_interval_invalid(self, config_file):
        """Should reject invalid poll intervals"""
        config = SettingsConfig(config_file)
        config.set('poll_interval', -0.01)

        is_valid, error_msg = config.validate()
        assert is_valid is False
        assert 'poll_interval' in error_msg.lower()

    def test_set_and_get_values(self, config_file):
        """Should allow setting and getting config values"""
        config = SettingsConfig(config_file)

        config.set('track_opponents', False)
        config.set('track_opponent_ai', True)

        assert config.get('track_opponents') is False
        assert config.get('track_opponent_ai') is True

    def test_merge_with_defaults(self, config_file):
        """Should merge loaded config with defaults for missing keys"""
        # Write partial config
        partial_config = {
            'output_dir': '/custom/path',
        }
        with open(config_file, 'w') as f:
            json.dump(partial_config, f)

        config = SettingsConfig(config_file)

        # Custom value preserved
        assert config.get('output_dir') == '/custom/path'
        # Missing values filled with defaults
        assert config.get('target_process') == 'Le Mans Ultimate'
        assert config.get('poll_interval') == 0.01

    def test_get_all_returns_copy(self, config_file):
        """Should return a copy of all config values"""
        config = SettingsConfig(config_file)
        all_config = config.get_all()

        # Modify returned dict
        all_config['output_dir'] = '/modified'

        # Original should be unchanged
        assert config.get('output_dir') == './telemetry_output'

    def test_hz_to_poll_interval_conversion(self, config_file):
        """Should provide helper to convert Hz to poll interval"""
        config = SettingsConfig(config_file)

        assert config.hz_to_interval(100) == 0.01
        assert config.hz_to_interval(50) == 0.02
        assert config.hz_to_interval(200) == 0.005

    def test_poll_interval_to_hz_conversion(self, config_file):
        """Should provide helper to convert poll interval to Hz"""
        config = SettingsConfig(config_file)

        assert config.interval_to_hz(0.01) == 100
        assert config.interval_to_hz(0.02) == 50
        assert config.interval_to_hz(0.005) == 200
