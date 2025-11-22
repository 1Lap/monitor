# 1Lap Race Dashboard Monitor

Background service that reads LMU telemetry and publishes to dashboard server for real-time team viewing.

## Overview

The **monitor** is one component of the 1Lap Race Dashboard system:

```
┌─────────────┐     WebSocket     ┌─────────────┐     WebSocket     ┌─────────────┐
│   Monitor   │ ──────────────────>│   Server    │ ──────────────────>│  Dashboard  │
│  (Python)   │      2Hz           │   (Flask)   │      Broadcast     │   (Browser) │
└─────────────┘                    └─────────────┘                    └─────────────┘
      ↑                                                                       ↑
      │ Shared Memory                                                         │
      │ + REST API                                                            │
      │                                                                       │
┌─────────────┐                                                     ┌─────────────────┐
│   LMU.exe   │                                                     │  Team Members   │
│  (Windows)  │                                                     │ (any device)    │
└─────────────┘                                                     └─────────────────┘
```

**Purpose:** Read telemetry from Le Mans Ultimate and publish to server so team can monitor car settings, fuel, tire temps, etc. without distracting the driver.

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/1Lap/monitor.git
cd monitor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Windows only (for LMU integration)
pip install -r requirements-windows.txt
```

### Configuration

Create `config.json`:

```json
{
  "server_url": "http://localhost:5000",
  "session_id": "auto",
  "update_rate_hz": 2,
  "poll_interval": 0.01,
  "target_process": "LMU.exe"
}
```

**Configuration Options:**
- `server_url` - Dashboard server URL (local or cloud)
- `session_id` - "auto" to request from server, or specific ID
- `update_rate_hz` - Telemetry publish rate (default: 2Hz)
- `poll_interval` - Telemetry read rate (default: 0.01s = 100Hz)
- `target_process` - Process to monitor (LMU.exe on Windows)

### Running

```bash
# Start monitor (publishes to server)
python monitor.py

# Log-only mode (console output, no server)
python monitor.py --log-only
```

## Features

- **Cross-platform:** Develop on macOS with mocks, deploy on Windows with LMU
- **Real-time telemetry:** Reads from LMU shared memory at 100Hz, publishes at 2Hz
- **Car setup:** Fetches complete setup from LMU REST API
- **Auto-connect:** Detects LMU process, connects to server automatically
- **WebSocket:** Efficient real-time communication with server

## Data Published

### Telemetry (2Hz updates)
- **Session:** Lap, position, lap time, player/car/track names
- **Fuel:** Current fuel, capacity, estimated laps remaining
- **Tires:** Pressures, temperatures, wear (FL/FR/RL/RR)
- **Brakes:** Temperatures (FL/FR/RL/RR)
- **Engine:** Water temperature
- **Weather:** Track temp, ambient temp
- **Driving:** Speed, gear, RPM

### Setup (once per session)
- Suspension (springs, dampers, ARBs, ride height)
- Aerodynamics (wing angles)
- Brakes (bias, balance)
- Gearing (ratios)
- Differential (settings)
- Base tire pressures

## Development

### Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_dashboard_publisher.py -v
```

### Architecture

**Components:**
- `src/telemetry/` - Telemetry reading (mock + real)
- `src/process_monitor.py` - LMU process detection
- `src/lmu_rest_api.py` - REST API client for setup
- `src/dashboard_publisher.py` - WebSocket publisher
- `monitor.py` - Main entry point

**Design Principles:**
- Test-Driven Development (TDD)
- Cross-platform compatibility
- Simple configuration
- Minimal dependencies

See `.claude/CLAUDE.md` for detailed development instructions.

## Project Structure

```
monitor/
├── src/
│   ├── telemetry/              # Telemetry reading (interface + implementations)
│   ├── process_monitor.py      # Process detection
│   ├── lmu_rest_api.py         # REST API client
│   └── dashboard_publisher.py  # WebSocket publisher
├── tests/                      # Unit and integration tests
├── bugs/                       # Task breakdown and feature requests
├── _archive/                   # Archived writer project code (reference)
├── monitor.py                  # Main entry point
├── config.json                 # Configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Related Projects

- **[server](https://github.com/1Lap/server)** - Dashboard web service
- **[RACE_DASHBOARD_PLAN.md](RACE_DASHBOARD_PLAN.md)** - Complete 3-repo system plan

## Requirements

- **Python:** 3.8+
- **LMU:** Le Mans Ultimate (Windows only)
- **Network:** Access to dashboard server

## Deployment

### Local Network
1. Run server on driver's PC
2. Run monitor on same PC
3. Team connects via LAN: `http://<ip>:5000/dashboard/<session-id>`

### Cloud Hosted
1. Deploy server to cloud (Heroku, Railway, etc.)
2. Run monitor on driver's PC
3. Team connects from anywhere: `https://dashboard.1lap.io/<session-id>`

See [RACE_DASHBOARD_PLAN.md](RACE_DASHBOARD_PLAN.md) for deployment details.

## Troubleshooting

### Monitor not detecting LMU
- **Windows:** Ensure LMU.exe is running
- **macOS:** Change `target_process` to a running process for testing

### Can't connect to server
- Check server is running: `curl http://localhost:5000`
- Verify `server_url` in config.json
- Check firewall settings

### REST API not available
- Verify LMU REST API is enabled (localhost:6397)
- Check LMU settings for API configuration

### Tests failing
- Activate virtual environment
- Install all dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
- Run `pytest -v` to see detailed error messages

## Contributing

See `bugs/MVP_MONITOR_TASKS.md` for current development tasks.

Development workflow:
1. Read `.claude/CLAUDE.md` for context
2. Pick a task from `bugs/`
3. Write tests first (TDD)
4. Implement feature
5. All tests must pass
6. Submit pull request

## License

See LICENSE file.

## Support

- **GitHub Issues:** [1Lap/monitor/issues](https://github.com/1Lap/monitor/issues)
- **Documentation:** [RACE_DASHBOARD_PLAN.md](RACE_DASHBOARD_PLAN.md)

---

**Note:** This project was forked from the `writer` telemetry logger. Old writer code is archived in `_archive/` for reference. The monitor is simpler: it publishes to a server instead of writing CSV files.
