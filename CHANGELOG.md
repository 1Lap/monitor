# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-20

### Added
- **Opponent Lap Tracking** for multiplayer sessions
  - Automatically captures telemetry from other drivers
  - "Fastest lap only" strategy to control storage (Option 2)
  - Filters by control type (remote players vs AI)
  - Configuration options: `track_opponents`, `track_opponent_ai`
  - OpponentTracker class with 11 unit tests
  - TelemetryReaderInterface.get_all_vehicles() for accessing opponent data
  - Mock and Real implementations for cross-platform development
  - Consistent file naming with player laps: `{date}_{time}_{track}_{car}_{driver}_lap{lap}_t{lap_time}s.csv`

### Changed
- Reorganized `BUGS.md` into `bugs/` folder with separate files:
  - `bugs/capture_opponent_laps.md` - Opponent tracking documentation
  - `bugs/performance_notes.md` - Performance analysis
  - `bugs/future_enhancements.md` - Future feature ideas
  - `bugs/data_quality.md` - Data quality issues and fixes

### Fixed
- Opponent lap filenames now use same format as player laps (includes track and car)

## [0.1.6] - Previous Releases

See git history for earlier changes.
