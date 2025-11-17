# LMU Telemetry Logger

A background telemetry logger for Le Mans Ultimate that automatically captures and exports telemetry data to CSV files.

## Project Status

🚧 **In Development** - Phase 1 Complete (Mock Telemetry System)

### Completed
- ✅ Project structure setup
- ✅ Mock telemetry system for macOS development
- ✅ Platform detection (macOS/Windows)
- ✅ 7/7 unit tests passing

### In Progress
- 🔄 Phase 2: Core logger with auto-detection

## Features (Planned)

- 🎯 **Zero-Config** - Single `.exe` file, no installation required
- 🔄 **Auto-Detection** - Automatically starts/stops with LMU
- 🖥️ **Background Service** - Runs silently in system tray
- 📊 **CSV Export** - Matches standard telemetry format
- 🍎 **Cross-Platform Dev** - Develop on macOS, deploy on Windows

## Development Setup (macOS)

```bash
# Clone repository
git clone <repo-url>
cd telemetry_writer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run tests
pytest -v
```

## Project Structure

```
telemetry_writer/
├── src/
│   ├── telemetry/
│   │   ├── telemetry_interface.py   # Abstract interface
│   │   ├── telemetry_mock.py        # macOS: mock data ✅
│   │   └── telemetry_real.py        # Windows: real data (TODO)
│   └── (more modules coming)
├── tests/
│   └── test_telemetry_mock.py       # 7/7 passing ✅
├── requirements.txt
└── example.csv                       # Reference output format
```

## Documentation

- **[TELEMETRY_LOGGER_PLAN.md](TELEMETRY_LOGGER_PLAN.md)** - High-level plan and architecture
- **[TECHNICAL_SPEC.md](TECHNICAL_SPEC.md)** - Detailed implementation guide
- **[GITHUB_ISSUES.md](GITHUB_ISSUES.md)** - Task breakdown
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - How to use the docs

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_telemetry_mock.py -v
```

Current test coverage: **100%** of implemented modules

## Timeline

- **Days 1-4**: macOS development (mock telemetry) ← **Currently here**
- **Days 5-6**: Windows testing and `.exe` build

## License

TBD

---

**Version**: 1.0.0-dev
**Last Updated**: 2025-01-17
