"""Tests for process monitor"""

import pytest
from src.process_monitor import ProcessMonitor


class TestProcessMonitor:
    """Test suite for ProcessMonitor"""

    def test_detects_running_process(self):
        """Should detect a known running process"""
        # Use Python itself as test target (we know it's running)
        monitor = ProcessMonitor({'target_process': 'python'})
        assert monitor.is_running() is True

    def test_does_not_detect_fake_process(self):
        """Should not detect a non-existent process"""
        monitor = ProcessMonitor({'target_process': 'definitely_not_a_real_process_name_xyz123'})
        assert monitor.is_running() is False

    def test_case_insensitive_detection(self):
        """Process detection should be case-insensitive"""
        monitor = ProcessMonitor({'target_process': 'PYTHON'})
        # Should still detect python (lowercase) process
        assert monitor.is_running() is True

    def test_partial_name_matching(self):
        """Should match partial process names"""
        # Test with partial name - 'python' should match 'python3.14' etc.
        monitor = ProcessMonitor({'target_process': 'py'})
        assert monitor.is_running() is True

    def test_default_target_process(self):
        """Should have default target process"""
        monitor = ProcessMonitor({})
        # Default should be LMU.exe
        assert monitor.target_process == 'LMU.exe'
