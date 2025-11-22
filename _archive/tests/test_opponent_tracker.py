"""Tests for OpponentTracker"""

import pytest
from src.opponent_tracker import OpponentTracker, OpponentLapData


# Helper function to create complete telemetry dict with all required fields
def create_telemetry_dict(driver_name='Test Driver', lap=1, lap_distance=100.0,
                          lap_time=5.0, last_lap_time=0.0, speed=150.0, control=2):
    """Create a complete telemetry dictionary for testing"""
    return {
        'driver_name': driver_name,
        'lap': lap,
        'lap_distance': lap_distance,
        'lap_time': lap_time,
        'last_lap_time': last_lap_time,
        'speed': speed,
        'control': control,
        'car_name': f'{driver_name} Team #1',
        'car_model': 'Test Car Model',
        'team_name': f'{driver_name} Team',
        'manufacturer': 'Test Manufacturer',
        'car_class': 'GT3',
    }


class TestOpponentTracker:
    """Test opponent lap tracking"""

    def test_init(self):
        """Test tracker initialization"""
        tracker = OpponentTracker()
        assert tracker.opponents == {}
        assert tracker.track_remote_only is True
        assert tracker.track_ai is False

    def test_init_with_config(self):
        """Test tracker initialization with config"""
        tracker = OpponentTracker(track_remote_only=False, track_ai=True)
        assert tracker.track_remote_only is False
        assert tracker.track_ai is True

    def test_should_track_remote_player(self):
        """Test that remote players are tracked by default"""
        tracker = OpponentTracker()

        # mControl: -1=nobody, 0=local, 1=AI, 2=remote, 3=replay
        assert tracker._should_track(control=2) is True  # Remote
        assert tracker._should_track(control=0) is False  # Local player
        assert tracker._should_track(control=1) is False  # AI (not tracked by default)
        assert tracker._should_track(control=3) is False  # Replay

    def test_should_track_ai_when_enabled(self):
        """Test that AI can be tracked when enabled"""
        tracker = OpponentTracker(track_ai=True, track_remote_only=False)

        assert tracker._should_track(control=2) is True  # Remote
        assert tracker._should_track(control=1) is True  # AI
        assert tracker._should_track(control=0) is False  # Still skip local player

    def test_update_opponent_first_lap(self):
        """Test updating opponent telemetry for first time"""
        tracker = OpponentTracker()

        telemetry = {
            'driver_name': 'John Doe',
            'lap': 1,
            'lap_distance': 100.0,
            'lap_time': 5.0,
            'speed': 150.0,
            'control': 2,  # Remote player
            'car_name': 'Test Team #1',
            'car_model': 'Test Car Model',
            'team_name': 'Test Team',
            'manufacturer': 'Test Manufacturer',
            'car_class': 'GT3',
        }

        completed_laps = tracker.update_opponent(telemetry, timestamp=1.0)

        # First lap, nothing completed yet
        assert completed_laps == []
        assert 'John Doe' in tracker.opponents
        assert tracker.opponents['John Doe']['current_lap'] == 1
        assert len(tracker.opponents['John Doe']['samples']) == 1

    def test_update_opponent_lap_completion(self):
        """Test detecting opponent lap completion"""
        tracker = OpponentTracker()

        # Add samples for lap 1
        for i in range(5):
            telemetry = {
                'driver_name': 'John Doe',
                'lap': 1,
                'lap_distance': 100.0 * i,
                'lap_time': 1.0 * i,
                'speed': 150.0,
                'control': 2,
            }
            completed = tracker.update_opponent(telemetry, timestamp=float(i))
            assert completed == []

        # Lap changes from 1 to 2 - lap 1 is completed
        telemetry = {
            'driver_name': 'John Doe',
            'lap': 2,
            'lap_distance': 10.0,
            'lap_time': 0.5,  # Time into new lap (not used for lap completion)
            'last_lap_time': 125.5,  # Completed lap time (from mLastLapTime)
            'speed': 150.0,
            'control': 2,
        }
        completed = tracker.update_opponent(telemetry, timestamp=6.0)

        assert len(completed) == 1
        lap_data = completed[0]
        assert lap_data.driver_name == 'John Doe'
        assert lap_data.lap_number == 1
        assert lap_data.lap_time == 125.5
        assert len(lap_data.samples) == 5
        assert lap_data.is_fastest is True  # First lap is always fastest

    def test_update_opponent_faster_lap_replaces_slower(self):
        """Test that faster lap replaces slower lap"""
        tracker = OpponentTracker()

        # Complete first lap (slow)
        for i in range(3):
            tracker.update_opponent({
                'driver_name': 'Jane Smith',
                'lap': 1,
                'lap_distance': 100.0 * i,
                'lap_time': 1.0 * i,
                'speed': 150.0,
                'control': 2,
            }, timestamp=float(i))

        completed = tracker.update_opponent({
            'driver_name': 'Jane Smith',
            'lap': 2,
            'lap_distance': 10.0,
            'lap_time': 0.5,  # Time into new lap
            'last_lap_time': 150.0,  # Slow completed lap time
            'speed': 150.0,
            'control': 2,
        }, timestamp=4.0)

        assert len(completed) == 1
        assert completed[0].lap_time == 150.0
        assert completed[0].is_fastest is True

        # Complete second lap (faster)
        for i in range(3):
            tracker.update_opponent({
                'driver_name': 'Jane Smith',
                'lap': 2,
                'lap_distance': 100.0 * i,
                'lap_time': 1.0 * i,
                'speed': 150.0,
                'control': 2,
            }, timestamp=float(5 + i))

        completed = tracker.update_opponent({
            'driver_name': 'Jane Smith',
            'lap': 3,
            'lap_distance': 10.0,
            'lap_time': 0.5,  # Time into new lap
            'last_lap_time': 120.0,  # Faster completed lap time
            'speed': 150.0,
            'control': 2,
        }, timestamp=9.0)

        # Should return the faster lap
        assert len(completed) == 1
        assert completed[0].lap_time == 120.0
        assert completed[0].is_fastest is True

        # Verify fastest lap time is stored
        assert tracker.opponents['Jane Smith']['fastest_lap_time'] == 120.0

    def test_update_opponent_slower_lap_not_returned(self):
        """Test that slower laps are not returned"""
        tracker = OpponentTracker()

        # Complete first lap (fast)
        for i in range(3):
            tracker.update_opponent({
                'driver_name': 'Bob',
                'lap': 1,
                'lap_distance': 100.0 * i,
                'lap_time': 1.0 * i,
                'speed': 150.0,
                'control': 2,
            }, timestamp=float(i))

        completed = tracker.update_opponent({
            'driver_name': 'Bob',
            'lap': 2,
            'lap_distance': 10.0,
            'lap_time': 0.5,  # Time into new lap
            'last_lap_time': 120.0,  # Fast completed lap
            'speed': 150.0,
            'control': 2,
        }, timestamp=4.0)

        assert len(completed) == 1
        assert completed[0].lap_time == 120.0

        # Complete second lap (slower)
        for i in range(3):
            tracker.update_opponent({
                'driver_name': 'Bob',
                'lap': 2,
                'lap_distance': 100.0 * i,
                'lap_time': 1.0 * i,
                'speed': 150.0,
                'control': 2,
            }, timestamp=float(5 + i))

        completed = tracker.update_opponent({
            'driver_name': 'Bob',
            'lap': 3,
            'lap_distance': 10.0,
            'lap_time': 0.5,  # Time into new lap
            'last_lap_time': 140.0,  # Slower completed lap
            'speed': 150.0,
            'control': 2,
        }, timestamp=9.0)

        # Should not return slower lap
        assert completed == []

        # Fastest lap time should still be 120.0
        assert tracker.opponents['Bob']['fastest_lap_time'] == 120.0

    def test_multiple_opponents(self):
        """Test tracking multiple opponents simultaneously"""
        tracker = OpponentTracker()

        # Update two different opponents
        tracker.update_opponent({
            'driver_name': 'Alice',
            'lap': 1,
            'lap_distance': 100.0,
            'lap_time': 5.0,
            'speed': 150.0,
            'control': 2,
        }, timestamp=1.0)

        tracker.update_opponent({
            'driver_name': 'Bob',
            'lap': 1,
            'lap_distance': 200.0,
            'lap_time': 10.0,
            'speed': 160.0,
            'control': 2,
        }, timestamp=2.0)

        assert 'Alice' in tracker.opponents
        assert 'Bob' in tracker.opponents
        # After normalization, field names are in MVP format
        assert tracker.opponents['Alice']['samples'][0]['Speed [km/h]'] == 150.0
        assert tracker.opponents['Bob']['samples'][0]['Speed [km/h]'] == 160.0

    def test_skip_non_tracked_control_types(self):
        """Test that non-tracked control types are skipped"""
        tracker = OpponentTracker()  # Only tracks remote players by default

        # Try to track AI player
        telemetry_ai = {
            'driver_name': 'AI Bot',
            'lap': 1,
            'lap_distance': 100.0,
            'lap_time': 5.0,
            'speed': 150.0,
            'control': 1,  # AI
        }

        completed = tracker.update_opponent(telemetry_ai, timestamp=1.0)

        # Should not track AI
        assert completed == []
        assert 'AI Bot' not in tracker.opponents

    def test_get_opponent_count(self):
        """Test getting count of tracked opponents"""
        tracker = OpponentTracker()

        assert tracker.get_opponent_count() == 0

        tracker.update_opponent({
            'driver_name': 'Alice',
            'lap': 1,
            'lap_distance': 100.0,
            'lap_time': 5.0,
            'speed': 150.0,
            'control': 2,
        }, timestamp=1.0)

        assert tracker.get_opponent_count() == 1

        tracker.update_opponent({
            'driver_name': 'Bob',
            'lap': 1,
            'lap_distance': 100.0,
            'lap_time': 5.0,
            'speed': 150.0,
            'control': 2,
        }, timestamp=2.0)

        assert tracker.get_opponent_count() == 2

    def test_samples_are_normalized(self):
        """Test that opponent samples are normalized to MVP format"""
        tracker = OpponentTracker()

        # Raw telemetry with various fields
        raw_telemetry = {
            'driver_name': 'Test Driver',
            'lap': 1,
            'lap_distance': 1000.0,
            'lap_time': 10.0,
            'speed': 200.0,  # km/h
            'engine_rpm': 7500.0,
            'throttle': 0.85,  # 0-1 range (should become 85%)
            'brake': 0.0,
            'steering': 0.125,  # Should become 12.5%
            'gear': 5,
            'position_x': 123.45,  # Correct field name for normalizer
            'position_z': -101.23,
            'track_length': 5000.0,
            'control': 2,  # Remote player
        }

        tracker.update_opponent(raw_telemetry, timestamp=1.0)

        # Get the stored sample
        assert 'Test Driver' in tracker.opponents
        samples = tracker.opponents['Test Driver']['samples']
        assert len(samples) == 1

        normalized = samples[0]

        # Verify normalized MVP format field names
        assert 'LapDistance [m]' in normalized
        assert 'Speed [km/h]' in normalized
        assert 'EngineRevs [rpm]' in normalized
        assert 'ThrottlePercentage [%]' in normalized
        assert 'BrakePercentage [%]' in normalized
        assert 'Steer [%]' in normalized
        assert 'Gear [int]' in normalized
        assert 'X [m]' in normalized
        assert 'Z [m]' in normalized

        # Verify values are correctly transformed
        assert normalized['LapDistance [m]'] == 1000.0
        assert normalized['Speed [km/h]'] == 200.0
        assert normalized['EngineRevs [rpm]'] == 7500.0
        assert normalized['ThrottlePercentage [%]'] == 85.0  # 0.85 * 100
        assert normalized['BrakePercentage [%]'] == 0.0
        assert normalized['Steer [%]'] == 12.5  # 0.125 * 100
        assert normalized['Gear [int]'] == 5
        assert normalized['X [m]'] == 123.45
        assert normalized['Z [m]'] == -101.23

    def test_partial_lap_discarded_when_joining_mid_race(self):
        """Test that partial laps are discarded when joining mid-race"""
        tracker = OpponentTracker()

        # Join mid-race: opponent is 75% through lap 8
        # We start collecting data from this point
        track_length = 5000.0
        lap_start_threshold = 0.05 * track_length  # 250m

        # Collect samples from 75% onwards (3750m to end)
        for i in range(5):
            telemetry = create_telemetry_dict(
                driver_name='Mid-Race Driver',
                lap=8,
                lap_distance=3750.0 + (i * 50),  # 3750m, 3800m, 3850m, etc.
                lap_time=10.0 + i,
                speed=150.0,
                control=2
            )
            telemetry['track_length'] = track_length
            completed = tracker.update_opponent(telemetry, timestamp=float(i))
            assert completed == []

        # Opponent completes lap 8 and starts lap 9
        telemetry = create_telemetry_dict(
            driver_name='Mid-Race Driver',
            lap=9,
            lap_distance=50.0,  # Just started lap 9
            lap_time=0.5,
            last_lap_time=95.0,  # Lap 8 time
            speed=150.0,
            control=2
        )
        telemetry['track_length'] = track_length
        completed = tracker.update_opponent(telemetry, timestamp=6.0)

        # Partial lap should be discarded (we never saw lap start)
        assert completed == []
        assert tracker.opponents['Mid-Race Driver']['seen_lap_start'] is False
        assert len(tracker.opponents['Mid-Race Driver']['samples']) == 0

        # Now collect full lap 9 from start to finish
        # First pass through lap start
        telemetry = create_telemetry_dict(
            driver_name='Mid-Race Driver',
            lap=9,
            lap_distance=100.0,  # Within lap start threshold (< 250m)
            lap_time=1.0,
            speed=150.0,
            control=2
        )
        telemetry['track_length'] = track_length
        tracker.update_opponent(telemetry, timestamp=7.0)
        assert tracker.opponents['Mid-Race Driver']['seen_lap_start'] is True

        # Continue through lap 9
        for i in range(5):
            telemetry = create_telemetry_dict(
                driver_name='Mid-Race Driver',
                lap=9,
                lap_distance=500.0 + (i * 100),
                lap_time=5.0 + i,
                speed=150.0,
                control=2
            )
            telemetry['track_length'] = track_length
            tracker.update_opponent(telemetry, timestamp=8.0 + i)

        # Complete lap 9
        telemetry = create_telemetry_dict(
            driver_name='Mid-Race Driver',
            lap=10,
            lap_distance=50.0,
            lap_time=0.5,
            last_lap_time=92.0,  # Lap 9 time (faster than lap 8)
            speed=150.0,
            control=2
        )
        telemetry['track_length'] = track_length
        completed = tracker.update_opponent(telemetry, timestamp=14.0)

        # This complete lap SHOULD be saved
        assert len(completed) == 1
        assert completed[0].lap_number == 9
        assert completed[0].lap_time == 92.0
        assert len(completed[0].samples) == 6  # 1 at start + 5 during lap

    def test_lap_number_skip_not_detected(self):
        """Test that lap number jumps (e.g., 1→3) are not detected as lap completion"""
        tracker = OpponentTracker()

        # Complete some samples for lap 1
        for i in range(3):
            telemetry = create_telemetry_dict(
                driver_name='Jumpy Driver',
                lap=1,
                lap_distance=100.0 * i,
                lap_time=1.0 * i,
                speed=150.0,
                control=2
            )
            tracker.update_opponent(telemetry, timestamp=float(i))

        # Lap number jumps from 1 to 3 (skipping 2)
        # This could happen if telemetry is unreliable
        telemetry = create_telemetry_dict(
            driver_name='Jumpy Driver',
            lap=3,  # Jump from 1 to 3
            lap_distance=50.0,
            lap_time=0.5,
            last_lap_time=95.0,
            speed=150.0,
            control=2
        )
        completed = tracker.update_opponent(telemetry, timestamp=4.0)

        # Should NOT detect completion (not exactly +1)
        assert completed == []
        assert tracker.opponents['Jumpy Driver']['current_lap'] == 3

    def test_lap_start_detection_with_various_distances(self):
        """Test that lap start is correctly detected at various distances"""
        tracker = OpponentTracker()
        track_length = 5000.0
        lap_start_threshold = 0.05 * track_length  # 250m

        # Test distances at lap start
        test_cases = [
            (0.0, True),      # Exactly at start line
            (50.0, True),     # Within threshold
            (249.9, True),    # Just inside threshold
            (250.0, False),   # At threshold boundary
            (251.0, False),   # Just outside threshold
            (1000.0, False),  # Mid-lap
            (4500.0, False),  # Near end of lap
        ]

        for distance, should_detect_start in test_cases:
            # Reset tracker for each test
            tracker.reset()

            telemetry = create_telemetry_dict(
                driver_name='Distance Test Driver',
                lap=1,
                lap_distance=distance,
                lap_time=5.0,
                speed=150.0,
                control=2
            )
            telemetry['track_length'] = track_length
            tracker.update_opponent(telemetry, timestamp=1.0)

            assert tracker.opponents['Distance Test Driver']['seen_lap_start'] == should_detect_start, \
                f"Failed for distance {distance}m: expected seen_lap_start={should_detect_start}"
