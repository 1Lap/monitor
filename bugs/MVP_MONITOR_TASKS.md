# Monitor Component - MVP Implementation Tasks

**Project:** 1Lap Race Dashboard - Monitor Component
**Phase:** MVP - Phase 1
**Status:** ✅ MVP 100% COMPLETE (2025-11-22) - Server Integration Verified

**Progress:** 12/12 tasks complete (100%)

---

## Overview

This document provides a roadmap for implementing the monitor component of the 1Lap Race Dashboard system. The monitor reads LMU telemetry and publishes to the dashboard server.

See `RACE_DASHBOARD_PLAN.md` for complete architecture and plan.

---

## Task Categories

### 🔍 Phase 1: API Exploration & Validation (4-6 hours)

**Goal:** Understand what data is available from LMU APIs

1. **[api_exploration_shared_memory.md](api_exploration_shared_memory.md)**
   - Priority: High
   - Time: 1-2 hours
   - Create test script to explore shared memory fields
   - Validate telemetry data structure
   - Document available fields
   - **Requires:** Windows + LMU running

2. **[api_exploration_rest_api.md](api_exploration_rest_api.md)**
   - Priority: High
   - Time: 1-2 hours
   - Create test script to explore REST API endpoints
   - Validate setup data structure
   - Document response formats
   - **Requires:** Windows + LMU running

3. **[dashboard_data_requirements.md](dashboard_data_requirements.md)**
   - Priority: High
   - Time: 1 hour
   - Define dashboard data needs
   - Map fields from APIs to dashboard
   - Create field specification document
   - **Depends on:** API exploration tasks

---

### 🛠️ Phase 2: Core Implementation (8-12 hours)

**Goal:** Build core monitor components

4. **[cleanup_writer_components.md](cleanup_writer_components.md)**
   - Priority: Medium
   - Time: 1-2 hours
   - Remove unneeded writer components
   - Clean up repository
   - Update dependencies
   - **Do first:** Before implementing new components

5. **[simplify_session_tracking.md](simplify_session_tracking.md)**
   - Priority: Medium
   - Time: 1-2 hours
   - Remove/simplify SessionManager
   - Implement simple setup tracking
   - **Depends on:** Cleanup task

6. **[implement_dashboard_publisher.md](implement_dashboard_publisher.md)**
   - Priority: High
   - Time: 3-4 hours
   - Implement DashboardPublisher class
   - WebSocket communication
   - Setup and telemetry publishing
   - Write comprehensive tests
   - **Core component**

7. **[create_monitor_entry_point.md](create_monitor_entry_point.md)**
   - Priority: High
   - Time: 2-3 hours
   - Create monitor.py entry point
   - Configuration system (config.json)
   - Main loop orchestration
   - Error handling
   - **Depends on:** DashboardPublisher

---

### 🧪 Phase 3: Testing & Debugging (4-6 hours)

**Goal:** Validate monitor works end-to-end

8. **[basic_telemetry_logging.md](basic_telemetry_logging.md)**
   - Priority: Medium
   - Time: 1 hour
   - Add --log-only mode
   - Console telemetry logging
   - Development/debugging tool
   - **Useful for:** Testing without server

9. **[test_server_connection.md](test_server_connection.md)**
   - Priority: Low
   - Time: 30 minutes
   - Create server connection test script
   - Validate WebSocket communication
   - Pre-flight checks
   - **Useful for:** Server integration testing

10. **[integration_testing.md](integration_testing.md)**
    - Priority: High
    - Time: 2-3 hours
    - Write integration tests
    - End-to-end testing
    - Manual testing checklist
    - Performance validation
    - **Final validation**

---

## Recommended Implementation Order

### Week 1: Foundation (if working full-time on this)

**Days 1-2: Exploration**
1. ✅ Read RACE_DASHBOARD_PLAN.md
2. ✅ Run `api_exploration_shared_memory.md` (Windows testing complete)
3. ✅ Run `api_exploration_rest_api.md` (Windows testing complete)
4. ✅ Complete `dashboard_data_requirements.md`

**Days 3-4: Cleanup & Setup**
5. ✅ Complete `cleanup_writer_components.md` (Repository already clean)
6. ✅ Complete `simplify_session_tracking.md` (No SessionManager exists)
7. ✅ Set up development environment

**Days 5-7: Core Implementation**
8. ✅ Complete `implement_dashboard_publisher.md` (2025-11-22)
9. ✅ Complete `create_monitor_entry_point.md` (2025-11-22)
10. ✅ Complete `basic_telemetry_logging.md` (2025-11-22)

### Week 2: Testing & Integration

**Days 8-9: Testing**
11. ✅ Complete `test_server_connection.md` (2025-11-22)
12. ✅ Complete `integration_testing.md` (2025-11-22)

**Days 10-12: Integration with Server**
13. ✅ Test with server (2025-11-22)
14. ✅ Bug fixes and refinements (field mappings, process detection)
15. ✅ Documentation updates (complete)

