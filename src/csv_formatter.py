"""CSV formatting to match example.csv format"""

from datetime import datetime
from typing import Dict, Any, List
import io


class CSVFormatter:
    """
    Formats telemetry data into CSV matching example.csv structure

    CSV Structure:
    1. Player metadata line
    2. Lap summary header
    3. Lap summary data
    4. Session metadata header
    5. Session metadata data
    6. Car setup header
    7. Car setup data
    8. Telemetry samples header
    9. Telemetry samples (one row per sample)
    """

    def __init__(self):
        pass

    def format_lap(
        self,
        lap_data: List[Dict[str, Any]],
        lap_summary: Dict[str, Any],
        session_info: Dict[str, Any]
    ) -> str:
        """
        Format a complete lap into CSV format

        Args:
            lap_data: List of telemetry samples for the lap
            lap_summary: Summary data (lap time, sectors, etc.)
            session_info: Session metadata (track, car, etc.)

        Returns:
            CSV string matching example.csv format
        """
        if not lap_data:
            return ""

        # Use first and last samples for reference data
        first_sample = lap_data[0]
        last_sample = lap_data[-1]

        lines = []

        # 1. Player metadata line
        lines.append(self._format_player_metadata(session_info))

        # 2-3. Lap summary
        lines.append(self._format_lap_summary_header())
        lines.append(self._format_lap_summary_data(lap_summary, session_info, first_sample))

        # 4-5. Session metadata
        lines.append(self._format_session_metadata_header())
        lines.append(self._format_session_metadata_data(first_sample, session_info))

        # 6-7. Car setup
        lines.append(self._format_car_setup_header())
        lines.append(self._format_car_setup_data(first_sample))

        # 8. Telemetry samples header
        lines.append(self._format_telemetry_header())

        # 9. Telemetry samples
        for sample in lap_data:
            lines.append(self._format_telemetry_sample(sample))

        return '\n'.join(lines) + '\n'

    def _format_player_metadata(self, session_info: Dict[str, Any]) -> str:
        """Format player metadata line"""
        player_name = session_info.get('player_name', 'Unknown Player')
        session_id = session_info.get('session_id', '')
        version = 'v8'  # Version identifier
        unknown1 = '0'  # Unknown field from example

        return f"player,{version},{player_name},{unknown1},{session_id}"

    def _format_lap_summary_header(self) -> str:
        """Format lap summary header"""
        return "Game,version,date,track,car,event,laptime [s],S1 [s],S2 [s],S3 [s],S4+ [s]"

    def _format_lap_summary_data(
        self,
        lap_summary: Dict[str, Any],
        session_info: Dict[str, Any],
        sample: Dict[str, Any]
    ) -> str:
        """Format lap summary data"""
        game = "LMU"
        version = "0.9"
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        track = session_info.get('track_name', 'Unknown Track')
        car = session_info.get('car_name', 'Unknown Car')
        event = session_info.get('event_type', 'Practice')

        lap_time = lap_summary.get('lap_time', 0.0)
        s1_time = lap_summary.get('sector1_time', 0.0)
        s2_time = lap_summary.get('sector2_time', 0.0)
        s3_time = lap_summary.get('sector3_time', 0.0)
        s4_time = ""  # S4+ is empty in example

        return f"{game},{version},{date},{track},{car},{event},{lap_time},{s1_time},{s2_time},{s3_time},{s4_time}"

    def _format_session_metadata_header(self) -> str:
        """Format session metadata header"""
        return ("TrackID [int],Tracklen [m],EventID [int],EventID2 [int],Weather [txt],"
                "TeamID [int],Tyre [txt],Valid [b],Pitlap [b],Online [b],Lap [int],"
                "LapsInRace [int],Fuel at Start [kg],MaxGears [int],MaxRevs [rpm],"
                "IdleRevs [rpm},TrackTemp [C],AmbientTemp [C],Windspeed [m/s],WindDirection [ ]")

    def _format_session_metadata_data(
        self,
        sample: Dict[str, Any],
        session_info: Dict[str, Any]
    ) -> str:
        """Format session metadata data"""
        track_id = session_info.get('track_id', 0)
        track_len = session_info.get('track_length', 0.0)
        event_id = session_info.get('event_id', 1)
        event_id2 = session_info.get('event_id2', 121)
        weather = session_info.get('weather', 'Clear')
        team_id = session_info.get('team_id', 0)
        tyre = sample.get('tyre_compound', 'Hard')
        valid = str(sample.get('lap_valid', True)).lower()
        pit_lap = str(sample.get('in_pits', False)).lower()
        online = str(session_info.get('online', False)).lower()
        lap = sample.get('lap', 0)
        laps_in_race = session_info.get('laps_in_race', 100)
        fuel_start = sample.get('fuel_remaining', 0.0)
        max_gears = session_info.get('max_gears', 7)
        max_revs = session_info.get('max_revs', 8400.0)
        idle_revs = session_info.get('idle_revs', 1680.0)
        track_temp = sample.get('track_temp', 0.0)
        ambient_temp = sample.get('ambient_temp', 0.0)
        wind_speed = sample.get('wind_speed', 0.0)
        wind_dir = sample.get('wind_direction', 0.0)

        return (f"{track_id},{track_len},{event_id},{event_id2},{weather},{team_id},"
                f"{tyre},{valid},{pit_lap},{online},{lap},{laps_in_race},{fuel_start},"
                f"{max_gears},{max_revs},{idle_revs},{track_temp},{ambient_temp},"
                f"{wind_speed},{wind_dir}")

    def _format_car_setup_header(self) -> str:
        """Format car setup header"""
        return ("FWing,RWing,OnThrottle,OffThrottle,FrontCamber,RearCamber,FrontToe,RearToe,"
                "FrontSusp,RearSusp,FrontAntiRoll,RearAntiRoll,FrontSuspH,RearSuspH,"
                "BrakePressure,BrakeBias,FLTyrePressure,FRTyrePressure,RLTyrePressure,"
                "RRTyrePressure,Ballast,FuelLoad")

    def _format_car_setup_data(self, sample: Dict[str, Any]) -> str:
        """Format car setup data"""
        # Most setup data is 0.0 in the example except brake_bias
        brake_bias = sample.get('brake_bias', 0.0)

        # Build setup string (all zeros except brake_bias)
        setup_values = [
            "0.0",  # FWing
            "0.0",  # RWing
            "0.0",  # OnThrottle
            "0.0",  # OffThrottle
            "0.0",  # FrontCamber
            "0.0",  # RearCamber
            "0.0",  # FrontToe
            "0.0",  # RearToe
            "0.0",  # FrontSusp
            "0.0",  # RearSusp
            "0.0",  # FrontAntiRoll
            "0.0",  # RearAntiRoll
            "0.0",  # FrontSuspH
            "0.0",  # RearSuspH
            "0.0",  # BrakePressure
            str(brake_bias),  # BrakeBias
            "0.0",  # FLTyrePressure
            "0.0",  # FRTyrePressure
            "0.0",  # RLTyrePressure
            "0.0",  # RRTyrePressure
            "0.0",  # Ballast
            "0.0",  # FuelLoad
        ]

        return ','.join(setup_values) + ','

    def _format_telemetry_header(self) -> str:
        """Format telemetry samples header (very long!)"""
        # This is the complete header from example.csv
        return ("LapDistance [m],TotalDistance [m],LapTime [s],Sector1Time [s],Sector2Time [s],"
                "Speed [km/h],EngineRevs [rpm],ThrottlePercentage [%],BrakePercentage [%],"
                "Steer [%],Clutch [%],Gear [int],DRS [0/1],CanUseDRS [0/1],KERSLevel [J],"
                "EngineTemperature [C],RacePosition [int],Sector [int],InPits [int],"
                "FuelRemaining [l],CurrentFlag [int],CurrentLapInvalid [int],X [m],Y [m],Z [m],"
                "GForceLatitudinal [G],GForceLongitudinal [G],GForceVertical [G],"
                "WheelSpeedRearLeft [km/h],WheelSpeedRearRight [km/h],WheelSpeedFrontLeft [km/h],"
                "WheelSpeedFrontRight [km/h],BrakeTemperatureRearLeft [C],"
                "BrakeTemperatureRearRight [C],BrakeTemperatureFrontLeft [C],"
                "BrakeTemperatureFrontRight [C],TyreTemperatureRearLeft [C],"
                "TyreTemperatureRearRight [C],TyreTemperatureFrontLeft [C],"
                "TyreTemperatureFrontRight [C],TyreWearRearLeft [%],TyreWearRearRight [%],"
                "TyreWearFrontLeft [%],TyreWearFrontRight [%],SuspensionPositionRearLeft [m],"
                "SuspensionPositionRearRight [m],SuspensionPositionFrontLeft [m],"
                "SuspensionPositionFrontRight [m],SuspensionVelocityRearLeft [m/s],"
                "SuspensionVelocityRearRight [m/s],SuspensionVelocityFrontLeft [m/s],"
                "SuspensionVelocityFrontRight [m/s],SuspensionAccelerationRearLeft [m/s^2],"
                "SuspensionAccelerationRearRight [m/s^2],SuspensionAccelerationFrontLeft [m/s^2],"
                "SuspensionAccelerationFrontRight [m/s^2],MGUKHarvested [J],MGUHHarvested [J],"
                "ERSSpent [J],ERSMode [int],FuelMixMode [int],Yaw [rad],Roll [rad],Pitch [rad],"
                "TyreCarcassTemperatureRearLeft [C],TyreCarcassTemperatureRearRight [C],"
                "TyreCarcassTemperatureFrontLeft [C],TyreCarcassTemperatureFrontRight [C],"
                "TyrePressureRearLeft [PSI],TyrePressureRearRight [PSI],"
                "TyrePressureFrontLeft [PSI],TyrePressureFrontRight [PSI],"
                "WheelSlipRearLeft [%],WheelSlipRearRight [%],WheelSlipFrontLeft [%],"
                "WheelSlipFrontRight [%],Torque [Nm],Handbrake [%],RearLeftInside [C],"
                "RearLeftMiddle [C],RearLeftOutside [C],RearRightInside [C],RearRightMiddle [C],"
                "RearRightOutside [C],FrontLeftInside [C],FrontLeftMiddle [C],"
                "FrontLeftOutside [C],FrontRightInside [C],FrontRightMiddle [C],"
                "FrontRightOutside [C],WoldSpeedX [km/h],WoldSpeedY [km/h],WoldSpeedZ [km/h],"
                "LocalAngularVelocityX [rad/s],LocalAngularVelocityY [rad/s],"
                "LocalAngularVelocityZ [rad/s],IcePower [W],MgukPower [W],FrontRideHeight [m],"
                "RearRideHeight [m],LoadRearLeft [N],LoadRearRight [N],LoadFrontLeft [N],"
                "LoadFrontRight [N],Extra1 [m],Extra2 [],Extra3 [],Extra4 []")

    def _format_telemetry_sample(self, sample: Dict[str, Any]) -> str:
        """Format a single telemetry sample row"""
        # Extract all required fields with defaults
        values = [
            sample.get('lap_distance', 0.0),
            sample.get('total_distance', 0.0),
            sample.get('lap_time', 0.0),
            sample.get('sector1_time', 0.0),
            sample.get('sector2_time', 0.0),
            sample.get('speed', 0.0),
            sample.get('engine_rpm', 0.0),
            sample.get('throttle', 0.0),
            sample.get('brake', 0.0),
            sample.get('steering', 0.0),
            sample.get('clutch', 0.0),
            sample.get('gear', 0),
            sample.get('drs', 0),
            sample.get('can_use_drs', 0),
            sample.get('ers_level', 0.0),
            sample.get('engine_temp', 0.0),
            sample.get('position', 0),
            sample.get('sector', 0),
            sample.get('in_pits', 0),
            sample.get('fuel_remaining', 0.0),
            sample.get('current_flag', 0),
            sample.get('lap_invalid', 0),
            sample.get('position_x', 0.0),
            sample.get('position_y', 0.0),
            sample.get('position_z', 0.0),
            sample.get('g_force_lat', 0.0),
            sample.get('g_force_lon', 0.0),
            sample.get('g_force_vert', 0.0),
        ]

        # Wheel speeds
        wheel_speed = sample.get('wheel_speed', {})
        values.extend([
            wheel_speed.get('rl', 0.0),
            wheel_speed.get('rr', 0.0),
            wheel_speed.get('fl', 0.0),
            wheel_speed.get('fr', 0.0),
        ])

        # Brake temps
        brake_temp = sample.get('brake_temp', {})
        values.extend([
            brake_temp.get('rl', 0.0),
            brake_temp.get('rr', 0.0),
            brake_temp.get('fl', 0.0),
            brake_temp.get('fr', 0.0),
        ])

        # Tyre temps
        tyre_temp = sample.get('tyre_temp', {})
        values.extend([
            tyre_temp.get('rl', 0.0),
            tyre_temp.get('rr', 0.0),
            tyre_temp.get('fl', 0.0),
            tyre_temp.get('fr', 0.0),
        ])

        # Tyre wear
        tyre_wear = sample.get('tyre_wear', {})
        values.extend([
            tyre_wear.get('rl', 0.0),
            tyre_wear.get('rr', 0.0),
            tyre_wear.get('fl', 0.0),
            tyre_wear.get('fr', 0.0),
        ])

        # Suspension position
        susp_pos = sample.get('suspension_position', {})
        values.extend([
            susp_pos.get('rl', 0.0),
            susp_pos.get('rr', 0.0),
            susp_pos.get('fl', 0.0),
            susp_pos.get('fr', 0.0),
        ])

        # Suspension velocity
        susp_vel = sample.get('suspension_velocity', {})
        values.extend([
            susp_vel.get('rl', 0.0),
            susp_vel.get('rr', 0.0),
            susp_vel.get('fl', 0.0),
            susp_vel.get('fr', 0.0),
        ])

        # Suspension acceleration
        susp_accel = sample.get('suspension_acceleration', {})
        values.extend([
            susp_accel.get('rl', 0.0),
            susp_accel.get('rr', 0.0),
            susp_accel.get('fl', 0.0),
            susp_accel.get('fr', 0.0),
        ])

        # ERS/Hybrid
        values.extend([
            sample.get('mguk_harvested', 0.0),
            sample.get('mguh_harvested', 0.0),
            sample.get('ers_spent', 0.0),
            sample.get('ers_mode', 0),
            sample.get('fuel_mix_mode', 0),
        ])

        # Orientation
        values.extend([
            sample.get('yaw', 0.0),
            sample.get('roll', 0.0),
            sample.get('pitch', 0.0),
        ])

        # Tyre carcass temps
        tyre_carcass = sample.get('tyre_carcass_temp', {})
        values.extend([
            tyre_carcass.get('rl', 0.0),
            tyre_carcass.get('rr', 0.0),
            tyre_carcass.get('fl', 0.0),
            tyre_carcass.get('fr', 0.0),
        ])

        # Tyre pressure
        tyre_pressure = sample.get('tyre_pressure', {})
        values.extend([
            tyre_pressure.get('rl', 0.0),
            tyre_pressure.get('rr', 0.0),
            tyre_pressure.get('fl', 0.0),
            tyre_pressure.get('fr', 0.0),
        ])

        # Wheel slip
        wheel_slip = sample.get('wheel_slip', {})
        values.extend([
            wheel_slip.get('rl', 0.0),
            wheel_slip.get('rr', 0.0),
            wheel_slip.get('fl', 0.0),
            wheel_slip.get('fr', 0.0),
        ])

        # Engine
        values.extend([
            sample.get('torque', 0.0),
            sample.get('handbrake', 0.0),
        ])

        # Tyre surface temps (3 points per tyre)
        tyre_surface = sample.get('tyre_surface_temp', {})
        for pos in ['rl', 'rr', 'fl', 'fr']:
            temps = tyre_surface.get(pos, {})
            values.extend([
                temps.get('inside', 0.0),
                temps.get('middle', 0.0),
                temps.get('outside', 0.0),
            ])

        # World speed
        values.extend([
            sample.get('world_speed_x', 0.0),
            sample.get('world_speed_y', 0.0),
            sample.get('world_speed_z', 0.0),
        ])

        # Angular velocity
        values.extend([
            sample.get('angular_velocity_x', 0.0),
            sample.get('angular_velocity_y', 0.0),
            sample.get('angular_velocity_z', 0.0),
        ])

        # Power
        values.extend([
            sample.get('ice_power', 0.0),
            sample.get('mguk_power', 0.0),
        ])

        # Ride height
        values.extend([
            sample.get('front_ride_height', 0.0),
            sample.get('rear_ride_height', 0.0),
        ])

        # Load
        load = sample.get('load', {})
        values.extend([
            load.get('rl', 0.0),
            load.get('rr', 0.0),
            load.get('fl', 0.0),
            load.get('fr', 0.0),
        ])

        # Extra fields
        values.extend([
            sample.get('extra1', 0.0),
            sample.get('extra2', 0.0),
            sample.get('extra3', 0.0),
            sample.get('extra4', 0.0),
        ])

        # Convert all values to strings and join with commas
        return ','.join(str(v) for v in values)
