"""Tests for CSV formatter"""

import pytest
from src.csv_formatter import CSVFormatter


class TestCSVFormatter:
    """Test suite for CSVFormatter"""

    def test_format_lap_returns_string(self):
        """Should return a non-empty string"""
        formatter = CSVFormatter()

        lap_data = [
            {'lap': 1, 'speed': 200.0, 'engine_rpm': 7000.0},
            {'lap': 1, 'speed': 210.0, 'engine_rpm': 7200.0},
        ]

        lap_summary = {
            'lap': 1,
            'lap_time': 90.5,
            'sector1_time': 30.0,
            'sector2_time': 32.0,
            'sector3_time': 28.5,
        }

        session_info = {
            'player_name': 'Test Player',
            'session_id': '20251118120000',
            'track_name': 'Test Track',
            'car_name': 'Test Car',
        }

        result = formatter.format_lap(lap_data, lap_summary, session_info)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_empty_lap_data_returns_empty_string(self):
        """Should return empty string for empty lap data"""
        formatter = CSVFormatter()

        result = formatter.format_lap([], {}, {})
        assert result == ""

    def test_has_player_metadata_line(self):
        """Should include player metadata in first line"""
        formatter = CSVFormatter()

        lap_data = [{'lap': 1, 'speed': 200.0}]
        lap_summary = {'lap': 1, 'lap_time': 90.0}
        session_info = {
            'player_name': 'John Doe',
            'session_id': '12345',
        }

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        assert len(lines) > 0
        assert lines[0].startswith('player,v8,John Doe')
        assert '12345' in lines[0]

    def test_has_lap_summary_section(self):
        """Should include lap summary header and data"""
        formatter = CSVFormatter()

        lap_data = [{'lap': 1, 'speed': 200.0}]
        lap_summary = {
            'lap': 1,
            'lap_time': 112.993,
            'sector1_time': 33.966,
            'sector2_time': 51.070,
            'sector3_time': 27.957,
        }
        session_info = {
            'track_name': 'Bahrain',
            'car_name': 'Toyota GR010',
            'event_type': 'Practice',
        }

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        # Line 2: Header
        assert 'Game,version,date,track,car,event' in lines[1]
        assert 'laptime [s]' in lines[1]

        # Line 3: Data
        assert 'LMU' in lines[2]
        assert 'Bahrain' in lines[2]
        assert 'Toyota GR010' in lines[2]
        assert '112.993' in lines[2]

    def test_has_session_metadata_section(self):
        """Should include session metadata header and data"""
        formatter = CSVFormatter()

        lap_data = [{'lap': 18, 'track_temp': 41.8, 'ambient_temp': 24.0}]
        lap_summary = {'lap': 18}
        session_info = {
            'track_length': 5386.80,
            'track_id': 3,
        }

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        # Line 4: Header
        assert 'TrackID [int],Tracklen [m]' in lines[3]
        assert 'Weather [txt]' in lines[3]

        # Line 5: Data
        assert '5386.80' in lines[4] or '5386.8' in lines[4]
        assert '3,' in lines[4] or lines[4].startswith('3,')

    def test_has_car_setup_section(self):
        """Should include car setup header and data"""
        formatter = CSVFormatter()

        lap_data = [{'lap': 1, 'brake_bias': 43.5}]
        lap_summary = {'lap': 1}
        session_info = {}

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        # Line 6: Header
        assert 'FWing,RWing' in lines[5]
        assert 'BrakeBias' in lines[5]

        # Line 7: Data (mostly zeros except brake_bias)
        assert '43.5' in lines[6]

    def test_has_telemetry_header(self):
        """Should include comprehensive telemetry header"""
        formatter = CSVFormatter()

        lap_data = [{'lap': 1, 'speed': 200.0}]
        lap_summary = {'lap': 1}
        session_info = {}

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        # Line 8: Telemetry header
        header = lines[7]
        assert 'LapDistance [m]' in header
        assert 'Speed [km/h]' in header
        assert 'EngineRevs [rpm]' in header
        assert 'BrakeTemperatureRearLeft [C]' in header
        assert 'TyreTemperatureRearLeft [C]' in header
        assert 'Extra4 []' in header

    def test_has_telemetry_samples(self):
        """Should include telemetry sample rows"""
        formatter = CSVFormatter()

        lap_data = [
            {'lap': 1, 'speed': 200.0, 'engine_rpm': 7000.0, 'lap_distance': 100.5},
            {'lap': 1, 'speed': 210.0, 'engine_rpm': 7200.0, 'lap_distance': 200.8},
            {'lap': 1, 'speed': 220.0, 'engine_rpm': 7400.0, 'lap_distance': 300.2},
        ]
        lap_summary = {'lap': 1}
        session_info = {}

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        # Lines 9+: Telemetry samples
        assert len(lines) >= 11  # 8 header lines + 3 samples

        # Check first sample
        sample1 = lines[8]
        assert '100.5' in sample1
        assert '200.0' in sample1

        # Check second sample
        sample2 = lines[9]
        assert '200.8' in sample2
        assert '210.0' in sample2

    def test_wheel_data_formatted_correctly(self):
        """Should format wheel-specific data (4 wheels)"""
        formatter = CSVFormatter()

        lap_data = [{
            'lap': 1,
            'wheel_speed': {'rl': 250.0, 'rr': 251.0, 'fl': 252.0, 'fr': 253.0},
            'brake_temp': {'rl': 600.0, 'rr': 601.0, 'fl': 470.0, 'fr': 471.0},
            'tyre_temp': {'rl': 70.0, 'rr': 68.0, 'fl': 75.0, 'fr': 66.0},
        }]
        lap_summary = {'lap': 1}
        session_info = {}

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        sample = lines[8]

        # Check wheel speeds are in order: RL, RR, FL, FR
        assert '250.0' in sample
        assert '251.0' in sample
        assert '252.0' in sample
        assert '253.0' in sample

    def test_handles_missing_fields_with_defaults(self):
        """Should use default values for missing fields"""
        formatter = CSVFormatter()

        # Minimal lap data
        lap_data = [{'lap': 1}]
        lap_summary = {'lap': 1}
        session_info = {}

        result = formatter.format_lap(lap_data, lap_summary, session_info)

        # Should not raise errors and should produce valid CSV
        assert isinstance(result, str)
        assert len(result) > 0

        lines = result.strip().split('\n')
        # Should have all required sections
        assert len(lines) >= 9  # 8 headers + at least 1 sample

    def test_multiple_samples_all_included(self):
        """Should include all samples from lap_data"""
        formatter = CSVFormatter()

        # 10 samples
        lap_data = [{'lap': 1, 'speed': 200.0 + i} for i in range(10)]
        lap_summary = {'lap': 1}
        session_info = {}

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        # 8 header lines + 10 sample lines = 18 total
        assert len(lines) == 18

    def test_tyre_surface_temps_formatted(self):
        """Should format 3-point tyre surface temps correctly"""
        formatter = CSVFormatter()

        lap_data = [{
            'lap': 1,
            'tyre_surface_temp': {
                'rl': {'inside': 80.0, 'middle': 81.0, 'outside': 82.0},
                'rr': {'inside': 83.0, 'middle': 84.0, 'outside': 85.0},
                'fl': {'inside': 86.0, 'middle': 87.0, 'outside': 88.0},
                'fr': {'inside': 89.0, 'middle': 90.0, 'outside': 91.0},
            }
        }]
        lap_summary = {'lap': 1}
        session_info = {}

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        sample = lines[8]

        # All 12 values should be present (4 tyres × 3 points)
        for temp in [80.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0, 89.0, 90.0, 91.0]:
            assert str(temp) in sample

    def test_session_id_in_player_metadata(self):
        """Should include session ID in player metadata"""
        formatter = CSVFormatter()

        lap_data = [{'lap': 1}]
        lap_summary = {'lap': 1}
        session_info = {'session_id': '2025111417168338', 'player_name': 'Test'}

        result = formatter.format_lap(lap_data, lap_summary, session_info)
        lines = result.strip().split('\n')

        assert '2025111417168338' in lines[0]
