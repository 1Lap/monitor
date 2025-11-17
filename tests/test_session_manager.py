"""Tests for session manager"""

import pytest
from src.session_manager import SessionManager, SessionState


class TestSessionManager:
    """Test suite for SessionManager"""

    def test_initial_state_is_idle(self):
        """Session should start in IDLE state"""
        manager = SessionManager()
        assert manager.state == SessionState.IDLE

    def test_detects_lap_change(self):
        """Should detect when lap number changes"""
        manager = SessionManager()

        # First sample - lap 1
        telemetry1 = {'lap': 1, 'speed': 200.0}
        events1 = manager.update(telemetry1)
        assert 'lap_completed' not in events1  # No lap change yet

        # Second sample - still lap 1
        telemetry2 = {'lap': 1, 'speed': 210.0}
        events2 = manager.update(telemetry2)
        assert 'lap_completed' not in events2

        # Third sample - lap 2
        telemetry3 = {'lap': 2, 'speed': 150.0}
        events3 = manager.update(telemetry3)
        assert events3.get('lap_completed') is True

    def test_session_id_generation(self):
        """Should generate unique session IDs"""
        manager = SessionManager()
        id1 = manager.generate_session_id()
        id2 = manager.generate_session_id()

        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0

    def test_lap_buffer_management(self):
        """Should buffer telemetry samples correctly"""
        manager = SessionManager()

        sample1 = {'lap': 1, 'speed': 200.0}
        sample2 = {'lap': 1, 'speed': 210.0}
        sample3 = {'lap': 1, 'speed': 220.0}

        manager.add_sample(sample1)
        manager.add_sample(sample2)
        manager.add_sample(sample3)

        lap_data = manager.get_lap_data()
        assert len(lap_data) == 3
        assert lap_data[0]['speed'] == 200.0
        assert lap_data[2]['speed'] == 220.0

    def test_clear_lap_buffer(self):
        """Should clear buffer correctly"""
        manager = SessionManager()

        manager.add_sample({'lap': 1, 'speed': 200.0})
        manager.add_sample({'lap': 1, 'speed': 210.0})

        assert len(manager.get_lap_data()) == 2

        manager.clear_lap_buffer()

        assert len(manager.get_lap_data()) == 0

    def test_state_transitions(self):
        """Should transition states correctly"""
        manager = SessionManager()

        assert manager.state == SessionState.IDLE

        manager.state = SessionState.DETECTED
        assert manager.state == SessionState.DETECTED

        manager.state = SessionState.LOGGING
        assert manager.state == SessionState.LOGGING

    def test_tracks_current_lap(self):
        """Should track current lap number"""
        manager = SessionManager()

        telemetry = {'lap': 5, 'speed': 200.0}
        manager.update(telemetry)

        assert manager.current_lap == 5
