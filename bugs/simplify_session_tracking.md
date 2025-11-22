# Task: Simplify Session Tracking for Monitor

**Type:** Refactoring
**Priority:** Medium
**Phase:** MVP - Phase 1
**Estimated Time:** 1-2 hours

---

## Overview

Simplify or remove the `SessionManager` class from the writer codebase, as the monitor doesn't need complex lap tracking and buffering. The monitor only needs to track whether setup data has been sent.

## Current Problem

The `SessionManager` from writer is designed for CSV lap logging:
- Tracks session state (IDLE → DETECTED → LOGGING)
- Buffers telemetry samples per lap
- Detects lap changes
- Normalizes samples
- Triggers callbacks on lap completion

**For dashboard monitoring, we only need:**
- Track if setup has been sent (boolean flag)
- No lap tracking
- No sample buffering
- No lap completion callbacks

## Objective

Decide on one of these approaches:

### Option 1: Remove SessionManager Entirely ✅ RECOMMENDED

Remove `SessionManager` and handle session state directly in `monitor.py`:

```python
class Monitor:
    def __init__(self, config_path: str = 'config.json'):
        # ...
        self.setup_sent = False  # Simple flag instead of SessionManager

    def _send_setup(self):
        """Fetch and send setup data once"""
        if self.setup_sent:
            return  # Already sent

        setup = self.rest_api.fetch_setup_data()
        if setup:
            self.publisher.publish_setup(setup)
            self.setup_sent = True
```

**Pros:**
- Simpler code
- Less dependencies
- Clearer logic
- No unnecessary abstractions

**Cons:**
- None for dashboard use case

### Option 2: Create Minimal SessionTracker

Create a lightweight `SessionTracker` just for setup state:

```python
class SessionTracker:
    """Minimal session tracking for dashboard monitor"""

    def __init__(self):
        self.session_active = False
        self.setup_sent = False
        self.session_id = None

    def start_session(self, session_id: str):
        """Start new session"""
        self.session_active = True
        self.session_id = session_id
        self.setup_sent = False

    def end_session(self):
        """End current session"""
        self.session_active = False
        self.setup_sent = False
        self.session_id = None

    def mark_setup_sent(self):
        """Mark setup as sent"""
        self.setup_sent = True

    def is_setup_sent(self) -> bool:
        """Check if setup has been sent"""
        return self.setup_sent
```

**Pros:**
- Encapsulated logic
- Easier to extend later
- Clear API

**Cons:**
- Extra abstraction for simple need
- More code to maintain

### Option 3: Keep SessionManager and Simplify

Keep `SessionManager` but remove lap tracking:
- Remove lap change detection
- Remove sample buffering
- Remove lap completion callbacks
- Keep session state tracking

**Pros:**
- Familiar structure from writer
- Can add features later

**Cons:**
- Still more complex than needed
- Carries unnecessary code

## Recommendation

**Use Option 1: Remove SessionManager entirely**

The monitor's needs are simple:
1. Track if setup has been sent (boolean)
2. Reset flag when LMU restarts (process detection)

No need for abstractions or complex state management.

## Implementation

### 1. Remove SessionManager

```bash
git rm src/session_manager.py
git rm tests/test_session_manager.py
```

### 2. Update Monitor

Handle state directly in `monitor.py`:

```python
class Monitor:
    """Main monitor application"""

    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self.running = False
        self.setup_sent = False  # Simple flag
        self.lmu_was_running = False  # Track LMU state

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

    def start(self):
        """Start monitor"""
        # ... connection logic ...

        self.running = True
        update_interval = 1.0 / self.config['update_rate_hz']
        last_update = 0

        while self.running:
            lmu_running = self.process_monitor.is_running()

            # Detect LMU restart
            if lmu_running and not self.lmu_was_running:
                print("[Monitor] LMU detected")
                self.setup_sent = False  # Reset for new session

            # Detect LMU stop
            if not lmu_running and self.lmu_was_running:
                print("[Monitor] LMU stopped")
                self.setup_sent = False

            self.lmu_was_running = lmu_running

            if not lmu_running:
                time.sleep(1)
                continue

            # Send setup once per session
            if not self.setup_sent:
                self._send_setup()

            # Publish telemetry at configured rate
            current_time = time.time()
            if current_time - last_update >= update_interval:
                self._send_telemetry()
                last_update = current_time

            time.sleep(self.config['poll_interval'])

    def _send_setup(self):
        """Fetch and send setup data once"""
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
            self.setup_sent = True
```

### 3. Update Tests

Remove session manager tests:
```bash
git rm tests/test_session_manager.py
```

Add simple state tests to `test_monitor_integration.py`:
```python
def test_setup_sent_flag():
    """Test setup sent flag logic"""
    monitor = Monitor('test_config.json')

    # Initially not sent
    assert not monitor.setup_sent

    # After sending
    monitor._send_setup()
    assert monitor.setup_sent

def test_lmu_restart_resets_setup():
    """Test setup flag resets on LMU restart"""
    # TODO: Test LMU restart detection
    pass
```

## Session State in Monitor

The monitor tracks these states:

| State | Flag | Behavior |
|-------|------|----------|
| LMU stopped | `setup_sent = False` | Wait for LMU |
| LMU started | `setup_sent = False` | Fetch setup once |
| Setup sent | `setup_sent = True` | Only send telemetry |
| LMU restart | `setup_sent = False` | Fetch setup again |

## Validation Checklist

- [ ] SessionManager removed (or simplified)
- [ ] Setup sent flag works correctly
- [ ] LMU restart detection works
- [ ] Setup fetched once per session
- [ ] Tests updated
- [ ] No regressions in core functionality

## Files to Modify

- `monitor.py` - Add setup_sent flag logic
- `src/session_manager.py` - Remove (Option 1) or simplify (Option 2/3)
- `tests/test_session_manager.py` - Remove or update
- `tests/test_monitor_integration.py` - Add state tests

## Related Files

- `bugs/create_monitor_entry_point.md` - Monitor implementation
- `bugs/cleanup_writer_components.md` - Component removal

---

**Next Steps:** Implement chosen approach when creating monitor.py entry point.
