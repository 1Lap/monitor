"""
1Lap Race Dashboard Monitor

Reads LMU telemetry and publishes to dashboard server via WebSocket.
"""
import json
import time
import signal
import sys
import argparse
from pathlib import Path
from datetime import datetime

from src.telemetry.telemetry_interface import get_telemetry_reader
from src.lmu_rest_api import LMURestAPI
from src.process_monitor import ProcessMonitor
from src.dashboard_publisher import DashboardPublisher


def log_telemetry(data: dict):
    """
    Pretty-print telemetry to console

    Args:
        data: Telemetry dictionary
    """
    print("\n" + "=" * 60)
    print(f"Telemetry @ {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    # Session info
    print(f"Driver: {data.get('player_name', 'N/A')}")
    print(f"Car: {data.get('car_name', 'N/A')}")
    print(f"Track: {data.get('track_name', 'N/A')}")
    print(f"Session: {data.get('session_type', 'N/A')}")
    print()

    # Position & lap
    print(f"Position: P{data.get('race_position', 0)} | Lap: {data.get('lap', 0)}")
    print(f"Lap Time: {data.get('lap_time', 0.0):.3f}s")
    print()

    # Fuel
    fuel = data.get('fuel_remaining', 0.0)
    fuel_cap = data.get('fuel_at_start', 90.0)
    fuel_pct = (fuel / fuel_cap * 100) if fuel_cap > 0 else 0
    print(f"Fuel: {fuel:.1f}L / {fuel_cap:.1f}L ({fuel_pct:.0f}%)")
    print()

    # Tires
    tire_psi = data.get('tyre_pressure', {})
    tire_temp = data.get('tyre_temp', {})
    print("Tires:")
    print(f"  FL: {tire_psi.get('fl', 0):.1f} PSI, {tire_temp.get('fl', 0):.1f}°C")
    print(f"  FR: {tire_psi.get('fr', 0):.1f} PSI, {tire_temp.get('fr', 0):.1f}°C")
    print(f"  RL: {tire_psi.get('rl', 0):.1f} PSI, {tire_temp.get('rl', 0):.1f}°C")
    print(f"  RR: {tire_psi.get('rr', 0):.1f} PSI, {tire_temp.get('rr', 0):.1f}°C")
    print()

    # Brakes
    brake_temp = data.get('brake_temp', {})
    print("Brakes:")
    print(f"  FL: {brake_temp.get('fl', 0):.0f}°C | FR: {brake_temp.get('fr', 0):.0f}°C")
    print(f"  RL: {brake_temp.get('rl', 0):.0f}°C | RR: {brake_temp.get('rr', 0):.0f}°C")
    print()

    # Engine & weather
    print(f"Engine: {data.get('engine_temp', 0):.1f}°C")
    print(f"Track: {data.get('track_temp', 0):.1f}°C | Ambient: {data.get('ambient_temp', 0):.1f}°C")
    print()

    # Speed/gear
    print(f"Speed: {data.get('speed', 0):.0f} km/h | Gear: {data.get('gear', 0)} | RPM: {data.get('rpm', 0):.0f}")


class Monitor:
    """Main monitor application"""

    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize monitor

        Args:
            config_path: Path to config.json
        """
        self.config = self._load_config(config_path)
        self.running = False
        self.setup_sent = False

        # Initialize components
        self.telemetry = get_telemetry_reader()
        self.rest_api = LMURestAPI()
        self.process_monitor = ProcessMonitor({
            'target_process': self.config['target_process']
        })
        self.publisher = DashboardPublisher(
            server_url=self.config['server_url'],
            session_id=self.config.get('session_id', 'auto')
        )

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path) as f:
                config = json.load(f)
            print(f"[Monitor] Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            print(f"[Monitor] ERROR: Config file not found: {config_path}")
            print("[Monitor] Creating default config.json...")
            self._create_default_config(config_path)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[Monitor] ERROR: Invalid JSON in config: {e}")
            sys.exit(1)

    def _create_default_config(self, config_path: str):
        """Create default config.json"""
        default_config = {
            "server_url": "http://localhost:5000",
            "session_id": "auto",
            "update_rate_hz": 2,
            "poll_interval": 0.01,
            "target_process": "LMU.exe"
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print(f"[Monitor] Default config created: {config_path}")
        print("[Monitor] Edit config.json and run again")

    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        print("\n[Monitor] Shutdown signal received")
        self.stop()

    def start(self):
        """Start monitor"""
        print("=" * 60)
        print("1Lap Race Dashboard Monitor")
        print("=" * 60)
        print(f"Server: {self.config['server_url']}")
        print(f"Update rate: {self.config['update_rate_hz']} Hz")
        print(f"Target process: {self.config['target_process']}")
        print("=" * 60)

        # Connect to server
        print("[Monitor] Connecting to dashboard server...")
        if not self.publisher.connect():
            print("[Monitor] ERROR: Failed to connect to server")
            print("[Monitor] Make sure server is running")
            return

        # Wait for session ID
        print("[Monitor] Waiting for session ID...")
        timeout = 10
        start_time = time.time()
        while not self.publisher.is_ready():
            if time.time() - start_time > timeout:
                print("[Monitor] ERROR: Timeout waiting for session ID")
                return
            time.sleep(0.1)

        print("[Monitor] Ready!")
        print("=" * 60)

        # Main loop
        self.running = True
        update_interval = 1.0 / self.config['update_rate_hz']
        last_update = 0

        try:
            while self.running:
                # Check if LMU is running
                if not self.process_monitor.is_running():
                    if self.setup_sent:
                        print("[Monitor] LMU process stopped")
                        self.setup_sent = False
                    time.sleep(1)
                    continue

                # LMU detected - send setup once
                if not self.setup_sent:
                    print("[Monitor] LMU detected, fetching setup...")
                    self._send_setup()

                # Publish telemetry at configured rate
                current_time = time.time()
                if current_time - last_update >= update_interval:
                    self._send_telemetry()
                    last_update = current_time

                # Sleep briefly to avoid busy loop
                time.sleep(self.config['poll_interval'])

        except Exception as e:
            print(f"[Monitor] ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()

    def start_logging_mode(self):
        """Start monitor in logging mode (no server connection)"""
        print("=" * 60)
        print("1Lap Race Dashboard Monitor - LOGGING MODE")
        print("=" * 60)
        print(f"Update rate: {self.config['update_rate_hz']} Hz")
        print(f"Target process: {self.config['target_process']}")
        print("=" * 60)
        print("Waiting for LMU...")

        self.running = True
        update_interval = 1.0 / self.config['update_rate_hz']
        last_update = 0

        try:
            while self.running:
                # Check if LMU is running
                if not self.process_monitor.is_running():
                    time.sleep(1)
                    continue

                # Log telemetry at configured rate
                current_time = time.time()
                if current_time - last_update >= update_interval:
                    if self.telemetry.is_available():
                        data = self.telemetry.read()
                        if data:
                            log_telemetry(data)
                    last_update = current_time

                time.sleep(self.config['poll_interval'])

        except KeyboardInterrupt:
            print("\n[Monitor] Stopped")

    def _send_setup(self):
        """Fetch and send setup data"""
        if not self.rest_api.is_available():
            print("[Monitor] REST API not available, skipping setup")
            self.setup_sent = True  # Don't keep trying
            return

        setup = self.rest_api.fetch_setup_data()
        if setup:
            self.publisher.publish_setup(setup)
            print("[Monitor] Setup data sent")
            self.setup_sent = True
        else:
            print("[Monitor] No setup data available")
            self.setup_sent = True  # Don't keep trying

    def _send_telemetry(self):
        """Read and send telemetry data"""
        if not self.telemetry.is_available():
            return

        data = self.telemetry.read()
        if data:
            self.publisher.publish_telemetry(data)

    def stop(self):
        """Stop monitor"""
        print("[Monitor] Stopping...")
        self.running = False
        self.publisher.disconnect()
        print("[Monitor] Stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='1Lap Race Dashboard Monitor')
    parser.add_argument('--log-only', action='store_true',
                        help='Log telemetry to console instead of publishing to server')
    parser.add_argument('--config', default='config.json',
                        help='Path to config file (default: config.json)')
    args = parser.parse_args()

    monitor = Monitor(args.config)

    if args.log_only:
        monitor.start_logging_mode()
    else:
        monitor.start()


if __name__ == '__main__':
    main()
