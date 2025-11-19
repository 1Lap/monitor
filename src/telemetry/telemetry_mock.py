"""Mock telemetry reader for macOS development"""

import time
import math
from datetime import datetime
from typing import Dict, Any
from .telemetry_interface import TelemetryReaderInterface


class MockTelemetryReader(TelemetryReaderInterface):
    """
    Mock telemetry for development without LMU

    Simulates realistic telemetry data that changes over time,
    including lap progression, speed variation, and complete lap cycles.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        # Use perf_counter for high-resolution timing so rapid successive
        # calls (like unit tests) still see forward progress on platforms
        # with coarse wall-clock resolution.
        self.start_time = time.perf_counter()
        self.lap = 1
        self.lap_start_time = self.start_time

        # Default to Bahrain reference lap from telemetry_format_analysis.md
        self.track_name = "Bahrain International Circuit"
        self.track_length = 5386.80  # meters
        self.player_name = "Dev User"
        self.car_name = "Toyota GR010"

    def is_available(self) -> bool:
        """Mock is always available"""
        return True

    def get_session_info(self) -> Dict[str, Any]:
        """Return session metadata"""
        return {
            'player_name': self.player_name,
            'track_name': self.track_name,
            'car_name': self.car_name,
            'session_type': 'Practice',
            'game_version': '0.9',
            'date': datetime.now(),
            'track_id': 3,
            'track_length': self.track_length,
        }

    def read(self) -> Dict[str, Any]:
        """
        Return mock telemetry matching rF2 structure

        Simulates a car driving around the track with realistic values:
        - Speed varies (slower in corners, faster on straights)
        - Lap distance increments based on time
        - Lap completion triggers when lap distance resets
        - All fields required by the MVP CSV schema are populated
        """
        now = time.perf_counter()
        elapsed = now - self.lap_start_time
        total_elapsed = now - self.start_time

        # Simulate car progressing around track (~70m/s average speed)
        raw_distance = elapsed * 70
        lap_distance = raw_distance % self.track_length
        total_distance = 91576.37 + (total_elapsed * 70)

        # Check for lap completion (when we've completed a full lap)
        if raw_distance >= self.track_length and elapsed > 0.5:
            self.lap += 1
            self.lap_start_time = time.perf_counter()
            elapsed = 0
            raw_distance = 0
            lap_distance = 0

        # Simulate speed variation (slower in corners, faster on straights)
        # Use sine wave based on position around track
        speed_variation = math.sin(lap_distance / 1000) * 20
        speed = 256 + speed_variation  # km/h

        # Calculate sector index (0,1,2)
        sector_index = min(2, int((lap_distance / self.track_length) * 3))

        # Simulate RPM based on speed
        rpm = 7267 + (speed_variation * 10)

        # Simulate throttle/brake based on speed
        throttle = 100.0 if speed > 200 else 55.0
        brake = 8.0 if speed < 180 else 0.0

        # Simulate position (moving around track)
        angle = (lap_distance / self.track_length) * 2 * math.pi
        position_x = -269.26 + (1000 * math.cos(angle))
        position_z = -218.97 + (1000 * math.sin(angle))

        # Return complete telemetry dictionary
        return {
            # Player/Session Info
            'player_name': self.player_name,
            'track_name': self.track_name,
            'car_name': self.car_name,
            'session_type': 'Practice',
            'game_version': '0.9',
            'date': datetime.now(),

            # Lap Info
            'lap': self.lap,
            'lap_distance': lap_distance,
            'total_distance': total_distance,
            'lap_time': elapsed,
            'sector_index': sector_index,
            'sector1_time': 0.0 if sector_index < 1 else 33.966,
            'sector2_time': 0.0 if sector_index < 2 else 51.070,
            'sector3_time': 0.0,

            # Track Info
            'track_id': 3,
            'track_length': self.track_length,
            'track_temp': 41.80,
            'ambient_temp': 24.02,
            'weather': 'Clear',
            'wind_speed': 0.0,
            'wind_direction': 0.0,

            # Car State
            'speed': speed,
            'rpm': rpm,
            'gear': 6,
            'throttle': throttle,
            'brake': brake,
            'steering': math.sin(elapsed) * 35.0,  # Percent steering input
            'clutch': 0.0,
            'drs': 0,

            # Position
            'position_x': position_x,
            'position_y': 7.30,
            'position_z': position_z,
            'yaw': angle,
            'pitch': -0.002,
            'roll': 0.026,

            # Physics
            'g_force_lateral': -0.065 + (math.sin(elapsed) * 0.1),
            'g_force_longitudinal': 0.340 + (speed_variation * 0.01),
            'g_force_vertical': 0.092,

            # Wheels (RL, RR, FL, FR)
            'wheel_speed': {
                'rl': speed + 0.2,
                'rr': speed - 0.2,
                'fl': speed + 0.3,
                'fr': speed - 0.1
            },
            'tyre_temp': {
                'rl': 70.78,
                'rr': 68.89,
                'fl': 75.57,
                'fr': 66.94
            },
            'tyre_pressure': {
                'rl': 23.95,
                'rr': 23.63,
                'fl': 24.20,
                'fr': 23.32
            },
            'tyre_wear': {
                'rl': 14.35,
                'rr': 13.10,
                'fl': 15.83,
                'fr': 11.88
            },
            'brake_temp': {
                'rl': 611.19,
                'rr': 611.50,
                'fl': 474.79,
                'fr': 475.18
            },
            'suspension_position': {
                'rl': 0.018,
                'rr': 0.017,
                'fl': 0.009,
                'fr': 0.009
            },
            'suspension_velocity': {
                'rl': -16.43,
                'rr': -8.83,
                'fl': -1.06,
                'fr': 25.71
            },

            # Hybrid/ERS (for LMH cars)
            'ers_level': 453702.47,
            'mguk_harvested': 0.0,
            'mguh_harvested': 0.0,
            'ers_spent': 0.0,
            'ers_mode': 2,

            # Engine
            'engine_temp': 109.15,
            'fuel_remaining': 40.30,
            'fuel_mix_mode': 0,

            # Car Setup
            'front_wing': 0.0,
            'rear_wing': 0.0,
            'brake_bias': 43.5,

            # Session State
            'race_position': 6,
            'in_pits': False,
            'current_flag': 0,
            'lap_invalid': False,

            # Event details
            'event_id': 1,
            'event_id2': 121,
            'team_id': 6,
            'tyre_compound': 'Hard',
            'laps_in_race': 101,
            'fuel_at_start': 40.30,
            'max_gears': 7,
            'max_revs': 8400.0,
            'idle_revs': 1680.0,
        }

    def get_all_vehicles(self) -> list[Dict[str, Any]]:
        """
        Return mock opponent data for testing multiplayer features

        Returns list of 2-3 mock opponents with telemetry data
        """
        now = time.perf_counter()
        elapsed = now - self.lap_start_time

        opponents = []

        # Opponent 1: Remote player, slightly behind
        lap1_time_offset = 2.5  # 2.5 seconds behind player
        lap1_elapsed = max(0, elapsed - lap1_time_offset)
        lap1_distance = (lap1_elapsed * 70) % self.track_length
        lap1_speed = 250 + math.sin(lap1_distance / 1000) * 25

        opponents.append({
            'driver_name': 'Alice Johnson',
            'car_name': 'Ferrari 499P',
            'control': 2,  # Remote player
            'position': 4,
            'lap': self.lap if lap1_elapsed > 0 else self.lap - 1,
            'lap_distance': lap1_distance,
            'lap_time': lap1_elapsed,
            'speed': lap1_speed,
            'rpm': 7100 + (lap1_speed - 250) * 10,
            'gear': 6,
            'throttle': 95.0 if lap1_speed > 200 else 50.0,
            'brake': 10.0 if lap1_speed < 180 else 0.0,
            'steering': math.sin(lap1_elapsed) * 30.0,
            'position_x': -269.26 + (1000 * math.cos(lap1_distance / self.track_length * 2 * math.pi)),
            'position_y': 7.30,
            'position_z': -218.97 + (1000 * math.sin(lap1_distance / self.track_length * 2 * math.pi)),
            'track_length': self.track_length,
        })

        # Opponent 2: Remote player, ahead of player
        lap2_time_offset = -3.2  # 3.2 seconds ahead of player
        lap2_elapsed = elapsed - lap2_time_offset
        lap2_distance = (lap2_elapsed * 72) % self.track_length
        lap2_speed = 265 + math.sin(lap2_distance / 1000) * 22
        lap2_lap = self.lap if lap2_elapsed >= 0 else self.lap + 1

        opponents.append({
            'driver_name': 'Bob Martinez',
            'car_name': 'Porsche 963',
            'control': 2,  # Remote player
            'position': 2,
            'lap': lap2_lap,
            'lap_distance': lap2_distance,
            'lap_time': lap2_elapsed if lap2_elapsed > 0 else 0,
            'speed': lap2_speed,
            'rpm': 7300 + (lap2_speed - 265) * 10,
            'gear': 7,
            'throttle': 98.0 if lap2_speed > 200 else 48.0,
            'brake': 5.0 if lap2_speed < 180 else 0.0,
            'steering': math.sin(lap2_elapsed) * 28.0,
            'position_x': -269.26 + (1000 * math.cos(lap2_distance / self.track_length * 2 * math.pi)),
            'position_y': 7.30,
            'position_z': -218.97 + (1000 * math.sin(lap2_distance / self.track_length * 2 * math.pi)),
            'track_length': self.track_length,
        })

        # Opponent 3: AI player (to test filtering)
        lap3_time_offset = 5.0  # 5 seconds behind
        lap3_elapsed = max(0, elapsed - lap3_time_offset)
        lap3_distance = (lap3_elapsed * 68) % self.track_length
        lap3_speed = 245 + math.sin(lap3_distance / 1000) * 20

        opponents.append({
            'driver_name': 'AI Driver',
            'car_name': 'Cadillac V-Series.R',
            'control': 1,  # AI
            'position': 8,
            'lap': self.lap if lap3_elapsed > 0 else self.lap - 1,
            'lap_distance': lap3_distance,
            'lap_time': lap3_elapsed,
            'speed': lap3_speed,
            'rpm': 7000 + (lap3_speed - 245) * 10,
            'gear': 6,
            'throttle': 92.0 if lap3_speed > 200 else 52.0,
            'brake': 12.0 if lap3_speed < 180 else 0.0,
            'steering': math.sin(lap3_elapsed) * 32.0,
            'position_x': -269.26 + (1000 * math.cos(lap3_distance / self.track_length * 2 * math.pi)),
            'position_y': 7.30,
            'position_z': -218.97 + (1000 * math.sin(lap3_distance / self.track_length * 2 * math.pi)),
            'track_length': self.track_length,
        })

        return opponents