---

## Success Criteria

### MVP Complete When:

- ✅ All core components implemented (DashboardPublisher, Monitor)
- ✅ Monitor connects to server (WebSocket client working)
- ✅ Telemetry published at 2Hz (configurable, verified)
- ✅ Setup data published once per session (REST API integration, verified)
- ✅ All tests passing (51/51 tests)
- ✅ Manual testing checklist complete (server + Windows tested)
- ✅ Works on Windows with LMU (Windows testing complete)
- ✅ Works on macOS with mock data (verified)
- ✅ Documentation updated (bug files marked complete)

---

## Dependencies

### External Dependencies

- **LMU (Windows):** Required for API exploration and final testing
- **Server:** Required for end-to-end testing (can develop in parallel)
- **Network:** For cloud server testing (optional)

### Python Dependencies

```txt
pyRfactor2SharedMemory>=0.1.0  # Windows only
psutil>=5.9.0                   # Process monitoring
python-socketio[client]>=5.9.0  # WebSocket client
requests>=2.28.0                # REST API client
pytest>=7.0.0                   # Testing
pytest-cov>=3.0.0               # Coverage
```

---

## Parallel Development

Tasks that can be done **without LMU/Windows:**

1. ✅ Repository cleanup
2. ✅ DashboardPublisher implementation
3. ✅ Monitor.py entry point
4. ✅ Logging mode
5. ✅ Unit tests (with mocks)
6. ✅ Server connection test script

Tasks that **require Windows + LMU:**

1. ✅ API exploration (shared memory)
2. ✅ API exploration (REST API)
3. ✅ Final integration testing
4. ⏳ Performance validation (extended runs - optional enhancement)

**Strategy:** Implement core components on macOS with mocks, then validate on Windows with LMU.

---

## Communication with Server Team

The monitor publishes these WebSocket events:

### Events: Monitor → Server

1. **`request_session_id`** - Request new session
2. **`setup_data`** - Publish car setup (once per session)
3. **`telemetry_update`** - Publish telemetry (2Hz)

### Events: Server → Monitor

1. **`session_id_assigned`** - Receive session ID

See `RACE_DASHBOARD_PLAN.md` section "API Contracts" for complete payloads.

---

## Testing Strategy

### Unit Tests (Existing)
- ✅ `test_telemetry_mock.py` (7 tests)
- ✅ `test_telemetry_real.py` (2 tests)
- ✅ `test_process_monitor.py` (5 tests)
- ✅ `test_lmu_rest_api.py` (existing)

### Unit Tests (New)
- ⬜ `test_dashboard_publisher.py` (8+ tests)
- ⬜ `test_monitor_integration.py` (10+ tests)

### Manual Testing
- ⬜ See `integration_testing.md` for checklist

### Performance Testing
- ⬜ Update rate: 2Hz ± 10%
- ⬜ Memory: < 100MB
- ⬜ CPU: < 5%

---

## Risk Mitigation

### Risk 1: API Not Available on Windows
**Mitigation:** API exploration tasks validate this first

### Risk 2: Server Not Ready
**Mitigation:** Logging mode allows development without server

### Risk 3: Network Issues
**Mitigation:** Reconnection logic, local server option

### Risk 4: Performance Issues
**Mitigation:** Configurable update rate, performance tests

---

## Documentation

### Files to Update

- ⬜ `README.md` - Monitor-specific documentation
- ⬜ `CLAUDE.md` - Update project context
- ⬜ Remove old writer documentation

### New Documentation

- ⬜ `docs/DASHBOARD_DATA_SPEC.md` - Data specification
- ⬜ `docs/shared_memory_fields.txt` - API exploration results
- ⬜ `docs/rest_api_responses.txt` - API exploration results
- ⬜ User guide for monitor setup

---

## Questions to Resolve

Before starting:
1. ✅ Deployment: Local server or cloud? (See RACE_DASHBOARD_PLAN.md)
2. ✅ Update rate: 2Hz (confirmed in plan)
3. ⬜ Session ID: Auto or manual? (Auto recommended)
4. ⬜ Data retention: In-memory only? (Yes for MVP)

---

## Getting Help

- **GitHub Issues:** [1Lap/monitor/issues](https://github.com/1Lap/monitor/issues)
- **Plan Document:** `RACE_DASHBOARD_PLAN.md`
- **Bug Files:** `bugs/` directory

---

## Progress Tracking

Track progress by marking tasks complete:

```bash
# Example: Mark task as complete
echo "✅ COMPLETE" >> bugs/api_exploration_shared_memory.md
```

Or use GitHub issues/project board.

---

## Estimated Timeline

- **Minimum (experienced developer):** 3-5 days
- **Comfortable (with testing):** 5-7 days
- **Including Windows validation:** 7-10 days

**Total estimated time:** 16-24 hours of development

---

**Last Updated:** 2025-11-22
**Status:** Ready to begin implementation
